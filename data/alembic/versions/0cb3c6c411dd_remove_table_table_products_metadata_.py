"""( [('remove_table', Table('products', MetaData(), Column('id', VARCHAR(), table=_products_, primary_key=True, nullable=False), schema=))]_,)

Revision ID: 0cb3c6c411dd
Revises: de099edacab1
Create Date: 2023-06-11 10:20:34.333986

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cb3c6c411dd'
down_revision = 'de099edacab1'
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
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
