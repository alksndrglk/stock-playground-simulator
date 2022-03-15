"""from linux to mac

Revision ID: 4c4228efd7d5
Revises: 
Create Date: 2022-03-13 09:08:17.948308

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4c4228efd7d5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_stock_in_game_symbol'), table_name='stock_in_game')
    op.drop_table('stock_in_game')
    op.drop_table('games_x_users')
    op.drop_table('brokerage_accounts')
    op.drop_index(op.f('ix_stock_symbol'), table_name='stock')
    op.drop_table('stock')
    op.drop_table('player')
    op.drop_table('market_events')
    op.drop_table('game')
    op.drop_table('admins')
    # ### end Alembic commands ###
