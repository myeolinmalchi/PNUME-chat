"""학기 구분에 여름, 겨울방학 추가

Revision ID: 697d4c9be412
Revises: 52432bfbaee2
Create Date: 2025-02-02 03:41:10.484414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '697d4c9be412'
down_revision: Union[str, None] = '52432bfbaee2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('notice_content_chunks', 'notice_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('notice_content_chunks', 'notice_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
