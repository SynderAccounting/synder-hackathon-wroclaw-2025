"""Add price column to listed_products

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2025-11-09 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e5f6g7h8i9j0'
down_revision: Union[str, None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add price column to listed_products table"""
    # Add column as nullable first
    op.add_column('listed_products',
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True,
                  comment='Selling price on this marketplace')
    )

    # Set a default value for existing rows (0.00)
    op.execute("UPDATE listed_products SET price = 0.00 WHERE price IS NULL")

    # Now make it non-nullable
    op.alter_column('listed_products', 'price',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    nullable=False)


def downgrade() -> None:
    """Remove price column from listed_products table"""
    op.drop_column('listed_products', 'price')
