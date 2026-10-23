"""Auditoria adversarial independente do caminho feliz: casos que devem falhar fechados.

Estes testes nao tocam PostgreSQL, rede, dados pessoais ou segredos reais.
"""
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.g3c_transaction_guards_offline import (
    EmailFacts, SessionFacts, email_challenge_eligible,
    session_current_with_server_facts,
)

NOW = datetime(2026, 10, 23, 12, 0, tzinfo=timezone.utc)
IDENTITY = UUID(int=707)


class G3C138AdversarialTests(unittest.TestCase):
    def test_session_created_before_email_verification_stays_denied(self):
        """Um token anterior a confirmacao nao pode ganhar validade retroativa."""
        facts = SessionFacts(
            IDENTITY, IDENTITY, "ATIVA", "ACTIVE",
            NOW - timedelta(seconds=30),
            NOW - timedelta(minutes=10),
            NOW - timedelta(minutes=2),
            NOW + timedelta(minutes=13),
        )
        self.assertFalse(session_current_with_server_facts(facts, now=NOW))

    def test_email_challenge_rejects_malformed_address_even_if_equal(self):
        """Contato malformado nao vira prova so porque snapshot == estado atual."""
        facts = EmailFacts(
            IDENTITY, IDENTITY, "teste@example.org", "teste@example.org",
            "PENDENTE", "INITIAL_EMAIL",
            NOW - timedelta(minutes=1), NOW + timedelta(minutes=9),
        )
        for invalid in (
            "nao-e-email",
            "teste@example.org\n",
            "a@b",
            "t..este@example.org",
            "testE@example.org",
        ):
            with self.subTest(invalid=repr(invalid)):
                self.assertFalse(email_challenge_eligible(
                    replace(facts, snapshot_email=invalid, current_email=invalid),
                    now=NOW,
                ))


if __name__ == "__main__":
    unittest.main()
