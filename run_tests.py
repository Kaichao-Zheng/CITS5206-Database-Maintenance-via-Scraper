#!/usr/bin/env python3
"""
Test runner script for the Flask application.
This script runs all tests and provides a summary of results.
"""

import sys
import subprocess
import os
from pathlib import Path

def run_tests():
    """Run all tests and display results."""
    print("=" * 60)
    print("Running Flask Application Tests")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Run pytest with verbose output
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', 
            '-v', 
            '--tb=short',
            '--color=yes',
            '--durations=10'
        ], check=True, capture_output=False)
        
        print("\n" + "=" * 60)
        print("All tests completed successfully! ✅")
        print("=" * 60)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest:")
        print("pip install pytest")
        return False

def run_specific_test(test_file):
    """Run a specific test file."""
    print(f"Running {test_file}...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            f'tests/{test_file}', 
            '-v', 
            '--tb=short',
            '--color=yes'
        ], check=True, capture_output=False)
        return True
    except subprocess.CalledProcessError:
        return False

def run_coverage():
    """Run tests with coverage report."""
    print("Running tests with coverage...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', 
            '--cov=app',
            '--cov-report=html',
            '--cov-report=term-missing',
            '-v'
        ], check=True, capture_output=False)
        
        print("\nCoverage report generated in htmlcov/index.html")
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print("❌ pytest-cov not found. Please install pytest-cov:")
        print("pip install pytest-cov")
        return False

def main():
    """Main test runner function."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'coverage':
            success = run_coverage()
        elif command == 'auth':
            success = run_specific_test('test_auth.py')
        elif command == 'models':
            success = run_specific_test('test_models.py')
        elif command == 'upload':
            success = run_specific_test('test_upload.py')
        elif command == 'scraping':
            success = run_specific_test('test_scraping.py')
        elif command == 'integration':
            success = run_specific_test('test_integration.py')
        elif command == 'routes':
            success = run_specific_test('test_routes.py')
        else:
            print(f"Unknown command: {command}")
            print("Available commands: coverage, auth, models, upload, scraping, integration, routes")
            return False
    else:
        success = run_tests()
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
