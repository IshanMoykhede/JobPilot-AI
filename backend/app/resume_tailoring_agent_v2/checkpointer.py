import logging
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from app.core.config import settings

logger = logging.getLogger(__name__)

# The checkpoint postgres library expects standard PostgreSQL connection strings
# SQLAlchemy might have 'postgresql+psycopg2://', so we clean it.
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql+psycopg2://"):
    db_url = db_url.replace("postgresql+psycopg2://", "postgresql://")
    
# Initialize a global connection pool for the checkpointer
# This should ideally be closed during app shutdown, but for simplicity we keep it global.
connection_pool = ConnectionPool(
    conninfo=db_url,
    max_size=10,
    kwargs={"autocommit": True, "prepare_threshold": 0}
)

def get_checkpointer() -> PostgresSaver:
    """
    Returns a configured PostgresSaver instance using the connection pool.
    The `setup()` method automatically creates the `checkpoints`, 
    `checkpoint_blobs`, and `checkpoint_writes` tables if they do not exist.
    """
    checkpointer = PostgresSaver(connection_pool)
    try:
        checkpointer.setup()  # Ensures tables exist
    except Exception as e:
        logger.warning(f"Checkpointer setup warning (tables may already exist): {e}")
    return checkpointer
