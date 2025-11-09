"""Update products table - remove platform-specific fields

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-08 22:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop platform-specific columns
    op.drop_index('ix_products_country_of_selling', table_name='products')
    op.drop_index('ix_products_date_of_selling', table_name='products')
    op.drop_index('ix_products_platform', table_name='products')

    op.drop_column('products', 'country_of_selling')
    op.drop_column('products', 'date_of_selling')
    op.drop_column('products', 'platform')
    op.drop_column('products', 'selling_price')

    # Rename orig_price to price
    op.alter_column('products', 'orig_price',
                    new_column_name='price',
                    comment='Base product price')


def downgrade() -> None:
    # Rename price back to orig_price
    op.alter_column('products', 'price',
                    new_column_name='orig_price',
                    comment='Original price')

    # Add back platform-specific columns
    op.add_column('products',
        sa.Column('selling_price', sa.Numeric(precision=10, scale=2), nullable=False,
                  comment='Actual selling price', server_default='0.00'))
    op.add_column('products',
        sa.Column('platform', sa.String(length=100), nullable=False,
                  comment='Platform where product was sold', server_default='unknown'))
    op.add_column('products',
        sa.Column('date_of_selling', sa.DateTime(timezone=True), nullable=False,
                  comment='Date and time of sale', server_default=sa.text('now()')))
    op.add_column('products',
        sa.Column('country_of_selling', sa.String(length=100), nullable=False,
                  comment='Country where sale occurred', server_default='unknown'))

    # Recreate indexes
    op.create_index('ix_products_platform', 'products', ['platform'])
    op.create_index('ix_products_date_of_selling', 'products', ['date_of_selling'])
    op.create_index('ix_products_country_of_selling', 'products', ['country_of_selling'])
