"""Fix category_id column

Revision ID: 1a9c8a6bf49b
Revises: ad907d732dfa
Create Date: 2024-11-29 15:13:21.107306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a9c8a6bf49b'
down_revision: Union[str, None] = 'ad907d732dfa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
