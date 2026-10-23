"""Draft of offline identity bootstrap storage; never applied by this file.

Revision ID: f2p4_20261022
Revises: c16r5_20261020
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "f2p4_20261022"
down_revision = "c16r5_20261020"
branch_labels = None
depends_on = None


_TABLE_ORDER = (
    "identity_credentials",
    "email_confirmation_challenges",
    "registration_idempotency",
    "identity_sessions",
)


def upgrade() -> None:
    op.create_table(
        "identity_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("identity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("password_digest", sa.String(160), nullable=False),
        sa.Column("status", sa.String(24), nullable=False,
                  server_default=sa.text("'PENDING_EMAIL'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id", name="pk_identity_credentials"),
        sa.UniqueConstraint("identity_id", name="uq_identity_credentials_identity_id"),
        sa.ForeignKeyConstraint(["identity_id"], ["user_identities.id"],
                                name="fk_identity_credentials_identity_id_user_identities",
                                ondelete="RESTRICT"),
        sa.CheckConstraint(
            "status IN ('PENDING_EMAIL', 'ACTIVE', 'REVOKED')",
            name="ck_identity_credentials_status_valid",
        ),
        sa.CheckConstraint(
            "password_digest LIKE 'scrypt$v1$%'",
            name="ck_identity_credentials_digest_format",
        ),
    )
    op.create_table(
        "email_confirmation_challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("identity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("verifier_sha256", sa.LargeBinary(), nullable=False),
        sa.Column("purpose", sa.String(32), nullable=False,
                  server_default=sa.text("'INITIAL_EMAIL'")),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("id", name="pk_email_confirmation_challenges"),
        sa.UniqueConstraint("verifier_sha256",
                            name="uq_email_confirmation_challenges_verifier"),
        sa.ForeignKeyConstraint(["identity_id"], ["user_identities.id"],
                                name="fk_email_confirmation_challenges_identity_id_user_identities",
                                ondelete="RESTRICT"),
        sa.CheckConstraint("octet_length(verifier_sha256) = 32",
                           name="ck_email_confirmation_challenges_verifier_size"),
        sa.CheckConstraint("purpose = 'INITIAL_EMAIL'",
                           name="ck_email_confirmation_challenges_purpose"),
        sa.CheckConstraint(
            "expires_at > issued_at AND "
            "expires_at <= issued_at + INTERVAL '10 minutes'",
            name="ck_email_confirmation_challenges_lifetime",
        ),
        sa.CheckConstraint("consumed_at IS NULL OR revoked_at IS NULL",
                           name="ck_email_confirmation_challenges_not_consumed_revoked"),
    )
    op.create_index(
        "ix_email_confirmation_challenges_identity_expires",
        "email_confirmation_challenges", ["identity_id", "expires_at"],
    )
    op.create_table(
        "registration_idempotency",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("origin_digest", sa.LargeBinary(), nullable=False),
        sa.Column("attempt_digest", sa.LargeBinary(), nullable=False),
        sa.Column("request_fingerprint", sa.LargeBinary(), nullable=False),
        sa.Column("identity_id", postgresql.UUID(as_uuid=True)),
        sa.Column("party_id", postgresql.UUID(as_uuid=True)),
        sa.Column("state", sa.String(16), nullable=False,
                  server_default=sa.text("'RESERVED'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_registration_idempotency"),
        sa.UniqueConstraint("origin_digest", "attempt_digest",
                            name="uq_registration_idempotency_origin_attempt"),
        sa.ForeignKeyConstraint(["identity_id"], ["user_identities.id"],
                                name="fk_registration_idempotency_identity_id_user_identities",
                                ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["party_id"], ["contracting_parties.id"],
                                name="fk_registration_idempotency_party_id_contracting_parties",
                                ondelete="RESTRICT"),
        sa.CheckConstraint(
            "octet_length(origin_digest) = 32 AND "
            "octet_length(attempt_digest) = 32 AND "
            "octet_length(request_fingerprint) = 32",
            name="ck_registration_idempotency_digest_sizes",
        ),
        sa.CheckConstraint(
            "(state = 'RESERVED' AND identity_id IS NULL AND party_id IS NULL) "
            "OR (state = 'COMPLETED' AND identity_id IS NOT NULL "
            "AND party_id IS NOT NULL)",
            name="ck_registration_idempotency_state_result",
        ),
        sa.CheckConstraint(
            "expires_at > created_at AND "
            "expires_at <= created_at + INTERVAL '15 minutes'",
            name="ck_registration_idempotency_lifetime",
        ),
    )
    op.create_index("ix_registration_idempotency_expires",
                    "registration_idempotency", ["expires_at"])
    op.create_table(
        "identity_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("identity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("verifier_sha256", sa.LargeBinary(), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("id", name="pk_identity_sessions"),
        sa.UniqueConstraint("verifier_sha256",
                            name="uq_identity_sessions_verifier"),
        sa.ForeignKeyConstraint(["identity_id"], ["user_identities.id"],
                                name="fk_identity_sessions_identity_id_user_identities",
                                ondelete="RESTRICT"),
        sa.CheckConstraint("octet_length(verifier_sha256) = 32",
                           name="ck_identity_sessions_verifier_size"),
        sa.CheckConstraint(
            "expires_at > issued_at AND "
            "expires_at <= issued_at + INTERVAL '15 minutes'",
            name="ck_identity_sessions_lifetime",
        ),
    )
    op.create_index("ix_identity_sessions_identity_expires",
                    "identity_sessions", ["identity_id", "expires_at"])


def downgrade() -> None:
    raise RuntimeError("F2P4_DOWNGRADE_NOT_AUTHORIZED")
