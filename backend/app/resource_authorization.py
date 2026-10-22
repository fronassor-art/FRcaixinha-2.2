"""Deterministic offline resource policy; callers must supply server-verified facts.

This module does not authenticate a caller, query a database or grant operational
financial permissions. A future API must load every fact from trusted storage.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class Action(str, Enum):
    PLATFORM_CATALOG_READ = "PLATFORM_CATALOG_READ"
    PLATFORM_LICENSE_REVENUE_READ = "PLATFORM_LICENSE_REVENUE_READ"
    PLATFORM_CAPACITY_AGGREGATE_READ = "PLATFORM_CAPACITY_AGGREGATE_READ"
    TENANT_CAPACITY_READ = "TENANT_CAPACITY_READ"
    TENANT_MEMBER_SUMMARY_READ = "TENANT_MEMBER_SUMMARY_READ"
    MEMBER_OWN_PROFILE_READ = "MEMBER_OWN_PROFILE_READ"
    FINANCIAL_READ = "FINANCIAL_READ"
    FINANCIAL_WRITE = "FINANCIAL_WRITE"
    PIX_SEND = "PIX_SEND"


_PLATFORM = frozenset({
    Action.PLATFORM_CATALOG_READ,
    Action.PLATFORM_LICENSE_REVENUE_READ,
    Action.PLATFORM_CAPACITY_AGGREGATE_READ,
})
_ADMIN = frozenset({Action.TENANT_CAPACITY_READ, Action.TENANT_MEMBER_SUMMARY_READ})


@dataclass(frozen=True, slots=True)
class Actor:
    user_id: UUID
    authenticated: bool
    identity_status: str


@dataclass(frozen=True, slots=True)
class SelectedContext:
    grant_id: UUID
    tenant_id: UUID | None
    cycle_id: UUID | None


@dataclass(frozen=True, slots=True)
class RoleGrantFact:
    id: UUID
    user_id: UUID
    tenant_id: UUID | None
    role: str
    active_from: datetime
    active_until: datetime | None
    revoked_at: datetime | None


@dataclass(frozen=True, slots=True)
class MembershipFact:
    user_id: UUID
    tenant_id: UUID
    cycle_id: UUID
    status: str
    accepted: bool


@dataclass(frozen=True, slots=True)
class LicenseFact:
    tenant_id: UUID
    status: str
    active_from: datetime
    active_until: datetime


@dataclass(frozen=True, slots=True)
class ResourceFact:
    tenant_id: UUID | None
    cycle_id: UUID | None
    owner_user_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class TrustedFacts:
    """Snapshot from trusted storage, never directly from request headers/body."""

    grants: tuple[RoleGrantFact, ...]
    memberships: tuple[MembershipFact, ...] = ()
    license: LicenseFact | None = None
    tenant_id: UUID | None = None
    tenant_status: str | None = None
    cycle_id: UUID | None = None
    cycle_tenant_id: UUID | None = None
    cycle_status: str | None = None


@dataclass(frozen=True, slots=True)
class Decision:
    allowed: bool
    reason: str


_DENIED = Decision(False, "ACCESS_DENIED")
_ALLOWED = Decision(True, "ALLOWED_OFFLINE_POLICY")


def _uuid(value: object) -> bool:
    return isinstance(value, UUID) and value.int != 0


def _aware(value: object) -> bool:
    return isinstance(value, datetime) and value.tzinfo is not None and value.utcoffset() is not None


def authorize(
    action: Action, *, actor: Actor, context: SelectedContext,
    resource: ResourceFact, facts: TrustedFacts, now: datetime,
) -> Decision:
    """Evaluate one explicit role context and the resource's trusted scope.

    An ALLOWED_OFFLINE_POLICY result is not an API authorization or payment gate.
    """
    if (not isinstance(action, Action) or not isinstance(actor, Actor)
            or not isinstance(context, SelectedContext)
            or not isinstance(resource, ResourceFact)
            or not isinstance(facts, TrustedFacts) or not _aware(now)
            or not _uuid(actor.user_id) or actor.authenticated is not True
            or actor.identity_status != "ATIVA" or not _uuid(context.grant_id)
            or not isinstance(facts.grants, tuple)
            or any(not isinstance(grant, RoleGrantFact) for grant in facts.grants)
            or not isinstance(facts.memberships, tuple)
            or any(not isinstance(member, MembershipFact) for member in facts.memberships)):
        return _DENIED
    if action in {Action.FINANCIAL_READ, Action.FINANCIAL_WRITE, Action.PIX_SEND}:
        return _DENIED
    matching = [grant for grant in facts.grants if grant.id == context.grant_id]
    if len(matching) != 1:
        return _DENIED
    grant = matching[0]
    if (grant.user_id != actor.user_id or not _aware(grant.active_from)
            or grant.active_from > now or (grant.active_until is not None and
            (not _aware(grant.active_until) or now >= grant.active_until))
            or (grant.revoked_at is not None and
            (not _aware(grant.revoked_at) or now >= grant.revoked_at))):
        return _DENIED
    if action in _PLATFORM:
        if (grant.role == "MASTER" and grant.tenant_id is None
                and context.tenant_id is None and context.cycle_id is None
                and resource.tenant_id is None and resource.cycle_id is None
                and resource.owner_user_id is None):
            return _ALLOWED
        return _DENIED
    if (grant.role not in {"TENANT_ADMIN", "TENANT_MEMBER"}
            or not _uuid(context.tenant_id) or not _uuid(context.cycle_id)
            or grant.tenant_id != context.tenant_id
            or resource.tenant_id != context.tenant_id
            or resource.cycle_id != context.cycle_id
            or facts.tenant_id != context.tenant_id
            or facts.cycle_id != context.cycle_id
            or facts.cycle_tenant_id != context.tenant_id
            or facts.tenant_status != "ATIVO" or facts.cycle_status != "ATIVO"):
        return _DENIED
    license = facts.license
    if (not isinstance(license, LicenseFact) or license.tenant_id != context.tenant_id
            or license.status != "ATIVA" or not _aware(license.active_from)
            or not _aware(license.active_until)
            or not (license.active_from <= now < license.active_until)):
        return _DENIED
    if action in _ADMIN:
        return _ALLOWED if grant.role == "TENANT_ADMIN" else _DENIED
    if action == Action.MEMBER_OWN_PROFILE_READ:
        if grant.role != "TENANT_MEMBER" or resource.owner_user_id != actor.user_id:
            return _DENIED
        active_memberships = [member for member in facts.memberships if (
            member.user_id == actor.user_id and member.tenant_id == context.tenant_id
            and member.cycle_id == context.cycle_id and member.status == "ATIVA"
            and member.accepted is True
        )]
        return _ALLOWED if len(active_memberships) == 1 else _DENIED
    return _DENIED
