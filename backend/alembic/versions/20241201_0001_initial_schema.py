"""Initial schema for Neighborhood Story Weaver.

Revision ID: 0001
Revises:
Create Date: 2024-12-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create anecdotes table
    op.create_table(
        "anecdotes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_name", sa.String(length=100), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("is_approved", sa.Boolean(), nullable=False, default=True),
        sa.Column("is_featured", sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_anecdotes_id"), "anecdotes", ["id"], unique=False)

    # Create weather_snapshots table
    op.create_table(
        "weather_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("temp_high", sa.Float(), nullable=True),
        sa.Column("temp_low", sa.Float(), nullable=True),
        sa.Column("temp_current", sa.Float(), nullable=True),
        sa.Column("feels_like", sa.Float(), nullable=True),
        sa.Column("condition", sa.String(length=100), nullable=True),
        sa.Column("condition_description", sa.String(length=255), nullable=True),
        sa.Column("icon", sa.String(length=20), nullable=True),
        sa.Column("humidity", sa.Integer(), nullable=True),
        sa.Column("wind_speed", sa.Float(), nullable=True),
        sa.Column("wind_direction", sa.Integer(), nullable=True),
        sa.Column("sunrise", sa.DateTime(), nullable=True),
        sa.Column("sunset", sa.DateTime(), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("snapshot_date"),
    )
    op.create_index(
        op.f("ix_weather_snapshots_id"), "weather_snapshots", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_weather_snapshots_snapshot_date"),
        "weather_snapshots",
        ["snapshot_date"],
        unique=True,
    )

    # Create story_chapters table
    op.create_table(
        "story_chapters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chapter_date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("weather_summary", sa.String(length=500), nullable=True),
        sa.Column("tide_state", sa.String(length=50), nullable=True),
        sa.Column("season", sa.String(length=20), nullable=False),
        sa.Column("month_name", sa.String(length=20), nullable=False),
        sa.Column("day_of_week", sa.String(length=15), nullable=False),
        sa.Column("used_anecdote_ids", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column(
            "generation_context", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chapter_date", name="uq_chapter_date"),
    )
    op.create_index(
        op.f("ix_story_chapters_id"), "story_chapters", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_story_chapters_chapter_date"),
        "story_chapters",
        ["chapter_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_story_chapters_chapter_date"), table_name="story_chapters")
    op.drop_index(op.f("ix_story_chapters_id"), table_name="story_chapters")
    op.drop_table("story_chapters")

    op.drop_index(
        op.f("ix_weather_snapshots_snapshot_date"), table_name="weather_snapshots"
    )
    op.drop_index(op.f("ix_weather_snapshots_id"), table_name="weather_snapshots")
    op.drop_table("weather_snapshots")

    op.drop_index(op.f("ix_anecdotes_id"), table_name="anecdotes")
    op.drop_table("anecdotes")
