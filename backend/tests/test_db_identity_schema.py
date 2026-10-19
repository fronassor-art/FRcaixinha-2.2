"""Testes de esquema sem conexao ao PostgreSQL."""

import re
import unittest

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.schema import CreateIndex, CreateTable

from app.db.models import Base, ContractingParty, UserIdentity


class IdentitySchemaTests(unittest.TestCase):
    def test_only_initial_tables_are_declared(self):
        self.assertEqual(
            set(Base.metadata.tables),
            {"user_identities", "contracting_parties", "tenants", "cycles", "role_grants"},
        )

    def test_sensitive_documents_are_not_plaintext_columns(self):
        cases = (
            (UserIdentity, "cpf_ciphertext", "cpf_lookup_hmac", "cpf", False),
            (
                ContractingParty,
                "tax_id_ciphertext",
                "tax_id_lookup_hmac",
                "cpf_or_cnpj",
                True,
            ),
        )

        for entity, encrypted, lookup, plaintext, nullable in cases:
            with self.subTest(entity=entity.__name__):
                columns = entity.__table__.c
                self.assertIn(encrypted, columns)
                self.assertIn(lookup, columns)
                self.assertNotIn(plaintext, columns)
                self.assertEqual(columns[encrypted].nullable, nullable)
                self.assertEqual(columns[lookup].nullable, nullable)
                self.assertTrue(columns[lookup].unique)

    def test_identifiers_and_timestamps(self):
        for entity in (UserIdentity, ContractingParty):
            with self.subTest(entity=entity.__name__):
                columns = entity.__table__.c
                self.assertTrue(columns.id.primary_key)
                self.assertFalse(columns.created_at.nullable)
                self.assertTrue(columns.created_at.type.timezone)
                self.assertFalse(columns.updated_at.nullable)
                self.assertTrue(columns.updated_at.type.timezone)

    def test_status_domains_and_initial_values(self):
        cases = (
            (
                UserIdentity,
                "PENDENTE",
                "status IN ('PENDENTE', 'ATIVA', 'SUSPENSA', 'ENCERRADA')",
            ),
            (
                ContractingParty,
                "PRELIMINAR",
                "status IN ('PRELIMINAR', 'EM_ANALISE', 'APTO', "
                "'SUSPENSO', 'ENCERRADO')",
            ),
        )
        for entity, initial, expected_check in cases:
            with self.subTest(entity=entity.__name__):
                table = entity.__table__
                status = table.c.status
                self.assertFalse(status.nullable)
                self.assertEqual(status.type.length, 32)
                self.assertEqual(status.default.arg, initial)
                self.assertEqual(str(status.server_default.arg), f"'{initial}'")
                checks = [
                    constraint
                    for constraint in table.constraints
                    if isinstance(constraint, CheckConstraint)
                    and constraint.name == f"ck_{table.name}_status_valid"
                ]
                self.assertEqual(len(checks), 1)
                self.assertEqual(str(checks[0].sqltext), expected_check)

    def test_status_domains_exclude_invalid_and_foreign_values(self):
        approved = (
            (UserIdentity, ("PENDENTE", "ATIVA", "SUSPENSA", "ENCERRADA")),
            (
                ContractingParty,
                ("PRELIMINAR", "EM_ANALISE", "APTO", "SUSPENSO", "ENCERRADO"),
            ),
        )
        for entity, expected in approved:
            with self.subTest(entity=entity.__name__):
                check = next(
                    constraint
                    for constraint in entity.__table__.constraints
                    if isinstance(constraint, CheckConstraint)
                    and constraint.name == f"ck_{entity.__tablename__}_status_valid"
                )
                values = tuple(re.findall(r"'([^']*)'", str(check.sqltext)))
                self.assertEqual(values, expected)
                for invalid in (
                    "", " ", "\t", "UNKNOWN",
                    f" {expected[0]}", f"{expected[0]} ",
                ):
                    self.assertNotIn(invalid, values)
        user_values = set(approved[0][1])
        party_values = set(approved[1][1])
        self.assertTrue(user_values.isdisjoint(party_values))

    def test_party_links_have_distinct_foreign_keys(self):
        columns = ContractingParty.__table__.c
        for name in ("pf_user_id", "representative_user_id"):
            with self.subTest(column=name):
                self.assertTrue(columns[name].nullable)
                self.assertEqual(
                    {fk.target_fullname for fk in columns[name].foreign_keys},
                    {"user_identities.id"},
                )
        self.assertIsNot(columns.pf_user_id, columns.representative_user_id)
        self.assertTrue(columns.pf_user_id.unique)
        self.assertFalse(columns.party_type.nullable)

    def test_pj_representation_records_are_separate_and_optional(self):
        columns = ContractingParty.__table__.c
        references = (
            "representation_declaration_ref",
            "representation_evidence_ref",
            "representation_verification_ref",
        )
        for name in references:
            with self.subTest(column=name):
                column = columns[name]
                self.assertTrue(column.nullable)
                self.assertIsInstance(column.type, String)
                self.assertEqual(column.type.length, 512)
                self.assertIsNone(column.default)
                self.assertIsNone(column.server_default)
        verified_at = columns.representation_verified_at
        self.assertTrue(verified_at.nullable)
        self.assertIsInstance(verified_at.type, DateTime)
        self.assertTrue(verified_at.type.timezone)
        self.assertIsNone(verified_at.default)
        self.assertIsNone(verified_at.server_default)
        self.assertEqual(len({columns[name] for name in references}), 3)

    def test_party_type_link_checks(self):
        checks = {
            constraint.name: str(constraint.sqltext)
            for constraint in ContractingParty.__table__.constraints
            if isinstance(constraint, CheckConstraint)
        }
        self.assertEqual(
            checks,
            {
                "ck_contracting_parties_status_valid":
                    "status IN ('PRELIMINAR', 'EM_ANALISE', 'APTO', "
                    "'SUSPENSO', 'ENCERRADO')",
                "ck_contracting_parties_party_type_valid":
                    "party_type IN ('PF', 'PJ')",
                "ck_contracting_parties_pj_representative_required":
                    "party_type = 'PF' OR representative_user_id IS NOT NULL",
                "ck_contracting_parties_pf_identity_required":
                    "party_type = 'PJ' OR pf_user_id IS NOT NULL",
                "ck_contracting_parties_pf_representative_absent":
                    "party_type = 'PJ' OR representative_user_id IS NULL",
                "ck_contracting_parties_pj_pf_identity_absent":
                    "party_type = 'PF' OR pf_user_id IS NULL",
                "ck_contracting_parties_pf_pj_document_absent":
                    "party_type = 'PJ' OR (tax_id_ciphertext IS NULL "
                    "AND tax_id_lookup_hmac IS NULL)",
                "ck_contracting_parties_pj_cnpj_required":
                    "party_type = 'PF' OR (tax_id_ciphertext IS NOT NULL "
                    "AND tax_id_lookup_hmac IS NOT NULL)",
                "ck_contracting_parties_pf_representation_fields_absent":
                    "party_type = 'PJ' OR (representation_declaration_ref IS NULL "
                    "AND representation_evidence_ref IS NULL "
                    "AND representation_verification_ref IS NULL "
                    "AND representation_verified_at IS NULL)",
                "ck_contracting_parties_representation_verification_evidenced":
                    "representation_verified_at IS NULL OR (party_type = 'PJ' "
                    "AND representation_declaration_ref IS NOT NULL "
                    "AND representation_verification_ref IS NOT NULL)",
                "ck_contracting_parties_pj_apto_representation_verified":
                    "party_type = 'PF' OR status <> 'APTO' OR "
                    "(representative_user_id IS NOT NULL "
                    "AND representation_declaration_ref IS NOT NULL "
                    "AND representation_verification_ref IS NOT NULL "
                    "AND representation_verified_at IS NOT NULL)",
                "ck_contracting_parties_representation_declaration_ref_nonblank":
                    "representation_declaration_ref IS NULL OR "
                    "representation_declaration_ref ~ '[^[:space:]]'",
                "ck_contracting_parties_representation_evidence_ref_nonblank":
                    "representation_evidence_ref IS NULL OR "
                    "representation_evidence_ref ~ '[^[:space:]]'",
                "ck_contracting_parties_representation_verification_ref_nonblank":
                    "representation_verification_ref IS NULL OR "
                    "representation_verification_ref ~ '[^[:space:]]'",
            },
        )

    def test_party_document_source_matches_party_type(self):
        """Especificacao logica; nao executa as CHECKs no PostgreSQL."""
        columns = ContractingParty.__table__.c
        self.assertTrue(columns.tax_id_ciphertext.nullable)
        self.assertTrue(columns.tax_id_lookup_hmac.nullable)
        self.assertTrue(columns.tax_id_lookup_hmac.unique)
        self.assertTrue(columns.pf_user_id.unique)

        cases = (
            ("PF", "pf-user", None, None, True),
            ("PF", "pf-user", b"documento-pj", None, False),
            ("PF", "pf-user", None, b"lookup-pj", False),
            ("PF", "pf-user", b"documento-pj", b"lookup-pj", False),
            ("PJ", None, b"documento-pj", b"lookup-pj", True),
            ("PJ", None, None, b"lookup-pj", False),
            ("PJ", None, b"documento-pj", None, False),
            ("PJ", None, None, None, False),
        )
        for party_type, pf_user_id, document, lookup, valid in cases:
            with self.subTest(
                party_type=party_type,
                pf_user_id=pf_user_id,
                document=document,
                lookup=lookup,
            ):
                has_document = document is not None and lookup is not None
                no_document = document is None and lookup is None
                expected = (
                    (party_type == "PF" and pf_user_id is not None and no_document)
                    or (party_type == "PJ" and pf_user_id is None and has_document)
                )
                self.assertEqual(expected, valid)

    def test_pj_aptitude_requires_representation_records(self):
        """Matriz de requisitos; autenticidade depende do servico futuro."""
        cases = (
            ("PJ", "PRELIMINAR", "representative", None, None, None, True),
            ("PJ", "APTO", None, "declaration", "verification", "date", False),
            ("PJ", "APTO", "representative", None, "verification", "date", False),
            ("PJ", "APTO", "representative", "declaration", None, "date", False),
            ("PJ", "APTO", "representative", "declaration", "verification", None, False),
            ("PJ", "APTO", "representative", "", "verification", "date", False),
            ("PJ", "APTO", "representative", "  ", "verification", "date", False),
            ("PJ", "APTO", "representative", "declaration", " \t ", "date", False),
            ("PJ", "APTO", "representative", "declaration", "verification", "date", True),
        )
        for party_type, status, representative, declaration, verification, at, valid in cases:
            with self.subTest(status=status, declaration=declaration, verification=verification):
                structural = (
                    party_type != "PJ"
                    or status != "APTO"
                    or all(
                        value is not None
                        for value in (representative, declaration, verification, at)
                    )
                )
                nonblank = all(
                    value is None or bool(re.search(r"\S", value))
                    for value in (declaration, verification)
                )
                self.assertEqual(structural and nonblank, valid)

    def test_representation_references_reject_blank_values(self):
        checks = {
            constraint.name: str(constraint.sqltext)
            for constraint in ContractingParty.__table__.constraints
            if isinstance(constraint, CheckConstraint)
        }
        for name in (
            "representation_declaration_ref",
            "representation_evidence_ref",
            "representation_verification_ref",
        ):
            with self.subTest(column=name):
                self.assertEqual(
                    checks[f"ck_contracting_parties_{name}_nonblank"],
                    f"{name} IS NULL OR {name} ~ '[^[:space:]]'",
                )
                for value, valid in (
                    (None, True),
                    ("opaque-ref", True),
                    ("", False),
                    (" ", False),
                    (" \t\n ", False),
                ):
                    self.assertEqual(
                        value is None or bool(re.search(r"\S", value)),
                        valid,
                    )

    def test_party_link_checks_accept_only_consistent_combinations(self):
        """Valida a logica das CHECKs sem executar SQL em um banco."""
        checks = [
            str(constraint.sqltext)
            for constraint in ContractingParty.__table__.constraints
            if isinstance(constraint, CheckConstraint)
            and constraint.name in {
                "ck_contracting_parties_party_type_valid",
                "ck_contracting_parties_pj_representative_required",
                "ck_contracting_parties_pf_identity_required",
                "ck_contracting_parties_pf_representative_absent",
                "ck_contracting_parties_pj_pf_identity_absent",
            }
        ]
        self.assertEqual(len(checks), 5)
        cases = (
            ("PF", "pf-user", None, True),
            ("PJ", None, "pj-representative", True),
            ("PF", None, None, False),
            ("PF", None, "pj-representative", False),
            ("PF", "pf-user", "pj-representative", False),
            ("PJ", None, None, False),
            ("PJ", "pf-user", None, False),
            ("PJ", "pf-user", "pj-representative", False),
            ("XX", "pf-user", None, False),
        )
        predicate = re.compile(
            r"party_type = '(PF|PJ)' OR "
            r"(pf_user_id|representative_user_id) IS (NOT )?NULL"
        )
        for party_type, pf_user_id, representative_user_id, valid in cases:
            with self.subTest(
                party_type=party_type,
                pf_user_id=pf_user_id,
                representative_user_id=representative_user_id,
            ):
                values = {
                    "pf_user_id": pf_user_id,
                    "representative_user_id": representative_user_id,
                }
                results = []
                for expression in checks:
                    if expression == "party_type IN ('PF', 'PJ')":
                        results.append(party_type in ("PF", "PJ"))
                        continue
                    match = predicate.fullmatch(expression)
                    self.assertIsNotNone(match, expression)
                    allowed_type, column, not_null = match.groups()
                    results.append(
                        party_type == allowed_type
                        or (values[column] is not None) == bool(not_null)
                    )
                self.assertEqual(all(results), valid)

    def test_postgresql_ddl_compiles_without_connection(self):
        user_ddl = str(
            CreateTable(UserIdentity.__table__).compile(
                dialect=dialect()
            )
        )
        party_ddl = str(
            CreateTable(ContractingParty.__table__).compile(
                dialect=dialect()
            )
        )

        self.assertIn("BYTEA", user_ddl)
        self.assertIn("BYTEA", party_ddl)
        self.assertIn("DEFAULT 'PENDENTE' NOT NULL", user_ddl)
        self.assertIn("DEFAULT 'PRELIMINAR' NOT NULL", party_ddl)
        self.assertIn(
            "CONSTRAINT ck_user_identities_status_valid CHECK "
            "(status IN ('PENDENTE', 'ATIVA', 'SUSPENSA', 'ENCERRADA'))",
            user_ddl,
        )
        self.assertIn(
            "CONSTRAINT ck_contracting_parties_status_valid CHECK "
            "(status IN ('PRELIMINAR', 'EM_ANALISE', 'APTO', "
            "'SUSPENSO', 'ENCERRADO'))",
            party_ddl,
        )
        self.assertIn(
            "FOREIGN KEY(pf_user_id) REFERENCES user_identities (id)",
            party_ddl,
        )
        self.assertIn(
            "FOREIGN KEY(representative_user_id)",
            party_ddl,
        )
        self.assertIn(
            "party_type = 'PJ' OR pf_user_id IS NOT NULL",
            party_ddl,
        )
        self.assertIn(
            "party_type = 'PJ' OR representative_user_id IS NULL",
            party_ddl,
        )
        self.assertIn(
            "party_type = 'PF' OR pf_user_id IS NULL",
            party_ddl,
        )
        self.assertIn("party_type IN ('PF', 'PJ')", party_ddl)
        self.assertIn("UNIQUE (pf_user_id)", party_ddl)
        self.assertIn("UNIQUE (tax_id_lookup_hmac)", party_ddl)
        self.assertIn("TIMESTAMP WITH TIME ZONE", user_ddl)
        for fragment in (
            "party_type = 'PJ' OR (tax_id_ciphertext IS NULL "
            "AND tax_id_lookup_hmac IS NULL)",
            "party_type = 'PF' OR (tax_id_ciphertext IS NOT NULL "
            "AND tax_id_lookup_hmac IS NOT NULL)",
            "representation_declaration_ref VARCHAR(512)",
            "representation_evidence_ref VARCHAR(512)",
            "representation_verification_ref VARCHAR(512)",
            "representation_verified_at TIMESTAMP WITH TIME ZONE",
            "party_type = 'PJ' OR (representation_declaration_ref IS NULL "
            "AND representation_evidence_ref IS NULL "
            "AND representation_verification_ref IS NULL "
            "AND representation_verified_at IS NULL)",
            "representation_verified_at IS NULL OR (party_type = 'PJ' "
            "AND representation_declaration_ref IS NOT NULL "
            "AND representation_verification_ref IS NOT NULL)",
            "party_type = 'PF' OR status <> 'APTO' OR "
            "(representative_user_id IS NOT NULL "
            "AND representation_declaration_ref IS NOT NULL "
            "AND representation_verification_ref IS NOT NULL "
            "AND representation_verified_at IS NOT NULL)",
            "representation_declaration_ref IS NULL OR "
            "representation_declaration_ref ~ '[^[:space:]]'",
            "representation_evidence_ref IS NULL OR "
            "representation_evidence_ref ~ '[^[:space:]]'",
            "representation_verification_ref IS NULL OR "
            "representation_verification_ref ~ '[^[:space:]]'",
        ):
            with self.subTest(ddl_fragment=fragment):
                self.assertIn(fragment, party_ddl)

    def test_email_unique_case_insensitive_index(self):
        table = UserIdentity.__table__
        self.assertFalse(table.c.email.unique)

        indexes = [
            index for index in table.indexes
            if index.name == "uq_user_identities_email_lower"
        ]

        self.assertEqual(len(indexes), 1)
        self.assertTrue(indexes[0].unique)

        sql = str(
            CreateIndex(indexes[0]).compile(
                dialect=dialect()
            )
        )

        self.assertIn(
            "CREATE UNIQUE INDEX "
            "uq_user_identities_email_lower "
            "ON user_identities (lower(email))",
            sql,
        )
