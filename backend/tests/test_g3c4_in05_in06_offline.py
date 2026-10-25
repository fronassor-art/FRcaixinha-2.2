"""G3-C.4 IN-05/IN-06: provas e contraexemplos offline.

Nao conecta ao PostgreSQL e nao instala/aplica a migration F2P4.
Testes verdes de lacunas documentam limites, nao resolucao transacional.
"""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID

from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.schema import CreateIndex, CreateTable

from app.crypto_documents import DocumentCrypto, DocumentKeySet
from app.db.models import ContractingParty, IdentityCredential, UserIdentity
from app.identity_registration_offline import (
    RegistrationPreparationError, prepare_pf_registration,
    prepare_pj_registration,
)


class _Probe:
    def __init__(self, *, cpf=False, email=False, cnpj=False):
        self.cpf = cpf
        self.email = email
        self.cnpj = cnpj

    def cpf_exists(self, _value):
        return self.cpf

    def email_exists(self, _value):
        return self.email

    def cnpj_exists(self, _value):
        return self.cnpj


class G3C4In05In06OfflineTests(unittest.TestCase):
    def setUp(self):
        self.crypto = DocumentCrypto(
            {"synthetic": DocumentKeySet(
                "synthetic", b"E" * 32, b"L" * 32,
            )}, current_key_id="synthetic",
        )

    def pf(self, *, identity_id=101, party_id=201, probe=None):
        return prepare_pf_registration(
            name="Pessoa Exemplo", cpf="529.982.247-25",
            email="PERSON@EXAMPLE.COM", phone="(91) 91234-5678",
            identity_id=UUID(int=identity_id), party_id=UUID(int=party_id),
            crypto=self.crypto, probe=probe or _Probe(),
        )

    def pj(self, *, identity_id=301, party_id=401, probe=None):
        return prepare_pj_registration(
            legal_name="Empresa Exemplo Ltda",
            cnpj="12.ABC.345/01DE-35",
            representative_name="Pessoa Exemplo",
            representative_cpf="529.982.247-25",
            representative_email="PERSON@EXAMPLE.COM",
            representative_phone="(91) 91234-5678",
            identity_id=UUID(int=identity_id), party_id=UUID(int=party_id),
            crypto=self.crypto, probe=probe or _Probe(),
        )

    def test_in05_orm_onupdate_is_not_database_server_onupdate(self):
        """Onupdate in SQLAlchemy is not a PostgreSQL trigger."""
        for model in (UserIdentity, ContractingParty, IdentityCredential):
            with self.subTest(model=model.__name__):
                col = model.__table__.c.updated_at
                self.assertIsNotNone(col.server_default)
                self.assertIsNotNone(col.onupdate)
                self.assertIsNone(col.server_onupdate)
                sql = str(CreateTable(model.__table__).compile(
                    dialect=dialect(),
                ))
                self.assertIn("updated_at TIMESTAMP WITH TIME ZONE", sql)
                self.assertNotIn("CREATE TRIGGER", sql)

    def test_in05_python_uuid_default_is_not_server_default(self):
        """Offline metadata does not prove UUID generation in raw SQL."""
        for model in (UserIdentity, ContractingParty, IdentityCredential):
            with self.subTest(model=model.__name__):
                col = model.__table__.c.id
                self.assertIsNotNone(col.default)
                self.assertIsNone(col.server_default)
                sql = str(CreateTable(model.__table__).compile(
                    dialect=dialect(),
                ))
                self.assertIn("id UUID NOT NULL", sql)

    def test_in05_create_table_compilation_has_no_write_time_trigger(self):
        """Compiled DDL alone does not prove any future production setup."""
        for model in (UserIdentity, ContractingParty, IdentityCredential):
            with self.subTest(model=model.__name__):
                ddl = str(CreateTable(model.__table__).compile(
                    dialect=dialect(),
                ))
                self.assertNotIn("ON UPDATE", ddl)
                self.assertNotIn("CREATE FUNCTION", ddl)
                self.assertNotIn("CREATE TRIGGER", ddl)

    def test_in06_global_cpf_uniqueness_also_covers_pending(self):
        table = UserIdentity.__table__
        self.assertTrue(table.c.cpf_lookup_hmac.unique)
        status_checks = [
            str(c.sqltext) for c in table.constraints
            if isinstance(c, CheckConstraint)
            and c.name == "ck_user_identities_status_valid"
        ]
        self.assertEqual(len(status_checks), 1)
        self.assertIn("'PENDENTE'", status_checks[0])
        self.assertIn(
            "UNIQUE (cpf_lookup_hmac)",
            str(CreateTable(table).compile(dialect=dialect())),
        )

    def test_in06_global_lower_email_unique_index_is_not_conditional(self):
        table = UserIdentity.__table__
        idx = next(
            item for item in table.indexes
            if item.name == "uq_user_identities_email_lower"
        )
        self.assertTrue(idx.unique)
        self.assertIsNone(idx.dialect_options["postgresql"]["where"])
        self.assertEqual(
            str(CreateIndex(idx).compile(dialect=dialect())),
            "CREATE UNIQUE INDEX uq_user_identities_email_lower "
            "ON user_identities (lower(email))",
        )

    def test_in06_global_cnpj_uniqueness_also_covers_preliminary(self):
        table = ContractingParty.__table__
        self.assertTrue(table.c.tax_id_lookup_hmac.unique)
        self.assertIn(
            "UNIQUE (tax_id_lookup_hmac)",
            str(CreateTable(table).compile(dialect=dialect())),
        )
        status_checks = [
            str(c.sqltext) for c in table.constraints
            if isinstance(c, CheckConstraint)
            and c.name == "ck_contracting_parties_status_valid"
        ]
        self.assertEqual(len(status_checks), 1)
        self.assertIn("'PRELIMINAR'", status_checks[0])

    def test_in06_repeated_pf_document_has_same_global_hmac(self):
        first = self.pf(identity_id=101, party_id=201)
        second = self.pf(identity_id=102, party_id=202)
        self.assertEqual(
            first.identity.cpf_lookup_hmac, second.identity.cpf_lookup_hmac,
        )
        self.assertNotEqual(
            first.identity.cpf_ciphertext, second.identity.cpf_ciphertext,
        )
        self.assertEqual(first.identity.email, second.identity.email)
        self.assertEqual(first.identity.status, "PENDENTE")
        self.assertEqual(second.identity.status, "PENDENTE")

    def test_in06_pf_and_pj_representative_share_global_cpf_lookup(self):
        pf = self.pf()
        pj = self.pj()
        self.assertEqual(
            pf.identity.cpf_lookup_hmac, pj.identity.cpf_lookup_hmac,
        )
        self.assertNotEqual(
            pf.identity.cpf_ciphertext, pj.identity.cpf_ciphertext,
        )
        self.assertEqual(pj.identity.status, "PENDENTE")
        self.assertEqual(pj.party.status, "PRELIMINAR")

    def test_in06_pending_duplicate_probe_rejects_before_proof_of_ownership(self):
        """A generic conflict check cannot prove claimant owns reserved CPF."""
        with self.assertRaisesRegex(
            RegistrationPreparationError, "^IDENTITY_CONFLICT$",
        ):
            self.pf(probe=_Probe(cpf=True))

    def test_in06_preliminary_cnpj_probe_rejects_before_representation_proof(self):
        """Same CNPJ blocks this candidate; no takeover is justified."""
        first = self.pj()
        self.assertEqual(first.party.status, "PRELIMINAR")
        self.assertEqual(first.party.party_type, "PJ")
        with self.assertRaisesRegex(
            RegistrationPreparationError, "^PARTY_CONFLICT$",
        ):
            self.pj(identity_id=302, party_id=402,
                    probe=_Probe(cnpj=True))

    def test_in06_duplicate_pj_representative_email_is_not_ownership_proof(self):
        with self.assertRaisesRegex(
            RegistrationPreparationError, "^IDENTITY_CONFLICT$",
        ):
            self.pj(probe=_Probe(email=True))

    def test_in06_uncertain_email_or_cnpj_probe_fails_without_disclosure(self):
        for prepare, method in (
            (self.pf, "email_exists"),
            (self.pj, "email_exists"),
            (self.pj, "cnpj_exists"),
        ):
            with self.subTest(flow=prepare.__name__, method=method):
                probe = _Probe()
                with patch.object(probe, method, return_value=1):
                    with self.assertRaisesRegex(
                        RegistrationPreparationError, "^CONFLICT_CHECK_FAILED$",
                    ):
                        prepare(probe=probe)
                with patch.object(
                    probe, method,
                    side_effect=RuntimeError(
                        "52998224725 12ABC34501DE35 PERSON@EXAMPLE.COM SECRET"
                    ),
                ):
                    with self.assertRaises(RegistrationPreparationError) as caught:
                        prepare(probe=probe)
                self.assertEqual(str(caught.exception), "CONFLICT_CHECK_FAILED")
                self.assertIsNone(caught.exception.__cause__)
                for secret in (
                    "52998224725", "12ABC34501DE35", "PERSON@EXAMPLE.COM",
                    "SECRET",
                ):
                    self.assertNotIn(secret, repr(caught.exception))

    def test_in05_in06_no_implicit_pg_network_or_file_access(self):
        with patch("psycopg.connect") as db, patch("socket.socket") as net:
            with patch("builtins.open") as file:
                self.pf()
                self.pj()
                str(CreateTable(UserIdentity.__table__).compile(
                    dialect=dialect(),
                ))
        db.assert_not_called()
        net.assert_not_called()
        file.assert_not_called()


if __name__ == "__main__":
    unittest.main()
