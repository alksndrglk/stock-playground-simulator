"""Unique symbol in Stocks

Revision ID: 88e7affa8ea3
Revises: 4c4228efd7d5
Create Date: 2022-03-15 14:05:59.540921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88e7affa8ea3'
down_revision = '4c4228efd7d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_stock_symbol', table_name='stock')
    op.create_index(op.f('ix_stock_symbol'), 'stock', ['symbol'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_stock_symbol'), table_name='stock')
    op.create_index('ix_stock_symbol', 'stock', ['symbol'], unique=False)
    # ### end Alembic commands ###
