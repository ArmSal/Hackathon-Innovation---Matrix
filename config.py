import os

class Config:
    # Using SQLite as fallback database (no PostgreSQL server required)
    # To use PostgreSQL, change this to:
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:YourPassword@localhost:5432/devops_db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///devops.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hackathon-secret-key-matrix-2026')
    SQLALCHEMY_ECHO = False
