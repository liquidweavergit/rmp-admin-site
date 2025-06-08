"""
Test suite for Docker file requirements (Task 1.4)
Tests for simple Dockerfiles with:
- Backend: Python 3.11
- Frontend: Node 18
"""

import os
import pytest
import re
import yaml
from pathlib import Path

class TestDockerfiles:
    """Test suite for Docker file requirements."""
    
    def test_backend_dockerfile_exists(self):
        """Test that backend Dockerfile exists."""
        backend_dockerfile = Path("docker/backend.Dockerfile")
        assert backend_dockerfile.exists(), "Backend Dockerfile should exist in docker/ directory"
    
    def test_frontend_dockerfile_exists(self):
        """Test that frontend Dockerfile exists."""
        frontend_dockerfile = Path("docker/frontend.Dockerfile")
        assert frontend_dockerfile.exists(), "Frontend Dockerfile should exist in docker/ directory"
    
    def test_backend_dockerfile_uses_python_311(self):
        """Test that backend Dockerfile uses Python 3.11 as required by task 1.4."""
        backend_dockerfile = Path("docker/backend.Dockerfile")
        content = backend_dockerfile.read_text()
        
        # Check for Python 3.11 base image
        python_311_pattern = r'FROM\s+python:3\.11'
        matches = re.findall(python_311_pattern, content, re.IGNORECASE)
        
        assert len(matches) >= 1, f"Backend Dockerfile must use Python 3.11, found matches: {matches}"
    
    def test_frontend_dockerfile_uses_node_18(self):
        """Test that frontend Dockerfile uses Node 18 as required by task 1.4."""
        frontend_dockerfile = Path("docker/frontend.Dockerfile")
        content = frontend_dockerfile.read_text()
        
        # Check for Node 18 base image
        node_18_pattern = r'FROM\s+node:18'
        matches = re.findall(node_18_pattern, content, re.IGNORECASE)
        
        assert len(matches) >= 1, f"Frontend Dockerfile must use Node 18, found matches: {matches}"
    
    def test_backend_dockerfile_structure(self):
        """Test that backend Dockerfile has proper structure."""
        backend_dockerfile = Path("docker/backend.Dockerfile")
        content = backend_dockerfile.read_text()
        
        # Check for essential Dockerfile commands
        assert 'WORKDIR' in content, "Backend Dockerfile should set WORKDIR"
        assert 'COPY' in content, "Backend Dockerfile should have COPY instructions"
        assert 'RUN' in content, "Backend Dockerfile should have RUN instructions"
        assert 'EXPOSE' in content, "Backend Dockerfile should expose a port"
        assert 'CMD' in content or 'ENTRYPOINT' in content, "Backend Dockerfile should have CMD or ENTRYPOINT"
    
    def test_frontend_dockerfile_structure(self):
        """Test that frontend Dockerfile has proper structure."""
        frontend_dockerfile = Path("docker/frontend.Dockerfile")
        content = frontend_dockerfile.read_text()
        
        # Check for essential Dockerfile commands
        assert 'WORKDIR' in content, "Frontend Dockerfile should set WORKDIR"
        assert 'COPY' in content, "Frontend Dockerfile should have COPY instructions"
        assert 'RUN' in content, "Frontend Dockerfile should have RUN instructions"
        assert 'EXPOSE' in content, "Frontend Dockerfile should expose a port"
        assert 'CMD' in content or 'ENTRYPOINT' in content, "Frontend Dockerfile should have CMD or ENTRYPOINT"
    
    def test_backend_dockerfile_exposes_port_8000(self):
        """Test that backend Dockerfile exposes port 8000."""
        backend_dockerfile = Path("docker/backend.Dockerfile")
        content = backend_dockerfile.read_text()
        
        # Check for port 8000 exposure
        port_pattern = r'EXPOSE\s+8000'
        assert re.search(port_pattern, content), "Backend Dockerfile should expose port 8000"
    
    def test_frontend_dockerfile_exposes_port_80(self):
        """Test that frontend Dockerfile exposes appropriate port (80 for nginx)."""
        frontend_dockerfile = Path("docker/frontend.Dockerfile")
        content = frontend_dockerfile.read_text()
        
        # Check for port exposure (80 is common for nginx)
        port_pattern = r'EXPOSE\s+(80|3000)'
        assert re.search(port_pattern, content), "Frontend Dockerfile should expose port 80 or 3000"
    
    def test_backend_dockerfile_has_health_check(self):
        """Test that backend Dockerfile includes health check."""
        backend_dockerfile = Path("docker/backend.Dockerfile")
        content = backend_dockerfile.read_text()
        
        assert 'HEALTHCHECK' in content, "Backend Dockerfile should include health check"
    
    def test_frontend_dockerfile_has_health_check(self):
        """Test that frontend Dockerfile includes health check."""
        frontend_dockerfile = Path("docker/frontend.Dockerfile")
        content = frontend_dockerfile.read_text()
        
        assert 'HEALTHCHECK' in content, "Frontend Dockerfile should include health check"
    
    def test_dockerfiles_are_simple_but_complete(self):
        """Test that Dockerfiles are simple but contain necessary components."""
        backend_dockerfile = Path("docker/backend.Dockerfile")
        frontend_dockerfile = Path("docker/frontend.Dockerfile")
        
        backend_content = backend_dockerfile.read_text()
        frontend_content = frontend_dockerfile.read_text()
        
        # Backend should have key components
        backend_lines = len(backend_content.splitlines())
        assert 30 <= backend_lines <= 100, f"Backend Dockerfile should be simple but complete (30-100 lines), found {backend_lines} lines"
        
        # Frontend should have key components  
        frontend_lines = len(frontend_content.splitlines())
        assert 30 <= frontend_lines <= 100, f"Frontend Dockerfile should be simple but complete (30-100 lines), found {frontend_lines} lines"
    
    def test_dockerfiles_security_practices(self):
        """Test that Dockerfiles follow basic security practices."""
        backend_dockerfile = Path("docker/backend.Dockerfile")
        frontend_dockerfile = Path("docker/frontend.Dockerfile")
        
        backend_content = backend_dockerfile.read_text()
        frontend_content = frontend_dockerfile.read_text()
        
        # Check for non-root user usage
        assert 'USER' in backend_content, "Backend Dockerfile should use non-root user"
        assert 'USER' in frontend_content, "Frontend Dockerfile should use non-root user"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 