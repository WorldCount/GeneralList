"""Init Tables

Revision ID: a5e52a296789
Revises: 
Create Date: 2018-03-20 15:55:45.218410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5e52a296789'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('completion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('index', sa.String(length=6), nullable=False),
    sa.Column('reception', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_completion_index'), 'completion', ['index'], unique=False)
    op.create_index(op.f('ix_completion_reception'), 'completion', ['reception'], unique=False)
    op.create_table('config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_config_name'), 'config', ['name'], unique=False)
    op.create_index(op.f('ix_config_value'), 'config', ['value'], unique=False)
    op.create_table('index',
    sa.Column('index', sa.String(length=6), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('head', sa.String(), nullable=True),
    sa.Column('region', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_index(op.f('ix_index_index'), 'index', ['index'], unique=False)
    op.create_index(op.f('ix_index_name'), 'index', ['name'], unique=False)
    op.create_table('list_rpo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('num', sa.Integer(), nullable=True),
    sa.Column('mail_type', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('mass_rate', sa.Float(), nullable=True),
    sa.Column('mass', sa.Integer(), nullable=True),
    sa.Column('rpo_count', sa.Integer(), nullable=True),
    sa.Column('error_count', sa.Integer(), nullable=True),
    sa.Column('double_count', sa.Integer(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('load_date', sa.DateTime(), nullable=False),
    sa.Column('change_date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_list_rpo_date'), 'list_rpo', ['date'], unique=False)
    op.create_index(op.f('ix_list_rpo_num'), 'list_rpo', ['num'], unique=False)
    op.create_table('rpo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('barcode', sa.String(length=14), nullable=True),
    sa.Column('index', sa.String(length=6), nullable=True),
    sa.Column('address', sa.String(length=140), nullable=True),
    sa.Column('reception', sa.String(length=140), nullable=True),
    sa.Column('mass', sa.Integer(), nullable=True),
    sa.Column('mass_rate', sa.Float(), nullable=True),
    sa.Column('num_string', sa.Integer(), nullable=True),
    sa.Column('error_count', sa.Integer(), nullable=True),
    sa.Column('double', sa.Boolean(), nullable=False),
    sa.Column('list_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['list_id'], ['list_rpo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rpo_barcode'), 'rpo', ['barcode'], unique=False)
    op.create_index(op.f('ix_rpo_error_count'), 'rpo', ['error_count'], unique=False)
    op.create_table('error',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Integer(), nullable=False),
    sa.Column('msg', sa.String(length=100), nullable=True),
    sa.Column('comment', sa.String(length=140), nullable=True),
    sa.Column('rpo_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rpo_id'], ['rpo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_error_type'), 'error', ['type'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_error_type'), table_name='error')
    op.drop_table('error')
    op.drop_index(op.f('ix_rpo_error_count'), table_name='rpo')
    op.drop_index(op.f('ix_rpo_barcode'), table_name='rpo')
    op.drop_table('rpo')
    op.drop_index(op.f('ix_list_rpo_num'), table_name='list_rpo')
    op.drop_index(op.f('ix_list_rpo_date'), table_name='list_rpo')
    op.drop_table('list_rpo')
    op.drop_index(op.f('ix_index_name'), table_name='index')
    op.drop_index(op.f('ix_index_index'), table_name='index')
    op.drop_table('index')
    op.drop_index(op.f('ix_config_value'), table_name='config')
    op.drop_index(op.f('ix_config_name'), table_name='config')
    op.drop_table('config')
    op.drop_index(op.f('ix_completion_reception'), table_name='completion')
    op.drop_index(op.f('ix_completion_index'), table_name='completion')
    op.drop_table('completion')
    # ### end Alembic commands ###
