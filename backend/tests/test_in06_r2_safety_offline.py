"""Cenários adversariais IN06-R2: apenas propriedades offline."""

import socket
import unittest
from dataclasses import FrozenInstanceError, replace
from unittest.mock import patch
from uuid import UUID

from app.in06_r2_safety_offline import (
    Disposition, NeutralClaimReceipt, OfflineSafetyError, PfClaimFacts,
    PjActFacts, RecoveryFacts, ReviewFacts, assess_pf_claim, assess_pj_act,
    assess_recovery, assess_review, receive_neutral_claim,
)


TENANT = UUID(int=101)
OTHER_TENANT = UUID(int=102)
CASE = UUID(int=103)
CLAIMANT = UUID(int=104)
REVIEWER = UUID(int=105)
EVIDENCE = UUID(int=106)


class In06R2SafetyOfflineTests(unittest.TestCase):
    def assert_no_access(self, assessment, expected=None):
        self.assertIn(assessment.disposition, {Disposition.DENY, Disposition.ESCALATE})
        self.assertFalse(assessment.grants_access)
        self.assertEqual(repr(assessment), "OfflineAssessment(<redacted>)")
        if expected is not None:
            self.assertEqual(assessment.disposition, expected)

    def pj(self, **changes):
        values = dict(tenant_ref=TENANT, requested_tenant_ref=TENANT)
        values.update(changes)
        return PjActFacts(**values)

    def review(self, **changes):
        values = dict(case_ref=CASE, claimant_ref=CLAIMANT, reviewer_ref=REVIEWER)
        values.update(changes)
        return ReviewFacts(**values)

    def recovery(self, **changes):
        values = dict(token_present=True)
        values.update(changes)
        return RecoveryFacts(**values)

    def test_r2_pf01_contacts_and_formal_cpf_do_not_prove_civil_identity(self):
        facts = PfClaimFacts(
            cpf_formal=True, email_confirmed=True, phone_possession=True,
            evidence_kinds=frozenset({
                "CPF_FORMAL", "EMAIL_CONFIRMATION", "PHONE_POSSESSION",
            }),
        )
        result = assess_pf_claim(facts)
        self.assert_no_access(result, Disposition.DENY)
        self.assertEqual(result.reason, "INSUFFICIENT_CIVIL_EVIDENCE")

    def test_r2_pf02_intake_is_neutral_without_login_or_internal_identity(self):
        with patch("builtins.open") as opened, patch.object(socket, "socket") as net:
            first = receive_neutral_claim(
                party_type="PF", allegation_kind="IDENTITY_MISUSE")
            second = receive_neutral_claim(
                party_type="PJ", allegation_kind="REPRESENTATION_DISPUTE",
                evidence_refs=(EVIDENCE,))
        opened.assert_not_called()
        net.assert_not_called()
        for receipt in (first, second):
            self.assertIsInstance(receipt, NeutralClaimReceipt)
            self.assertEqual(receipt.case_ref.version, 4)
            self.assertEqual(receipt.state, "RECEIVED_UNVERIFIED_OFFLINE")
            self.assertEqual(repr(receipt), "NeutralClaimReceipt(<redacted>)")
            for forbidden in (
                "reserved_identity_id", "account_id", "authenticated_subject",
                "role_grants", "membership", "financial_access", "claimant_ref",
            ):
                self.assertFalse(hasattr(receipt, forbidden))
        self.assertNotEqual(first.case_ref, second.case_ref)
        with self.assertRaises(FrozenInstanceError):
            first.case_ref = CASE

    def test_r2_pf03_weak_proofs_and_recent_or_compromised_contact(self):
        weak = PfClaimFacts(
            email_confirmed=True, phone_possession=True,
            evidence_kinds=frozenset({"SELFIE", "SCREENSHOT", "OTP"}),
        )
        self.assert_no_access(assess_pf_claim(weak), Disposition.DENY)
        for change in ("contact_compromised", "contact_recently_changed", "ownership_conflict"):
            with self.subTest(change=change):
                result = assess_pf_claim(replace(weak, **{change: True}))
                self.assert_no_access(result, Disposition.ESCALATE)
                self.assertEqual(result.reason, "CONTACT_OR_OWNERSHIP_RISK")

    def test_r2_pf04_legal_rep_without_evidence_and_candidate_civil_document(self):
        facts = PfClaimFacts(
            legal_rep_required=True,
            evidence_kinds=frozenset({"CIVIL_DOCUMENT"}),
        )
        self.assert_no_access(assess_pf_claim(facts), Disposition.DENY)
        plausible = replace(facts, legal_rep_evidence_present=True)
        self.assert_no_access(assess_pf_claim(plausible), Disposition.ESCALATE)
        for kind in ("MINOR", "INCAPACITY", "DEATH"):
            with self.subTest(kind=kind):
                special = replace(facts, special_case=kind)
                result = assess_pf_claim(special)
                self.assert_no_access(result, Disposition.ESCALATE)
                self.assertEqual(result.reason,
                                 "LEGAL_REPRESENTATION_REVIEW_REQUIRED")

    def test_r2_pj01_cnpj_qsa_without_power_per_act(self):
        facts = self.pj(cnpj_formal=True, qsa_record_present=True)
        result = assess_pj_act(facts)
        self.assert_no_access(result, Disposition.DENY)
        self.assertEqual(result.reason, "REPRESENTATION_NOT_PROVEN")
        candidate = replace(facts, representative_evidence_present=True,
                            source_verifiable=True)
        self.assertEqual(assess_pj_act(candidate).reason, "ACT_POWER_NOT_PROVEN")

    def test_r2_pj02_mandate_expiry_revocation_scope_and_source(self):
        base = self.pj(representative_evidence_present=True,
                       source_verifiable=True, act_power_evidence_present=True,
                       power_scope_matches=True)
        for change in ("mandate_expired", "mandate_revoked"):
            with self.subTest(change=change):
                self.assert_no_access(assess_pj_act(replace(base, **{change: True})),
                                      Disposition.DENY)
        self.assert_no_access(assess_pj_act(replace(base, power_scope_matches=False)),
                              Disposition.DENY)
        self.assert_no_access(assess_pj_act(replace(base, source_verifiable=False)),
                              Disposition.DENY)
        self.assert_no_access(assess_pj_act(replace(base, financial_act=True)),
                              Disposition.ESCALATE)
        self.assertEqual(assess_pj_act(base).reason, "PJ_AUTHORITY_PENDING")
        self.assertEqual(assess_pj_act(replace(base, authority_defined=True)).reason,
                         "PJ_POSITIVE_POLICY_PENDING")

    def test_r2_pj03_cross_tenant_request_is_denied(self):
        result = assess_pj_act(self.pj(requested_tenant_ref=OTHER_TENANT))
        self.assert_no_access(result, Disposition.DENY)
        self.assertEqual(result.reason, "TENANT_MISMATCH")

    def test_r2_c01_self_review_and_interested_reviewer_denied(self):
        for facts in (
            self.review(reviewer_ref=CLAIMANT, authority_defined=True),
            self.review(reviewer_interested=True, authority_defined=True),
        ):
            with self.subTest(facts=repr(facts)):
                self.assert_no_access(assess_review(facts), Disposition.DENY)
        self.assertEqual(assess_review(self.review()).reason,
                         "REVIEW_AUTHORITY_PENDING")
        self.assertEqual(assess_review(self.review(authority_defined=True)).reason,
                         "REVIEW_POSITIVE_POLICY_PENDING")

    def test_r2_c01_case_ref_equal_claimant_is_rejected(self):
        for make in (
            lambda: self.review(case_ref=CLAIMANT),
            lambda: replace(self.review(), case_ref=CLAIMANT),
        ):
            with self.subTest(creation=make.__code__.co_firstlineno):
                with patch("builtins.open") as opened, patch.object(socket, "socket") as net:
                    with self.assertRaises(OfflineSafetyError) as caught:
                        make()
                self.assertEqual(str(caught.exception), "REVIEW_FACTS_DENIED")
                self.assertIsNone(caught.exception.__cause__)
                self.assertNotIn(str(CLAIMANT), repr(caught.exception))
                opened.assert_not_called()
                net.assert_not_called()

    def test_r2_c01_case_ref_equal_reviewer_is_rejected(self):
        for make in (
            lambda: self.review(case_ref=REVIEWER),
            lambda: replace(self.review(), case_ref=REVIEWER),
        ):
            with self.subTest(creation=make.__code__.co_firstlineno):
                with patch("builtins.open") as opened, patch.object(socket, "socket") as net:
                    with self.assertRaises(OfflineSafetyError) as caught:
                        make()
                self.assertEqual(str(caught.exception), "REVIEW_FACTS_DENIED")
                self.assertIsNone(caught.exception.__cause__)
                self.assertNotIn(str(REVIEWER), repr(caught.exception))
                opened.assert_not_called()
                net.assert_not_called()

    def test_r2_c02_competing_claims_do_not_transfer_identity(self):
        result = assess_review(self.review(competing_claims=True))
        self.assert_no_access(result, Disposition.ESCALATE)
        self.assertEqual(result.reason, "REVIEW_EVIDENCE_DISPUTE")

    def test_r2_c03_contradiction_or_unavailable_appeal_escalates(self):
        for facts in (
            self.review(evidence_contradictory=True),
            self.review(appeal_required=True, appeal_available=False),
        ):
            self.assert_no_access(assess_review(facts), Disposition.ESCALATE)

    def test_r2_rec01_invalid_expired_consumed_or_replayed_token_denied(self):
        for change in (
            {"token_present": False}, {"token_expired": True},
            {"token_consumed": True}, {"token_replayed": True},
        ):
            with self.subTest(change=change):
                result = assess_recovery(self.recovery(**change))
                self.assert_no_access(result, Disposition.DENY)
                self.assertEqual(result.reason, "RECOVERY_TOKEN_INVALID")

    def test_r2_rec02_compromised_or_recent_channel_never_recovers(self):
        for change in (
            {"only_channel_compromised": True},
            {"channel_recently_changed": True},
            {"independent_method_approved": False},
        ):
            with self.subTest(change=change):
                self.assert_no_access(assess_recovery(self.recovery(**change)),
                                      Disposition.DENY)
        plausible = self.recovery(independent_method_approved=True,
                                  exceptional_authority_defined=True)
        self.assertEqual(assess_recovery(plausible).reason,
                         "RECOVERY_POSITIVE_POLICY_PENDING")
        no_authority = replace(plausible, exceptional_authority_defined=False)
        self.assertEqual(assess_recovery(no_authority).reason,
                         "RECOVERY_AUTHORITY_PENDING")

    def test_malformed_and_unapproved_inputs_fail_closed_without_disclosure(self):
        invalid_intake = (
            {"party_type": "pf", "allegation_kind": "IDENTITY_MISUSE"},
            {"party_type": "PF"},
            {"party_type": "PF", "allegation_kind": "UNKNOWN"},
            {"party_type": "PF", "allegation_kind": "IDENTITY_MISUSE", "evidence_refs": []},
            {"party_type": "PF", "allegation_kind": "IDENTITY_MISUSE",
             "evidence_refs": (EVIDENCE, EVIDENCE)},
            {"party_type": "PF", "allegation_kind": "IDENTITY_MISUSE",
             "evidence_refs": (UUID(int=0),)},
            {"party_type": "PF", "allegation_kind": "IDENTITY_MISUSE",
             "evidence_refs": ("private@example.invalid",)},
            {"party_type": "PF", "allegation_kind": "IDENTITY_MISUSE",
             "reserved_identity_id": CASE},
            {"party_type": "PF", "allegation_kind": "IDENTITY_MISUSE",
             "decision": "APPROVED"},
        )
        for values in invalid_intake:
            with self.subTest(values=list(values)):
                with self.assertRaises(OfflineSafetyError) as caught:
                    receive_neutral_claim(**values)
                self.assertEqual(str(caught.exception), "NEUTRAL_INTAKE_DENIED")
                self.assertIsNone(caught.exception.__cause__)
                self.assertNotIn("private@example.invalid", repr(caught.exception))
        for constructor, values in (
            (PfClaimFacts, {"email_confirmed": 1}),
            (PfClaimFacts, {"evidence_kinds": frozenset({"SECRET"})}),
            (PfClaimFacts, {"special_case": "NOT_APPROVED"}),
            (PjActFacts, {"tenant_ref": "101", "requested_tenant_ref": TENANT}),
            (ReviewFacts, {"case_ref": CASE, "claimant_ref": CLAIMANT,
                           "reviewer_ref": UUID.__new__(UUID)}),
            (RecoveryFacts, {"token_present": "true"}),
        ):
            with self.subTest(constructor=constructor.__name__):
                with self.assertRaises(OfflineSafetyError):
                    constructor(**values)

    def test_no_files_network_or_external_effects_in_evaluators(self):
        with patch("builtins.open") as opened, patch.object(socket, "socket") as net:
            results = (
                assess_pf_claim(PfClaimFacts()),
                assess_pj_act(self.pj()),
                assess_review(self.review()),
                assess_recovery(self.recovery()),
            )
        for result in results:
            self.assert_no_access(result)
        opened.assert_not_called()
        net.assert_not_called()


if __name__ == "__main__":
    unittest.main()
