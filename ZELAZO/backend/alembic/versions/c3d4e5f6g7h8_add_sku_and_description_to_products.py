"""Add SKU and description to products table

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2025-11-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add SKU and description columns to products table"""
    # Add sku column
    op.add_column('products',
        sa.Column('sku', sa.String(length=100), nullable=True,
                  comment='Stock Keeping Unit - unique identifier for matching across platforms'))

    # Add description column
    op.add_column('products',
        sa.Column('description', sa.String(length=2000), nullable=True,
                  comment='Product description for AI matching'))

    # Create unique index on sku
    op.create_index('ix_products_sku', 'products', ['sku'], unique=True)


def downgrade() -> None:
    """Remove SKU and description columns from products table"""
    # Drop index
    op.drop_index('ix_products_sku', table_name='products')

    # Drop columns
    op.drop_column('products', 'description')
    op.drop_column('products', 'sku')
