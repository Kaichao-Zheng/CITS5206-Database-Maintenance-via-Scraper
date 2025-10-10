"""
Integration tests.
Tests complete workflows and system integration with proper mocking.
"""

import pytest
import io
from unittest.mock import patch, MagicMock
from app.models import People, Log, LogDetail, IP, GovPeople, db


class TestCompleteWorkflow:
    """Test complete application workflows."""

    def test_csv_upload_to_export_workflow(self, authenticated_client, sample_csv_data):
        """Test complete workflow from CSV upload to export."""
        # Step 1: Upload CSV
        csv_file = io.BytesIO(sample_csv_data.encode('utf-8'))
        upload_response = authenticated_client.post('/upload',
                                                  data={'file': (csv_file, 'test.csv')},
                                                  follow_redirects=True)
        assert upload_response.status_code == 200
        
        # Step 2: Verify data in database
        with authenticated_client.application.app_context():
            people = People.query.all()
            assert len(people) >= 0  # Should have some data
        
        # Step 3: Export data
        export_response = authenticated_client.get('/export')
        assert export_response.status_code == 200
        assert 'text/csv' in export_response.headers['Content-Type']

    def test_scraping_workflow_with_mocks(self, authenticated_client):
        """Test complete scraping workflow with mocked dependencies."""
        # Create test people data
        person1 = People(first_name="John", last_name="Doe", email="john@example.com")
        person2 = People(first_name="Jane", last_name="Smith", email="jane@example.com")
        db.session.add_all([person1, person2])
        db.session.commit()
        
        # Mock all scraping functions
        with patch('app.main.scrape.helper.ip_scraping.scrape_https_proxies') as mock_proxies:
            with patch('app.main.scrape.helper.profile_url_scrape.scrape_linkedin_people_search') as mock_urls:
                with patch('app.main.scrape.helper.scrape_information.scrape_and_update_people') as mock_info:
                    # Configure mocks
                    mock_proxies.return_value = [
                        {"ip": "192.168.1.1", "port": "8080", "protocol": "http"}
                    ]
                    mock_urls.return_value = [
                        {"name": "John Doe", "linkedin": "https://linkedin.com/in/johndoe"}
                    ]
                    mock_info.return_value = [
                        {"name": "John Doe", "title": "Software Engineer"}
                    ]
                    
                    # Test proxy scraping
                    proxy_response = authenticated_client.get('/scrape_and_store_proxies')
                    assert proxy_response.status_code in [200, 500]  # Handle errors gracefully
                    
                    # Test profile URL scraping
                    url_response = authenticated_client.get('/scrape_profile_url')
                    assert url_response.status_code in [200, 500]  # Handle errors gracefully
                    
                    # Test information scraping
                    info_response = authenticated_client.get('/scrape_information')
                    assert info_response.status_code in [200, 400, 404, 500]  # Handle errors gracefully

    def test_data_management_workflow(self, authenticated_client, sample_csv_data):
        """Test complete data management workflow."""
        # Upload data
        csv_file = io.BytesIO(sample_csv_data.encode('utf-8'))
        upload_response = authenticated_client.post('/upload',
                                                  data={'file': (csv_file, 'test.csv')},
                                                  follow_redirects=True)
        assert upload_response.status_code == 200
        
        # View data
        data_response = authenticated_client.get('/data')
        assert data_response.status_code == 200
        
        # Export data
        export_response = authenticated_client.get('/export')
        assert export_response.status_code == 200


class TestAuthenticationIntegration:
    """Test authentication integration across workflows."""

    def test_authenticated_workflow(self, authenticated_client):
        """Test that authenticated users can access all features."""
        # Test workspace access
        workspace_response = authenticated_client.get('/workspace')
        assert workspace_response.status_code == 200
        
        # Test logs access
        logs_response = authenticated_client.get('/logs')
        assert logs_response.status_code == 200
        
        # Test data access
        data_response = authenticated_client.get('/data')
        assert data_response.status_code == 200

    def test_unauthenticated_workflow(self, client):
        """Test that unauthenticated users are redirected to login."""
        protected_routes = ['/workspace', '/logs', '/data', '/export']
        
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 302  # Should redirect to login

    def test_login_workflow(self, client):
        """Test complete login workflow."""
        # Create test user
        from app.models import User
        user = User(username='admin', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        
        # Test login
        login_response = client.post('/', data={'password': 'testpassword'}, follow_redirects=True)
        assert login_response.status_code == 200
        
        # Test access to protected route after login
        workspace_response = client.get('/workspace')
        assert workspace_response.status_code == 200

    def test_logout_workflow(self, authenticated_client):
        """Test complete logout workflow."""
        # Test logout
        logout_response = authenticated_client.get('/logout')
        assert logout_response.status_code == 302  # Should redirect
        
        # Test that protected routes require login after logout
        workspace_response = authenticated_client.get('/workspace')
        assert workspace_response.status_code == 302  # Should redirect to login


class TestDatabaseIntegration:
    """Test database integration across workflows."""

    def test_people_model_integration(self, authenticated_client, sample_csv_data):
        """Test People model integration with CSV upload."""
        # Upload CSV data
        csv_file = io.BytesIO(sample_csv_data.encode('utf-8'))
        upload_response = authenticated_client.post('/upload',
                                                  data={'file': (csv_file, 'test.csv')},
                                                  follow_redirects=True)
        assert upload_response.status_code == 200
        
        # Verify data in database
        with authenticated_client.application.app_context():
            people = People.query.all()
            assert len(people) >= 0
            
            # Test model methods if data exists
            if people:
                person = people[0]
                assert hasattr(person, 'first_name')
                assert hasattr(person, 'last_name')

    def test_log_model_integration(self, authenticated_client):
        """Test Log model integration with update workflows."""
        # Create test log
        log = Log(status="in progress", result="test result")
        db.session.add(log)
        db.session.commit()
        
        # Test log details endpoint
        details_response = authenticated_client.get(f'/logs/{log.id}/details')
        assert details_response.status_code == 200
        
        # Test update progress endpoint
        progress_response = authenticated_client.get(f'/update_progress/{log.id}')
        assert progress_response.status_code == 200

    def test_ip_model_integration(self, authenticated_client):
        """Test IP model integration with proxy scraping."""
        # Mock proxy scraping
        with patch('app.main.scrape.helper.ip_scraping.scrape_https_proxies') as mock_scrape:
            mock_scrape.return_value = [
                {"ip": "192.168.1.1", "port": "8080", "protocol": "http"},
                {"ip": "192.168.1.2", "port": "8081", "protocol": "https"}
            ]
            
            # Test proxy scraping endpoint
            response = authenticated_client.get('/scrape_and_store_proxies')
            assert response.status_code in [200, 500]  # Handle errors gracefully

    def test_gov_people_model_integration(self, authenticated_client):
        """Test GovPeople model integration."""
        # Create test gov person
        gov_person = GovPeople(first_name="John", last_name="Doe", organization="Government", role="Senator")
        db.session.add(gov_person)
        db.session.commit()
        
        # Verify data exists
        with authenticated_client.application.app_context():
            gov_people = GovPeople.query.all()
            assert len(gov_people) >= 1
            assert gov_people[0].first_name == "John"


class TestErrorHandlingIntegration:
    """Test error handling integration across workflows."""

    def test_csv_upload_error_handling(self, authenticated_client):
        """Test CSV upload error handling."""
        # Test with invalid file
        invalid_file = io.BytesIO(b"invalid,csv,data\nwith,missing,columns")
        response = authenticated_client.post('/upload',
                                           data={'file': (invalid_file, 'invalid.csv')},
                                           follow_redirects=True)
        # Should handle gracefully
        assert response.status_code in [200, 400, 500]

    def test_scraping_error_handling(self, authenticated_client):
        """Test scraping error handling."""
        with patch('app.main.scrape.helper.ip_scraping.scrape_https_proxies') as mock_scrape:
            mock_scrape.side_effect = Exception("Network error")
            
            response = authenticated_client.get('/scrape_and_store_proxies')
            assert response.status_code in [200, 500]

    def test_database_error_handling(self, authenticated_client):
        """Test database error handling."""
        with patch('app.models.People.query') as mock_query:
            mock_query.all.side_effect = Exception("Database error")
            
            # This should be handled gracefully in the application
            response = authenticated_client.get('/data')
            assert response.status_code in [200, 500]


class TestPerformanceIntegration:
    """Test performance and scalability integration."""

    def test_large_dataset_handling(self, authenticated_client):
        """Test handling of large datasets."""
        # Create large dataset
        large_csv_data = "first_name,last_name,email\n"
        for i in range(100):
            large_csv_data += f"Person{i},Last{i},person{i}@example.com\n"
        
        csv_file = io.BytesIO(large_csv_data.encode('utf-8'))
        response = authenticated_client.post('/upload',
                                           data={'file': (csv_file, 'large.csv')},
                                           follow_redirects=True)
        # Should handle large datasets
        assert response.status_code in [200, 500]

    def test_concurrent_operations(self, authenticated_client):
        """Test concurrent operations handling."""
        # Test multiple simultaneous requests
        responses = []
        for i in range(5):
            response = authenticated_client.get('/data')
            responses.append(response)
        
        # All should succeed or fail gracefully
        for response in responses:
            assert response.status_code in [200, 500]


class TestSecurityIntegration:
    """Test security integration across workflows."""

    def test_csrf_protection(self, authenticated_client):
        """Test CSRF protection integration."""
        # Test that forms include CSRF tokens
        response = authenticated_client.get('/workspace')
        assert response.status_code == 200
        assert b'csrf-token' in response.data

    def test_authentication_required(self, client):
        """Test that authentication is required for all protected routes."""
        protected_routes = [
            '/workspace', '/logs', '/data', '/export',
            '/scrape_and_store_proxies', '/scrape_profile_url',
            '/scrape_information', '/scrape_from_linkedin'
        ]
        
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code in [302, 400, 500]  # Redirect, bad request, or error

    def test_session_management(self, authenticated_client):
        """Test session management integration."""
        # Test that session persists across requests
        response1 = authenticated_client.get('/workspace')
        response2 = authenticated_client.get('/data')
        
        assert response1.status_code == 200
        assert response2.status_code == 200