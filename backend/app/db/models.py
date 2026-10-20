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
    SmallInteger,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import INET
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
        UniqueConstraint("id", "contracting_party_id"),
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
        Index("uq_license_plans_id_limits", "id", "member_limit", "quota_limit", unique=True),
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


class LicenseOffer(IdentityColumns, Base):
    """Fotografia comercial inativa; emissão e cobrança dependem de serviço futuro."""

    __tablename__ = "license_offers"

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "contracting_party_id"],
            ["tenants.id", "tenants.contracting_party_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["plan_id", "plan_member_limit", "plan_quota_limit"],
            ["license_plans.id", "license_plans.member_limit", "license_plans.quota_limit"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["plan_id", "price_version_id"],
            ["license_price_versions.plan_id", "license_price_versions.id"],
            ondelete="RESTRICT",
        ),
        # A chave composta permite ao aceite comprovar que todos os dados
        # replicados vieram da mesma oferta, inclusive identidade e documento.
        UniqueConstraint(
            "id", "tenant_id", "signer_user_id", "price_version_id",
            "effective_price", "period", "duration_months",
            "document_version", "document_hash",
        ),
        CheckConstraint(
            "contracting_party_name_snapshot ~ '[^[:space:]]'",
            name="party_name_nonblank",
        ),
        CheckConstraint(
            "plan_member_limit > 0 AND plan_quota_limit > 0",
            name="plan_limits_positive",
        ),
        CheckConstraint(
            "requested_member_count > 0 AND requested_member_count <= plan_member_limit",
            name="requested_members_within_plan",
        ),
        CheckConstraint(
            "requested_quota_count > 0 AND requested_quota_count <= plan_quota_limit",
            name="requested_quotas_within_plan",
        ),
        CheckConstraint(
            "(period = 'MENSAL' AND duration_months = 1) OR "
            "(period = 'ANUAL' AND duration_months = 12)",
            name="period_duration_valid",
        ),
        CheckConstraint("effective_price > 0", name="effective_price_positive"),
        CheckConstraint("currency = 'BRL'", name="currency_brl"),
        CheckConstraint(
            "document_version ~ '[^[:space:]]'",
            name="document_version_nonblank",
        ),
        CheckConstraint("length(btrim(document_ref)) > 0", name="document_ref_nonblank"),
        CheckConstraint(
            "octet_length(document_hash) = 32",
            name="document_hash_sha256_length",
        ),
        CheckConstraint("expires_at > issued_at", name="finite_validity"),
        CheckConstraint(
            "status = 'RASCUNHO_INATIVO'",
            name="status_initial_only",
        ),
        Index(
            "ix_license_offers_tenant_party",
            "tenant_id", "contracting_party_id",
        ),
        Index("ix_license_offers_tenant_plan", "tenant_id", "plan_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    contracting_party_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    signer_user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user_identities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    plan_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    price_version_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    contracting_party_name_snapshot: Mapped[str] = mapped_column(
        String(200), nullable=False
    )
    plan_member_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    plan_quota_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    requested_member_count: Mapped[int] = mapped_column(Integer, nullable=False)
    requested_quota_count: Mapped[int] = mapped_column(Integer, nullable=False)
    period: Mapped[str] = mapped_column(String(8), nullable=False)
    duration_months: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    effective_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default=text("'BRL'")
    )
    document_version: Mapped[str] = mapped_column(String(128), nullable=False)
    document_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    document_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="RASCUNHO_INATIVO",
        server_default=text("'RASCUNHO_INATIVO'"),
    )


class TermAcceptance(IdentityColumns, Base):
    """Aceite de licença inativo; não comprova representação nem pagamento."""

    __tablename__ = "term_acceptances"

    __table_args__ = (
        UniqueConstraint("offer_id"),
        UniqueConstraint("id", "offer_id", "tenant_id", "price_version_id", "effective_price"),
        ForeignKeyConstraint(
            [
                "offer_id", "tenant_id", "user_id", "price_version_id",
                "effective_price", "period", "duration_months",
                "document_version", "document_hash",
            ],
            [
                "license_offers.id", "license_offers.tenant_id",
                "license_offers.signer_user_id", "license_offers.price_version_id",
                "license_offers.effective_price", "license_offers.period",
                "license_offers.duration_months", "license_offers.document_version",
                "license_offers.document_hash",
            ],
            ondelete="RESTRICT",
        ),
        CheckConstraint("scope = 'LICENCA'", name="scope_initial_only"),
        CheckConstraint("cycle_id IS NULL", name="license_cycle_absent"),
        CheckConstraint("effective_price > 0", name="effective_price_positive"),
        CheckConstraint(
            "document_version ~ '[^[:space:]]'",
            name="document_version_nonblank",
        ),
        CheckConstraint(
            "octet_length(document_hash) = 32",
            name="document_hash_sha256_length",
        ),
        CheckConstraint(
            "evidence_ref ~ '[^[:space:]]'",
            name="evidence_ref_nonblank",
        ),
        Index("ix_term_acceptances_tenant_offer", "tenant_id", "offer_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    cycle_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    offer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user_identities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    price_version_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    effective_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    period: Mapped[str] = mapped_column(String(8), nullable=False)
    duration_months: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    document_version: Mapped[str] = mapped_column(String(128), nullable=False)
    document_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ip_address: Mapped[str] = mapped_column(INET, nullable=False)
    evidence_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    scope: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="LICENCA",
        server_default=text("'LICENCA'"),
    )

    # Uma etapa futura deve validar: autorização PF/PJ do signatário,
    # versão vigente e preço efetivo da oferta, estado do plano, ausência
    # de checkout Ampliado e imutabilidade contra UPDATE/DELETE no banco.


class LicensePaymentObligation(IdentityColumns, Base):
    """Obrigação comercial inativa ancorada em um aceite de licença."""

    __tablename__ = "license_payment_obligations"

    __table_args__ = (
        UniqueConstraint("offer_id"),
        UniqueConstraint("term_acceptance_id"),
        UniqueConstraint(
            "id", "tenant_id", "offer_id", "price_version_id", "expected_amount"
        ),
        ForeignKeyConstraint(
            [
                "term_acceptance_id", "offer_id", "tenant_id",
                "price_version_id", "expected_amount",
            ],
            [
                "term_acceptances.id", "term_acceptances.offer_id",
                "term_acceptances.tenant_id", "term_acceptances.price_version_id",
                "term_acceptances.effective_price",
            ],
            ondelete="RESTRICT",
        ),
        CheckConstraint("cycle_id IS NULL", name="license_cycle_absent"),
        CheckConstraint("expected_amount > 0", name="expected_amount_positive"),
        CheckConstraint("currency = 'BRL'", name="currency_brl"),
        CheckConstraint("purpose = 'LICENCA'", name="purpose_license"),
        CheckConstraint(
            "status = 'RASCUNHO_INATIVO'",
            name="status_initial_only",
        ),
        Index(
            "ix_license_payment_obligations_tenant_offer",
            "tenant_id", "offer_id",
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    cycle_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    offer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    term_acceptance_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    price_version_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    expected_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default=text("'BRL'")
    )
    purpose: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'LICENCA'")
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="RASCUNHO_INATIVO",
        server_default=text("'RASCUNHO_INATIVO'"),
    )


class Payment(IdentityColumns, Base):
    """Pagamento lógico inativo; futuras tentativas reutilizam este id."""

    __tablename__ = "payments"

    __table_args__ = (
        UniqueConstraint("obligation_id"),
        UniqueConstraint("idempotency_key"),
        UniqueConstraint("id", "tenant_id", "expected_amount"),
        ForeignKeyConstraint(
            [
                "obligation_id", "tenant_id", "offer_id",
                "price_version_id", "expected_amount",
            ],
            [
                "license_payment_obligations.id",
                "license_payment_obligations.tenant_id",
                "license_payment_obligations.offer_id",
                "license_payment_obligations.price_version_id",
                "license_payment_obligations.expected_amount",
            ],
            ondelete="RESTRICT",
        ),
        CheckConstraint("cycle_id IS NULL", name="license_cycle_absent"),
        CheckConstraint("expected_amount > 0", name="expected_amount_positive"),
        CheckConstraint(
            "confirmed_amount IS NULL OR confirmed_amount >= 0",
            name="confirmed_amount_nonnegative",
        ),
        CheckConstraint("currency = 'BRL'", name="currency_brl"),
        CheckConstraint("purpose = 'LICENCA'", name="purpose_license"),
        CheckConstraint(
            "receiver_domain = 'PLATAFORMA'",
            name="receiver_domain_platform",
        ),
        CheckConstraint(
            "(provider IS NULL AND external_id IS NULL) OR "
            "(provider IS NOT NULL AND external_id IS NOT NULL)",
            name="provider_external_pair",
        ),
        CheckConstraint(
            "external_id IS NULL OR receiver_ref IS NOT NULL",
            name="external_receiver_required",
        ),
        CheckConstraint(
            "status = 'NAO_INICIADO_INATIVO'",
            name="status_initial_only",
        ),
        CheckConstraint(
            "confirmed_amount IS NULL AND provider IS NULL "
            "AND external_id IS NULL AND receiver_ref IS NULL "
            "AND confirmed_at IS NULL AND evidence_ref IS NULL",
            name="initial_financial_fields_absent",
        ),
        Index("ix_payments_tenant_obligation", "tenant_id", "obligation_id"),
        Index("ix_payments_tenant_offer", "tenant_id", "offer_id"),
        Index(
            "uq_payments_provider_receiver_external",
            "provider", "receiver_ref", "external_id",
            unique=True,
            postgresql_where=text("external_id IS NOT NULL"),
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    cycle_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    obligation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    offer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    price_version_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    expected_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    confirmed_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default=text("'BRL'")
    )
    purpose: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'LICENCA'")
    )
    receiver_domain: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'PLATAFORMA'")
    )
    idempotency_key: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    receiver_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    evidence_ref: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="NAO_INICIADO_INATIVO",
        server_default=text("'NAO_INICIADO_INATIVO'"),
    )

    # Serviço e migration futuros devem proteger valor, histórico e transições,
    # validar conta recebedora, consultar o provedor e conciliar reversões.


class PaymentAttempt(IdentityColumns, Base):
    """Tentativa inativa vinculada ao mesmo pagamento economico."""

    __tablename__ = "payment_attempts"

    __table_args__ = (
        UniqueConstraint("payment_id", "attempt_number"),
        UniqueConstraint("idempotency_key"),
        UniqueConstraint("id", "payment_id", "tenant_id", "environment"),
        ForeignKeyConstraint(
            ["payment_id", "tenant_id", "expected_amount"],
            ["payments.id", "payments.tenant_id", "payments.expected_amount"],
            ondelete="RESTRICT",
        ),
        CheckConstraint("attempt_number > 0", name="attempt_number_positive"),
        CheckConstraint(
            "environment IN ('DEMO', 'HOMOLOGACAO', 'PRODUCAO')",
            name="environment_valid",
        ),
        CheckConstraint(
            "status = 'NAO_INICIADA_INATIVA'",
            name="status_initial_only",
        ),
        CheckConstraint(
            "provider IS NULL AND charge_ref IS NULL AND receiver_ref IS NULL",
            name="initial_external_fields_absent",
        ),
        Index(
            "ix_payment_attempts_tenant_payment_number",
            "tenant_id", "payment_id", "attempt_number",
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    payment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    environment: Mapped[str] = mapped_column(String(16), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    charge_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    receiver_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="NAO_INICIADA_INATIVA",
        server_default=text("'NAO_INICIADA_INATIVA'"),
    )


class PaymentReconciliationEvent(IdentityColumns, Base):
    """Observacao registrada para conciliacao operacional futura."""

    __tablename__ = "payment_reconciliation_events"

    __table_args__ = (
        UniqueConstraint(
            "provider", "environment", "observation_source", "event_key"
        ),
        ForeignKeyConstraint(
            ["attempt_id", "payment_id", "tenant_id", "environment"],
            [
                "payment_attempts.id", "payment_attempts.payment_id",
                "payment_attempts.tenant_id", "payment_attempts.environment",
            ],
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "environment IN ('DEMO', 'HOMOLOGACAO', 'PRODUCAO')",
            name="environment_valid",
        ),
        CheckConstraint("provider ~ '[^[:space:]]'", name="provider_nonblank"),
        CheckConstraint(
            "observation_source ~ '[^[:space:]]'",
            name="observation_source_nonblank",
        ),
        CheckConstraint("event_key ~ '[^[:space:]]'", name="event_key_nonblank"),
        CheckConstraint(
            "provider_status ~ '[^[:space:]]'",
            name="provider_status_nonblank",
        ),
        CheckConstraint(
            "observed_currency IS NULL OR observed_currency ~ '[^[:space:]]'",
            name="observed_currency_nonblank",
        ),
        CheckConstraint(
            "observed_receiver_ref IS NULL OR observed_receiver_ref ~ '[^[:space:]]'",
            name="observed_receiver_ref_nonblank",
        ),
        CheckConstraint(
            "evidence_ref ~ '[^[:space:]]'",
            name="evidence_ref_nonblank",
        ),
        CheckConstraint(
            "octet_length(evidence_hash) = 32",
            name="evidence_hash_sha256_length",
        ),
        CheckConstraint(
            "status = 'REGISTRADO_NAO_CONCILIADO'",
            name="status_initial_only",
        ),
        Index(
            "ix_payment_reconciliation_events_tenant_payment_attempt",
            "tenant_id", "payment_id", "attempt_id",
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    payment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    attempt_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    environment: Mapped[str] = mapped_column(String(16), nullable=False)
    observation_source: Mapped[str] = mapped_column(String(32), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    event_key: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_status: Mapped[str] = mapped_column(String(64), nullable=False)
    observed_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    observed_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    observed_receiver_ref: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    observed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    evidence_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    evidence_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="REGISTRADO_NAO_CONCILIADO",
        server_default=text("'REGISTRADO_NAO_CONCILIADO'"),
    )

    # Sem payload bruto ou efeito financeiro. Imutabilidade, replay e
    # conciliacao de divergencias exigem PostgreSQL e servicos futuros.
