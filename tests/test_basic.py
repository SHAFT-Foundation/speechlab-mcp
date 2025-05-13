#!/usr/bin/env python3
"""
Basic tests for the Speechlab MCP package.
"""

import unittest
from speechlab_mcp import __version__
from speechlab_mcp.model import McpProject, McpDubProject, DubMedia


class TestBasic(unittest.TestCase):
    def test_version(self):
        """Test that the version is a string."""
        self.assertIsInstance(__version__, str)
    
    def test_models(self):
        """Test that the models can be instantiated correctly."""
        # Test McpProject
        project = McpProject(
            id="123",
            name="Test Project",
            status="created",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z"
        )
        self.assertEqual(project.id, "123")
        self.assertEqual(project.name, "Test Project")
        
        # Test McpDubProject
        dub_project = McpDubProject(
            id="456",
            name="Test Dub Project",
            status="created",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            source_language="en",
            target_language="es"
        )
        self.assertEqual(dub_project.id, "456")
        self.assertEqual(dub_project.source_language, "en")
        self.assertEqual(dub_project.target_language, "es")
        
        # Test DubMedia
        media = DubMedia(
            id="789",
            uri="https://example.com/media/789",
            category="VIDEO",
            content_type="video/mp4",
            format="mp4",
            operation_type="OUTPUT"
        )
        self.assertEqual(media.id, "789")
        self.assertEqual(media.operation_type, "OUTPUT")


if __name__ == "__main__":
    unittest.main() 