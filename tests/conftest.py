import pytest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Mock problematic imports before importing the app
sys.modules['undetected_chromedriver'] = MagicMock()
sys.modules['selenium'] = MagicMock()

# Mock requests module with exceptions
requests_mock = MagicMock()
requests_mock.exceptions = MagicMock()
requests_mock.exceptions.RequestException = Exception
sys.modules['requests'] = requests_mock
sys.modules['requests.exceptions'] = requests_mock.exceptions

from app import create_app, db
from app.models import User, People, Log, LogDetail, IP, GovPeople
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to serve as the database
    db_fd, db_path = tempfile.mkstemp()
    
    # Create app with testing configuration
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the Flask application's CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Create a test user and return authentication headers."""
    # Create test user with default username 'admin'
    user = User(
        username='admin',
        email='test@example.com'
    )
    user.set_password('testpassword')
    
    db.session.add(user)
    db.session.commit()
    
    # Login and get session (username is default 'admin', only need password)
    response = client.post('/', data={
        'password': 'testpassword'
    }, follow_redirects=True)
    
    return {'Cookie': response.headers.get('Set-Cookie', '')}


@pytest.fixture
def authenticated_client(client):
    """Create an authenticated test client."""
    # Create test user with default username 'admin'
    user = User(
        username='admin',
        email='test@example.com'
    )
    user.set_password('testpassword')
    
    db.session.add(user)
    db.session.commit()
    
    # Login
    client.post('/', data={
        'password': 'testpassword'
    }, follow_redirects=True)
    
    return client


@pytest.fixture
def sample_people_data():
    """Sample people data for testing."""
    return [
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'organization': 'Test Corp',
            'role': 'Manager',
            'email': 'john.doe@test.com',
            'city': 'Sydney',
            'state': 'NSW',
            'country': 'Australia'
        },
        {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'organization': 'Test Inc',
            'role': 'Developer',
            'email': 'jane.smith@test.com',
            'city': 'Melbourne',
            'state': 'VIC',
            'country': 'Australia'
        }
    ]


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing file uploads."""
    return """FirstName,LastName,Organization,Role,EmailAddress,City (if outside AUS),State AUS only,Country
John,Doe,Test Corp,Manager,john.doe@test.com,Sydney,NSW,Australia
Jane,Smith,Test Inc,Developer,jane.smith@test.com,Melbourne,VIC,Australia"""


@pytest.fixture
def sample_log_data():
    """Sample log data for testing."""
    return {
        'status': 'completed',
        'result': 'Successfully updated 2 records'
    }
