"""Cascade

Revision ID: e47d95cdb50a
Revises: 23d6b1e6663b
Create Date: 2022-03-07 11:55:07.957118

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e47d95cdb50a'
down_revision = '23d6b1e6663b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('brokerage_accounts_game_id_fkey', 'brokerage_accounts', type_='foreignkey')
    op.drop_constraint('brokerage_accounts_user_id_fkey', 'brokerage_accounts', type_='foreignkey')
    op.create_foreign_key(None, 'brokerage_accounts', 'game', ['game_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'brokerage_accounts', 'player', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('games_x_users_game_id_fkey', 'games_x_users', type_='foreignkey')
    op.drop_constraint('games_x_users_user_id_fkey', 'games_x_users', type_='foreignkey')
    op.create_foreign_key(None, 'games_x_users', 'game', ['game_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'games_x_users', 'player', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('stock_in_game_game_id_fkey', 'stock_in_game', type_='foreignkey')
    op.create_foreign_key(None, 'stock_in_game', 'game', ['game_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'stock_in_game', type_='foreignkey')
    op.create_foreign_key('stock_in_game_game_id_fkey', 'stock_in_game', 'game', ['game_id'], ['id'])
    op.drop_constraint(None, 'games_x_users', type_='foreignkey')
    op.drop_constraint(None, 'games_x_users', type_='foreignkey')
    op.create_foreign_key('games_x_users_user_id_fkey', 'games_x_users', 'player', ['user_id'], ['id'])
    op.create_foreign_key('games_x_users_game_id_fkey', 'games_x_users', 'game', ['game_id'], ['id'])
    op.drop_constraint(None, 'brokerage_accounts', type_='foreignkey')
    op.drop_constraint(None, 'brokerage_accounts', type_='foreignkey')
    op.create_foreign_key('brokerage_accounts_user_id_fkey', 'brokerage_accounts', 'player', ['user_id'], ['id'])
    op.create_foreign_key('brokerage_accounts_game_id_fkey', 'brokerage_accounts', 'game', ['game_id'], ['id'])
    # ### end Alembic commands ###