"""Add listed_products table

Revision ID: a1b2c3d4e5f6
Revises: ff1e4baaaf00
Create Date: 2025-11-08 21:59:07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ff1e4baaaf00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create listed_products table
    op.create_table('listed_products',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to the product being listed'),
        sa.Column('marketplace', sa.String(length=100), nullable=False, comment='Marketplace where product is listed (e.g., amazon, allegro, temu)'),
        sa.Column('amount', sa.Integer(), nullable=False, comment='Quantity of items listed'),
        sa.Column('date_of_listing', sa.DateTime(timezone=True), nullable=False, comment='Date and time when product was listed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_listed_products_product_id'), 'listed_products', ['product_id'], unique=False)
    op.create_index(op.f('ix_listed_products_marketplace'), 'listed_products', ['marketplace'], unique=False)
    op.create_index(op.f('ix_listed_products_date_of_listing'), 'listed_products', ['date_of_listing'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_listed_products_date_of_listing'), table_name='listed_products')
    op.drop_index(op.f('ix_listed_products_marketplace'), table_name='listed_products')
    op.drop_index(op.f('ix_listed_products_product_id'), table_name='listed_products')

    # Drop table
    op.drop_table('listed_products')
