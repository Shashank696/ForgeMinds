"""
Integration tests for ForgeMinds API endpoints.
Assigned to: SP (integration testing)
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self):
        """Test GET /api/health returns 200."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestRootEndpoint:
    """Tests for the root API path."""

    def test_root(self):
        """Test GET / returns app metadata."""
        response = client.get("/")
        assert response.status_code == 200
        assert "version" in response.json()
        assert "title" in response.json()


class TestAuthEndpoints:
    """Tests for authentication endpoints (stubs verification)."""

    def test_register_user_validation(self):
        """Test POST /api/auth/register input validation."""
        response = client.post("/api/auth/register", json={})
        assert response.status_code == 422  # validation error

    def test_login_validation(self):
        """Test POST /api/auth/login input validation."""
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 422  # validation error

    def test_get_me_unauthenticated(self):
        """Test GET /api/auth/me without token returns 401."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401


class TestDocumentEndpoints:
    """Tests for document endpoints (stubs verification)."""

    def test_list_documents_unauthenticated(self):
        """Test GET /api/documents without token returns 401."""
        response = client.get("/api/documents")
        assert response.status_code == 401


class TestSearchEndpoint:
    """Tests for search endpoint (stubs verification)."""

    def test_search_unauthenticated(self):
        """Test POST /api/search without token returns 401."""
        response = client.post("/api/search", json={"query": "test"})
        assert response.status_code == 401


class TestChatEndpoint:
    """Tests for chat endpoint (stubs verification)."""

    def test_send_message_unauthenticated(self):
        """Test POST /api/chat without token returns 401."""
        response = client.post("/api/chat", json={"message": "hello"})
        assert response.status_code == 401
