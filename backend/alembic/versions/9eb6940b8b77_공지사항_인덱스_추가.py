"""공지사항 인덱스 추가

Revision ID: 9eb6940b8b77
Revises: afe8a1d6d543
Create Date: 2025-02-09 20:58:54.708426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9eb6940b8b77'
down_revision: Union[str, None] = 'afe8a1d6d543'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    weekday_enum = postgresql.ENUM(
        '월',
        '화',
        '수',
        '목',
        '금',
        '토',
        '일',
        name='weekdayenum',
        create_type=False
    )

    weekday_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('courses', sa.Column('note', sa.String(), nullable=True))
    op.create_index(
        op.f('ix_notice_attachments_notice_id'),
        'notice_attachments', ['notice_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_notice_content_chunks_notice_id'),
        'notice_content_chunks', ['notice_id'],
        unique=False
    )
    op.create_index(
        'ix_notice_department_semester',
        'notices', ['department_id', 'semester_id'],
        unique=False
    )
    op.alter_column(
        'subjects', 'department_id', existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        'subjects',
        'level',
        existing_type=postgresql.ENUM('대학', '대학원', name='levelenum'),
        nullable=False
    )
    op.alter_column(
        'timetables',
        'day_of_week',
        existing_type=sa.VARCHAR(),
        type_=sa.Enum('월', '화', '수', '목', '금', '토', '일', name='weekdayenum'),
        postgresql_using="day_of_week::weekdayenum"
        #existing_nullable=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'timetables',
        'day_of_week',
        existing_type=sa.Enum(
            '월', '화', '수', '목', '금', '토', '일', name='weekdayenum'
        ),
        type_=sa.VARCHAR(),
        existing_nullable=False
    )
    op.alter_column(
        'subjects',
        'level',
        existing_type=postgresql.ENUM('대학', '대학원', name='levelenum'),
        nullable=True
    )
    op.alter_column(
        'subjects', 'department_id', existing_type=sa.INTEGER(), nullable=True
    )
    op.drop_index('ix_notice_department_semester', table_name='notices')
    op.drop_index(
        op.f('ix_notice_content_chunks_notice_id'),
        table_name='notice_content_chunks'
    )
    op.drop_index(
        op.f('ix_notice_attachments_notice_id'),
        table_name='notice_attachments'
    )
    op.drop_column('courses', 'note')
    # ### end Alembic commands ###
