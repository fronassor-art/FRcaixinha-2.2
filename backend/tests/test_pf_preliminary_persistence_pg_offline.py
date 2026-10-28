"""Contrato de escrita PF em SQL compilado e mocks; nenhum PostgreSQL é aberto."""

import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, create_autospec, patch
from uuid import UUID

from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection

from app.crypto_documents import DocumentCrypto, DocumentKeySet
from app.g3c_transaction_guards_offline import TransactionGateError
from app.identity_persistence_contract import PreliminaryCommitResult
from app.identity_registration_offline import prepare_pf_registration
from app.offline_credentials import SessionFacts
from app.pf_preliminary_persistence_pg import (
    PfPreliminaryStorageUnavailable, _prepare_digests,
    complete_pf_statement, reserve_pf_statement,
    write_pf_preliminary_within_transaction,
)
from app.trusted_auth_subject import VerifiedAuthAssertion


NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)
IDENTITY = UUID("00000000-0000-4000-8000-000000000501")
PARTY = UUID("00000000-0000-4000-8000-000000000502")
RESERVATION = UUID("00000000-0000-4000-8000-000000000503")
ASSERTION = b"synthetic-verified-assertion"
KEY = b"K" * 32
ATTEMPT = b"synthetic-attempt-key-001"


class EmptyProbe:
    def cpf_exists(self, _value): return False
    def email_exists(self, _value): return False
    def cnpj_exists(self, _value): return False


class FixedVerifier:
    def __init__(self, fact): self.fact = fact
    def verify_assertion(self, _assertion): return self.fact


class PfPreliminaryPgOfflineTests(unittest.TestCase):
    def setUp(self):
        self.crypto = DocumentCrypto({"synthetic": DocumentKeySet(
            "synthetic", b"E" * 32, b"L" * 32,
        )}, current_key_id="synthetic")
        self.registration = self.prepare(IDENTITY, PARTY)
        self.session = SessionFacts(
            IDENTITY, NOW - timedelta(minutes=1),
            NOW + timedelta(minutes=14), None,
        )
        self.verifier = FixedVerifier(VerifiedAuthAssertion(
            "local", "frcaixinha-api", IDENTITY, self.session,
        ))
        self.connection = create_autospec(Connection, instance=True)

    def prepare(self, identity_id, party_id, *, name="Pessoa Ficticia",
                email="person@example.org", phone="(91) 91234-5678"):
        return prepare_pf_registration(
            name=name, cpf="529.982.247-25", email=email,
            phone=phone, identity_id=identity_id,
            party_id=party_id, crypto=self.crypto, probe=EmptyProbe(),
        )

    def args(self, **changes):
        kwargs = dict(
            registration=self.registration, assertion=ASSERTION,
            verifier=self.verifier, expected_issuer="local",
            idempotency_key=ATTEMPT, crypto=self.crypto,
            digest_key=KEY,
        )
        kwargs.update(changes)
        return kwargs

    def digests(self, **changes):
        return _prepare_digests(now=NOW, **self.args(**changes))[0]

    def run_writer(self, *responses, **changes):
        self.connection.execute.side_effect = [
            Mock(scalar_one=Mock(return_value=NOW)), *responses,
        ]
        with patch(
            "app.pf_preliminary_persistence_pg.require_pg_transaction"
        ) as guard, patch(
            "app.pf_preliminary_persistence_pg.uuid4", return_value=RESERVATION,
        ):
            outcome = write_pf_preliminary_within_transaction(
                self.connection, **self.args(**changes),
            )
        guard.assert_called_once_with(self.connection, denial="PF_WRITE_DENIED")
        return outcome

    def test_protected_fingerprint_is_stable_despite_random_ciphertext(self):
        second = self.prepare(IDENTITY, PARTY)
        self.assertNotEqual(
            self.registration.identity.cpf_ciphertext,
            second.identity.cpf_ciphertext,
        )
        self.assertEqual(self.digests(), self.digests(registration=second))
        self.assertNotIn("person@example.org", repr(self.digests()))
        changed = self.prepare(IDENTITY, PARTY, name="Outra Pessoa Ficticia")
        self.assertNotEqual(
            self.digests().fingerprint,
            self.digests(registration=changed).fingerprint,
        )
        self.assertNotEqual(
            self.digests().attempt,
            self.digests(idempotency_key=b"synthetic-attempt-key-002").attempt,
        )

    def test_valid_ten_digit_landline_remains_eligible(self):
        landline = self.prepare(
            IDENTITY, PARTY, phone="(91) 3234-5678",
        )
        self.assertEqual(landline.identity.phone, "9132345678")
        self.assertEqual(len(self.digests(registration=landline).fingerprint), 32)

    def test_sql_uses_unique_reservation_and_conditional_completion(self):
        digests = self.digests()
        reservation = str(reserve_pf_statement(
            digests, reservation_id=RESERVATION,
        ).compile(dialect=postgresql.dialect()))
        completion = str(complete_pf_statement(
            digests, reservation_id=RESERVATION,
            identity_id=IDENTITY, party_id=PARTY,
            session_expires_at=self.session.expires_at,
        ).compile(dialect=postgresql.dialect()))
        self.assertIn("ON CONFLICT ON CONSTRAINT uq_registration_idempotency_origin_attempt DO NOTHING", reservation)
        self.assertIn("statement_timestamp()", reservation)
        self.assertIn("INTERVAL '15 minutes'", reservation)
        self.assertIn("request_fingerprint =", completion)
        self.assertIn("expires_at > clock_timestamp()", completion)
        self.assertIn("clock_timestamp() <", completion)
        self.assertIn("RETURNING registration_idempotency.id", completion)

    def test_new_write_is_preliminary_and_uses_one_savepoint(self):
        outcome = self.run_writer(
            Mock(scalar_one_or_none=Mock(return_value=RESERVATION)),
            Mock(), Mock(),
            Mock(scalar_one_or_none=Mock(return_value=RESERVATION)),
        )
        self.assertEqual(outcome, PreliminaryCommitResult(IDENTITY, PARTY, True))
        self.connection.begin_nested.assert_called_once()
        self.connection.commit.assert_not_called()
        self.connection.rollback.assert_not_called()
        statements = [call.args[0] for call in self.connection.execute.call_args_list]
        compiled = " ".join(str(statement.compile(
            dialect=postgresql.dialect(),
        )) for statement in statements)
        for table in ("registration_idempotency", "user_identities",
                      "contracting_parties"):
            self.assertIn(table, compiled)
        for forbidden in ("identity_credentials", "role_grants", "tenants",
                          "membership", "license_", "financial_"):
            self.assertNotIn(forbidden, compiled)
        identity_values = statements[2].compile(dialect=postgresql.dialect()).params
        party_values = statements[3].compile(dialect=postgresql.dialect()).params
        self.assertEqual(identity_values["status"], "PENDENTE")
        self.assertEqual(party_values["status"], "PRELIMINAR")
        self.assertEqual(party_values["initial_registration_identity_id"], IDENTITY)

    def test_replay_returns_only_verified_ids_and_no_second_insert(self):
        self.connection.execute.side_effect = [
            Mock(scalar_one=Mock(return_value=NOW)),
            Mock(scalar_one_or_none=Mock(return_value=None)),
            Mock(scalar_one_or_none=Mock(return_value=f"local:{IDENTITY}")),
            Mock(scalar_one=Mock(return_value=NOW)),
        ]
        with patch("app.pf_preliminary_persistence_pg.require_pg_transaction"), \
                patch("app.pf_preliminary_persistence_pg.fetch_verified_completed_replay",
                      return_value=(IDENTITY, PARTY)) as replay:
            outcome = write_pf_preliminary_within_transaction(
                self.connection, **self.args(),
            )
        self.assertEqual(outcome, PreliminaryCommitResult(IDENTITY, PARTY, False))
        replay.assert_called_once()
        self.assertEqual(self.connection.execute.call_count, 4)

    def test_reserved_conflict_and_mismatched_replay_fail_closed(self):
        self.connection.execute.side_effect = [
            Mock(scalar_one=Mock(return_value=NOW)),
            Mock(scalar_one_or_none=Mock(return_value=None)),
        ]
        with patch("app.pf_preliminary_persistence_pg.require_pg_transaction"), \
                patch("app.pf_preliminary_persistence_pg.fetch_verified_completed_replay",
                      side_effect=TransactionGateError("REPLAY_DENIED")):
            with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
                write_pf_preliminary_within_transaction(
                    self.connection, **self.args(),
                )
        self.assertEqual(self.connection.execute.call_count, 2)

    def test_competing_reservation_cannot_replay_other_identity(self):
        self.connection.execute.side_effect = [
            Mock(scalar_one=Mock(return_value=NOW)),
            Mock(scalar_one_or_none=Mock(return_value=None)),
        ]
        with patch("app.pf_preliminary_persistence_pg.require_pg_transaction"), \
                patch("app.pf_preliminary_persistence_pg.fetch_verified_completed_replay",
                      return_value=(UUID(int=999), PARTY)):
            with self.assertRaisesRegex(TransactionGateError, "^PF_WRITE_DENIED$"):
                write_pf_preliminary_within_transaction(
                    self.connection, **self.args(),
                )
        self.assertEqual(self.connection.execute.call_count, 2)
        self.connection.begin_nested.return_value.__exit__.assert_called()

    def test_replay_after_session_expires_inside_transaction_is_denied(self):
        self.connection.execute.side_effect = [
            Mock(scalar_one=Mock(return_value=NOW)),
            Mock(scalar_one_or_none=Mock(return_value=None)),
            Mock(scalar_one_or_none=Mock(return_value=f"local:{IDENTITY}")),
            Mock(scalar_one=Mock(return_value=self.session.expires_at)),
        ]
        with patch("app.pf_preliminary_persistence_pg.require_pg_transaction"), \
                patch("app.pf_preliminary_persistence_pg.fetch_verified_completed_replay",
                      return_value=(IDENTITY, PARTY)):
            with self.assertRaisesRegex(TransactionGateError, "^PF_WRITE_DENIED$"):
                write_pf_preliminary_within_transaction(
                    self.connection, **self.args(),
                )
        self.assertEqual(self.connection.execute.call_count, 4)
        self.connection.begin_nested.return_value.__exit__.assert_called()

    def test_duplicate_cpf_or_email_constraint_error_is_neutral(self):
        for field in ("cpf", "email"):
            with self.subTest(field=field):
                self.connection.reset_mock()
                self.connection.execute.side_effect = [
                    Mock(scalar_one=Mock(return_value=NOW)),
                    Mock(scalar_one_or_none=Mock(return_value=RESERVATION)),
                    RuntimeError(f"duplicate {field} person@example.org"),
                ]
                with (
                    patch("app.pf_preliminary_persistence_pg.require_pg_transaction"),
                    patch("app.pf_preliminary_persistence_pg.uuid4", return_value=RESERVATION),
                ):
                    with self.assertRaisesRegex(
                        PfPreliminaryStorageUnavailable, "^PF_STORAGE_UNAVAILABLE$"
                    ) as error:
                        write_pf_preliminary_within_transaction(
                            self.connection, **self.args(),
                        )
                self.assertNotIn(field, str(error.exception))
                self.connection.begin_nested.return_value.__exit__.assert_called()
                self.connection.commit.assert_not_called()

    def test_failed_completion_exits_savepoint_with_exception(self):
        self.connection.execute.side_effect = [
            Mock(scalar_one=Mock(return_value=NOW)),
            Mock(scalar_one_or_none=Mock(return_value=RESERVATION)),
            Mock(), Mock(),
            Mock(scalar_one_or_none=Mock(return_value=None)),
        ]
        with patch("app.pf_preliminary_persistence_pg.require_pg_transaction"):
            with self.assertRaisesRegex(TransactionGateError, "^PF_WRITE_DENIED$"):
                write_pf_preliminary_within_transaction(
                    self.connection, **self.args(),
                )
        exit_args = self.connection.begin_nested.return_value.__exit__.call_args.args
        self.assertIs(exit_args[0], TransactionGateError)
        self.connection.commit.assert_not_called()

    def test_untrusted_expired_or_revoked_subject_never_inserts(self):
        cases = (
            None,
            FixedVerifier(VerifiedAuthAssertion(
                "local", "frcaixinha-api", UUID(int=999), self.session,
            )),
            FixedVerifier(VerifiedAuthAssertion(
                "local", "frcaixinha-api", UUID(int=999),
                replace(self.session, subject_id=UUID(int=999)),
            )),
            FixedVerifier(VerifiedAuthAssertion(
                "local", "frcaixinha-api", IDENTITY,
                replace(self.session, expires_at=NOW),
            )),
            FixedVerifier(VerifiedAuthAssertion(
                "local", "frcaixinha-api", IDENTITY,
                replace(self.session, revoked_at=NOW),
            )),
        )
        for verifier in cases:
            with self.subTest(verifier=repr(verifier)):
                self.connection.reset_mock()
                self.connection.execute.side_effect = [
                    Mock(scalar_one=Mock(return_value=NOW)),
                ]
                with patch("app.pf_preliminary_persistence_pg.require_pg_transaction"):
                    with self.assertRaisesRegex(TransactionGateError, "^PF_WRITE_DENIED$"):
                        write_pf_preliminary_within_transaction(
                            self.connection, **self.args(verifier=verifier),
                        )
                self.assertEqual(self.connection.execute.call_count, 1)
                self.connection.begin_nested.assert_not_called()

    def test_forged_document_and_crypto_failure_never_insert(self):
        forged = replace(self.registration, identity=replace(
            self.registration.identity, cpf_lookup_hmac=b"X" * 32,
        ))
        invalid_name = replace(self.registration, identity=replace(
            self.registration.identity, name="123",
        ))
        for registration, crypto in (
            (forged, self.crypto),
            (invalid_name, self.crypto),
            (self.registration, DocumentCrypto({"other": DocumentKeySet(
                "other", b"Q" * 32, b"Z" * 32,
            )}, current_key_id="other")),
        ):
            with self.subTest(registration=repr(registration)):
                self.connection.reset_mock()
                self.connection.execute.side_effect = [
                    Mock(scalar_one=Mock(return_value=NOW)),
                ]
                with patch("app.pf_preliminary_persistence_pg.require_pg_transaction"):
                    with self.assertRaisesRegex(TransactionGateError, "^PF_WRITE_DENIED$"):
                        write_pf_preliminary_within_transaction(
                            self.connection,
                            **self.args(registration=registration, crypto=crypto),
                        )
                self.assertEqual(self.connection.execute.call_count, 1)
                self.connection.begin_nested.assert_not_called()

    def test_wrong_database_gate_denies_before_sql(self):
        with patch("app.pf_preliminary_persistence_pg.require_pg_transaction",
                   side_effect=TransactionGateError("PF_WRITE_DENIED")):
            with self.assertRaisesRegex(TransactionGateError, "^PF_WRITE_DENIED$"):
                write_pf_preliminary_within_transaction(
                    self.connection, **self.args(),
                )
        self.connection.execute.assert_not_called()

    def test_no_file_network_or_database_connection_is_opened(self):
        with patch("builtins.open") as file, patch("socket.socket") as network:
            self.digests()
        file.assert_not_called()
        network.assert_not_called()
