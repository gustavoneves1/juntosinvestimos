"""Add email confirmation fields to User model

Revision ID: 44c067c7f23f
Revises: 7d45d6f73d54
Create Date: 2024-09-12 14:03:20.032058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44c067c7f23f'
down_revision = '7d45d6f73d54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('ix_user_username')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index('ix_user_username', ['username'], unique=True)

    # ### end Alembic commands ###
