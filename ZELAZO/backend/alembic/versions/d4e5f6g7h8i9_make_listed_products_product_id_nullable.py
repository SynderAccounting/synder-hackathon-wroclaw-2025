"""Make listed_products product_id nullable for unmatched listings

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2025-11-09 09:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make product_id nullable to allow unmatched external listings"""
    # Make product_id column nullable
    op.alter_column('listed_products', 'product_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=True)


def downgrade() -> None:
    """Revert product_id to non-nullable (will fail if NULL values exist)"""
    # Note: This will fail if there are any NULL product_id values in the table
    op.alter_column('listed_products', 'product_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=False)
