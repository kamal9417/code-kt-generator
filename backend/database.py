import sqlite3
from contextlib import contextmanager
from pathlib import Path

# Database file location
DB_PATH = Path("./data/kt_generator.db")

def init_database():
    """Initialize database with required tables"""
    
    # Create data directory if it doesn't exist
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            role TEXT NOT NULL,
            files_analyzed INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Files table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            complexity INTEGER,
            classes TEXT,  -- JSON string
            functions TEXT,  -- JSON string
            imports TEXT,  -- JSON string
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    
    # Documentation table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    
    # KT Plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kt_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            plan TEXT NOT NULL,  -- JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    
    # User Progress table (for tracking KT completion)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            day INTEGER NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at {DB_PATH}")

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()