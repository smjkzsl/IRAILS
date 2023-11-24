"""( [('remove_table', Table('products', MetaData(), Column('id', VARCHAR(), table=_products_, primary_key=True, nullable=False), Column('name', VARCHAR(length=50), table=_products_, nullable=False), schema=))]_,)

Revision ID: 4fd8b844de33
Revises: 999d5f90b444
Create Date: 2023-11-24 19:48:41.486718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4fd8b844de33'
down_revision = '999d5f90b444'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('irails_products')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('irails_products',
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
