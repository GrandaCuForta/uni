"""add age colum

Revision ID: e030e836ce46
Revises: ad51563f84f7
Create Date: 2026-09-03 19:55:34.068941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e030e836ce46'
down_revision: Union[str, Sequence[str], None] = 'ad51563f84f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'students',
        sa.Column('age', sa.Integer())
    )


def downgrade() -> None:
    op.drop_column('students', 'age')
