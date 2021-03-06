"""Unique Events Message

Revision ID: 4077bc6ff889
Revises: 88e7affa8ea3
Create Date: 2022-03-15 15:35:34.053541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4077bc6ff889'
down_revision = '88e7affa8ea3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'market_events', ['message'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'market_events', type_='unique')
    # ### end Alembic commands ###
