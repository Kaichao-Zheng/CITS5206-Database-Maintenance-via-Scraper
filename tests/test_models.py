"""
Database model tests.
Tests all database models including User, People, Log, LogDetail, IP, and GovPeople.
"""

import pytest
from datetime import datetime
from app.models import User, People, Log, LogDetail, IP, GovPeople
from app import db


class TestUserModel:
    """Test User model functionality."""

    def test_user_creation(self, app):
        """Test creating a new user."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com'
            )
            user.set_password('testpassword')
            
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            saved_user = User.query.filter_by(username='testuser').first()
            assert saved_user is not None
            assert saved_user.email == 'test@example.com'
            assert saved_user.check_password('testpassword')

    def test_user_password_hashing(self, app):
        """Test password hashing and verification."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            
            # Password should be hashed
            assert user.password_hash != 'testpassword'
            assert user.password_hash is not None
            
            # Should verify correct password
            assert user.check_password('testpassword')
            assert not user.check_password('wrongpassword')

    def test_user_repr(self):
        """Test User string representation."""
        user = User(username='testuser', email='test@example.com')
        assert str(user) == '<User testuser>'

    def test_user_unique_constraints(self, app):
        """Test that username and email are unique."""
        with app.app_context():
            # Create first user
            user1 = User(username='testuser', email='test@example.com')
            user1.set_password('password')
            db.session.add(user1)
            db.session.commit()
            
            # Try to create user with same username
            user2 = User(username='testuser', email='different@example.com')
            user2.set_password('password')
            db.session.add(user2)
            
            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()


class TestPeopleModel:
    """Test People model functionality."""

    def test_people_creation(self, app):
        """Test creating a new People record."""
        with app.app_context():
            person = People(
                first_name='John',
                last_name='Doe',
                organization='Test Corp',
                role='Manager',
                email='john.doe@test.com',
                city='Sydney',
                state='NSW',
                country='Australia'
            )
            
            db.session.add(person)
            db.session.commit()
            
            # Verify person was created
            saved_person = People.query.filter_by(first_name='John').first()
            assert saved_person is not None
            assert saved_person.last_name == 'Doe'
            assert saved_person.organization == 'Test Corp'

    def test_people_as_dict(self, app):
        """Test People as_dict method."""
        with app.app_context():
            person = People(
                first_name='John',
                last_name='Doe',
                organization='Test Corp',
                role='Manager',
                email='john.doe@test.com'
            )
            
            db.session.add(person)
            db.session.commit()
            
            person_dict = person.as_dict()
            assert person_dict['first_name'] == 'John'
            assert person_dict['last_name'] == 'Doe'
            assert person_dict['organization'] == 'Test Corp'
            assert 'id' not in person_dict  # Should exclude id field

    def test_people_repr(self):
        """Test People string representation."""
        person = People(first_name='John', last_name='Doe')
        assert str(person) == '<People John Doe>'

    def test_people_optional_fields(self, app):
        """Test that People fields are optional."""
        with app.app_context():
            person = People(first_name='John', last_name='Doe')
            
            db.session.add(person)
            db.session.commit()
            
            # Should be able to create person with minimal fields
            saved_person = People.query.filter_by(first_name='John').first()
            assert saved_person is not None
            assert saved_person.organization is None


class TestLogModel:
    """Test Log model functionality."""

    def test_log_creation(self, app):
        """Test creating a new Log record."""
        with app.app_context():
            log = Log(
                status='completed',
                result='Successfully updated 10 records'
            )
            
            db.session.add(log)
            db.session.commit()
            
            # Verify log was created
            saved_log = Log.query.first()
            assert saved_log is not None
            assert saved_log.status == 'completed'
            assert saved_log.result == 'Successfully updated 10 records'
            assert isinstance(saved_log.created_at, datetime)

    def test_log_repr(self):
        """Test Log string representation."""
        log = Log(status='completed')
        assert str(log) == f'<Log {log.id}>'

    def test_log_default_values(self, app):
        """Test Log default values."""
        with app.app_context():
            log = Log()
            
            db.session.add(log)
            db.session.commit()
            
            # Should have default created_at timestamp
            assert log.created_at is not None
            assert isinstance(log.created_at, datetime)


class TestLogDetailModel:
    """Test LogDetail model functionality."""

    def test_log_detail_creation(self, app):
        """Test creating a new LogDetail record."""
        with app.app_context():
            # Create parent log first
            log = Log(status='in progress')
            db.session.add(log)
            db.session.commit()
            
            log_detail = LogDetail(
                log_id=log.id,
                record_name='John Doe',
                status='success',
                source='LinkedIn',
                detail='Successfully scraped profile information'
            )
            
            db.session.add(log_detail)
            db.session.commit()
            
            # Verify log detail was created
            saved_detail = LogDetail.query.first()
            assert saved_detail is not None
            assert saved_detail.record_name == 'John Doe'
            assert saved_detail.status == 'success'
            assert saved_detail.log_id == log.id

    def test_log_detail_repr(self):
        """Test LogDetail string representation."""
        log_detail = LogDetail(record_name='John Doe')
        assert str(log_detail) == f'<LogDetail {log_detail.id}>'

    def test_log_detail_foreign_key_relationship(self, app):
        """Test LogDetail foreign key relationship with Log."""
        with app.app_context():
            # Create parent log
            log = Log(status='in progress')
            db.session.add(log)
            db.session.commit()
            
            # Create log detail
            log_detail = LogDetail(
                log_id=log.id,
                record_name='John Doe',
                status='success'
            )
            db.session.add(log_detail)
            db.session.commit()
            
            # Test relationship
            assert log_detail.log_id == log.id
            assert log.id is not None


class TestIPModel:
    """Test IP model functionality."""

    def test_ip_creation(self, app):
        """Test creating a new IP record."""
        with app.app_context():
            ip_record = IP(
                address='192.168.1.1',
                port=8080,
                type='https',
                source='free-proxy-list',
                is_expired=False
            )
            
            db.session.add(ip_record)
            db.session.commit()
            
            # Verify IP record was created
            saved_ip = IP.query.first()
            assert saved_ip is not None
            assert saved_ip.address == '192.168.1.1'
            assert saved_ip.port == 8080
            assert saved_ip.type == 'https'
            assert saved_ip.is_expired is False

    def test_ip_default_values(self, app):
        """Test IP model default values."""
        with app.app_context():
            ip_record = IP(address='192.168.1.1')
            
            db.session.add(ip_record)
            db.session.commit()
            
            # Should have default is_expired value
            assert ip_record.is_expired is False


class TestGovPeopleModel:
    """Test GovPeople model functionality."""

    def test_gov_people_creation(self, app):
        """Test creating a new GovPeople record."""
        with app.app_context():
            gov_person = GovPeople(
                first_name='John',
                last_name='Doe',
                organization='Government Agency',
                role='Public Servant',
                email='john.doe@gov.au',
                city='Canberra',
                state='ACT',
                country='Australia'
            )
            
            db.session.add(gov_person)
            db.session.commit()
            
            # Verify gov person was created
            saved_gov_person = GovPeople.query.filter_by(first_name='John').first()
            assert saved_gov_person is not None
            assert saved_gov_person.organization == 'Government Agency'
            assert saved_gov_person.role == 'Public Servant'

    def test_gov_people_as_dict(self, app):
        """Test GovPeople as_dict method."""
        with app.app_context():
            gov_person = GovPeople(
                first_name='John',
                last_name='Doe',
                organization='Government Agency',
                role='Public Servant'
            )
            
            db.session.add(gov_person)
            db.session.commit()
            
            person_dict = gov_person.as_dict()
            assert person_dict['first_name'] == 'John'
            assert person_dict['last_name'] == 'Doe'
            assert person_dict['organization'] == 'Government Agency'
            assert 'id' not in person_dict  # Should exclude id field

    def test_gov_people_repr(self):
        """Test GovPeople string representation."""
        gov_person = GovPeople(first_name='John', last_name='Doe')
        assert str(gov_person) == '<GovPeople John Doe>'
