"""Tests for the chat API endpoints — OpenAI calls are mocked."""

import json
import pytest
from unittest.mock import patch, MagicMock


MOCK_RESPONSE = "Annual leave is 20 days per year as per company policy."


def _patch_ai_service(response_text: str = MOCK_RESPONSE):
    """Return a context manager that patches get_ai_service to return a mock."""
    mock_service = MagicMock()
    mock_service.generate_response.return_value = response_text
    mock_service.stream_response.return_value = iter(response_text.split())
    return patch("app.routes.chat.get_ai_service", return_value=mock_service)


class TestChatEndpoint:
    def test_chat_returns_response(self, client, db):
        """POST /api/chat with a valid message returns a response."""
        with _patch_ai_service():
            response = client.post(
                "/api/chat",
                data=json.dumps({"message": "How many days of annual leave do I get?"}),
                content_type="application/json",
            )
        assert response.status_code == 200
        data = response.get_json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    def test_chat_empty_message_returns_400(self, client, db):
        """POST /api/chat with an empty message returns 400."""
        response = client.post(
            "/api/chat",
            data=json.dumps({"message": ""}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_chat_missing_message_returns_400(self, client, db):
        """POST /api/chat without a message key returns 400."""
        response = client.post(
            "/api/chat",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_chat_whitespace_only_message_returns_400(self, client, db):
        """POST /api/chat with whitespace-only message returns 400."""
        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "   "}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_chat_with_employee_id(self, client, db, sample_employee):
        """POST /api/chat with an employee_id attaches context."""
        with _patch_ai_service() as mock_patch:
            response = client.post(
                "/api/chat",
                data=json.dumps({
                    "message": "What leave do I have?",
                    "employee_id": sample_employee.id,
                }),
                content_type="application/json",
            )
        assert response.status_code == 200
        data = response.get_json()
        assert "response" in data

    def test_chat_with_nonexistent_employee_id(self, client, db):
        """POST /api/chat with a nonexistent employee_id still returns 200 (no context)."""
        with _patch_ai_service():
            response = client.post(
                "/api/chat",
                data=json.dumps({
                    "message": "What are the expense limits?",
                    "employee_id": 99999,
                }),
                content_type="application/json",
            )
        assert response.status_code == 200

    def test_chat_ai_service_error_returns_500(self, client, db):
        """POST /api/chat returns 500 when the AI service raises an exception."""
        mock_service = MagicMock()
        mock_service.generate_response.side_effect = RuntimeError("OpenAI is down")
        with patch("app.routes.chat.get_ai_service", return_value=mock_service):
            response = client.post(
                "/api/chat",
                data=json.dumps({"message": "Hello"}),
                content_type="application/json",
            )
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data


class TestChatStreamEndpoint:
    def test_chat_stream_returns_event_stream(self, client, db):
        """POST /api/chat/stream returns text/event-stream content type."""
        with _patch_ai_service():
            response = client.post(
                "/api/chat/stream",
                data=json.dumps({"message": "Tell me about leave policy"}),
                content_type="application/json",
            )
        assert response.status_code == 200
        assert "text/event-stream" in response.content_type

    def test_chat_stream_empty_message_returns_400(self, client, db):
        """POST /api/chat/stream with empty message returns 400."""
        response = client.post(
            "/api/chat/stream",
            data=json.dumps({"message": ""}),
            content_type="application/json",
        )
        assert response.status_code == 400
