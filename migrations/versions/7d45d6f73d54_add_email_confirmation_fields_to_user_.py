"""Add email confirmation fields to User model

Revision ID: 7d45d6f73d54
Revises: 795fa9e974e9
Create Date: 2024-09-12 13:41:35.617591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d45d6f73d54'
down_revision = '795fa9e974e9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_confirmed', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('confirmed_on', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('confirmed_on')
        batch_op.drop_column('is_confirmed')

    # ### end Alembic commands ###
