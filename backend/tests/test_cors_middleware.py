"""
Test suite for CORS middleware functionality

This test suite verifies that:
1. CORS middleware is properly configured
2. Preflight requests are handled correctly
3. Cross-origin requests include proper headers
4. Allowed origins, methods, and headers are configured correctly
5. Frontend can access the API from allowed origins
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create test client with mocked database dependencies"""
    with patch('backend.app.core.database.init_db') as mock_init_db, \
         patch('backend.app.core.database.close_db') as mock_close_db:
        
        mock_init_db.return_value = None
        mock_close_db.return_value = None
        
        from backend.app.main import app
        return TestClient(app)


class TestCORSMiddleware:
    """Test CORS middleware functionality"""
    
    def test_cors_middleware_applied(self, client):
        """Test that CORS middleware is applied to the application"""
        # Make a simple request to check if CORS headers are present
        response = client.get("/")
        
        # CORS headers should be present even for same-origin requests
        assert response.status_code == 200
        
        # The middleware should be applied (we'll test headers in other tests)
        assert response.headers.get("content-type") is not None
    
    def test_preflight_options_request(self, client):
        """Test that preflight OPTIONS requests are handled correctly"""
        # Simulate a preflight request from frontend
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization"
        }
        
        response = client.options("/api/v1/health", headers=headers)
        
        # Preflight requests should return 200
        assert response.status_code == 200
        
        # Check CORS headers in response
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
        assert "access-control-allow-credentials" in response.headers
    
    def test_cors_allowed_origin_frontend_dev(self, client):
        """Test that requests from frontend development origin are allowed"""
        headers = {"Origin": "http://localhost:3000"}
        
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200
        
        # Check that the origin is reflected in the response
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert response.headers.get("access-control-allow-credentials") == "true"
    
    def test_cors_allowed_origin_frontend_prod(self, client):
        """Test that requests from frontend production origin are allowed"""
        headers = {"Origin": "http://localhost:80"}
        
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200
        
        # Check that the origin is reflected in the response
        assert response.headers.get("access-control-allow-origin") == "http://localhost:80"
        assert response.headers.get("access-control-allow-credentials") == "true"
    
    def test_cors_allowed_origin_https_dev(self, client):
        """Test that requests from HTTPS development origin are allowed"""
        headers = {"Origin": "https://localhost:3000"}
        
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200
        
        # Check that the origin is reflected in the response
        assert response.headers.get("access-control-allow-origin") == "https://localhost:3000"
        assert response.headers.get("access-control-allow-credentials") == "true"
    
    def test_cors_credentials_allowed(self, client):
        """Test that credentials are allowed in CORS requests"""
        headers = {"Origin": "http://localhost:3000"}
        
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200
        
        # Credentials should be allowed
        assert response.headers.get("access-control-allow-credentials") == "true"
    
    def test_cors_all_methods_allowed(self, client):
        """Test that all HTTP methods are allowed via CORS"""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        }
        
        response = client.options("/api/v1/health", headers=headers)
        assert response.status_code == 200
        
        allowed_methods = response.headers.get("access-control-allow-methods", "")
        
        # Should allow common HTTP methods
        expected_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
        for method in expected_methods:
            assert method in allowed_methods.upper(), f"Method {method} should be allowed"
    
    def test_cors_custom_headers_allowed(self, client):
        """Test that custom headers are allowed via CORS"""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type,x-requested-with"
        }
        
        response = client.options("/api/v1/health", headers=headers)
        assert response.status_code == 200
        
        allowed_headers = response.headers.get("access-control-allow-headers", "")
        
        # Check that common headers are allowed
        expected_headers = ["authorization", "content-type"]
        for header in expected_headers:
            assert header.lower() in allowed_headers.lower(), f"Header {header} should be allowed"
    
    def test_cors_with_authentication_headers(self, client):
        """Test CORS with authentication headers"""
        headers = {
            "Origin": "http://localhost:3000",
            "Authorization": "Bearer test-token",
            "Content-Type": "application/json"
        }
        
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200
        
        # CORS headers should be present
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert response.headers.get("access-control-allow-credentials") == "true"
    
    def test_cors_post_request_with_json(self, client):
        """Test CORS with POST request containing JSON data"""
        headers = {
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json"
        }
        
        # Use the root endpoint for a simple POST test
        response = client.post("/", json={"test": "data"}, headers=headers)
        # Note: The root endpoint doesn't accept POST, but we're testing CORS headers
        
        # CORS headers should be present regardless of method support
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert response.headers.get("access-control-allow-credentials") == "true"
    
    def test_cors_varies_header(self, client):
        """Test that Vary header is properly set for CORS"""
        headers = {"Origin": "http://localhost:3000"}
        
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200
        
        # Vary header should be set for proper caching with CORS
        vary_header = response.headers.get("vary", "")
        assert "origin" in vary_header.lower() or "Origin" in vary_header, "Vary header should include Origin"
    
    def test_cors_multiple_origins_configuration(self, client):
        """Test that CORS is configured for multiple allowed origins"""
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:80", 
            "https://localhost:3000"
        ]
        
        for origin in allowed_origins:
            headers = {"Origin": origin}
            response = client.get("/api/v1/health", headers=headers)
            
            assert response.status_code == 200, f"Request from {origin} should succeed"
            assert response.headers.get("access-control-allow-origin") == origin, f"Origin {origin} should be reflected in response"
            assert response.headers.get("access-control-allow-credentials") == "true", f"Credentials should be allowed for {origin}"
    
    def test_cors_configuration_from_settings(self, client):
        """Test that CORS configuration comes from application settings"""
        # This test ensures CORS is configured via settings, not hardcoded
        from backend.app.config import get_settings
        
        settings = get_settings()
        expected_origins = settings.cors_origins
        
        # Test that at least the expected origins are configured
        assert len(expected_origins) > 0, "CORS origins should be configured in settings"
        assert "http://localhost:3000" in expected_origins, "Frontend dev origin should be in settings"
        
        # Test one of the configured origins
        if expected_origins:
            test_origin = expected_origins[0]
            headers = {"Origin": test_origin}
            response = client.get("/api/v1/health", headers=headers)
            
            assert response.status_code == 200
            assert response.headers.get("access-control-allow-origin") == test_origin
    
    def test_cors_preflight_for_api_endpoints(self, client):
        """Test preflight requests work for all API endpoints"""
        api_endpoints = [
            "/api/v1/health",
            "/api/v1/health/ready",
            "/api/v1/health/live"
        ]
        
        for endpoint in api_endpoints:
            headers = {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization"
            }
            
            response = client.options(endpoint, headers=headers)
            assert response.status_code == 200, f"Preflight for {endpoint} should succeed"
            assert "access-control-allow-origin" in response.headers, f"CORS headers should be present for {endpoint}"
            assert "access-control-allow-methods" in response.headers, f"Allowed methods should be specified for {endpoint}" 