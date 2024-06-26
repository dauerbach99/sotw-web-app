"""fresh start with alembic

Revision ID: abcde3fdd9fc
Revises: 
Create Date: 2024-05-20 18:22:18.560175

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "abcde3fdd9fc"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "sotw",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("results_datetime", sa.Integer(), nullable=False),
        sa.Column("master_playlist_link", sa.String(), nullable=False),
        sa.Column("soty_playlist_link", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sotw_user_association_table",
        sa.Column("sotw_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["sotw_id"],
            ["sotw.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("sotw_id", "user_id"),
    )
    op.create_table(
        "userplaylist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("playlist_link", sa.String(), nullable=True),
        sa.Column("sotw_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["sotw_id"],
            ["sotw.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "week",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("week_num", sa.Integer(), nullable=False),
        sa.Column("playlist_link", sa.String(), nullable=False),
        sa.Column("sotw_id", sa.Integer(), nullable=False),
        sa.Column("next_results_release", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["sotw_id"],
            ["sotw.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "response",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("next_song_id", sa.Integer(), nullable=False),
        sa.Column("sotw_id", sa.Integer(), nullable=False),
        sa.Column("week_id", sa.String(), nullable=False),
        sa.Column("submitter_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["sotw_id"],
            ["sotw.id"],
        ),
        sa.ForeignKeyConstraint(
            ["submitter_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["week_id"],
            ["week.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "song",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("submitter_id", sa.Integer(), nullable=False),
        sa.Column("response_id", sa.Integer(), nullable=False),
        sa.Column("spotify_link", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["response_id"],
            ["response.id"],
        ),
        sa.ForeignKeyConstraint(
            ["submitter_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "usersongmatch",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("song_id", sa.Integer(), nullable=False),
        sa.Column("correct_guess", sa.Boolean(), nullable=False),
        sa.Column("response_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["response_id"],
            ["response.id"],
        ),
        sa.ForeignKeyConstraint(
            ["song_id"],
            ["song.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("usersongmatch")
    op.drop_table("song")
    op.drop_table("result")
    op.drop_table("response")
    op.drop_table("week")
    op.drop_table("userplaylist")
    op.drop_table("sotw_user_association_table")
    op.drop_table("user")
    op.drop_table("sotw")
    # ### end Alembic commands ###
