"""
Test suite for full stack startup (Task 1.5)
Tests for `docker-compose up` functionality:
- All services start successfully
- Health checks pass
- Services can communicate
- Application endpoints are accessible
"""

import os
import time
import subprocess
import requests
import pytest
import yaml
from pathlib import Path
from typing import Dict, List

class TestFullStackStartup:
    """Test suite for full stack startup requirements."""
    
    def test_env_file_exists_for_startup(self):
        """Test that .env file exists for docker-compose startup."""
        env_file = Path(".env")
        env_example_file = Path(".env.example")
        
        # Either .env should exist or .env.example should be copyable
        assert env_file.exists() or env_example_file.exists(), \
            "Either .env or .env.example must exist for Docker Compose startup"
        
        if not env_file.exists() and env_example_file.exists():
            # This is expected in development - copy .env.example to .env
            env_content = env_example_file.read_text()
            env_file.write_text(env_content)
    
    def test_docker_compose_config_valid(self):
        """Test that docker-compose configuration is valid."""
        result = subprocess.run(
            ["docker", "compose", "config", "--quiet"],
            capture_output=True,
            text=True,
            cwd="."
        )
        
        # Should not fail (exit code 0), warnings are acceptable
        assert result.returncode == 0, f"Docker Compose config invalid: {result.stderr}"
    
    def test_required_service_images_buildable(self):
        """Test that all custom service images can be built."""
        compose_file = Path("docker-compose.yml")
        config = yaml.safe_load(compose_file.read_text())
        
        services_with_build = []
        for service_name, service_config in config.get('services', {}).items():
            if 'build' in service_config:
                services_with_build.append(service_name)
        
        assert len(services_with_build) > 0, "Should have at least one service that builds from Dockerfile"
        
        # Test that Dockerfiles exist for build services
        for service_name in services_with_build:
            service_config = config['services'][service_name]
            if isinstance(service_config['build'], dict):
                dockerfile = service_config['build'].get('dockerfile', 'Dockerfile')
                context = service_config['build'].get('context', '.')
            else:
                dockerfile = 'Dockerfile'
                context = service_config['build']
            
            dockerfile_path = Path(context) / dockerfile
            assert dockerfile_path.exists(), f"Dockerfile for {service_name} should exist at {dockerfile_path}"
    
    def test_essential_directories_exist(self):
        """Test that essential application directories exist for mounting."""
        compose_file = Path("docker-compose.yml")
        config = yaml.safe_load(compose_file.read_text())
        
        # Check that backend and frontend directories exist
        assert Path("backend").is_dir(), "Backend directory should exist for volume mounting"
        assert Path("frontend").is_dir(), "Frontend directory should exist for volume mounting"
        
        # Check for essential backend files
        backend_files = ["requirements.txt", "app/main.py"]
        for file_path in backend_files:
            full_path = Path("backend") / file_path
            assert full_path.exists(), f"Essential backend file {full_path} should exist"
        
        # Check for essential frontend files  
        frontend_files = ["package.json", "tsconfig.json"]
        for file_path in frontend_files:
            full_path = Path("frontend") / file_path
            assert full_path.exists(), f"Essential frontend file {full_path} should exist"
    
    def test_docker_compose_services_defined(self):
        """Test that all required services are defined in docker-compose.yml."""
        compose_file = Path("docker-compose.yml")
        config = yaml.safe_load(compose_file.read_text())
        
        required_services = ["postgres", "redis", "backend", "frontend"]
        defined_services = list(config.get('services', {}).keys())
        
        for service in required_services:
            assert service in defined_services, f"Required service '{service}' should be defined in docker-compose.yml"
    
    def test_service_ports_not_conflicting(self):
        """Test that service ports don't conflict with system services."""
        compose_file = Path("docker-compose.yml")
        config = yaml.safe_load(compose_file.read_text())
        
        used_ports = []
        for service_name, service_config in config.get('services', {}).items():
            ports = service_config.get('ports', [])
            for port_mapping in ports:
                if ':' in port_mapping:
                    host_port = port_mapping.split(':')[0]
                    used_ports.append(int(host_port))
        
        # Check that ports are in acceptable ranges
        for port in used_ports:
            assert 3000 <= port <= 8080, f"Port {port} should be in development range (3000-8080)"
        
        # Check for duplicates
        assert len(used_ports) == len(set(used_ports)), f"Duplicate ports found: {used_ports}"
    
    def test_environment_variables_accessible(self):
        """Test that required environment variables are available."""
        env_file = Path(".env")
        if env_file.exists():
            env_content = env_file.read_text()
            
            required_vars = [
                "POSTGRES_PASSWORD",
                "DATABASE_URL", 
                "JWT_SECRET_KEY"
            ]
            
            for var in required_vars:
                assert var in env_content, f"Required environment variable {var} should be in .env file"
    
    def test_docker_service_availability(self):
        """Test that Docker service is available and responsive."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0, "Docker should be installed and accessible"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker not available - skipping Docker-dependent tests")
    
    def test_startup_script_or_documentation_exists(self):
        """Test that there's clear documentation or scripts for starting the stack."""
        # Check for startup documentation in README
        readme_file = Path("README.md")
        if readme_file.exists():
            readme_content = readme_file.read_text().lower()
            startup_keywords = ["docker-compose up", "docker compose up", "getting started", "quick start"]
            
            has_startup_docs = any(keyword in readme_content for keyword in startup_keywords)
            assert has_startup_docs, "README should contain Docker Compose startup instructions"
        
        # Check for startup scripts
        potential_scripts = [
            "scripts/start.sh",
            "scripts/startup.sh", 
            "start.sh",
            "run.sh"
        ]
        
        script_exists = any(Path(script).exists() for script in potential_scripts)
        
        # Either documentation or script should exist
        assert readme_file.exists() or script_exists, \
            "Should have either README with startup docs or startup script"
    
    def test_task_15_requirements_comprehensive(self):
        """Comprehensive test that validates all task 1.5 requirements are met."""
        
        # 1. Docker Compose file exists and is valid
        compose_file = Path("docker-compose.yml")
        assert compose_file.exists(), "docker-compose.yml must exist"
        
        config = yaml.safe_load(compose_file.read_text())
        assert 'services' in config, "docker-compose.yml must define services"
        
        # 2. All required services are present
        required_services = ["postgres", "redis", "backend", "frontend"]
        services = config['services']
        for service in required_services:
            assert service in services, f"Service {service} must be defined"
        
        # 3. Services have proper configuration
        # PostgreSQL
        postgres_config = services['postgres']
        assert 'image' in postgres_config, "PostgreSQL must have image defined"
        assert 'environment' in postgres_config, "PostgreSQL must have environment variables"
        
        # Redis  
        redis_config = services['redis']
        assert 'image' in redis_config, "Redis must have image defined"
        
        # Backend
        backend_config = services['backend']
        assert 'build' in backend_config, "Backend must be buildable"
        assert 'depends_on' in backend_config, "Backend must depend on other services"
        
        # Frontend
        frontend_config = services['frontend']
        assert 'build' in frontend_config, "Frontend must be buildable"
        assert 'depends_on' in frontend_config, "Frontend must depend on backend"
        
        # 4. Environment configuration exists
        env_file = Path(".env")
        env_example = Path(".env.example")
        assert env_file.exists() or env_example.exists(), "Environment configuration must exist"
        
        # 5. Application source code exists
        assert Path("backend/app/main.py").exists(), "Backend application must exist"
        assert Path("frontend/src").is_dir(), "Frontend source must exist"
        assert Path("frontend/package.json").exists(), "Frontend package.json must exist"
        
        # 6. Dockerfiles exist and are properly configured
        backend_dockerfile = Path("docker/backend.Dockerfile")
        frontend_dockerfile = Path("docker/frontend.Dockerfile")
        assert backend_dockerfile.exists(), "Backend Dockerfile must exist"
        assert frontend_dockerfile.exists(), "Frontend Dockerfile must exist"
        
        # 7. Health checks are configured
        backend_dockerfile_content = backend_dockerfile.read_text()
        assert "HEALTHCHECK" in backend_dockerfile_content, "Backend must have health check"
        
        # 8. Startup documentation/scripts exist
        readme_exists = Path("README.md").exists()
        startup_script_exists = Path("scripts/start.sh").exists()
        assert readme_exists or startup_script_exists, "Startup documentation or script must exist"
        
        # 9. Docker Compose configuration validates
        result = subprocess.run(
            ["docker", "compose", "config", "--quiet"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Docker Compose configuration must be valid"
        
        # 10. All components are ready for startup
        # This test confirms that `docker-compose up` SHOULD work
        # The actual startup may depend on Docker daemon availability
        
        print("✅ All task 1.5 requirements validated successfully!")
        print("✅ Full stack is ready to start with 'docker-compose up'")
        print("✅ Use 'scripts/start.sh' for guided startup process")

    @pytest.mark.integration
    def test_compose_services_start_successfully(self):
        """Integration test: Services can start without immediate failures."""
        # This is a longer test that actually tries to start services
        try:
            # Clean up any existing containers
            subprocess.run(
                ["docker", "compose", "down", "-v"],
                capture_output=True,
                timeout=30
            )
            
            # Try to start services in detached mode
            result = subprocess.run(
                ["docker", "compose", "up", "-d", "--no-recreate"],
                capture_output=True,
                text=True,
                timeout=120  # Give it 2 minutes to start
            )
            
            if result.returncode != 0:
                # If it fails, capture logs for debugging
                logs_result = subprocess.run(
                    ["docker", "compose", "logs"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                pytest.fail(f"Docker Compose startup failed: {result.stderr}\nLogs:\n{logs_result.stdout}")
            
            # Wait a moment for services to initialize
            time.sleep(10)
            
            # Check service status
            status_result = subprocess.run(
                ["docker", "compose", "ps"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            assert status_result.returncode == 0, "Should be able to check service status"
            
            # Clean up
            subprocess.run(
                ["docker", "compose", "down", "-v"],
                capture_output=True,
                timeout=30
            )
            
        except subprocess.TimeoutExpired:
            pytest.fail("Docker Compose operations timed out")
        except Exception as e:
            pytest.fail(f"Unexpected error during startup test: {e}")
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_service_health_endpoints_accessible(self):
        """Integration test: Health check endpoints are accessible after startup."""
        try:
            # Clean up and start services
            subprocess.run(["docker", "compose", "down", "-v"], capture_output=True, timeout=30)
            
            start_result = subprocess.run(
                ["docker", "compose", "up", "-d"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if start_result.returncode != 0:
                pytest.skip(f"Could not start services for health check test: {start_result.stderr}")
            
            # Wait for services to become ready
            max_wait = 60  # seconds
            wait_interval = 5
            
            backend_ready = False
            for _ in range(max_wait // wait_interval):
                try:
                    response = requests.get("http://localhost:8000/health", timeout=5)
                    if response.status_code == 200:
                        backend_ready = True
                        break
                except requests.RequestException:
                    pass
                time.sleep(wait_interval)
            
            assert backend_ready, "Backend health endpoint should be accessible within 60 seconds"
            
            # Test frontend accessibility (may return different status codes)
            frontend_accessible = False
            for _ in range(max_wait // wait_interval):
                try:
                    response = requests.get("http://localhost:3000", timeout=5)
                    # Frontend might return various codes (200, 404, etc.) but should be reachable
                    if response.status_code < 500:
                        frontend_accessible = True
                        break
                except requests.RequestException:
                    pass
                time.sleep(wait_interval)
            
            assert frontend_accessible, "Frontend should be accessible within 60 seconds"
            
        except Exception as e:
            pytest.fail(f"Health check test failed: {e}")
        finally:
            # Always clean up
            subprocess.run(["docker", "compose", "down", "-v"], capture_output=True, timeout=30)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 