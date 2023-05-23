"""( [('add_column', , 'roles', Column('is_deleted', Boolean(), table=_roles_, default=ScalarElementColumnDefault(False))), ('add_column', , 'users', Column('is_deleted', Boolean(), table=_users_, default=ScalarElementColumnDefault(False)))]_,)

Revision ID: c507750a5b6d
Revises: 
Create Date: 2023-05-23 15:00:38.548853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c507750a5b6d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('irails_roles', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.add_column('irails_users', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('irails_users', 'is_deleted')
    op.drop_column('irails_roles', 'is_deleted')
    # ### end Alembic commands ###