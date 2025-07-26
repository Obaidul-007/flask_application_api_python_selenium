"""
Basic health check tests for the Flask application API.

These tests verify that the application is running and responding correctly.
"""

import pytest
import requests
from requests.exceptions import RequestException


class TestHealthChecks:
    """Basic health check test suite"""
    
    @pytest.mark.smoke
    @pytest.mark.api
    def test_application_is_running(self, base_url):
        """Test that the Flask application is running and accessible"""
        try:
            response = requests.get(base_url, timeout=10)
            assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
            
        except RequestException as e:
            pytest.fail(f"Could not connect to application at {base_url}: {e}")
    
    @pytest.mark.smoke
    @pytest.mark.api  
    def test_health_endpoint(self, base_url):
        """Test the health endpoint if it exists"""
        health_url = f"{base_url}/health"
        
        try:
            response = requests.get(health_url, timeout=10)
            # Health endpoint might not exist, so we accept 404 as well
            assert response.status_code in [200, 404], f"Unexpected status code: {response.status_code}"
            
            if response.status_code == 200:
                # If health endpoint exists, verify it returns valid data
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                assert isinstance(data, dict), "Health endpoint should return JSON object"
                
        except RequestException as e:
            pytest.fail(f"Could not connect to health endpoint at {health_url}: {e}")
    
    @pytest.mark.api
    def test_login_page_accessible(self, base_url):
        """Test that the login page is accessible"""
        login_url = f"{base_url}/login"
        
        try:
            response = requests.get(login_url, timeout=10)
            assert response.status_code == 200, f"Login page returned status {response.status_code}"
            assert "login" in response.text.lower(), "Login page should contain login form"
            
        except RequestException as e:
            pytest.fail(f"Could not access login page at {login_url}: {e}")
    
    @pytest.mark.api
    def test_static_files_accessible(self, base_url):
        """Test that static files are being served (if any exist)"""
        # This is a basic test - modify based on your actual static files
        static_endpoints = [
            "/static/css/style.css",
            "/static/js/main.js", 
            "/favicon.ico"
        ]
        
        for endpoint in static_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                response = requests.get(url, timeout=5)
                # Static files might not exist, so we accept 404
                assert response.status_code in [200, 404], f"Unexpected status for {endpoint}: {response.status_code}"
                
            except RequestException:
                # Static file requests failing is acceptable for basic health checks
                pass
    
    @pytest.mark.regression
    @pytest.mark.api
    def test_api_endpoints_basic_structure(self, base_url):
        """Test basic API endpoint structure"""
        api_endpoints = [
            "/api",
            "/api/users",
            "/api/auth"
        ]
        
        for endpoint in api_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                response = requests.get(url, timeout=5)
                # API endpoints might return various status codes
                # We just want to ensure they don't return server errors (5xx)
                assert response.status_code < 500, f"Server error on {endpoint}: {response.status_code}"
                
            except RequestException:
                # API endpoints might not exist in basic app
                pass
    
    @pytest.mark.smoke
    def test_application_response_time(self, base_url):
        """Test that application responds within acceptable time"""
        import time
        
        start_time = time.time()
        try:
            response = requests.get(base_url, timeout=30)
            response_time = time.time() - start_time
            
            assert response_time < 5.0, f"Application response time too slow: {response_time:.2f}s"
            assert response.status_code == 200, f"Application returned status {response.status_code}"
            
        except RequestException as e:
            pytest.fail(f"Application did not respond within acceptable time: {e}")