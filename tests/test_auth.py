"""
Authentication and user management tests.
Tests login, logout, user creation, and authentication flows.
"""

import pytest
from flask import url_for
from app.models import User


class TestAuthentication:
    """Test authentication functionality."""

    def test_login_page_loads(self, client):
        """Test that the login page loads correctly."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'password' in response.data
        assert b'Please enter your password' in response.data

    def test_login_with_valid_credentials(self, client):
        """Test login with valid username and password."""
        # Create test user with default username 'admin'
        user = User(username='admin', email='test@example.com')
        user.set_password('testpassword')
        
        from app import db
        db.session.add(user)
        db.session.commit()
        
        # Test login (username is default 'admin', only need to provide password)
        response = client.post('/', data={
            'password': 'testpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to workspace after successful login
        assert b'workspace' in response.data or response.request.path == '/workspace'

    def test_login_with_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        # Create test user with default username 'admin'
        user = User(username='admin', email='test@example.com')
        user.set_password('testpassword')
        
        from app import db
        db.session.add(user)
        db.session.commit()
        
        # Test login with wrong password
        response = client.post('/', data={
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_login_with_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post('/', data={
            'password': 'password'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_logout_requires_login(self, client):
        """Test that logout requires user to be logged in."""
        response = client.get('/logout')
        # Should redirect to login page
        assert response.status_code == 302

    def test_logout_after_login(self, client):
        """Test logout after successful login."""
        # Create and login user
        user = User(username='admin', email='test@example.com')
        user.set_password('testpassword')
        
        from app import db
        db.session.add(user)
        db.session.commit()
        
        # Login
        client.post('/', data={
            'password': 'testpassword'
        })
        
        # Logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page
        assert b'password' in response.data

    def test_protected_route_redirects_to_login(self, client):
        """Test that protected routes redirect to login when not authenticated."""
        response = client.get('/workspace')
        assert response.status_code == 302
        # Should redirect to login page
        assert '/index' in response.location

    def test_user_password_hashing(self):
        """Test that user passwords are properly hashed."""
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword')
        
        # Password should be hashed, not stored in plain text
        assert user.password_hash != 'testpassword'
        assert user.password_hash is not None
        
        # Should be able to verify correct password
        assert user.check_password('testpassword')
        assert not user.check_password('wrongpassword')

    def test_user_model_creation(self):
        """Test User model creation and attributes."""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.password_hash is not None
        assert user.id is None  # Not saved yet

    def test_user_repr(self):
        """Test User model string representation."""
        user = User(username='testuser', email='test@example.com')
        assert str(user) == '<User testuser>'

    def test_login_form_validation(self, client):
        """Test login form validation."""
        # Test empty form submission
        response = client.post('/', data={}, follow_redirects=True)
        assert response.status_code == 200
        
        # Test with only password (username is default 'admin')
        response = client.post('/', data={'password': 'password'}, follow_redirects=True)
        assert response.status_code == 200
