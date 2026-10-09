"""add professional to appointments

Revision ID: 6c2a41fca425
Revises: 32e97b38046d
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "6c2a41fca425"
down_revision = "32e97b38046d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "appointments",
        sa.Column("professional_id", sa.Integer(), nullable=True),
    )

    op.create_foreign_key(
        "fk_appointments_professional_id_professionals",
        "appointments",
        "professionals",
        ["professional_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "fk_appointments_professional_id_professionals",
        "appointments",
        type_="foreignkey",
    )

    op.drop_column(
        "appointments",
        "professional_id",
    )
