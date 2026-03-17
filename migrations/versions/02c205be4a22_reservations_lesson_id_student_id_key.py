"""reservations_lesson_id_student_id_key

Revision ID: 02c205be4a22
Revises: a3e914fd0265
Create Date: 2026-02-02 11:44:54.788340

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "02c205be4a22"
down_revision: Union[str, Sequence[str], None] = "a3e914fd0265"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "reservations_lesson_id_student_id_key", "reservations", type_="unique"
    )

    op.execute("""
                   CREATE UNIQUE INDEX ux_active_reservation_student_lesson
                       ON reservations (student_id, lesson_id) WHERE is_active = true;
                   """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP INDEX ux_active_reservation_student_lesson;
    """)

    op.create_unique_constraint(
        "reservations_lesson_id_student_id_key",
        "reservations",
        ["lesson_id", "student_id"],
    )
