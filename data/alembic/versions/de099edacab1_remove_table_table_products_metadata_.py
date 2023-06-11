"""( [('remove_table', Table('products', MetaData(), Column('id', VARCHAR(), table=_products_, primary_key=True, nullable=False), schema=))]_,)

Revision ID: de099edacab1
Revises: 68e47defb0d3
Create Date: 2023-06-11 10:10:55.909261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de099edacab1'
down_revision = '68e47defb0d3'
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
