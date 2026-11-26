"""001 — Initial schema: users, profiles, aqi_readings, daily_plans, 
knowledge_chunks (pgvector), communities, alert_subscriptions.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

EMBEDDING_DIM = 1536


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", sa.String(254), unique=True, nullable=True),
        sa.Column("hashed_password", sa.Text, nullable=True),
        sa.Column("is_anonymous", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("preferred_language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── user_profiles ─────────────────────────────────────────────────────────
    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=False, server_default="Maharashtra"),
        sa.Column("country", sa.String(100), nullable=False, server_default="India"),
        sa.Column("pin_code", sa.String(10), nullable=True),
        sa.Column("nearest_aqi_station_id", sa.String(64), nullable=True),
        sa.Column("has_children", sa.Boolean, server_default="false"),
        sa.Column("has_elderly", sa.Boolean, server_default="false"),
        sa.Column("has_asthma_respiratory", sa.Boolean, server_default="false"),
        sa.Column("has_pregnancy", sa.Boolean, server_default="false"),
        sa.Column("household_size", sa.Integer, server_default="2"),
        sa.Column("home_type", sa.String(32), server_default="apartment"),
        sa.Column("cooking_fuel", sa.String(32), server_default="lpg"),
        sa.Column("has_kitchen_exhaust", sa.Boolean, server_default="false"),
        sa.Column("num_windows", sa.Integer, server_default="4"),
        sa.Column("heating_type", sa.String(32), server_default="none"),
        sa.Column("commute_mode", sa.String(32), server_default="two_wheeler_petrol"),
        sa.Column("commute_distance_km", sa.Float, server_default="10.0"),
        sa.Column("budget_level", sa.String(16), server_default="medium"),
        sa.Column("available_devices", postgresql.JSONB, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── aqi_readings ──────────────────────────────────────────────────────────
    op.create_table(
        "aqi_readings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("lat_rounded", sa.Float, nullable=False),
        sa.Column("lon_rounded", sa.Float, nullable=False),
        sa.Column("station_id", sa.String(64), nullable=True),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("aqi", sa.Integer, nullable=True),
        sa.Column("aqi_category", sa.String(32), nullable=True),
        sa.Column("pm25", sa.Float, nullable=True),
        sa.Column("pm10", sa.Float, nullable=True),
        sa.Column("no2", sa.Float, nullable=True),
        sa.Column("so2", sa.Float, nullable=True),
        sa.Column("co", sa.Float, nullable=True),
        sa.Column("o3", sa.Float, nullable=True),
        sa.Column("temperature_c", sa.Float, nullable=True),
        sa.Column("humidity_pct", sa.Float, nullable=True),
        sa.Column("wind_speed_ms", sa.Float, nullable=True),
        sa.Column("wind_direction_deg", sa.Integer, nullable=True),
        sa.Column("temperature_inversion", sa.Boolean, server_default="false"),
        sa.Column("raw_payload", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_aqi_readings_location_time", "aqi_readings", ["lat_rounded", "lon_rounded", "observed_at"])

    # ── daily_plans ───────────────────────────────────────────────────────────
    op.create_table(
        "daily_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_date", sa.Date, nullable=False),
        sa.Column("aqi_reading_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("aqi_readings.id"), nullable=True),
        sa.Column("plan_json", postgresql.JSONB, nullable=False),
        sa.Column("total_pm25_reduction_ug_m3_h", sa.Float, server_default="0"),
        sa.Column("total_co2e_avoided_kg", sa.Float, server_default="0"),
        sa.Column("total_pm_avoided_kg", sa.Float, server_default="0"),
        sa.Column("confidence_level", sa.String(16), server_default="medium"),
        sa.Column("llm_model_used", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── knowledge_chunks ──────────────────────────────────────────────────────
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("source_title", sa.String(256), nullable=False),
        sa.Column("source_url", sa.String(512), nullable=True),
        sa.Column("source_type", sa.String(64), nullable=False),
        sa.Column("tags", postgresql.JSONB, server_default="[]"),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("token_count", sa.Integer, nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    # HNSW index for fast approximate nearest-neighbour search
    op.execute("""
        CREATE INDEX ix_knowledge_chunks_embedding_hnsw
        ON knowledge_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    # ── communities ───────────────────────────────────────────────────────────
    op.create_table(
        "communities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("community_type", sa.String(32), server_default="neighbourhood"),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("is_public", sa.Boolean, server_default="true"),
        sa.Column("invite_code", sa.String(16), unique=True, nullable=True),
        sa.Column("total_co2e_avoided_kg", sa.Float, server_default="0"),
        sa.Column("total_pm25_reduction_ug_m3_h", sa.Float, server_default="0"),
        sa.Column("member_count", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "community_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("community_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("communities.id", ondelete="CASCADE")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("role", sa.String(16), server_default="member"),
        sa.Column("weekly_score", sa.Float, server_default="0"),
        sa.Column("total_score", sa.Float, server_default="0"),
        sa.Column("streak_days", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("community_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("communities.id", ondelete="CASCADE")),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("status", sa.String(16), server_default="upcoming"),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("target_co2e_kg", sa.Float, nullable=True),
        sa.Column("achieved_co2e_kg", sa.Float, server_default="0"),
        sa.Column("badge_icon", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── alert_subscriptions / deliveries ──────────────────────────────────────
    op.create_table(
        "alert_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("push_enabled", sa.Boolean, server_default="false"),
        sa.Column("push_subscription_json", postgresql.JSONB, nullable=True),
        sa.Column("whatsapp_enabled", sa.Boolean, server_default="false"),
        sa.Column("whatsapp_phone", sa.String(20), nullable=True),
        sa.Column("sms_enabled", sa.Boolean, server_default="false"),
        sa.Column("sms_phone", sa.String(20), nullable=True),
        sa.Column("aqi_threshold", sa.Integer, server_default="200"),
        sa.Column("alert_best_window", sa.Boolean, server_default="true"),
        sa.Column("quiet_start_hour", sa.Integer, server_default="22"),
        sa.Column("quiet_end_hour", sa.Integer, server_default="7"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "alert_deliveries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("alert_subscriptions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alert_type", sa.String(32), nullable=False),
        sa.Column("channel", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload_json", postgresql.JSONB, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("alert_deliveries")
    op.drop_table("alert_subscriptions")
    op.drop_table("challenges")
    op.drop_table("community_members")
    op.drop_table("communities")
    op.drop_table("knowledge_chunks")
    op.drop_table("daily_plans")
    op.drop_table("aqi_readings")
    op.drop_table("user_profiles")
    op.drop_table("users")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
    op.execute("DROP EXTENSION IF EXISTS vector")

