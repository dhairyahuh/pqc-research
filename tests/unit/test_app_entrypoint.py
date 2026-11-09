"""Unit tests verifying FastAPI application entry points and ASGI export compatibility."""

import unittest
from fastapi import FastAPI


class TestAppEntrypoint(unittest.TestCase):
    """Test suite validating ASGI module entry points and application factory consistency."""

    def test_dashboard_app_singleton(self):
        """Verifies that astra_sec.dashboard.app:app exists and is a FastAPI instance."""
        from astra_sec.dashboard.app import app, create_app
        self.assertIsInstance(app, FastAPI)
        self.assertTrue(callable(create_app))

    def test_app_module_lazy_export(self):
        """Verifies that astra_sec.app exports 'app' and 'create_app' without duplicating instances."""
        from astra_sec import app as cli_app_module
        from astra_sec.dashboard.app import app as canonical_app

        exported_app = getattr(cli_app_module, "app")
        self.assertIs(exported_app, canonical_app, "astra_sec.app:app must reference the canonical FastAPI instance")

        exported_factory = getattr(cli_app_module, "create_app")
        self.assertTrue(callable(exported_factory))

    def test_routes_and_websocket_registered(self):
        """Verifies that /api/health and /ws/live are properly registered on the application."""
        from astra_sec.dashboard.app import app

        route_paths = [getattr(r, "path", None) for r in app.routes]
        self.assertIn("/api/health", route_paths)
        self.assertIn("/ws/live", route_paths)
        self.assertIn("/api/admin/dispatch", route_paths)
        self.assertIn("/api/orbital/satellites", route_paths)


if __name__ == "__main__":
    unittest.main()
