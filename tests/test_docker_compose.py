"""
Test suite for docker-compose.yml file validation
Tests that all required services are configured correctly as specified in task 1.3
"""
import os
import yaml
import pytest
from pathlib import Path


class TestDockerCompose:
    """Test suite for docker-compose.yml validation"""
    
    @pytest.fixture
    def compose_file_path(self):
        """Fixture to get the path to docker-compose.yml file"""
        project_root = Path(__file__).parent.parent
        return project_root / "docker-compose.yml"
    
    @pytest.fixture
    def compose_content(self, compose_file_path):
        """Fixture to read and parse docker-compose.yml file content"""
        if not compose_file_path.exists():
            pytest.fail(f"docker-compose.yml file not found at {compose_file_path}")
        
        with open(compose_file_path, 'r') as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in docker-compose.yml: {e}")
    
    def test_compose_file_exists(self, compose_file_path):
        """Test that docker-compose.yml file exists in project root"""
        assert compose_file_path.exists(), f"docker-compose.yml file should exist at {compose_file_path}"
        assert compose_file_path.is_file(), f"docker-compose.yml should be a file, not a directory"
    
    def test_compose_version(self, compose_content):
        """Test that docker-compose.yml uses proper version"""
        assert "version" in compose_content, "docker-compose.yml must specify a version"
        version = compose_content["version"]
        # Accept version 3.x format (string or float)
        assert str(version).startswith("3"), f"Docker Compose version should be 3.x, got {version}"
    
    def test_required_services_present(self, compose_content):
        """Test that all required services from task 1.3 are present"""
        assert "services" in compose_content, "docker-compose.yml must have services section"
        
        services = compose_content["services"]
        required_services = ["postgres", "redis", "backend", "frontend"]
        
        for service in required_services:
            # Check for exact name or variations (postgres-main, etc.)
            postgres_variants = ["postgres", "postgres-main", "database", "db"]
            if service == "postgres":
                found = any(variant in services for variant in postgres_variants)
                assert found, f"PostgreSQL service not found. Expected one of: {postgres_variants}"
            else:
                assert service in services, f"Required service '{service}' not found in docker-compose.yml"
    
    def test_postgresql_service_configuration(self, compose_content):
        """Test PostgreSQL service configuration"""
        services = compose_content["services"]
        
        # Find PostgreSQL service (could be 'postgres', 'postgres-main', etc.)
        postgres_service = None
        postgres_variants = ["postgres", "postgres-main", "database", "db"]
        
        for variant in postgres_variants:
            if variant in services:
                postgres_service = services[variant]
                postgres_name = variant
                break
        
        assert postgres_service is not None, f"PostgreSQL service not found among {postgres_variants}"
        
        # Check image
        assert "image" in postgres_service, f"PostgreSQL service '{postgres_name}' must specify an image"
        image = postgres_service["image"]
        assert "postgres" in image.lower(), f"PostgreSQL service should use postgres image, got {image}"
        
        # Check environment variables
        assert "environment" in postgres_service, f"PostgreSQL service '{postgres_name}' must have environment variables"
        env = postgres_service["environment"]
        
        # Required PostgreSQL environment variables
        required_env_vars = ["POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
        for var in required_env_vars:
            # Check if variable exists in environment (as dict or list)
            if isinstance(env, dict):
                assert var in env, f"PostgreSQL service missing required environment variable: {var}"
            elif isinstance(env, list):
                env_names = [item.split('=')[0] if '=' in item else item for item in env]
                assert var in env_names, f"PostgreSQL service missing required environment variable: {var}"
        
        # Check ports
        if "ports" in postgres_service:
            ports = postgres_service["ports"]
            # Should expose PostgreSQL port (5432)
            port_found = any("5432" in str(port) for port in ports)
            assert port_found, "PostgreSQL service should expose port 5432"
    
    def test_redis_service_configuration(self, compose_content):
        """Test Redis service configuration"""
        services = compose_content["services"]
        assert "redis" in services, "Redis service not found"
        
        redis_service = services["redis"]
        
        # Check image
        assert "image" in redis_service, "Redis service must specify an image"
        image = redis_service["image"]
        assert "redis" in image.lower(), f"Redis service should use redis image, got {image}"
        
        # Check ports
        if "ports" in redis_service:
            ports = redis_service["ports"]
            # Should expose Redis port (6379)
            port_found = any("6379" in str(port) for port in ports)
            assert port_found, "Redis service should expose port 6379"
    
    def test_backend_service_configuration(self, compose_content):
        """Test backend service configuration"""
        services = compose_content["services"]
        assert "backend" in services, "Backend service not found"
        
        backend_service = services["backend"]
        
        # Check build configuration
        assert "build" in backend_service, "Backend service must have build configuration"
        build_config = backend_service["build"]
        
        if isinstance(build_config, dict):
            assert "dockerfile" in build_config, "Backend build must specify dockerfile"
            dockerfile = build_config["dockerfile"]
            assert "backend" in dockerfile.lower(), f"Backend should use backend Dockerfile, got {dockerfile}"
        elif isinstance(build_config, str):
            # Simple build path, should point to directory with Dockerfile
            assert build_config in [".", "./", "backend"], f"Backend build path should be valid, got {build_config}"
        
        # Check ports
        if "ports" in backend_service:
            ports = backend_service["ports"]
            # Should expose backend port (8000)
            port_found = any("8000" in str(port) for port in ports)
            assert port_found, "Backend service should expose port 8000"
        
        # Check dependencies
        if "depends_on" in backend_service:
            depends_on = backend_service["depends_on"]
            # Should depend on database and redis
            if isinstance(depends_on, list):
                deps_lower = [dep.lower() for dep in depends_on]
            elif isinstance(depends_on, dict):
                deps_lower = [dep.lower() for dep in depends_on.keys()]
            else:
                deps_lower = []
            
            postgres_dep = any("postgres" in dep or "db" in dep for dep in deps_lower)
            redis_dep = any("redis" in dep for dep in deps_lower)
            
            assert postgres_dep, "Backend should depend on PostgreSQL service"
            assert redis_dep, "Backend should depend on Redis service"
    
    def test_frontend_service_configuration(self, compose_content):
        """Test frontend service configuration"""
        services = compose_content["services"]
        assert "frontend" in services, "Frontend service not found"
        
        frontend_service = services["frontend"]
        
        # Check build configuration
        assert "build" in frontend_service, "Frontend service must have build configuration"
        build_config = frontend_service["build"]
        
        if isinstance(build_config, dict):
            assert "dockerfile" in build_config, "Frontend build must specify dockerfile"
            dockerfile = build_config["dockerfile"]
            assert "frontend" in dockerfile.lower(), f"Frontend should use frontend Dockerfile, got {dockerfile}"
        elif isinstance(build_config, str):
            # Simple build path, should point to directory with Dockerfile
            assert build_config in [".", "./", "frontend"], f"Frontend build path should be valid, got {build_config}"
        
        # Check ports
        if "ports" in frontend_service:
            ports = frontend_service["ports"]
            # Should expose frontend port (3000 or 80)
            port_found = any("3000" in str(port) or "80" in str(port) for port in ports)
            assert port_found, "Frontend service should expose port 3000 or 80"
        
        # Check dependencies (optional but recommended)
        if "depends_on" in frontend_service:
            depends_on = frontend_service["depends_on"]
            if isinstance(depends_on, list):
                deps_lower = [dep.lower() for dep in depends_on]
            elif isinstance(depends_on, dict):
                deps_lower = [dep.lower() for dep in depends_on.keys()]
            else:
                deps_lower = []
            
            backend_dep = any("backend" in dep for dep in deps_lower)
            assert backend_dep, "Frontend should depend on Backend service"
    
    def test_environment_variable_usage(self, compose_content):
        """Test that services use environment variables appropriately"""
        services = compose_content["services"]
        
        # Check that services use environment variables for configuration
        for service_name, service_config in services.items():
            if "environment" in service_config:
                env = service_config["environment"]
                
                # Convert to list format for easier checking
                env_vars = []
                if isinstance(env, dict):
                    env_vars = [f"{k}={v}" for k, v in env.items()]
                elif isinstance(env, list):
                    env_vars = env
                
                # Check for use of environment variables (${VAR} or ${VAR:-default})
                env_var_usage = any("${" in str(var) for var in env_vars)
                
                # At least some services should use environment variables
                if service_name in ["backend", "postgres", "postgres-main"]:
                    # These services should definitely use environment variables
                    if not env_var_usage:
                        # Check if they have hardcoded values that should be variables
                        sensitive_patterns = ["password", "secret", "key"]
                        has_sensitive = any(pattern in str(env_vars).lower() for pattern in sensitive_patterns)
                        if has_sensitive:
                            assert env_var_usage, f"Service {service_name} should use environment variables for sensitive configuration"
    
    def test_volumes_configuration(self, compose_content):
        """Test that persistent volumes are properly configured"""
        services = compose_content["services"]
        
        # Check PostgreSQL has persistent volume
        postgres_variants = ["postgres", "postgres-main", "database", "db"]
        postgres_service = None
        
        for variant in postgres_variants:
            if variant in services:
                postgres_service = services[variant]
                break
        
        if postgres_service and "volumes" in postgres_service:
            volumes = postgres_service["volumes"]
            # Should have PostgreSQL data volume
            data_volume_found = any("postgresql" in str(vol).lower() or "data" in str(vol).lower() for vol in volumes)
            assert data_volume_found, "PostgreSQL service should have persistent data volume"
        
        # Check if top-level volumes are defined when used
        if "volumes" in compose_content:
            volumes_section = compose_content["volumes"]
            assert isinstance(volumes_section, dict), "Volumes section should be a dictionary"
    
    def test_networks_configuration(self, compose_content):
        """Test network configuration (optional but good practice)"""
        # Networks are optional but if present should be properly configured
        if "networks" in compose_content:
            networks = compose_content["networks"]
            assert isinstance(networks, dict), "Networks section should be a dictionary"
            
            # If custom networks are defined, services should use them
            if networks:
                services = compose_content["services"]
                for service_name, service_config in services.items():
                    if "networks" in service_config:
                        service_networks = service_config["networks"]
                        # Service networks should reference defined networks
                        if isinstance(service_networks, list):
                            for network in service_networks:
                                assert network in networks, f"Service {service_name} references undefined network: {network}"
    
    def test_yaml_structure_validity(self, compose_file_path):
        """Test that the YAML structure is valid and well-formed"""
        with open(compose_file_path, 'r') as f:
            content = f.read()
        
        # Check for common YAML issues
        lines = content.split('\n')
        
        # Check indentation consistency
        indent_sizes = set()
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    indent_sizes.add(leading_spaces)
        
        # Should use consistent indentation (typically 2 or 4 spaces)
        if indent_sizes:
            # All indentations should be multiples of the smallest
            min_indent = min(indent_sizes)
            assert min_indent in [2, 4], f"Should use 2 or 4 space indentation, found minimum: {min_indent}"
            
            for indent in indent_sizes:
                assert indent % min_indent == 0, f"Inconsistent indentation found: {indent} (should be multiple of {min_indent})"
    
    def test_service_health_checks(self, compose_content):
        """Test that critical services have health checks (optional but recommended)"""
        services = compose_content["services"]
        
        # Critical services that should have health checks
        critical_services = ["backend", "postgres", "postgres-main", "redis"]
        
        for service_name in critical_services:
            if service_name in services:
                service = services[service_name]
                # Health check can be in service config or Dockerfile
                # This is optional but good practice
                if "healthcheck" in service:
                    healthcheck = service["healthcheck"]
                    assert "test" in healthcheck, f"Health check for {service_name} should specify test command" 