"""replace age with student details

Revision ID: c4a7b9d1e2f3
Revises: 87ff195310ce
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4a7b9d1e2f3"
down_revision: Union[str, Sequence[str], None] = "87ff195310ce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "students",
        sa.Column("date_of_birth", sa.Date(), nullable=True),
    )
    op.add_column(
        "students",
        sa.Column("study_program", sa.String(100), nullable=True),
    )
    op.add_column(
        "students",
        sa.Column("phone", sa.String(30), nullable=True),
    )
    op.add_column(
        "students",
        sa.Column("enrollment_date", sa.Date(), nullable=True),
    )
    op.execute(
        """
        UPDATE students
        SET date_of_birth = STR_TO_DATE(CONCAT(YEAR(CURDATE()) - age, '-01-01'), '%Y-%m-%d'),
            study_program = 'Not specified',
            phone = 'Not specified',
            enrollment_date = CURDATE()
        """
    )
    op.drop_column("students", "age")
    op.alter_column(
        "students",
        "date_of_birth",
        existing_type=sa.Date(),
        nullable=False,
    )
    op.alter_column(
        "students",
        "study_program",
        existing_type=sa.String(100),
        nullable=False,
    )
    op.alter_column(
        "students",
        "phone",
        existing_type=sa.String(30),
        nullable=False,
    )
    op.alter_column(
        "students",
        "enrollment_date",
        existing_type=sa.Date(),
        nullable=False,
    )
    op.alter_column(
        "students",
        "name",
        existing_type=sa.String(100),
        nullable=False,
    )
    op.alter_column(
        "students",
        "email",
        existing_type=sa.String(100),
        nullable=False,
    )
    op.create_unique_constraint("uq_students_email", "students", ["email"])
    op.create_check_constraint(
        "ck_students_name_no_digits",
        "students",
        "name NOT REGEXP '[0-9]'",
    )
    op.create_check_constraint(
        "ck_students_dates_ordered",
        "students",
        "date_of_birth < enrollment_date",
    )


def downgrade() -> None:
    op.drop_constraint("ck_students_dates_ordered", "students", type_="check")
    op.drop_constraint("ck_students_name_no_digits", "students", type_="check")
    op.drop_constraint("uq_students_email", "students", type_="unique")
    op.add_column("students", sa.Column("age", sa.Integer(), nullable=True))
    op.drop_column("students", "enrollment_date")
    op.drop_column("students", "phone")
    op.drop_column("students", "study_program")
    op.drop_column("students", "date_of_birth")
