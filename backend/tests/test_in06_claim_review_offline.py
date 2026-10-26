"""IN-06 R1: preparação sem decisão, persistência ou privilégios."""

import socket
import unittest
from dataclasses import FrozenInstanceError, replace
from unittest.mock import patch
from uuid import UUID

from app.in06_claim_review_offline import (
    ClaimPreparationError, ClaimReviewIntent, prepare_claim_review,
)


CLAIM = UUID(int=101)
CLAIMANT = UUID(int=102)
RESERVED = UUID(int=103)
PARTY = UUID(int=104)
EVIDENCE = UUID(int=105)


class ClaimReviewOfflineTests(unittest.TestCase):
    def prepare(self, **changes):
        data = dict(
            claim_id=CLAIM, claimant_ref=CLAIMANT,
            reserved_identity_id=RESERVED, party_type="PF",
            party_id=None, evidence_refs=(EVIDENCE,),
        )
        data.update(changes)
        return prepare_claim_review(**data)

    def denied(self, **changes):
        with self.assertRaises(ClaimPreparationError) as caught:
            self.prepare(**changes)
        self.assertEqual(str(caught.exception), "CLAIM_PREPARATION_DENIED")
        self.assertIsNone(caught.exception.__cause__)

    def test_pf_and_pj_are_only_unreviewed_preparations(self):
        for party_type, party_id in (("PF", None), ("PJ", PARTY)):
            with self.subTest(party_type=party_type):
                intent = self.prepare(party_type=party_type, party_id=party_id)
                self.assertEqual(intent.party_type, party_type)
                self.assertEqual(intent.state, "PREPARED_OFFLINE_UNREVIEWED")
                self.assertEqual(intent.evidence_refs, (EVIDENCE,))
                for forbidden in (
                    "approved", "reviewer_id", "recovery_token", "tenant_id",
                    "role_grants", "memberships", "license", "financial_access",
                ):
                    self.assertFalse(hasattr(intent, forbidden))
                with self.assertRaises(FrozenInstanceError):
                    intent.state = "APPROVED"

    def test_invalid_kind_and_party_context_fail_closed(self):
        for changes in (
            {"party_type": "APROVADA"}, {"party_type": "pj"},
            {"party_type": 1}, {"party_type": "PJ", "party_id": None},
            {"party_type": "PJ", "party_id": "104"},
            {"party_id": CLAIM},
        ):
            with self.subTest(changes=changes):
                self.denied(**changes)

    def test_invalid_and_colliding_identifiers_fail_closed(self):
        for changes in (
            {"claim_id": UUID(int=0)}, {"claimant_ref": "102"},
            {"reserved_identity_id": None},
            {"claimant_ref": RESERVED}, {"claim_id": EVIDENCE},
            {"party_type": "PJ", "party_id": RESERVED},
        ):
            with self.subTest(changes=changes):
                self.denied(**changes)

    def test_evidence_must_be_opaque_distinct_references(self):
        for refs in (
            (), [], (EVIDENCE, EVIDENCE), (UUID(int=0),),
            (CLAIM,), (RESERVED,), ("52998224725",),
            ("12ABC34501DE35",), ("person@example.com",),
            (b"secret-token",), tuple(UUID(int=200 + n) for n in range(33)),
        ):
            with self.subTest(refs_type=type(refs).__name__):
                self.denied(evidence_refs=refs)

    def test_unapproved_review_recovery_and_context_inputs_are_rejected(self):
        for extra in (
            {"reviewer_id": UUID(int=106)}, {"decision": "APPROVED"},
            {"recovery_token": b"secret-token"},
            {"tenant_id": UUID(int=107)}, {"role": "MASTER"},
            {"contact_controlled": True},
        ):
            with self.subTest(field=next(iter(extra))):
                self.denied(**extra)

    def test_repr_and_errors_do_not_disclose_personal_data_or_secrets(self):
        intent = self.prepare()
        self.assertEqual(repr(intent), "ClaimReviewIntent(<redacted>)")
        with self.assertRaises(ClaimPreparationError) as caught:
            self.prepare(evidence_refs=("52998224725 person@example.com SECRET",))
        disclosure = repr(caught.exception) + str(caught.exception) + repr(intent)
        for secret in ("52998224725", "person@example.com", "SECRET"):
            self.assertNotIn(secret, disclosure)

    def test_preparation_does_not_call_builtin_open_or_socket_constructor(self):
        with patch("builtins.open") as opened, patch.object(socket, "socket") as net:
            self.prepare()
            self.prepare(party_type="PJ", party_id=PARTY)
        opened.assert_not_called()
        net.assert_not_called()

    def test_direct_constructor_rejects_pj_without_party(self):
        with self.assertRaises(ClaimPreparationError) as caught:
            ClaimReviewIntent(
                CLAIM, CLAIMANT, RESERVED, "PJ", None, (EVIDENCE,),
            )
        self.assertEqual(str(caught.exception), "CLAIM_PREPARATION_DENIED")
        self.assertIsNone(caught.exception.__cause__)

    def test_direct_constructor_rejects_invalid_evidence_references(self):
        invalid_refs = (
            ("00000000000 private@example.invalid SECRET",),
            (CLAIM,),
            (EVIDENCE, EVIDENCE),
        )
        for case_number, refs in enumerate(invalid_refs):
            with self.subTest(case_number=case_number):
                with self.assertRaises(ClaimPreparationError) as caught:
                    ClaimReviewIntent(
                        CLAIM, CLAIMANT, RESERVED, "PF", None, refs,
                    )
                self.assertEqual(str(caught.exception), "CLAIM_PREPARATION_DENIED")
                self.assertIsNone(caught.exception.__cause__)

    def test_replace_cannot_create_invalid_preparation(self):
        intent = self.prepare()
        changes = (
            {"party_type": "PJ", "party_id": None},
            {"evidence_refs": ("private@example.invalid",)},
        )
        for case_number, fields in enumerate(changes):
            with self.subTest(case_number=case_number):
                with self.assertRaises(ClaimPreparationError) as caught:
                    replace(intent, **fields)
                self.assertEqual(str(caught.exception), "CLAIM_PREPARATION_DENIED")
                self.assertIsNone(caught.exception.__cause__)

    def test_incomplete_uuid_fails_with_stable_redacted_error(self):
        with self.assertRaises(ClaimPreparationError) as caught:
            self.prepare(claim_id=UUID.__new__(UUID))
        self.assertEqual(str(caught.exception), "CLAIM_PREPARATION_DENIED")
        self.assertIsNone(caught.exception.__cause__)

    def test_direct_constructor_error_does_not_disclose_evidence(self):
        private_marker = "private@example.invalid"
        with self.assertRaises(ClaimPreparationError) as caught:
            ClaimReviewIntent(
                CLAIM, CLAIMANT, RESERVED, "PF", None, (private_marker,),
            )
        disclosure = repr(caught.exception) + str(caught.exception)
        self.assertNotIn(private_marker, disclosure)
        self.assertEqual(str(caught.exception), "CLAIM_PREPARATION_DENIED")
        self.assertIsNone(caught.exception.__cause__)


if __name__ == "__main__":
    unittest.main()
