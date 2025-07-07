
import sqlite3
import threading
from contextlib import contextmanager

DATABASE_FILE = "nexuskit_tasks.db"

# Use thread-local data to manage database connections, ensuring thread safety.
local = threading.local()

def get_db_connection():
    """
    Establishes and retrieves the database connection for the current thread.
    If a connection does not exist, it creates one.
    """
    if not hasattr(local, "connection"):
        # Using check_same_thread=False is suitable for FastAPI's multi-threaded nature.
        # The connection is managed per-thread via the `local` object.
        local.connection = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
        local.connection.row_factory = sqlite3.Row  # Allows accessing columns by name
    return local.connection

@contextmanager
def get_db():
    """
    A context manager to safely handle database connections.
    """
    conn = get_db_connection()
    try:
        yield conn
    finally:
        # The connection is managed by the thread-local storage, so we don't close it here.
        # It will persist for the lifetime of the thread.
        pass

def init_db():
    """
    Initializes the database by creating the 'tasks' table if it doesn't already exist.
    This function should be called once at application startup.
    """
    print("Initializing database...")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                tool_name TEXT NOT NULL,
                status TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                result_path TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    print("Database initialized successfully.")

def close_db_connection(exception=None):
    """
    Closes the database connection for the current thread, if it exists.
    This can be tied to the application's shutdown event.
    """
    if hasattr(local, "connection"):
        local.connection.close()
        del local.connection
