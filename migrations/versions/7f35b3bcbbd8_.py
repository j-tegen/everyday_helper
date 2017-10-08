"""empty message

Revision ID: 7f35b3bcbbd8
Revises: f73d901e6a88
Create Date: 2017-10-03 08:18:05.330252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f35b3bcbbd8'
down_revision = 'f73d901e6a88'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('firstname', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('lastname', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('verified', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'verified')
    op.drop_column('user', 'lastname')
    op.drop_column('user', 'firstname')
    # ### end Alembic commands ###
