"""first

Revision ID: 4b0e8dac8eb5
Revises: e5d48bd63d54
Create Date: 2022-03-04 11:02:18.436800

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4b0e8dac8eb5'
down_revision = 'e5d48bd63d54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.Unicode(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'email'),
    sa.UniqueConstraint('email')
    )
    op.create_table('game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default='now()', nullable=True),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.Column('round_info', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
    sa.Column('state', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('market_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message', sa.String(), nullable=False),
    sa.Column('diff', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('player',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('user_name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default='now()', nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('stock',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('symbol', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('cost', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_id'), 'stock', ['id'], unique=False)
    op.create_index(op.f('ix_stock_symbol'), 'stock', ['symbol'], unique=True)
    op.create_table('brokerage_accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('points', sa.Integer(), nullable=True),
    sa.Column('portfolio', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['player.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('games_x_users',
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['player.id'], )
    )
    op.create_table('stock_in_game',
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('symbol', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('cost', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_in_game_id'), 'stock_in_game', ['id'], unique=False)
    op.create_index(op.f('ix_stock_in_game_symbol'), 'stock_in_game', ['symbol'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_stock_in_game_symbol'), table_name='stock_in_game')
    op.drop_index(op.f('ix_stock_in_game_id'), table_name='stock_in_game')
    op.drop_table('stock_in_game')
    op.drop_table('games_x_users')
    op.drop_table('brokerage_accounts')
    op.drop_index(op.f('ix_stock_symbol'), table_name='stock')
    op.drop_index(op.f('ix_stock_id'), table_name='stock')
    op.drop_table('stock')
    op.drop_table('player')
    op.drop_table('market_events')
    op.drop_table('game')
    op.drop_table('admins')
    # ### end Alembic commands ###
