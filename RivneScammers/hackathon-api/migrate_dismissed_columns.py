"""Database migration to add dismissed columns to recommendations table."""
from sqlalchemy import inspect, text
from db.database import engine

def migrate():
    """Add dismissed_at and dismissed_reason columns if they don't exist."""
    print("Starting database migration...")

    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('recommendations')]
    print(f"Current columns: {columns}")

    with engine.connect() as conn:
        if 'dismissed_at' not in columns:
            print("Adding dismissed_at column...")
            conn.execute(text("ALTER TABLE recommendations ADD COLUMN dismissed_at DATETIME"))
            conn.commit()
            print("✓ Added dismissed_at")
        else:
            print("✓ dismissed_at already exists")

        if 'dismissed_reason' not in columns:
            print("Adding dismissed_reason column...")
            conn.execute(text("ALTER TABLE recommendations ADD COLUMN dismissed_reason TEXT"))
            conn.commit()
            print("✓ Added dismissed_reason")
        else:
            print("✓ dismissed_reason already exists")

    print("✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()

