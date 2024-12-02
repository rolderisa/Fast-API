from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context,op
import sqlalchemy as sa
from sqlalchemy.engine import reflection


# Import Base from your models
from app.models import Base

# This is the Alembic Config object, which provides access
# to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Set the target metadata
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


def upgrade():
    # Connect to the database
    conn = op.get_bind()
    inspector = reflection.Inspector.from_engine(conn)
    
    # Check if 'stock_quantity' column exists
    columns = [col['name'] for col in inspector.get_columns('products')]
    if 'stock_quantity' not in columns:
        op.add_column('products', sa.Column('stock_quantity', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('products', 'stock_quantity')