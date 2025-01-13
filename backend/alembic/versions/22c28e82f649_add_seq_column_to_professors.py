"""Add seq column to 'professors'

Revision ID: 22c28e82f649
Revises: 16593effbe7b
Create Date: 2025-01-13 22:24:30.221976

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22c28e82f649'
down_revision: Union[str, None] = '16593effbe7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('professors', sa.Column('seq', sa.Integer(), nullable=False))
    op.create_unique_constraint('uq_major_seq', 'professors', ['seq', 'major_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_major_seq', 'professors', type_='unique')
    op.drop_column('professors', 'seq')
    # ### end Alembic commands ###