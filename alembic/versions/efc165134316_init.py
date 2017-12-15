"""Init.

Revision ID: efc165134316
Revises: 
Create Date: 2017-12-16 00:42:52.171186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efc165134316'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('maps',
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('modes',
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('map_modes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('map', sa.String(), nullable=True),
    sa.Column('mode', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['map'], ['maps.name'], ),
    sa.ForeignKeyConstraint(['mode'], ['modes.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('servers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ip', sa.String(), nullable=True),
    sa.Column('info_port', sa.Integer(), nullable=True),
    sa.Column('port', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('map', sa.String(), nullable=True),
    sa.Column('mode', sa.String(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('country_name', sa.String(), nullable=True),
    sa.Column('version', sa.String(), nullable=True),
    sa.Column('hradba', sa.String(), nullable=True),
    sa.Column('num_players', sa.Integer(), nullable=True),
    sa.Column('max_players', sa.Integer(), nullable=True),
    sa.Column('password', sa.Boolean(), nullable=True),
    sa.Column('dedicated', sa.Boolean(), nullable=True),
    sa.Column('vietnam', sa.Boolean(), nullable=True),
    sa.Column('online', sa.Boolean(), nullable=True),
    sa.Column('online_since', sa.DateTime(), nullable=True),
    sa.Column('offline_since', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['map'], ['maps.name'], ),
    sa.ForeignKeyConstraint(['mode'], ['modes.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('players',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('ping', sa.Integer(), nullable=True),
    sa.Column('frags', sa.Integer(), nullable=True),
    sa.Column('server_id', sa.Integer(), nullable=True),
    sa.Column('online', sa.Boolean(), nullable=True),
    sa.Column('online_since', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('players')
    op.drop_table('servers')
    op.drop_table('map_modes')
    op.drop_table('modes')
    op.drop_table('maps')
    # ### end Alembic commands ###
