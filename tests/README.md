# Test Suite Documentation

This directory contains comprehensive tests for the Flask application database maintenance system.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Test configuration and fixtures
├── test_auth.py             # Authentication and user management tests
├── test_models.py           # Database model tests
├── test_upload.py           # File upload and data processing tests
├── test_scraping.py         # Scraping functionality tests
├── test_integration.py      # Integration and workflow tests
├── test_routes.py           # Route and endpoint tests
└── README.md               # This documentation
```

## Test Categories

### 1. Authentication Tests (`test_auth.py`)
- User login/logout functionality
- Password hashing and verification
- Authentication requirements for protected routes
- User model creation and validation
- Form validation and error handling

### 2. Database Model Tests (`test_models.py`)
- User model functionality
- People model operations
- Log and LogDetail model relationships
- IP model for proxy management
- GovPeople model for government data
- Model string representations and serialization

### 3. File Upload Tests (`test_upload.py`)
- CSV file upload and validation
- Field mapping and data transformation
- Error handling for invalid files
- Data export functionality
- Database operations and data consistency

### 4. Scraping Tests (`test_scraping.py`)
- LinkedIn profile URL scraping
- Profile information extraction
- Proxy management and storage
- Scraping parameter handling
- Error handling and failure scenarios
- Mocked external service interactions

### 5. Integration Tests (`test_integration.py`)
- Complete user workflows
- End-to-end functionality testing
- Data consistency across operations
- Error handling in complete workflows
- Performance testing with large datasets
- Concurrent operation handling

### 6. Route Tests (`test_routes.py`)
- All application routes and endpoints
- Authentication requirements
- Route parameter handling
- Security and access control
- Error responses and status codes

## Running Tests

### Prerequisites
Install test dependencies:
```bash
pip install -r requirements.txt
```

### Running All Tests
```bash
python run_tests.py
```

### Running Specific Test Categories
```bash
# Authentication tests
python run_tests.py auth

# Database model tests
python run_tests.py models

# File upload tests
python run_tests.py upload

# Scraping tests
python run_tests.py scraping

# Integration tests
python run_tests.py integration

# Route tests
python run_tests.py routes
```

### Running with Coverage
```bash
python run_tests.py coverage
```

### Direct pytest Usage
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run in parallel
pytest tests/ -n auto
```

## Test Configuration

### Fixtures (`conftest.py`)
- `app`: Flask application instance with test configuration
- `client`: Test client for making HTTP requests
- `runner`: CLI test runner
- `auth_headers`: Authentication headers for protected routes
- `sample_people_data`: Sample data for testing
- `sample_csv_data`: Sample CSV data for file upload tests
- `sample_log_data`: Sample log data for testing

### Test Database
- Uses SQLite in-memory database for testing
- Database is created and destroyed for each test
- No data persistence between tests
- Isolated test environment

## Test Coverage

The test suite covers:
- ✅ Authentication and user management
- ✅ Database models and relationships
- ✅ File upload and data processing
- ✅ LinkedIn scraping functionality
- ✅ Proxy management
- ✅ Data export and import
- ✅ Logging and progress tracking
- ✅ Error handling and edge cases
- ✅ Route security and access control
- ✅ Integration workflows
- ✅ Performance characteristics

## Mocking Strategy

External dependencies are mocked to ensure:
- Tests run independently of external services
- Predictable test results
- Fast test execution
- No network dependencies

Mocked components:
- LinkedIn scraping services
- Proxy scraping services
- External API calls
- File system operations
- Email services

## Test Data

### Sample CSV Format
```csv
FirstName,LastName,Organization,Role,EmailAddress,City (if outside AUS),State AUS only,Country
John,Doe,Test Corp,Manager,john.doe@test.com,Sydney,NSW,Australia
Jane,Smith,Test Inc,Developer,jane.smith@test.com,Melbourne,VIC,Australia
```

### Field Mapping
The application maps CSV columns to database fields:
- `FirstName` → `first_name`
- `LastName` → `last_name`
- `Organization` → `organization`
- `Role` → `role`
- `EmailAddress` → `email`
- `City (if outside AUS)` → `city`
- `State AUS only` → `state`
- `Country` → `country`

## Best Practices

### Test Organization
- Each test file focuses on a specific functionality area
- Tests are organized by feature and complexity
- Clear naming conventions for test methods
- Comprehensive docstrings for test classes

### Test Isolation
- Each test runs independently
- Database state is reset between tests
- No shared state between tests
- Proper cleanup after each test

### Error Testing
- Tests both success and failure scenarios
- Validates error messages and status codes
- Tests edge cases and boundary conditions
- Ensures graceful error handling

### Performance Testing
- Tests with large datasets
- Concurrent operation testing
- Memory usage validation
- Response time verification

## Continuous Integration

The test suite is designed to run in CI/CD environments:
- No external dependencies
- Deterministic test results
- Fast execution time
- Comprehensive coverage reporting
- Clear failure reporting

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Errors**: Check that test database is properly configured
3. **Authentication Errors**: Verify auth_headers fixture is working
4. **Mock Errors**: Ensure mocks are properly configured

### Debug Mode
Run tests with verbose output for debugging:
```bash
pytest tests/ -v -s --tb=long
```

### Test Database Issues
If database tests fail:
1. Check SQLite installation
2. Verify database permissions
3. Ensure no other processes are using the test database
4. Check for database lock issues

## Contributing

When adding new tests:
1. Follow existing naming conventions
2. Add comprehensive docstrings
3. Test both success and failure cases
4. Use appropriate fixtures
5. Mock external dependencies
6. Ensure test isolation
7. Update this documentation
