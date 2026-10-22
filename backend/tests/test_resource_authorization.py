"""Offline policy tests. Active states here are synthetic future facts."""

import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.resource_authorization import (
    Action, Actor, LicenseFact, MembershipFact, ResourceFact, RoleGrantFact,
    SelectedContext, TrustedFacts, authorize,
)


USER = UUID("00000000-0000-4000-8000-000000000101")
OTHER = UUID("00000000-0000-4000-8000-000000000102")
TENANT = UUID("00000000-0000-4000-8000-000000000201")
OTHER_TENANT = UUID("00000000-0000-4000-8000-000000000202")
CYCLE = UUID("00000000-0000-4000-8000-000000000301")
OTHER_CYCLE = UUID("00000000-0000-4000-8000-000000000302")
GRANT = UUID("00000000-0000-4000-8000-000000000401")
MASTER_GRANT = UUID("00000000-0000-4000-8000-000000000402")
ADMIN_GRANT = UUID("00000000-0000-4000-8000-000000000403")
NOW = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)


class ResourceAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.actor = Actor(USER, True, "ATIVA")
        self.context = SelectedContext(GRANT, TENANT, CYCLE)
        self.resource = ResourceFact(TENANT, CYCLE, USER)
        self.grant = RoleGrantFact(GRANT, USER, TENANT, "TENANT_MEMBER",
                                   NOW - timedelta(days=1), None, None)
        self.membership = MembershipFact(USER, TENANT, CYCLE, "ATIVA", True)
        self.license = LicenseFact(TENANT, "ATIVA", NOW - timedelta(days=1),
                                   NOW + timedelta(days=1))
        self.facts = TrustedFacts(
            grants=(self.grant,), memberships=(self.membership,),
            license=self.license, tenant_id=TENANT, tenant_status="ATIVO",
            cycle_id=CYCLE, cycle_tenant_id=TENANT, cycle_status="ATIVO",
        )

    def decide(self, action=Action.MEMBER_OWN_PROFILE_READ, **changes):
        params = dict(action=action, actor=self.actor, context=self.context,
                      resource=self.resource, facts=self.facts, now=NOW)
        params.update(changes)
        return authorize(**params).allowed

    def test_active_member_can_read_only_own_profile(self):
        self.assertTrue(self.decide())
        for owner in (OTHER, None):
            self.assertFalse(self.decide(resource=replace(self.resource, owner_user_id=owner)))
        for status, accepted in (("PENDENTE_INATIVO", False), ("ATIVA", False)):
            facts = replace(self.facts, memberships=(replace(
                self.membership, status=status, accepted=accepted),))
            self.assertFalse(self.decide(facts=facts))

    def test_tenant_cycle_and_resource_must_match(self):
        for changed in (
            {"resource": replace(self.resource, tenant_id=OTHER_TENANT)},
            {"resource": replace(self.resource, cycle_id=OTHER_CYCLE)},
            {"context": replace(self.context, tenant_id=OTHER_TENANT)},
            {"facts": replace(self.facts, cycle_tenant_id=OTHER_TENANT)},
            {"facts": replace(self.facts, cycle_id=OTHER_CYCLE)},
        ):
            with self.subTest(changed=changed):
                self.assertFalse(self.decide(**changed))

    def test_master_has_only_platform_scope_and_explicit_context(self):
        master = RoleGrantFact(MASTER_GRANT, USER, None, "MASTER",
                               NOW - timedelta(days=1), None, None)
        facts = replace(self.facts, grants=(master, self.grant))
        context = SelectedContext(MASTER_GRANT, None, None)
        platform = ResourceFact(None, None)
        self.assertTrue(self.decide(Action.PLATFORM_CATALOG_READ,
                                    context=context, resource=platform, facts=facts))
        self.assertTrue(self.decide(Action.PLATFORM_LICENSE_REVENUE_READ,
                                    context=context, resource=platform, facts=facts))
        self.assertFalse(self.decide(Action.MEMBER_OWN_PROFILE_READ,
                                     context=context, facts=facts))
        self.assertFalse(self.decide(Action.PLATFORM_CAPACITY_AGGREGATE_READ,
                                     context=self.context, resource=platform, facts=facts))
        # The same person must select the tenant grant to act as a member.
        self.assertTrue(self.decide(facts=facts))

    def test_admin_is_limited_to_own_tenant(self):
        admin = replace(self.grant, role="TENANT_ADMIN")
        facts = replace(self.facts, grants=(admin,))
        self.assertTrue(self.decide(Action.TENANT_CAPACITY_READ, facts=facts))
        self.assertTrue(self.decide(Action.TENANT_MEMBER_SUMMARY_READ, facts=facts))
        self.assertFalse(self.decide(Action.TENANT_CAPACITY_READ, facts=facts,
                                     resource=replace(self.resource, tenant_id=OTHER_TENANT)))
        self.assertFalse(self.decide(Action.PLATFORM_CATALOG_READ, facts=facts,
                                     resource=ResourceFact(None, None)))

    def test_admin_and_member_require_explicit_member_context_for_own_profile(self):
        admin = replace(self.grant, id=ADMIN_GRANT, role="TENANT_ADMIN")
        facts = replace(self.facts, grants=(self.grant, admin))
        admin_context = replace(self.context, grant_id=ADMIN_GRANT)
        self.assertFalse(self.decide(Action.MEMBER_OWN_PROFILE_READ,
                                     context=admin_context, facts=facts))
        self.assertTrue(self.decide(Action.MEMBER_OWN_PROFILE_READ, facts=facts))

    def test_no_financial_permission_for_any_role(self):
        for role in ("MASTER", "TENANT_ADMIN", "TENANT_MEMBER"):
            facts = replace(self.facts, grants=(replace(self.grant, role=role),))
            for action in (Action.FINANCIAL_READ, Action.FINANCIAL_WRITE, Action.PIX_SEND):
                with self.subTest(role=role, action=action):
                    self.assertFalse(self.decide(action, facts=facts))

    def test_identity_grant_and_license_fail_closed(self):
        self.assertFalse(self.decide(actor=replace(self.actor, authenticated=False)))
        self.assertFalse(self.decide(actor=replace(self.actor, identity_status="PENDENTE")))
        self.assertFalse(self.decide(facts=replace(self.facts, grants=(
            replace(self.grant, user_id=OTHER),))))
        self.assertFalse(self.decide(facts=replace(self.facts, grants=(
            replace(self.grant, revoked_at=NOW),))))
        self.assertFalse(self.decide(facts=replace(self.facts, grants=(
            replace(self.grant, active_until=NOW),))))
        self.assertFalse(self.decide(facts=replace(self.facts, grants=(self.grant, self.grant))))
        self.assertFalse(self.decide(facts=replace(self.facts, license=replace(
            self.license, status="SUSPENSA"))))
        self.assertFalse(self.decide(facts=replace(self.facts, license=replace(
            self.license, active_until=NOW))))
        self.assertFalse(self.decide(facts=replace(self.facts, license=None)))
        self.assertFalse(self.decide(facts=replace(self.facts, tenant_status="RASCUNHO_INATIVO")))
        self.assertFalse(self.decide(facts=replace(self.facts, cycle_status="PLANEJADO_INATIVO")))

    def test_invalid_or_implicit_context_is_denied(self):
        self.assertFalse(self.decide(action="MEMBER_OWN_PROFILE_READ"))
        self.assertFalse(self.decide(context=replace(self.context, grant_id=MASTER_GRANT)))
        self.assertFalse(self.decide(now=datetime(2026, 10, 22)))
        self.assertFalse(self.decide(context=replace(self.context, cycle_id=None)))


if __name__ == "__main__":
    unittest.main()
