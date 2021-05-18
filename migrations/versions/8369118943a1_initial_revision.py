"""Initial Revision

Revision ID: 8369118943a1
Revises:
Create Date: 2018-11-05 01:06:24.495010

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8369118943a1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "challenges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("max_attempts", sa.Integer(), nullable=True),
        sa.Column("value", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(length=80), nullable=True),
        sa.Column("type", sa.String(length=80), nullable=True),
        sa.Column("state", sa.String(length=80), nullable=False),
        sa.Column("requirements", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.Text(), nullable=True),
        sa.Column("value", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=80), nullable=True),
        sa.Column("route", sa.String(length=128), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("draft", sa.Boolean(), nullable=True),
        sa.Column("hidden", sa.Boolean(), nullable=True),
        sa.Column("auth_required", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("route"),
    )
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("oauth_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=128), nullable=True),
        sa.Column("email", sa.String(length=128), nullable=True),
        sa.Column("password", sa.String(length=128), nullable=True),
        sa.Column("secret", sa.String(length=128), nullable=True),
        sa.Column("website", sa.String(length=128), nullable=True),
        sa.Column("affiliation", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=32), nullable=True),
        sa.Column("bracket", sa.String(length=32), nullable=True),
        sa.Column("hidden", sa.Boolean(), nullable=True),
        sa.Column("banned", sa.Boolean(), nullable=True),
        sa.Column("created", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("id", "oauth_id"),
        sa.UniqueConstraint("oauth_id"),
    )
    op.create_table(
        "files",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=80), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("challenge_id", sa.Integer(), nullable=True),
        sa.Column("page_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"]),
        sa.ForeignKeyConstraint(["page_id"], ["pages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "flags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(length=80), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("data", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ressources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=80), nullable=True),
        sa.Column("challenge_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("cost", sa.Integer(), nullable=True),
        sa.Column("requirements", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=True),
        sa.Column("value", sa.String(length=80), nullable=True),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("oauth_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=128), nullable=True),
        sa.Column("password", sa.String(length=128), nullable=True),
        sa.Column("email", sa.String(length=128), nullable=True),
        sa.Column("type", sa.String(length=80), nullable=True),
        sa.Column("secret", sa.String(length=128), nullable=True),
        sa.Column("website", sa.String(length=128), nullable=True),
        sa.Column("affiliation", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=32), nullable=True),
        sa.Column("bracket", sa.String(length=32), nullable=True),
        sa.Column("hidden", sa.Boolean(), nullable=True),
        sa.Column("banned", sa.Boolean(), nullable=True),
        sa.Column("verified", sa.Boolean(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("created", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("id", "oauth_id"),
        sa.UniqueConstraint("oauth_id"),
    )
    op.create_table(
        "awards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=80), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("value", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(length=80), nullable=True),
        sa.Column("icon", sa.Text(), nullable=True),
        sa.Column("requirements", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("ip", sa.String(length=46), nullable=True),
        sa.Column("provided", sa.Text(), nullable=True),
        sa.Column("type", sa.String(length=32), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["challenge_id"], ["challenges.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tracking",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=True),
        sa.Column("ip", sa.String(length=46), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "unlocks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("target", sa.Integer(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("type", sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "solves",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["challenge_id"], ["challenges.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["id"], ["submissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("challenge_id", "team_id"),
        sa.UniqueConstraint("challenge_id", "user_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("solves")
    op.drop_table("unlocks")
    op.drop_table("tracking")
    op.drop_table("submissions")
    op.drop_table("notifications")
    op.drop_table("awards")
    op.drop_table("users")
    op.drop_table("tags")
    op.drop_table("ressources")
    op.drop_table("flags")
    op.drop_table("files")
    op.drop_table("teams")
    op.drop_table("pages")
    op.drop_table("config")
    op.drop_table("challenges")
    # ### end Alembic commands ###
