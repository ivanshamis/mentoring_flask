"""making changes

Revision ID: 949c346381b7
Revises: 43d779fc3ca1
Create Date: 2022-07-21 17:43:09.829863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '949c346381b7'
down_revision = '43d779fc3ca1'
branch_labels = ()
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('docs', sa.Column('thumbnail', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('docs', 'thumbnail')
    # ### end Alembic commands ###
