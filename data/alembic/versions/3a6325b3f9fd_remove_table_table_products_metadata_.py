"""( [('remove_table', Table('products', MetaData(), Column('id', VARCHAR(), table=_products_, primary_key=True, nullable=False), Column('name', VARCHAR(length=50), table=_products_, nullable=False), schema=))]_,)

Revision ID: 3a6325b3f9fd
Revises: 
Create Date: 2023-12-14 19:24:46.452743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a6325b3f9fd'
down_revision = None
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
