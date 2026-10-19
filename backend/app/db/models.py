"""Modelos iniciais de identidade e contratacao.

Somente definicoes de esquema. Nenhuma conexao e aberta.
CPF/CNPJ exigem criptografia e HMAC antes de persistencia.
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    Index,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    LargeBinary,
    MetaData,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_N_name)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class IdentityColumns:
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class UserIdentity(IdentityColumns, Base):
    __tablename__ = "user_identities"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf_ciphertext: Mapped[bytes] = mapped_column(
        LargeBinary, nullable=False
    )
    cpf_lookup_hmac: Mapped[bytes] = mapped_column(
        LargeBinary, nullable=False, unique=True
    )
    email: Mapped[str] = mapped_column(
        String(254), nullable=False
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    phone: Mapped[str] = mapped_column(String(11), nullable=False)
    phone_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    profile_photo_ref: Mapped[str | None] = mapped_column(
        String(512)
    )
    auth_subject: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="PENDENTE",
        server_default=text("'PENDENTE'"),
    )


    __table_args__ = (
        Index("uq_user_identities_email_lower", func.lower(email), unique=True),
        CheckConstraint(
            "status IN ('PENDENTE', 'ATIVA', 'SUSPENSA', 'ENCERRADA')",
            name="status_valid",
        ),
    )

class ContractingParty(IdentityColumns, Base):
    __tablename__ = "contracting_parties"

    __table_args__ = (
        CheckConstraint(
            "status IN ('PRELIMINAR', 'EM_ANALISE', 'APTO', 'SUSPENSO', 'ENCERRADO')",
            name="status_valid",
        ),
        CheckConstraint(
            "party_type IN ('PF', 'PJ')",
            name="party_type_valid",
        ),
        CheckConstraint(
            "party_type = 'PF' OR representative_user_id IS NOT NULL",
            name="pj_representative_required",
        ),
        CheckConstraint(
            "party_type = 'PJ' OR pf_user_id IS NOT NULL",
            name="pf_identity_required",
        ),
        CheckConstraint(
            "party_type = 'PJ' OR representative_user_id IS NULL",
            name="pf_representative_absent",
        ),
        CheckConstraint(
            "party_type = 'PF' OR pf_user_id IS NULL",
            name="pj_pf_identity_absent",
        ),
        CheckConstraint(
            "party_type = 'PJ' OR (tax_id_ciphertext IS NULL "
            "AND tax_id_lookup_hmac IS NULL)",
            name="pf_pj_document_absent",
        ),
        CheckConstraint(
            "party_type = 'PF' OR (tax_id_ciphertext IS NOT NULL "
            "AND tax_id_lookup_hmac IS NOT NULL)",
            name="pj_cnpj_required",
        ),
        CheckConstraint(
            "party_type = 'PJ' OR (representation_declaration_ref IS NULL "
            "AND representation_evidence_ref IS NULL "
            "AND representation_verification_ref IS NULL "
            "AND representation_verified_at IS NULL)",
            name="pf_representation_fields_absent",
        ),
        CheckConstraint(
            "representation_verified_at IS NULL OR (party_type = 'PJ' "
            "AND representation_declaration_ref IS NOT NULL "
            "AND representation_verification_ref IS NOT NULL)",
            name="representation_verification_evidenced",
        ),
        CheckConstraint(
            "party_type = 'PF' OR status <> 'APTO' OR "
            "(representative_user_id IS NOT NULL "
            "AND representation_declaration_ref IS NOT NULL "
            "AND representation_verification_ref IS NOT NULL "
            "AND representation_verified_at IS NOT NULL)",
            name="pj_apto_representation_verified",
        ),
        CheckConstraint(
            "representation_declaration_ref IS NULL OR "
            "representation_declaration_ref ~ '[^[:space:]]'",
            name="representation_declaration_ref_nonblank",
        ),
        CheckConstraint(
            "representation_evidence_ref IS NULL OR "
            "representation_evidence_ref ~ '[^[:space:]]'",
            name="representation_evidence_ref_nonblank",
        ),
        CheckConstraint(
            "representation_verification_ref IS NULL OR "
            "representation_verification_ref ~ '[^[:space:]]'",
            name="representation_verification_ref_nonblank",
        ),
    )

    party_type: Mapped[str] = mapped_column(
        String(2), nullable=False
    )
    legal_name: Mapped[str] = mapped_column(
        String(200), nullable=False
    )
    # Somente CNPJ de PJ; CPF de PF vem de UserIdentity via pf_user_id.
    tax_id_ciphertext: Mapped[bytes | None] = mapped_column(
        LargeBinary, nullable=True
    )
    tax_id_lookup_hmac: Mapped[bytes | None] = mapped_column(
        LargeBinary, nullable=True, unique=True
    )
    billing_address: Mapped[dict | None] = mapped_column(JSONB)
    pf_user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user_identities.id"),
        unique=True,
    )
    representative_user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user_identities.id"),
    )
    # Opaque references to protected records; never store document content here.
    representation_declaration_ref: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )
    representation_evidence_ref: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )
    representation_verification_ref: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )
    representation_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fiscal_data: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="PRELIMINAR",
        server_default=text("'PRELIMINAR'"),
    )



class Tenant(IdentityColumns, Base):
    __tablename__ = "tenants"

    __table_args__ = (
        CheckConstraint(
            "display_name ~ '[^[:space:]]'",
            name="display_name_nonblank",
        ),
        CheckConstraint(
            "status = 'RASCUNHO_INATIVO'",
            name="status_initial_only",
        ),
        Index("ix_tenants_contracting_party_id", "contracting_party_id"),
        Index("ix_tenants_admin_user_id", "admin_user_id"),
    )

    # A camada de servico deve conferir o titular PF ou representante PJ.
    # As duas FKs independentes nao comprovam essa correspondencia.
    admin_user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user_identities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    contracting_party_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("contracting_parties.id", ondelete="RESTRICT"),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="RASCUNHO_INATIVO",
        server_default=text("'RASCUNHO_INATIVO'"),
    )


class Cycle(IdentityColumns, Base):
    __tablename__ = "cycles"

    __table_args__ = (
        UniqueConstraint("tenant_id", "year"),
        # Permite FKs compostas (tenant_id, cycle_id) em tabelas futuras.
        UniqueConstraint("tenant_id", "id"),
        CheckConstraint("year >= 1", name="year_positive"),
        CheckConstraint("start_date = make_date(year, 1, 1)", name="start_date_calendar"),
        CheckConstraint("end_date = make_date(year, 12, 31)", name="end_date_calendar"),
        CheckConstraint(
            "settlement_date = make_date(year + 1, 1, 10)",
            name="settlement_date_calendar",
        ),
        CheckConstraint("status = 'PLANEJADO_INATIVO'", name="status_initial_only"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    # DATE representa o calendario civil em America/Belem.
    # A imutabilidade historica exige controles futuros de servico e banco.
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    settlement_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="PLANEJADO_INATIVO",
        server_default=text("'PLANEJADO_INATIVO'"),
    )


class RoleGrant(IdentityColumns, Base):
    __tablename__ = "role_grants"

    __table_args__ = (
        CheckConstraint(
            "role IN ('MASTER', 'TENANT_ADMIN', 'TENANT_MEMBER')",
            name="role_valid",
        ),
        CheckConstraint(
            "(role = 'MASTER' AND tenant_id IS NULL) OR "
            "(role IN ('TENANT_ADMIN', 'TENANT_MEMBER') "
            "AND tenant_id IS NOT NULL)",
            name="role_scope_valid",
        ),
        CheckConstraint(
            "active_until IS NULL OR active_until > active_from",
            name="active_interval_valid",
        ),
        # Estes indices barram duplicacao exata, nao intervalos sobrepostos.
        Index(
            "uq_role_grants_global_start",
            "user_id", "role", "active_from",
            unique=True,
            postgresql_where=text("tenant_id IS NULL"),
        ),
        Index(
            "uq_role_grants_tenant_start",
            "tenant_id", "user_id", "role", "active_from",
            unique=True,
            postgresql_where=text("tenant_id IS NOT NULL"),
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user_identities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=True,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    active_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    active_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Membership(IdentityColumns, Base):
    __tablename__ = "memberships"

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "cycle_id"],
            ["cycles.tenant_id", "cycles.id"],
            ondelete="RESTRICT",
        ),
        # Referencia composta para garantir o mesmo tenant/ciclo nas cotas.
        # O id continua unico por PK; esta chave nao restringe historico.
        UniqueConstraint("tenant_id", "cycle_id", "id"),
        CheckConstraint(
            "status = 'PENDENTE_INATIVO'",
            name="status_initial_only",
        ),
        CheckConstraint(
            "status <> 'PENDENTE_INATIVO' OR "
            "(joined_at IS NULL AND left_at IS NULL)",
            name="pending_dates_null",
        ),
        # O dominio atual rejeita ATIVA; este indice prepara a ativacao futura.
        Index(
            "uq_memberships_active_identity_cycle",
            "tenant_id", "cycle_id", "user_id",
            unique=True,
            postgresql_where=text("status = 'ATIVA'"),
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    cycle_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user_identities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    joined_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="PENDENTE_INATIVO",
        server_default=text("'PENDENTE_INATIVO'"),
    )


class Quota(IdentityColumns, Base):
    __tablename__ = "quotas"

    __table_args__ = (
        # Uma cota deve pertencer a um Membership do mesmo tenant e ciclo.
        ForeignKeyConstraint(
            ["tenant_id", "cycle_id", "membership_id"],
            ["memberships.tenant_id", "memberships.cycle_id", "memberships.id"],
            ondelete="RESTRICT",
        ),
        # Numero independente por ciclo; a mesma pessoa pode ter varias cotas.
        UniqueConstraint("tenant_id", "cycle_id", "quota_number"),
        Index(
            "ix_quotas_tenant_cycle_membership",
            "tenant_id", "cycle_id", "membership_id",
        ),
        CheckConstraint("quota_number > 0", name="quota_number_positive"),
        CheckConstraint(
            "status = 'PENDENTE_INATIVA'",
            name="status_initial_only",
        ),
        # Nenhum marco de vigencia nem capacidade enquanto inativa.
        CheckConstraint(
            "status <> 'PENDENTE_INATIVA' OR "
            "(effective_from IS NULL AND effective_to IS NULL)",
            name="inactive_dates_null",
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    cycle_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    membership_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    quota_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="PENDENTE_INATIVA",
        server_default=text("'PENDENTE_INATIVA'"),
    )
    effective_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class LicensePlan(IdentityColumns, Base):
    __tablename__ = "license_plans"

    __table_args__ = (
        UniqueConstraint("name"),
        CheckConstraint(
            "name IN ('Essencial', 'Intermediário', 'Ampliado')",
            name="name_valid",
        ),
        CheckConstraint(
            "member_limit IS NULL OR member_limit > 0",
            name="member_limit_positive",
        ),
        CheckConstraint(
            "quota_limit IS NULL OR quota_limit > 0",
            name="quota_limit_positive",
        ),
        CheckConstraint(
            "(member_limit IS NULL AND quota_limit IS NULL) OR "
            "(member_limit IS NOT NULL AND quota_limit IS NOT NULL)",
            name="capacity_pair_valid",
        ),
        CheckConstraint(
            "(name = 'Essencial' AND member_limit IS NOT DISTINCT FROM 20 AND quota_limit IS NOT DISTINCT FROM 40) OR "
            "(name = 'Intermediário' AND member_limit IS NOT DISTINCT FROM 50 AND quota_limit IS NOT DISTINCT FROM 50) OR "
            "(name = 'Ampliado' AND member_limit IS NULL AND quota_limit IS NULL)",
            name="approved_capacity",
        ),
        CheckConstraint("status = 'INATIVO'", name="status_initial_only"),
    )

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    member_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quota_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="INATIVO",
        server_default=text("'INATIVO'"),
    )


class LicensePriceVersion(IdentityColumns, Base):
    __tablename__ = "license_price_versions"

    __table_args__ = (
        # A chave composta impede vincular a versão anterior a outro plano.
        UniqueConstraint("plan_id", "id"),
        UniqueConstraint("plan_id", "effective_from"),
        UniqueConstraint("previous_price_version_id"),
        ForeignKeyConstraint(
            ["plan_id", "previous_price_version_id"],
            ["license_price_versions.plan_id", "license_price_versions.id"],
            ondelete="RESTRICT",
        ),
        CheckConstraint("monthly_price > 0", name="monthly_price_positive"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="effective_interval_valid",
        ),
        CheckConstraint("reason ~ '[^[:space:]]'", name="reason_nonblank"),
        CheckConstraint(
            "previous_price_version_id IS NULL OR "
            "previous_price_version_id <> id",
            name="previous_version_distinct",
        ),
        Index(
            "uq_license_price_versions_open_plan",
            "plan_id",
            unique=True,
            postgresql_where=text("effective_to IS NULL"),
        ),
    )

    plan_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("license_plans.id", ondelete="RESTRICT"),
        nullable=False,
    )
    previous_price_version_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    monthly_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    annual_price_computed: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), Computed("monthly_price * 10", persisted=True),
        nullable=False,
    )
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    changed_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user_identities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(512), nullable=False)
