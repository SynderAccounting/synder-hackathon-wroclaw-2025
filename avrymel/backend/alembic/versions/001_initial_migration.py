"""Initial migration - create users table

Revision ID: 001
Revises:
Create Date: 2025-11-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid  # noqa: F401

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'USER', 'VIEWER', name='userrole'), nullable=False, server_default='VIEWER'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )

    # Create indexes
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Insert default admin user
    # Password: admin123
    op.execute("""
        INSERT INTO users (id, username, email, hashed_password, full_name, role, is_active, created_at, updated_at)
        VALUES (
            gen_random_uuid(),
            'admin',
            'admin@synderhacks.com',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVGKZvW8u',
            'System Administrator',
            'ADMIN',
            true,
            NOW(),
            NOW()
        )
    """)


def downgrade() -> None:
    op.drop_index('ix_users_email', 'users')
    op.drop_index('ix_users_username', 'users')
    op.drop_index('ix_users_id', 'users')
    op.drop_table('users')
    op.execute('DROP TYPE userrole')
