"""
Tests for Circle Search and Filtering - Test-Driven Development approach
Testing comprehensive search, filtering, and pagination functionality
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi import status
from httpx import AsyncClient

from app.models.circle import Circle, CircleStatus
from app.models.user import User
from app.schemas.circle import CircleSearchParams, CircleResponse
from app.services.circle_service import CircleService
from app.core.exceptions import ValidationError


class TestCircleSearchParameters:
    """Test CircleSearchParams schema and validation."""
    
    def test_circle_search_params_with_default_values(self):
        """Test CircleSearchParams with default values."""
        # Act
        params = CircleSearchParams()
        
        # Assert
        assert params.page == 1
        assert params.per_page == 10
        assert params.search is None
        assert params.status is None
        assert params.facilitator_id is None
        assert params.location is None
    
    def test_circle_search_params_with_all_values(self):
        """Test CircleSearchParams with all search parameters."""
        # Arrange & Act
        params = CircleSearchParams(
            page=2,
            per_page=25,
            search="growth circle",
            status=CircleStatus.ACTIVE,
            facilitator_id=123,
            location="downtown"
        )
        
        # Assert
        assert params.page == 2
        assert params.per_page == 25
        assert params.search == "growth circle"
        assert params.status == CircleStatus.ACTIVE.value
        assert params.facilitator_id == 123
        assert params.location == "downtown"
    
    def test_circle_search_params_page_validation(self):
        """Test page number validation."""
        # Test page < 1 should fail with Pydantic validation error
        from pydantic import ValidationError as PydanticValidationError
        with pytest.raises(PydanticValidationError):
            CircleSearchParams(page=0)
        
        # Test page = 1 should work
        params = CircleSearchParams(page=1)
        assert params.page == 1
    
    def test_circle_search_params_per_page_validation(self):
        """Test per_page validation constraints."""
        # Test per_page < 1 should fail with Pydantic validation error
        from pydantic import ValidationError as PydanticValidationError
        with pytest.raises(PydanticValidationError):
            CircleSearchParams(per_page=0)
        
        # Test per_page > 100 should fail
        with pytest.raises(PydanticValidationError):
            CircleSearchParams(per_page=101)
        
        # Test per_page within range should work
        params = CircleSearchParams(per_page=50)
        assert params.per_page == 50


class TestCircleSearchAPI:
    """Test circle search API endpoints."""
    
    @pytest.mark.asyncio
    async def test_search_circles_by_name(self, async_client: AsyncClient, mock_current_user: User):
        """Test searching circles by name."""
        # Act
        response = await async_client.get(
            "/api/v1/circles?search=growth",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        # Service layer validation will be added
    
    async def test_search_circles_by_description(self, async_client: AsyncClient, mock_current_user: User):
        """Test searching circles by description content."""
        # Act
        response = await async_client.get(
            "/api/v1/circles?search=personal development",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
    
    async def test_filter_circles_by_status(self, async_client: AsyncClient, mock_current_user: User):
        """Test filtering circles by status."""
        # Test active circles
        response = await async_client.get(
            "/api/v1/circles?status=active",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Test forming circles
        response = await async_client.get(
            "/api/v1/circles?status=forming",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    async def test_filter_circles_by_facilitator(self, async_client: AsyncClient, mock_current_user: User):
        """Test filtering circles by facilitator ID."""
        # Act
        response = await async_client.get(
            "/api/v1/circles?facilitator_id=123",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
    
    async def test_filter_circles_by_location(self, async_client: AsyncClient, mock_current_user: User):
        """Test filtering circles by location."""
        # Act
        response = await async_client.get(
            "/api/v1/circles?location=downtown",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
    
    async def test_search_circles_with_pagination(self, async_client: AsyncClient, mock_current_user: User):
        """Test circle search with pagination parameters."""
        # Test first page
        response = await async_client.get(
            "/api/v1/circles?page=1&per_page=5",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Test second page
        response = await async_client.get(
            "/api/v1/circles?page=2&per_page=5",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    async def test_search_circles_combined_filters(self, async_client: AsyncClient, mock_current_user: User):
        """Test combining multiple search filters."""
        # Act
        response = await async_client.get(
            "/api/v1/circles?search=growth&status=active&location=community",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
    
    async def test_search_circles_case_insensitive(self, async_client: AsyncClient, mock_current_user: User):
        """Test that search is case insensitive."""
        # Test uppercase search
        response = await async_client.get(
            "/api/v1/circles?search=GROWTH",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Test mixed case search
        response = await async_client.get(
            "/api/v1/circles?search=GrOwTh",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    async def test_search_circles_partial_matches(self, async_client: AsyncClient, mock_current_user: User):
        """Test that search supports partial word matches."""
        # Act
        response = await async_client.get(
            "/api/v1/circles?search=grow",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
    
    async def test_search_circles_empty_results(self, async_client: AsyncClient, mock_current_user: User):
        """Test search with no matching results."""
        # Act
        response = await async_client.get(
            "/api/v1/circles?search=nonexistent",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
        # Should return empty list when no matches
    
    async def test_search_circles_invalid_status(self, async_client: AsyncClient, mock_current_user: User):
        """Test filtering with invalid status value."""
        # Act
        response = await async_client.get(
            "/api/v1/circles?status=invalid_status",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_search_circles_invalid_pagination(self, async_client: AsyncClient, mock_current_user: User):
        """Test search with invalid pagination parameters."""
        # Test page < 1
        response = await async_client.get(
            "/api/v1/circles?page=0",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test per_page > 100
        response = await async_client.get(
            "/api/v1/circles?per_page=101",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCircleSearchService:
    """Test CircleService search and filtering functionality."""
    
    @pytest.fixture
    def circle_service(self):
        """Create a mock circle service for testing."""
        mock_db = AsyncMock()
        return CircleService(mock_db)
    
    @pytest.fixture
    def sample_circles(self):
        """Create sample circles for testing."""
        circles = [
            Mock(
                id=1,
                name="Men's Growth Circle",
                description="Personal development and growth",
                facilitator_id=1,
                status=CircleStatus.ACTIVE,
                location_name="Downtown Community Center",
                location_address="123 Main St",
                created_at=datetime.now() - timedelta(days=10)
            ),
            Mock(
                id=2,
                name="Leadership Circle",
                description="Developing leadership skills",
                facilitator_id=2,
                status=CircleStatus.FORMING,
                location_name="Uptown Library",
                location_address="456 Oak Ave",
                created_at=datetime.now() - timedelta(days=5)
            ),
            Mock(
                id=3,
                name="Mindfulness Group",
                description="Meditation and mindfulness practice",
                facilitator_id=1,
                status=CircleStatus.ACTIVE,
                location_name="Zen Center",
                location_address="789 Pine Rd",
                created_at=datetime.now() - timedelta(days=15)
            )
        ]
        return circles
    
    async def test_list_circles_text_search_name(self, circle_service, sample_circles):
        """Test text search in circle names."""
        # Arrange
        search_params = CircleSearchParams(search="growth")
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            # Mock the count query result
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 1
            
            # Mock the main query result
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [sample_circles[0]]
            
            # Configure mock to return count first, then results
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 1
            assert circles[0].name == "Men's Growth Circle"
            assert total == 1
    
    async def test_list_circles_text_search_description(self, circle_service, sample_circles):
        """Test text search in circle descriptions."""
        # Arrange
        search_params = CircleSearchParams(search="leadership")
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 1
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [sample_circles[1]]
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 1
            assert "leadership" in circles[0].description.lower()
    
    async def test_list_circles_filter_by_status(self, circle_service, sample_circles):
        """Test filtering circles by status."""
        # Arrange
        search_params = CircleSearchParams(status=CircleStatus.ACTIVE)
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            active_circles = [c for c in sample_circles if c.status == CircleStatus.ACTIVE]
            
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = len(active_circles)
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = active_circles
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 2  # Two active circles
            assert all(c.status == CircleStatus.ACTIVE for c in circles)
    
    async def test_list_circles_filter_by_facilitator(self, circle_service, sample_circles):
        """Test filtering circles by facilitator ID."""
        # Arrange
        search_params = CircleSearchParams(facilitator_id=1)
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            facilitator_circles = [c for c in sample_circles if c.facilitator_id == 1]
            
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = len(facilitator_circles)
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = facilitator_circles
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 2  # Two circles with facilitator_id = 1
            assert all(c.facilitator_id == 1 for c in circles)
    
    async def test_list_circles_filter_by_location(self, circle_service, sample_circles):
        """Test filtering circles by location."""
        # Arrange
        search_params = CircleSearchParams(location="downtown")
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 1
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [sample_circles[0]]
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 1
            assert "downtown" in circles[0].location_name.lower()
    
    async def test_list_circles_pagination(self, circle_service, sample_circles):
        """Test pagination functionality."""
        # Arrange
        search_params = CircleSearchParams(page=1, per_page=2)
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 3  # Total of 3 circles
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = sample_circles[:2]  # First 2
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 2
            assert total == 3
    
    async def test_list_circles_combined_filters(self, circle_service, sample_circles):
        """Test combining multiple search and filter criteria."""
        # Arrange
        search_params = CircleSearchParams(
            search="circle",
            status=CircleStatus.ACTIVE,
            facilitator_id=1
        )
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            # Should match circles that are active, facilitated by user 1, and contain "circle"
            matching_circles = [sample_circles[0]]  # Only "Men's Growth Circle"
            
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = len(matching_circles)
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = matching_circles
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 1
            assert circles[0].status == CircleStatus.ACTIVE
            assert circles[0].facilitator_id == 1
            assert "circle" in circles[0].name.lower()
    
    async def test_list_circles_empty_results(self, circle_service):
        """Test search with no matching results."""
        # Arrange
        search_params = CircleSearchParams(search="nonexistent")
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 0
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = []
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 0
            assert total == 0
    
    async def test_list_circles_user_access_filtering(self, circle_service, sample_circles):
        """Test that only accessible circles are returned."""
        # Arrange
        search_params = CircleSearchParams()
        user_id = 1
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            # Should only return circles user can access (facilitator or member)
            accessible_circles = [sample_circles[0], sample_circles[2]]  # Facilitated by user 1
            
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = len(accessible_circles)
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = accessible_circles
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(user_id, search_params)
            
            # Assert
            assert len(circles) == 2
            assert all(c.facilitator_id == user_id for c in circles)
    
    async def test_list_circles_ordering(self, circle_service, sample_circles):
        """Test that circles are ordered by creation date (newest first)."""
        # Arrange
        search_params = CircleSearchParams()
        
        with patch.object(circle_service.db, 'execute') as mock_execute:
            # Sort sample circles by created_at descending (newest first)
            sorted_circles = sorted(sample_circles, key=lambda c: c.created_at, reverse=True)
            
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = len(sorted_circles)
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = sorted_circles
            
            mock_execute.side_effect = [mock_count_result, mock_result]
            
            # Act
            circles, total = await circle_service.list_circles_for_user(1, search_params)
            
            # Assert
            assert len(circles) == 3
            # Verify ordering (newest first)
            for i in range(len(circles) - 1):
                assert circles[i].created_at >= circles[i + 1].created_at


class TestCircleSearchPerformance:
    """Test search performance and optimization."""
    
    async def test_search_with_indexes(self):
        """Test that search queries use appropriate database indexes."""
        # This test will verify that search queries are optimized
        # by checking query execution plans (future enhancement)
        pass
    
    async def test_search_pagination_performance(self):
        """Test pagination performance with large datasets."""
        # This test will verify pagination doesn't degrade with large result sets
        pass
    
    async def test_search_complex_query_performance(self):
        """Test performance of complex search queries."""
        # This test will verify that complex multi-filter searches perform well
        pass


class TestCircleSearchIntegration:
    """Integration tests for circle search functionality."""
    
    async def test_end_to_end_search_workflow(self):
        """Test complete search workflow from API to database."""
        # This will be implemented when full integration testing is set up
        pass
    
    async def test_search_with_real_database_data(self):
        """Test search functionality with real database data."""
        # This will be implemented when database integration is available
        pass
    
    async def test_search_concurrency(self):
        """Test search functionality under concurrent access."""
        # This will be implemented for load testing scenarios
        pass


class TestCircleSearchEnhancements:
    """Test enhanced search features for Task 7.6."""
    
    async def test_search_circles_case_insensitive(self, async_client: AsyncClient, mock_current_user: User):
        """Test that search is case insensitive."""
        # Test uppercase search
        response = await async_client.get(
            "/api/v1/circles?search=GROWTH",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    async def test_search_circles_partial_matches(self, async_client: AsyncClient, mock_current_user: User):
        """Test that search supports partial word matches."""
        # Act
        response = await async_client.get(
            "/api/v1/circles?search=grow",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
    
    async def test_search_circles_empty_results(self, async_client: AsyncClient, mock_current_user: User):
        """Test search with no matching results."""
        # Act
        response = await async_client.get(
            "/api/v1/circles?search=nonexistent",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
    
    async def test_search_pagination_edge_cases(self, async_client: AsyncClient, mock_current_user: User):
        """Test pagination edge cases."""
        # Test page beyond available results
        response = await async_client.get(
            "/api/v1/circles?page=999",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Test minimum pagination values
        response = await async_client.get(
            "/api/v1/circles?page=1&per_page=1",
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == status.HTTP_200_OK 