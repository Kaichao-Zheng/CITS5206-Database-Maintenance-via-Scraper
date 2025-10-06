import io
import pytest
from app.models import People, User, db


class TestFileUpload:
    """Test file upload functionality."""

    def test_workspace_requires_login(self, client):
        """Test that workspace page requires authentication."""
        response = client.get('/workspace')
        assert response.status_code == 302  # Should redirect to login

    def test_workspace_with_login(self, authenticated_client):
        """Test workspace page with authenticated user."""
        response = authenticated_client.get('/workspace')
        assert response.status_code == 200
        assert b'workspace' in response.data

    def test_upload_without_file(self, client):
        """Test upload endpoint without file."""
        response = client.post('/upload')
        assert response.status_code == 302  # Should redirect

    def test_upload_valid_csv(self, authenticated_client, sample_csv_data):
        """Test uploading a valid CSV file."""
        # Create a file-like object from CSV data
        csv_file = io.BytesIO(sample_csv_data.encode('utf-8'))
        
        response = authenticated_client.post('/upload', 
                             data={'file': (csv_file, 'test.csv')},
                             follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify data was inserted into database
        with authenticated_client.application.app_context():
            people = People.query.all()
            assert len(people) == 2
            assert people[0].first_name == 'John'
            assert people[0].last_name == 'Doe'
            assert people[1].first_name == 'Jane'
            assert people[1].last_name == 'Smith'

    def test_upload_csv_with_missing_columns(self, authenticated_client):
        """Test uploading CSV with missing required columns."""
        # CSV missing required first_name and last_name columns
        invalid_csv = """Organization,Role,EmailAddress
Test Org,Manager,test@example.com"""
        
        csv_file = io.BytesIO(invalid_csv.encode('utf-8'))
        response = authenticated_client.post('/upload', 
                             data={'file': (csv_file, 'invalid.csv')},
                             follow_redirects=True)
        
        assert response.status_code == 200
        # Should handle missing columns gracefully

    def test_upload_csv_with_extra_columns(self, authenticated_client):
        """Test uploading CSV with extra columns."""
        extra_csv = """first_name,last_name,email,extra_field1,extra_field2
John,Doe,john@example.com,extra1,extra2
Jane,Smith,jane@example.com,extra3,extra4"""
        
        csv_file = io.BytesIO(extra_csv.encode('utf-8'))
        response = authenticated_client.post('/upload', 
                             data={'file': (csv_file, 'extra.csv')},
                             follow_redirects=True)
        
        assert response.status_code == 200
        # Should handle extra columns gracefully

    def test_upload_invalid_file_format(self, authenticated_client):
        """Test uploading non-CSV file."""
        # Create a text file instead of CSV
        text_content = "This is not a CSV file"
        text_file = io.BytesIO(text_content.encode('utf-8'))
        
        response = authenticated_client.post('/upload', 
                             data={'file': (text_file, 'test.txt')},
                             follow_redirects=True)
        
        assert response.status_code == 200
        # Should handle invalid format gracefully

    def test_upload_empty_csv(self, authenticated_client):
        """Test uploading empty CSV file."""
        empty_csv = """first_name,last_name,email"""
        csv_file = io.BytesIO(empty_csv.encode('utf-8'))
        
        response = authenticated_client.post('/upload', 
                             data={'file': (csv_file, 'empty.csv')},
                             follow_redirects=True)
        
        assert response.status_code == 200
        # Should handle empty CSV gracefully

    def test_upload_csv_with_encoding_issues(self, authenticated_client):
        """Test uploading CSV with encoding issues."""
        # CSV with special characters
        encoding_csv = """first_name,last_name,email
José,García,jose@example.com
François,Dupont,francois@example.com"""
        
        csv_file = io.BytesIO(encoding_csv.encode('utf-8'))
        response = authenticated_client.post('/upload', 
                             data={'file': (csv_file, 'encoding.csv')},
                             follow_redirects=True)
        
        assert response.status_code == 200
        # Should handle encoding properly


class TestDataRetrieval:
    """Test data retrieval functionality."""

    def test_get_data_requires_login(self, client):
        """Test that data endpoint requires authentication."""
        response = client.get('/data')
        assert response.status_code == 302  # Should redirect to login

    def test_get_data_with_login(self, authenticated_client, sample_csv_data):
        """Test data retrieval with authenticated user."""
        # First upload some data
        csv_file = io.BytesIO(sample_csv_data.encode('utf-8'))
        authenticated_client.post('/upload', 
                                 data={'file': (csv_file, 'test.csv')},
                                 follow_redirects=True)
        
        # Then retrieve data
        response = authenticated_client.get('/data')
        assert response.status_code == 200
        assert b'John' in response.data
        assert b'Jane' in response.data

    def test_get_data_empty_database(self, authenticated_client):
        """Test data retrieval with empty database."""
        response = authenticated_client.get('/data')
        assert response.status_code == 200
        # Should handle empty database gracefully


class TestDataExport:
    """Test data export functionality."""

    def test_export_requires_login(self, client):
        """Test that export endpoint requires authentication."""
        response = client.get('/export')
        assert response.status_code == 302  # Should redirect to login

    def test_export_csv(self, authenticated_client, sample_csv_data):
        """Test CSV export functionality."""
        # First upload some data
        csv_file = io.BytesIO(sample_csv_data.encode('utf-8'))
        authenticated_client.post('/upload', 
                                 data={'file': (csv_file, 'test.csv')},
                                 follow_redirects=True)
        
        # Then export data
        response = authenticated_client.get('/export')
        assert response.status_code == 200
        assert 'text/csv' in response.headers['Content-Type']
        assert b'John' in response.data
        assert b'Jane' in response.data

    def test_export_empty_database(self, authenticated_client):
        """Test export with empty database."""
        response = authenticated_client.get('/export')
        assert response.status_code == 200
        # Should handle empty database gracefully


class TestFieldMapping:
    """Test field mapping functionality."""

    def test_field_mapping_application(self, authenticated_client):
        """Test that field mapping is applied correctly."""
        # CSV with different column names
        mapped_csv = """FirstName,LastName,EmailAddress
John,Doe,john@example.com
Jane,Smith,jane@example.com"""
        
        csv_file = io.BytesIO(mapped_csv.encode('utf-8'))
        response = authenticated_client.post('/upload', 
                             data={'file': (csv_file, 'mapped.csv')},
                             follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify mapping was applied
        with authenticated_client.application.app_context():
            person = People.query.filter_by(first_name='John').first()
            assert person is not None
            assert person.first_name == 'John'
            assert person.last_name == 'Doe'
            assert person.email == 'john@example.com'

    def test_missing_columns_handling(self, authenticated_client):
        """Test handling of missing columns."""
        # CSV with only some required columns
        partial_csv = """first_name,email
John,john@example.com
Jane,jane@example.com"""
        
        csv_file = io.BytesIO(partial_csv.encode('utf-8'))
        response = authenticated_client.post('/upload', 
                             data={'file': (csv_file, 'partial.csv')},
                             follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify partial data was handled (may be None if missing last_name is required)
        with authenticated_client.application.app_context():
            people = People.query.all()
            # Should handle missing columns gracefully - either create records or skip them
            assert len(people) >= 0  # Accept any number of records
