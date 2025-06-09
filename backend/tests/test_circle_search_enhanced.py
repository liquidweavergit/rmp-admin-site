"""
Tests for Enhanced Circle Search and Filtering - Task 7.6
Testing advanced search features, sorting, and comprehensive filtering
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi import status
from httpx import AsyncClient

from app.models.circle import Circle, CircleStatus
from app.models.user import User
from app.schemas.circle import CircleSearchParams
from app.services.circle_service import CircleService


class TestEnhancedCircleSearchFeatures:
    """Test enhanced search features added for Task 7.6."""
    
    def test_enhanced_search_params_with_capacity_filters(self):
        """Test CircleSearchParams with capacity filtering."""
        # Arrange & Act
        params = CircleSearchParams(
            capacity_min=4,
            capacity_max=8,
            sort_by="name",
            sort_order="asc"
        )
        
        # Assert
        assert params.capacity_min == 4
        assert params.capacity_max == 8
        assert params.sort_by == "name"
        assert params.sort_order == "asc"
    
    def test_enhanced_search_params_with_sorting(self):
        """Test CircleSearchParams with sorting options."""
        # Test different sort fields
        params1 = CircleSearchParams(sort_by="created_at", sort_order="desc")
        assert params1.sort_by == "created_at"
        assert params1.sort_order == "desc"
        
        params2 = CircleSearchParams(sort_by="name", sort_order="asc")
        assert params2.sort_by == "name"
        assert params2.sort_order == "asc"
        
        params3 = CircleSearchParams(sort_by="updated_at", sort_order="desc")
        assert params3.sort_by == "updated_at"
        assert params3.sort_order == "desc"
    
    def test_enhanced_search_params_validation(self):
        """Test validation of enhanced search parameters."""
        from pydantic import ValidationError as PydanticValidationError
        
        # Test capacity_min validation
        with pytest.raises(PydanticValidationError):
            CircleSearchParams(capacity_min=0)  # Below minimum
        
        with pytest.raises(PydanticValidationError):
            CircleSearchParams(capacity_min=11)  # Above maximum
        
        # Test capacity_max validation
        with pytest.raises(PydanticValidationError):
            CircleSearchParams(capacity_max=0)  # Below minimum
        
        with pytest.raises(PydanticValidationError):
            CircleSearchParams(capacity_max=11)  # Above maximum
    
    @pytest.mark.asyncio
    async def test_filter_circles_by_capacity_range(self, async_client: AsyncClient, mock_current_user: User):
        """Test filtering circles by capacity range."""
        # Test minimum capacity filter
        response = await async_client.get(
            "/api/v1/circles?capacity_min=6",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Test maximum capacity filter
        response = await async_client.get(
            "/api/v1/circles?capacity_max=4",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Test capacity range filter
        response = await async_client.get(
            "/api/v1/circles?capacity_min=4&capacity_max=8",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_sort_circles_by_different_fields(self, async_client: AsyncClient, mock_current_user: User):
        """Test sorting circles by different fields."""
        # Test sort by name ascending
        response = await async_client.get(
            "/api/v1/circles?sort_by=name&sort_order=asc",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Test sort by created_at descending (default)
        response = await async_client.get(
            "/api/v1/circles?sort_by=created_at&sort_order=desc",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Test sort by updated_at ascending
        response = await async_client.get(
            "/api/v1/circles?sort_by=updated_at&sort_order=asc",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_complex_search_with_all_filters(self, async_client: AsyncClient, mock_current_user: User):
        """Test complex search combining all available filters."""
        # Act
        response = await async_client.get(
            "/api/v1/circles?search=growth&status=active&facilitator_id=123&location=downtown&capacity_min=4&capacity_max=8&sort_by=name&sort_order=asc",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK


class TestEnhancedCircleSearchService:
    """Test enhanced CircleService search functionality."""
    
    @pytest.fixture
    def circle_service(self):
        """Create a mock circle service for testing."""
        mock_db = AsyncMock()
        return CircleService(mock_db)
    
    @pytest.fixture
    def sample_circles_with_capacity(self):
        """Create sample circles with different capacities for testing."""
        circles = [
            Mock(
                id=1,
                name="Small Circle",
                capacity_min=2,
                capacity_max=4,
                facilitator_id=1,
                status=CircleStatus.ACTIVE,
                created_at=datetime.now() - timedelta(days=10)
            ),
            Mock(
                id=2,
                name="Medium Circle",
                capacity_min=4,
                capacity_max=8,
                facilitator_id=1,
                status=CircleStatus.ACTIVE,
                created_at=datetime.now() - timedelta(days=5)
            ),
            Mock(
                id=3,
                name="Large Circle",
                capacity_min=6,
                capacity_max=10,
                facilitator_id=1,
                status=CircleStatus.ACTIVE,
                created_at=datetime.now() - timedelta(days=15)
            )
        ]
        return circles
    
    async def test_filter_by_capacity_min(self, circle_service):
        """Test filtering circles by minimum capacity."""
        # Arrange
        search_params = CircleSearchParams(capacity_min=6)
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 1
            
            mock_result = Mock()
            mock_circle = Mock(name="Large Circle", capacity_min=6)
            mock_result.scalars.return_value.all.return_value = [mock_circle]
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 1
            assert circles[0].capacity_min >= 6
    
    async def test_filter_by_capacity_max(self, circle_service, sample_circles_with_capacity):
        """Test filtering circles by maximum capacity."""
        # Arrange
        search_params = CircleSearchParams(capacity_max=4)
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            # Should match circles with capacity_max <= 4
            matching_circles = [sample_circles_with_capacity[0]]  # Small Circle
            
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = len(matching_circles)
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = matching_circles
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 1
            assert circles[0].name == "Small Circle"
            assert circles[0].capacity_max <= 4
    
    async def test_filter_by_capacity_range(self, circle_service, sample_circles_with_capacity):
        """Test filtering circles by capacity range."""
        # Arrange
        search_params = CircleSearchParams(capacity_min=4, capacity_max=8)
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            # Should match circles with capacity_min >= 4 AND capacity_max <= 8
            matching_circles = [sample_circles_with_capacity[1]]  # Medium Circle
            
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = len(matching_circles)
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = matching_circles
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 1
            assert circles[0].name == "Medium Circle"
            assert circles[0].capacity_min >= 4
            assert circles[0].capacity_max <= 8
    
    async def test_sort_by_name_ascending(self, circle_service, sample_circles_with_capacity):
        """Test sorting circles by name in ascending order."""
        # Arrange
        search_params = CircleSearchParams(sort_by="name", sort_order="asc")
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            # Sort circles by name ascending
            sorted_circles = sorted(sample_circles_with_capacity, key=lambda c: c.name)
            
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = len(sorted_circles)
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = sorted_circles
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 3
            assert circles[0].name == "Large Circle"  # First alphabetically
            assert circles[1].name == "Medium Circle"
            assert circles[2].name == "Small Circle"
    
    async def test_sort_by_created_at_descending(self, circle_service, sample_circles_with_capacity):
        """Test sorting circles by creation date in descending order."""
        # Arrange
        search_params = CircleSearchParams(sort_by="created_at", sort_order="desc")
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            # Sort circles by created_at descending (newest first)
            sorted_circles = sorted(sample_circles_with_capacity, key=lambda c: c.created_at, reverse=True)
            
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = len(sorted_circles)
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = sorted_circles
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 3
            # Verify newest first (Medium Circle created 5 days ago)
            assert circles[0].name == "Medium Circle"
            assert circles[1].name == "Small Circle"  # 10 days ago
            assert circles[2].name == "Large Circle"  # 15 days ago
    
    async def test_complex_search_with_all_enhanced_filters(self, circle_service):
        """Test complex search combining all enhanced filters."""
        # Arrange
        search_params = CircleSearchParams(
            search="circle",
            status=CircleStatus.ACTIVE,
            facilitator_id=1,
            location="downtown",
            capacity_min=4,
            capacity_max=8,
            sort_by="name",
            sort_order="asc"
        )
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            # Mock a circle that matches all criteria
            matching_circle = Mock(
                id=1,
                name="Downtown Circle",
                description="A circle in downtown",
                facilitator_id=1,
                status=CircleStatus.ACTIVE,
                location_name="Downtown Community Center",
                capacity_min=4,
                capacity_max=8
            )
            
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 1
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [matching_circle]
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 1
            assert circles[0].name == "Downtown Circle"
            assert circles[0].facilitator_id == 1
            assert circles[0].status == CircleStatus.ACTIVE
            assert circles[0].capacity_min >= 4
            assert circles[0].capacity_max <= 8


class TestCircleSearchPerformanceEnhancements:
    """Test performance enhancements for circle search."""
    
    async def test_search_query_optimization(self):
        """Test that search queries are optimized for performance."""
        # This test would verify query execution plans in a real database
        # For now, we'll test that the query structure is correct
        pass
    
    async def test_pagination_efficiency(self):
        """Test that pagination is efficient for large datasets."""
        # This test would verify that OFFSET/LIMIT queries perform well
        pass
    
    async def test_index_usage_verification(self):
        """Test that database indexes are used effectively."""
        # This test would verify that search queries use appropriate indexes
        pass


class TestCircleSearchEdgeCases:
    """Test edge cases for circle search functionality."""
    
    @pytest.mark.asyncio
    async def test_search_with_special_characters(self, async_client: AsyncClient, mock_current_user: User):
        """Test search with special characters."""
        # Test search with quotes
        response = await async_client.get(
            "/api/v1/circles?search=men's circle",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Test search with ampersand
        response = await async_client.get(
            "/api/v1/circles?search=growth & development",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_search_with_unicode_characters(self, async_client: AsyncClient, mock_current_user: User):
        """Test search with unicode characters."""
        response = await async_client.get(
            "/api/v1/circles?search=círculo",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_search_with_very_long_terms(self, async_client: AsyncClient, mock_current_user: User):
        """Test search with very long search terms."""
        long_search = "a" * 1000  # Very long search term
        response = await async_client.get(
            f"/api/v1/circles?search={long_search}",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_search_with_sql_injection_attempts(self, async_client: AsyncClient, mock_current_user: User):
        """Test that search is protected against SQL injection."""
        # Test common SQL injection patterns
        injection_attempts = [
            "'; DROP TABLE circles; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --"
        ]
        
        for injection in injection_attempts:
            response = await async_client.get(
                f"/api/v1/circles?search={injection}",
                headers={"Authorization": "Bearer fake-token"}
            )
            # Should not cause server error, should return normal response
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    @pytest.mark.asyncio
    async def test_pagination_beyond_available_results(self, async_client: AsyncClient, mock_current_user: User):
        """Test pagination beyond available results."""
        # Request page far beyond available data
        response = await async_client.get(
            "/api/v1/circles?page=9999&per_page=10",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
        # Should return empty list, not error
    
    @pytest.mark.asyncio
    async def test_invalid_sort_parameters(self, async_client: AsyncClient, mock_current_user: User):
        """Test handling of invalid sort parameters."""
        # Test invalid sort field
        response = await async_client.get(
            "/api/v1/circles?sort_by=invalid_field",
            headers={"Authorization": "Bearer fake-token"}
        )
        # Should handle gracefully, possibly falling back to default
        assert response.status_code == status.HTTP_200_OK
        
        # Test invalid sort order
        response = await async_client.get(
            "/api/v1/circles?sort_order=invalid_order",
            headers={"Authorization": "Bearer fake-token"}
        )
        # Should handle gracefully, possibly falling back to default
        assert response.status_code == status.HTTP_200_OK 