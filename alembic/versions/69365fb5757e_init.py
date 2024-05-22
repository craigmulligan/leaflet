"""init

Revision ID: 69365fb5757e
Revises:
Create Date: 2024-05-13 14:47:16.029444

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector


# revision identifiers, used by Alembic.
revision: str = "69365fb5757e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_account",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("is_email_confirmed", sa.Boolean(), nullable=True),
        sa.Column("prompt", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "leaflet",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_account.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipe",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("leaflet_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("servings", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("estimated_time", sa.Integer(), nullable=False),
        sa.Column("image", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["leaflet_id"],
            ["leaflet.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipe_embedding",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(dim=1536), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipe.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipe_ingredient",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipe.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipe_step",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipe.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("recipe_step")
    op.drop_table("recipe_ingredient")
    op.drop_table("recipe_embedding")
    op.drop_table("recipe")
    op.drop_table("leaflet")
    op.drop_table("user_account")
    # ### end Alembic commands ###
