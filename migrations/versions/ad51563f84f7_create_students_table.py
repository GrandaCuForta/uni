"""create students table

Revision ID: ad51563f84f7
Revises: 
Create Date: 2026-09-03 19:46:10.717791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad51563f84f7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100)),
        sa.Column('email', sa.String(100))
    )


def downgrade() -> None:
    op.drop_table('students')