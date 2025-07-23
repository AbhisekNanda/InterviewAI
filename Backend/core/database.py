# file: database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database URL for SQLite.
# The 'check_same_thread' is only needed for SQLite.
DATABASE_URL = "sqlite:///./interview_ai.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session factory. This will be used to create new sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models to inherit from.
Base = declarative_base()

# Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()