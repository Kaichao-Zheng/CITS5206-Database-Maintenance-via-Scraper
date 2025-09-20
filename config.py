# config.py
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Base configuration class
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_secret"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLite specific configurations
    SQLITE_DATABASE_DIR = os.environ.get('SQLITE_DATABASE_DIR') or basedir
    SQLITE_DATABASE_NAME = os.environ.get('SQLITE_DATABASE_NAME') or 'app.db'
    
    # SQLite performance optimizations for development
    SQLITE_PRAGMA_SETTINGS = {
        'journal_mode': 'WAL',  # Write-Ahead Logging for better concurrency
        'synchronous': 'NORMAL',  # Balance between safety and performance
        'cache_size': -16000,  # 16MB cache (suitable for development)
        'temp_store': 'MEMORY',  # Store temp tables in memory
        'mmap_size': 67108864,  # 64MB memory-mapped I/O (development)
        'foreign_keys': 'ON',  # Enable foreign key constraints
        'busy_timeout': 10000,  # 10 seconds timeout for locked database
    }

class DevelopmentConfig(Config):
    DEBUG = True
    # Development database in project directory
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    # Development-specific SQLite optimizations
    SQLITE_PRAGMA_SETTINGS = {
        'journal_mode': 'WAL',
        'synchronous': 'NORMAL',
        'cache_size': -16000,  # 16MB cache for development
        'temp_store': 'MEMORY',
        'mmap_size': 67108864,  # 64MB memory-mapped I/O
        'foreign_keys': 'ON',
        'busy_timeout': 10000,  # 10 seconds timeout
        'auto_vacuum': 'INCREMENTAL',  # Enable incremental vacuum
    }

class TestingConfig(Config):
    TESTING = True
    # Test database in memory for faster tests
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///:memory:'
    
    # Testing-specific SQLite optimizations
    SQLITE_PRAGMA_SETTINGS = {
        'journal_mode': 'MEMORY',  # Use memory journal for tests
        'synchronous': 'OFF',  # Disable sync for speed
        'cache_size': -8000,  # 8MB cache for tests
        'temp_store': 'MEMORY',
        'foreign_keys': 'ON',
        'busy_timeout': 5000,  # 5 seconds timeout
    }
