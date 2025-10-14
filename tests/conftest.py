import pytest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Mock ALL selenium-related modules before any imports
selenium_modules = [
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.common',
    'selenium.webdriver.common.by',
    'selenium.webdriver.common.exceptions',
    'selenium.webdriver.support',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.wait',
    'selenium.webdriver.support.expected_conditions',
    'selenium.webdriver.chrome',
    'selenium.webdriver.chrome.options',
    'selenium.webdriver.chrome.service',
    'selenium.common',
    'selenium.common.exceptions',
    'undetected_chromedriver',
    'linkedin_scraper',
    'linkedin_scraper.actions',
    'linkedin_scraper.person',
    'linkedin_scraper.objects',
]

for module_name in selenium_modules:
    sys.modules[module_name] = MagicMock()

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
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
    })

    # Create the database
    with app.app_context():
        db.create_all()

    yield app

    # Clean up
    with app.app_context():
        db.session.remove()
        db.drop_all()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
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
def sample_csv_data():
    """Sample CSV data for testing."""
    return """FirstName,LastName,Organization,Role,Email
John,Doe,Acme Corp,Manager,john.doe@acme.com
Jane,Smith,Tech Inc,Developer,jane.smith@tech.com
Bob,Johnson,Startup Co,CEO,bob.johnson@startup.com"""
