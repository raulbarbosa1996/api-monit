"""empty message

Revision ID: 61453abe2c1f
Revises: 3145daa25fef
Create Date: 2021-02-24 14:16:52.101962

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61453abe2c1f'
down_revision = '3145daa25fef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('raul', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'raul')
    # ### end Alembic commands ###