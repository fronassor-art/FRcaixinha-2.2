"""Provas offline das guardas G3-C.5; NÃO exercem PostgreSQL ou concorrência."""
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.g3c_transaction_guards_offline import (
    CompletedAttempt, EmailFacts, PartyLink, SessionFacts,
    TransactionGateError, email_challenge_eligible,
    session_current_with_server_facts, verified_replay_ids,
)

NOW = datetime(2026, 10, 23, 12, tzinfo=timezone.utc)
IDENTITY = UUID(int=1234)
PARTY = UUID(int=5678)
HASH_A = b"A" * 32
HASH_B = b"B" * 32
HASH_C = b"C" * 32


class OfflineTransactionGuardsTests(unittest.TestCase):
    def setUp(self):
        self.attempt = CompletedAttempt(
            HASH_A, HASH_B, HASH_C, IDENTITY, PARTY,
            "COMPLETED", NOW - timedelta(minutes=2),
            NOW + timedelta(minutes=13),
        )
        self.party = PartyLink(PARTY, "PF", IDENTITY, None, IDENTITY)
        self.claim = dict(
            origin_digest=HASH_A, attempt_digest=HASH_B,
            request_fingerprint=HASH_C, now=NOW,
        )
        self.email = EmailFacts(
            IDENTITY, IDENTITY, "teste@example.org", "teste@example.org",
            "PENDENTE", "INITIAL_EMAIL",
            NOW - timedelta(minutes=1), NOW + timedelta(minutes=9),
        )
        self.session = SessionFacts(
            IDENTITY, IDENTITY, "ATIVA", "ACTIVE",
            NOW - timedelta(minutes=30),
            NOW - timedelta(minutes=2),
            NOW - timedelta(minutes=1),
            NOW + timedelta(minutes=14),
        )

    def assertReplayDenied(self, attempt=None, party=None, **kwargs):
        claim = {**self.claim, **kwargs}
        with self.assertRaisesRegex(TransactionGateError, "^REPLAY_DENIED$"):
            verified_replay_ids(
                self.attempt if attempt is None else attempt,
                self.party if party is None else party, **claim
            )

    def test_in01_pf_completed_matching_link(self):
        self.assertEqual(
            verified_replay_ids(self.attempt, self.party, **self.claim),
            (IDENTITY, PARTY),
        )

    def test_in01_pj_completed_matching_link(self):
        pj = PartyLink(PARTY, "PJ", None, IDENTITY, IDENTITY)
        self.assertEqual(
            verified_replay_ids(self.attempt, pj, **self.claim),
            (IDENTITY, PARTY),
        )

    def test_in01_pj_representative_change_preserves_historical_replay(self):
        party = PartyLink(PARTY, "PJ", None, UUID(int=7777), IDENTITY)
        self.assertEqual(
            verified_replay_ids(self.attempt, party, **self.claim),
            (IDENTITY, PARTY),
        )
        self.assertFalse(hasattr(party, "role_grant"))
        self.assertFalse(hasattr(party, "tenant_id"))

    def test_in01_crossed_foreign_keys_denied(self):
        for party in (
            replace(self.party, pf_user_id=UUID(int=7777)),
            replace(self.party, id=UUID(int=9999)),
            replace(self.party, representative_user_id=UUID(int=9999)),
            replace(self.party, initial_registration_identity_id=UUID(int=7777)),
            replace(self.party, initial_registration_identity_id=None),
            PartyLink(PARTY, "PJ", IDENTITY, IDENTITY, IDENTITY),
            PartyLink(PARTY, "??", IDENTITY, None, IDENTITY),
        ):
            with self.subTest(party=party.party_type):
                self.assertReplayDenied(party=party)

    def test_in02_digest_origin_attempt_and_fingerprint_binding(self):
        for claim in (
            {"origin_digest": b"X" * 32},
            {"attempt_digest": b"X" * 32},
            {"request_fingerprint": b"X" * 32},
            {"origin_digest": b"A" * 31},
            {"request_fingerprint": "C" * 32},
        ):
            with self.subTest(claim=list(claim)):
                self.assertReplayDenied(**claim)

    def test_in02_only_completed_and_valid_ttl(self):
        for attempt in (
            replace(self.attempt, state="RESERVED"),
            replace(self.attempt, state="COMPLETED", identity_id=UUID(int=0)),
            replace(self.attempt, state="COMPLETED", party_id=IDENTITY),
            replace(self.attempt, expires_at=NOW),
            replace(self.attempt, expires_at=NOW + timedelta(minutes=15)),
            replace(self.attempt, created_at=NOW + timedelta(seconds=1)),
        ):
            with self.subTest(attempt_state=attempt.state):
                self.assertReplayDenied(attempt=attempt)

    def test_in02_expiration_boundary_and_timezone_fail_closed(self):
        self.assertReplayDenied(now=self.attempt.expires_at)
        self.assertReplayDenied(now=NOW.replace(tzinfo=None))

    def test_in02_no_secret_exposure_in_repr_or_error(self):
        self.assertNotIn("AAAA", repr(self.attempt))
        self.assertNotIn(str(IDENTITY), repr(self.attempt))
        try:
            self.assertReplayDenied(request_fingerprint=b"X" * 32)
        except Exception:
            self.fail("error handler must remain generic")

    def test_in03_email_precondition_only(self):
        self.assertTrue(email_challenge_eligible(self.email, now=NOW))

    def test_in03_email_mutation_and_purpose_deny(self):
        for facts in (
            replace(self.email, current_email="new@example.org"),
            replace(self.email, purpose="OTHER"),
            replace(self.email, identity_status="SUSPENSA"),
            replace(self.email, challenge_identity_id=UUID(int=88)),
            replace(self.email, consumed_at=NOW),
            replace(self.email, revoked_at=NOW),
        ):
            with self.subTest(purpose=facts.purpose):
                self.assertFalse(email_challenge_eligible(facts, now=NOW))

    def test_in03_expiration_boundary_and_oversize_ttl(self):
        self.assertFalse(email_challenge_eligible(
            self.email, now=self.email.expires_at))
        self.assertFalse(email_challenge_eligible(
            replace(self.email, expires_at=NOW + timedelta(minutes=10)),
            now=NOW,
        ))
        self.assertFalse(email_challenge_eligible(
            self.email, now=NOW.replace(tzinfo=None)))

    def test_in04_session_valid_current_server_facts(self):
        self.assertTrue(session_current_with_server_facts(
            self.session, now=NOW))

    def test_in04_suspension_revocation_and_password_change(self):
        for facts in (
            replace(self.session, identity_status="SUSPENSA"),
            replace(self.session, credential_status="REVOKED"),
            replace(self.session, credential_updated_at=NOW),
            replace(self.session, revoked_at=NOW),
            replace(self.session, session_identity_id=UUID(int=88)),
            replace(self.session, email_verified_at=None),
        ):
            with self.subTest(status=facts.identity_status):
                self.assertFalse(session_current_with_server_facts(
                    facts, now=NOW))

    def test_in04_session_expiration_ttl_and_no_role_grant(self):
        self.assertFalse(session_current_with_server_facts(
            self.session, now=self.session.expires_at))
        self.assertFalse(session_current_with_server_facts(
            replace(self.session, expires_at=NOW + timedelta(minutes=15)),
            now=NOW,
        ))
        self.assertFalse(session_current_with_server_facts(
            self.session, now=NOW.replace(tzinfo=None)))
        self.assertFalse(hasattr(self.session, "role_grant"))
        self.assertFalse(hasattr(self.session, "tenant_id"))

    def test_no_sql_or_network_or_implicit_mutation(self):
        import inspect
        import app.g3c_transaction_guards_offline as module
        source = inspect.getsource(module)
        for forbidden in ("psycopg", "sqlalchemy", "requests.", "DELETE FROM",
                          "COMMIT;", "alembic upgrade"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
