"""( [('remove_table', Table('roles', MetaData(), Column('id', INTEGER(), table=_roles_, primary_key=True, nullable=False), Column('name', VARCHAR(length=50), table=_roles_, nullable=False), Column('update_at', DATETIME(), table=_roles_, server_default=DefaultClause(_sqlalchemy.sql.elements.TextClause object at 0x0000016CD1FAB760_, for_update=False)), Column('create_at', DATETIME(), table=_roles_, server_default=DefaultClause(_sqlalchemy.sql.elements.TextClause object at 0x0000016CD1FAB880_, for_update=False)), Column('is_deleted', BOOLEAN(), table=_roles_), schema=)), ('remove_table', Table('casbin_rule', MetaData(), Column('id', INTEGER(), table=_casbin_rule_, primary_key=True, nullable=False), Column('ptype', VARCHAR(length=255), table=_casbin_rule_), Column('v0', VARCHAR(length=255), table=_casbin_rule_), Column('v1', VARCHAR(length=255), table=_casbin_rule_), Column('v2', VARCHAR(length=255), table=_casbin_rule_), Column('v3', VARCHAR(length=255), table=_casbin_rule_), Column('v4', VARCHAR(length=255), table=_casbin_rule_), Column('v5', VARCHAR(length=255), table=_casbin_rule_), schema=)), ('remove_table', Table('users', MetaData(), Column('id', INTEGER(), table=_users_, primary_key=True, nullable=False), Column('username', VARCHAR(length=50), table=_users_, nullable=False), Column('fullname', VARCHAR(length=50), table=_users_, nullable=False), Column('domain', VARCHAR(length=50), table=_users_), Column('password', VARCHAR(length=50), table=_users_, nullable=False), Column('age', INTEGER(), table=_users_, nullable=False), Column('salt', VARCHAR(length=50), table=_users_), Column('remark', VARCHAR(length=255), table=_users_), Column('update_at', DATETIME(), table=_users_, server_default=DefaultClause(_sqlalchemy.sql.elements.TextClause object at 0x0000016CD1FA9780_, for_update=False)), Column('create_at', DATETIME(), table=_users_, server_default=DefaultClause(_sqlalchemy.sql.elements.TextClause object at 0x0000016CD1FA95A0_, for_update=False)), Column('is_deleted', BOOLEAN(), table=_users_), schema=)), ('remove_table', Table('user_role', MetaData(), Column('user_id', INTEGER(), ForeignKey('users.id'), table=_user_role_, primary_key=True, nullable=False), Column('role_id', INTEGER(), ForeignKey('roles.id'), table=_user_role_, primary_key=True, nullable=False), schema=)), ('remove_table', Table('products', MetaData(), Column('id', VARCHAR(), table=_products_, primary_key=True, nullable=False), Column('name', VARCHAR(length=50), table=_products_, nullable=False), schema=)), ('remove_table', Table('apikeys', MetaData(), Column('id', INTEGER(), table=_apikeys_, primary_key=True, nullable=False), Column('name', VARCHAR(length=50), table=_apikeys_, nullable=False), Column('key', VARCHAR(length=255), table=_apikeys_, nullable=False), Column('user_id', INTEGER(), ForeignKey('users.id'), table=_apikeys_), schema=))]_,)

Revision ID: 09e4916df893
Revises: 
Create Date: 2023-12-22 22:36:25.116645

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09e4916df893'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('irails_roles')
    op.drop_table('irails_casbin_rule')
    op.drop_table('irails_users')
    op.drop_table('irails_user_role')
    op.drop_table('irails_products')
    op.drop_table('irails_apikeys')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('irails_apikeys',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), nullable=False),
    sa.Column('key', sa.VARCHAR(length=255), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['irails_users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_table('irails_products',
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('irails_user_role',
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('role_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['irails_roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['irails_users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    op.create_table('irails_users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=50), nullable=False),
    sa.Column('fullname', sa.VARCHAR(length=50), nullable=False),
    sa.Column('domain', sa.VARCHAR(length=50), nullable=True),
    sa.Column('password', sa.VARCHAR(length=50), nullable=False),
    sa.Column('age', sa.INTEGER(), nullable=False),
    sa.Column('salt', sa.VARCHAR(length=50), nullable=True),
    sa.Column('remark', sa.VARCHAR(length=255), nullable=True),
    sa.Column('update_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('create_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('is_deleted', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('irails_casbin_rule',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('ptype', sa.VARCHAR(length=255), nullable=True),
    sa.Column('v0', sa.VARCHAR(length=255), nullable=True),
    sa.Column('v1', sa.VARCHAR(length=255), nullable=True),
    sa.Column('v2', sa.VARCHAR(length=255), nullable=True),
    sa.Column('v3', sa.VARCHAR(length=255), nullable=True),
    sa.Column('v4', sa.VARCHAR(length=255), nullable=True),
    sa.Column('v5', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('irails_roles',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), nullable=False),
    sa.Column('update_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('create_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('is_deleted', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###
