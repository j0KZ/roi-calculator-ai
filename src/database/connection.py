"""
Database connection and session management
Supports both SQLite (for development) and PostgreSQL (for production)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from .models import Base

class DatabaseConnection:
    """Manage database connections"""
    
    def __init__(self, db_url=None):
        """
        Initialize database connection
        
        Args:
            db_url: Database URL. If None, will try to use environment variable
                   or default to SQLite
        """
        if db_url:
            self.db_url = db_url
        else:
            # Try environment variable first
            self.db_url = os.environ.get('DATABASE_URL')
            
            if not self.db_url:
                # Default to SQLite for development
                db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'roi_calculator.db')
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                self.db_url = f'sqlite:///{db_path}'
                print(f"Using SQLite database: {db_path}")
        
        # Create engine with appropriate settings
        if 'sqlite' in self.db_url:
            # SQLite specific settings
            self.engine = create_engine(
                self.db_url,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                echo=False  # Set to True for SQL debugging
            )
        else:
            # PostgreSQL settings
            self.engine = create_engine(
                self.db_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False  # Set to True for SQL debugging
            )
        
        # Create session factory
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def close_session(self, session):
        """Close a database session"""
        session.close()
    
    def init_db(self):
        """Initialize database with tables"""
        Base.metadata.create_all(bind=self.engine)
        print("Database tables created successfully")
    
    def drop_all(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
        print("All database tables dropped")
    
    def test_connection(self):
        """Test database connection"""
        try:
            from sqlalchemy import text
            with self.engine.connect() as conn:
                result = conn.execute(text('SELECT 1'))
                return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False


# Global database connection instance
db = None

def get_db():
    """Get the global database connection"""
    global db
    if db is None:
        db = DatabaseConnection()
    return db

def get_session():
    """Get a database session"""
    return get_db().get_session()

def init_database(db_url=None):
    """Initialize the database with a specific URL"""
    global db
    db = DatabaseConnection(db_url)
    return db