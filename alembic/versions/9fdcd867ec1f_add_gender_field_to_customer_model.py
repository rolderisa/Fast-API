"""Add gender field to Customer model

Revision ID: 9fdcd867ec1f
Revises: f8edb8d068f2
Create Date: 2024-11-22 09:25:13.047864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fdcd867ec1f'
down_revision: Union[str, None] = 'f8edb8d068f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('customers', sa.Column('gender', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('customers', 'gender')
    # ### end Alembic commands ###
