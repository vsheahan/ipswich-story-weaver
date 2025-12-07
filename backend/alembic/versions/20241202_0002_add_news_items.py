"""Add news_items table and update story_chapters.

Revision ID: 0002
Revises: 0001
Create Date: 2024-12-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create news_items table
    op.create_table(
        "news_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("headline", sa.String(length=500), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("article_url", sa.String(length=1000), nullable=False),
        sa.Column("author", sa.String(length=200), nullable=True),
        sa.Column("category_label", sa.String(length=100), nullable=False, server_default="Ipswich"),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("article_url", name="uq_news_article_url"),
    )
    op.create_index(op.f("ix_news_items_id"), "news_items", ["id"], unique=False)

    # Add used_news_item_ids column to story_chapters
    op.add_column(
        "story_chapters",
        sa.Column("used_news_item_ids", postgresql.ARRAY(sa.Integer()), nullable=True),
    )

    # Drop used_anecdote_ids column from story_chapters (if it exists)
    # We'll wrap this in a try/except in case the column doesn't exist
    try:
        op.drop_column("story_chapters", "used_anecdote_ids")
    except Exception:
        pass  # Column may not exist in fresh installs

    # Drop anecdotes table (if it exists)
    try:
        op.drop_index(op.f("ix_anecdotes_id"), table_name="anecdotes")
        op.drop_table("anecdotes")
    except Exception:
        pass  # Table may not exist in fresh installs


def downgrade() -> None:
    # Re-add used_anecdote_ids to story_chapters
    op.add_column(
        "story_chapters",
        sa.Column("used_anecdote_ids", postgresql.ARRAY(sa.Integer()), nullable=True),
    )

    # Drop used_news_item_ids from story_chapters
    op.drop_column("story_chapters", "used_news_item_ids")

    # Drop news_items table
    op.drop_index(op.f("ix_news_items_id"), table_name="news_items")
    op.drop_table("news_items")

    # Re-create anecdotes table
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
