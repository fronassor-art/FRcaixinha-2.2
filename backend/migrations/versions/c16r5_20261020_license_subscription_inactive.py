"""Inactive license acts and entitlement segment placeholders.

This revision adds no data, payment confirmation, or usable license period.
The C15 initial migration remains frozen and unapplied by this code change.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "c16r5_20261020"
down_revision = "c15r2_20261020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_license_offers_c16_subscription_link",
        "license_offers",
        [
            "id", "tenant_id", "contracting_party_id", "plan_id",
            "price_version_id", "effective_price", "period", "duration_months",
        ],
    )
    op.create_table(
        "license_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "contracting_party_id", postgresql.UUID(as_uuid=True), nullable=False,
        ),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "term_acceptance_id", postgresql.UUID(as_uuid=True), nullable=False,
        ),
        sa.Column(
            "price_version_id", postgresql.UUID(as_uuid=True), nullable=False,
        ),
        sa.Column("period", sa.String(8), nullable=False),
        sa.Column("duration_months", sa.SmallInteger(), nullable=False),
        sa.Column("effective_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("paid_payment_id", postgresql.UUID(as_uuid=True)),
        sa.Column("starts_at", sa.DateTime(timezone=True)),
        sa.Column("ends_at", sa.DateTime(timezone=True)),
        sa.Column("anchor_day", sa.SmallInteger()),
        sa.Column(
            "status", sa.String(32),
            server_default=sa.text("'RASCUNHO_INATIVO'"), nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_license_subscriptions"),
        sa.UniqueConstraint("offer_id", name="uq_license_subscriptions_offer_id"),
        sa.UniqueConstraint(
            "term_acceptance_id",
            name="uq_license_subscriptions_term_acceptance_id",
        ),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_license_subscriptions_id_tenant",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "contracting_party_id"],
            ["tenants.id", "tenants.contracting_party_id"],
            name="fk_license_subscriptions_tenant_party",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            [
                "offer_id", "tenant_id", "contracting_party_id", "plan_id",
                "price_version_id", "effective_price", "period", "duration_months",
            ],
            [
                "license_offers.id", "license_offers.tenant_id",
                "license_offers.contracting_party_id", "license_offers.plan_id",
                "license_offers.price_version_id", "license_offers.effective_price",
                "license_offers.period", "license_offers.duration_months",
            ],
            name="fk_license_subscriptions_offer_context",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            [
                "term_acceptance_id", "offer_id", "tenant_id",
                "price_version_id", "effective_price",
            ],
            [
                "term_acceptances.id", "term_acceptances.offer_id",
                "term_acceptances.tenant_id", "term_acceptances.price_version_id",
                "term_acceptances.effective_price",
            ],
            name="fk_license_subscriptions_acceptance_context",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "(period = 'MENSAL' AND duration_months = 1) OR "
            "(period = 'ANUAL' AND duration_months = 12)",
            name="ck_license_subscriptions_period_duration_valid",
        ),
        sa.CheckConstraint(
            "effective_price > 0",
            name="ck_license_subscriptions_effective_price_positive",
        ),
        sa.CheckConstraint(
            "status = 'RASCUNHO_INATIVO'",
            name="ck_license_subscriptions_status_initial_only",
        ),
        sa.CheckConstraint(
            "paid_payment_id IS NULL AND starts_at IS NULL AND "
            "ends_at IS NULL AND anchor_day IS NULL",
            name="ck_license_subscriptions_initial_entitlement_absent",
        ),
    )
    op.create_index(
        "ix_license_subscriptions_tenant_offer",
        "license_subscriptions", ["tenant_id", "offer_id"],
    )
    op.create_table(
        "license_entitlement_segments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "subscription_id", postgresql.UUID(as_uuid=True), nullable=False,
        ),
        sa.Column("segment_number", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True)),
        sa.Column("period_end", sa.DateTime(timezone=True)),
        sa.Column("anchor_day", sa.SmallInteger()),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True)),
        sa.Column("amount_allocated", sa.Numeric(18, 2)),
        sa.Column("calculated_at", sa.DateTime(timezone=True)),
        sa.Column("origin_segment_id", postgresql.UUID(as_uuid=True)),
        sa.Column(
            "status", sa.String(32),
            server_default=sa.text("'RASCUNHO_INATIVO'"), nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_license_entitlement_segments"),
        sa.UniqueConstraint(
            "subscription_id", "segment_number",
            name="uq_license_entitlement_segments_subscription_number",
        ),
        sa.UniqueConstraint(
            "id", "tenant_id",
            name="uq_license_entitlement_segments_origin_key",
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id", "tenant_id"],
            ["license_subscriptions.id", "license_subscriptions.tenant_id"],
            name="fk_license_entitlement_segments_subscription_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["origin_segment_id", "tenant_id"],
            [
                "license_entitlement_segments.id",
                "license_entitlement_segments.tenant_id",
            ],
            name="fk_license_entitlement_segments_origin_context",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "segment_number > 0",
            name="ck_license_entitlement_segments_segment_number_positive",
        ),
        sa.CheckConstraint(
            "status = 'RASCUNHO_INATIVO'",
            name="ck_license_entitlement_segments_status_initial_only",
        ),
        sa.CheckConstraint(
            "period_start IS NULL AND period_end IS NULL AND anchor_day IS NULL "
            "AND payment_id IS NULL AND amount_allocated IS NULL "
            "AND calculated_at IS NULL AND origin_segment_id IS NULL",
            name="ck_license_entitlement_segments_initial_entitlement_absent",
        ),
    )
    op.create_index(
        "ix_license_entitlement_segments_tenant_subscription",
        "license_entitlement_segments", ["tenant_id", "subscription_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_license_entitlement_segments_tenant_subscription",
        table_name="license_entitlement_segments",
    )
    op.drop_table("license_entitlement_segments")
    op.drop_index(
        "ix_license_subscriptions_tenant_offer",
        table_name="license_subscriptions",
    )
    op.drop_table("license_subscriptions")
    op.drop_constraint(
        "uq_license_offers_c16_subscription_link",
        "license_offers",
        type_="unique",
    )
