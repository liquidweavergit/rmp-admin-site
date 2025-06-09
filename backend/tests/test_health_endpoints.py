"""
Test suite for health check endpoints

This test suite verifies that:
1. Health check endpoints are accessible and return correct data
2. Health checks properly detect service failures
3. Response formats match expected schemas
4. All health endpoints (main, ready, live) work correctly
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime
import redis
import json

@pytest.fixture
def client():
    """Create test client with mocked database dependencies"""
    with patch('backend.app.core.database.init_db') as mock_init_db, \
         patch('backend.app.core.database.close_db') as mock_close_db:
        
        mock_init_db.return_value = None
        mock_close_db.return_value = None
        
        from backend.app.main import app
        return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoint functionality"""
    
    def test_health_endpoint_exists(self, client):
        """Test that the main health endpoint exists and is accessible"""
        with patch('redis.from_url') as mock_redis:
            # Mock successful Redis connection
            mock_redis_client = MagicMock()
            mock_redis_client.ping.return_value = True
            mock_redis.return_value = mock_redis_client
            
            response = client.get("/api/v1/health")
            assert response.status_code == 200, f"Health endpoint should return 200, got {response.status_code}"
    
    def test_health_endpoint_response_format(self, client):
        """Test that health endpoint returns correctly formatted response"""
        with patch('redis.from_url') as mock_redis:
            # Mock successful Redis connection
            mock_redis_client = MagicMock()
            mock_redis_client.ping.return_value = True
            mock_redis.return_value = mock_redis_client
            
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            
            data = response.json()
            
            # Check required fields exist
            required_fields = ['status', 'service', 'version', 'timestamp', 'checks']
            for field in required_fields:
                assert field in data, f"Health response should contain '{field}' field"
            
            # Check field types and values
            assert isinstance(data['status'], str), "Status should be a string"
            assert data['service'] == "mens-circle-backend", "Service name should match expected value"
            assert isinstance(data['version'], str), "Version should be a string"
            assert isinstance(data['timestamp'], str), "Timestamp should be a string"
            assert isinstance(data['checks'], dict), "Checks should be a dictionary"
    
    def test_health_endpoint_redis_healthy(self, client):
        """Test health endpoint when Redis is healthy"""
        with patch('redis.from_url') as mock_redis:
            # Mock successful Redis connection
            mock_redis_client = MagicMock()
            mock_redis_client.ping.return_value = True
            mock_redis.return_value = mock_redis_client
            
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data['status'] == "healthy", "Overall status should be healthy when all services are up"
            assert 'redis' in data['checks'], "Redis check should be included"
            assert data['checks']['redis']['status'] == "healthy", "Redis should be marked as healthy"
            assert "Connection successful" in data['checks']['redis']['message'], "Redis message should indicate success"
    
    def test_health_endpoint_redis_unhealthy(self, client):
        """Test health endpoint when Redis is unavailable"""
        with patch('redis.from_url') as mock_redis:
            # Mock Redis connection failure
            mock_redis.side_effect = redis.ConnectionError("Connection failed")
            
            response = client.get("/api/v1/health")
            assert response.status_code == 200  # Endpoint should still return 200 but with degraded status
            
            data = response.json()
            assert data['status'] == "degraded", "Overall status should be degraded when Redis is down"
            assert 'redis' in data['checks'], "Redis check should be included"
            assert data['checks']['redis']['status'] == "unhealthy", "Redis should be marked as unhealthy"
            assert "Connection failed" in data['checks']['redis']['message'], "Redis message should indicate failure"
    
    def test_readiness_endpoint(self, client):
        """Test readiness probe endpoint"""
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200, "Readiness endpoint should return 200"
        
        data = response.json()
        assert "status" in data, "Readiness response should contain status"
        assert data["status"] == "ready", "Readiness status should be 'ready'"
    
    def test_liveness_endpoint(self, client):
        """Test liveness probe endpoint"""
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200, "Liveness endpoint should return 200"
        
        data = response.json()
        assert "status" in data, "Liveness response should contain status"
        assert data["status"] == "alive", "Liveness status should be 'alive'"
    
    def test_health_endpoints_performance(self, client):
        """Test that health endpoints respond quickly"""
        import time
        
        with patch('redis.from_url') as mock_redis:
            mock_redis_client = MagicMock()
            mock_redis_client.ping.return_value = True
            mock_redis.return_value = mock_redis_client
            
            # Test main health endpoint
            start_time = time.time()
            response = client.get("/api/v1/health")
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < 1.0, "Health endpoint should respond within 1 second"
            
            # Test readiness endpoint
            start_time = time.time()
            response = client.get("/api/v1/health/ready")
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < 0.5, "Readiness endpoint should respond within 0.5 seconds"
            
            # Test liveness endpoint
            start_time = time.time()
            response = client.get("/api/v1/health/live")
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < 0.5, "Liveness endpoint should respond within 0.5 seconds"
    
    def test_health_endpoint_headers(self, client):
        """Test that health endpoint returns appropriate headers"""
        with patch('redis.from_url') as mock_redis:
            mock_redis_client = MagicMock()
            mock_redis_client.ping.return_value = True
            mock_redis.return_value = mock_redis_client
            
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            
            # Check content type
            assert response.headers["content-type"].startswith("application/json"), "Health endpoint should return JSON"
    
    def test_health_endpoint_timestamp_format(self, client):
        """Test that timestamp is in correct ISO format"""
        with patch('redis.from_url') as mock_redis:
            mock_redis_client = MagicMock()
            mock_redis_client.ping.return_value = True
            mock_redis.return_value = mock_redis_client
            
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            
            data = response.json()
            timestamp_str = data['timestamp']
            
            # Try to parse the timestamp - should not raise exception
            try:
                datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except ValueError:
                pytest.fail(f"Timestamp '{timestamp_str}' is not in valid ISO format")
    
    def test_all_health_endpoints_accessible(self, client):
        """Test that all health endpoints are accessible without authentication"""
        endpoints = [
            "/api/v1/health",
            "/api/v1/health/ready", 
            "/api/v1/health/live"
        ]
        
        with patch('redis.from_url') as mock_redis:
            mock_redis_client = MagicMock()
            mock_redis_client.ping.return_value = True
            mock_redis.return_value = mock_redis_client
            
            for endpoint in endpoints:
                response = client.get(endpoint)
                assert response.status_code == 200, f"Endpoint {endpoint} should be accessible without authentication"
                assert response.headers["content-type"].startswith("application/json"), f"Endpoint {endpoint} should return JSON" 