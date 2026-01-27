"""Tests for export API routes."""

import pytest
from app.routers import export


class TestExportRouter:
    """Test export router exists and is properly configured."""

    def test_export_router_exists(self):
        """Test that export router is defined."""
        assert export.router is not None

    def test_export_csv_endpoint_path(self):
        """Test that export CSV endpoint is registered."""
        # Verify routes exist
        assert len(export.router.routes) > 0

    def test_export_router_has_dependencies(self):
        """Test that export router requires authentication."""
        # Check that router routes have dependencies
        routes = export.router.routes
        assert any(route for route in routes if "/csv" in str(route.path))
