"""add age column

Revision ID: 87ff195310ce
Revises: e030e836ce46
Create Date: 2026-09-03 20:05:27.795992

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87ff195310ce'
down_revision: Union[str, Sequence[str], None] = 'e030e836ce46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'students',
        sa.Column('age', sa.Integer())
    )


def downgrade() -> None:
    op.drop_column('students', 'age')

