"""
Tests for AI Assistant & Document OCR APIs.

Run with:
    python -m pytest tests/test_ai_ocr.py -v
"""
import io
import uuid
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

PREFIX = settings.API_V1_STR
client = TestClient(app)


def get_auth_headers() -> dict:
    """Register/login an inventory manager and return Bearer auth headers."""
    uid = uuid.uuid4().hex[:6]
    creds = {
        "email": f"ai_tester_{uid}@example.com",
        "password": "TestPassword123!",
        "name": f"AI Tester {uid}",
        "role": "inventory_manager",
    }
    client.post(f"{PREFIX}/auth/signup", json=creds)
    resp = client.post(
        f"{PREFIX}/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAIAssistantAPI:

    @pytest.fixture(autouse=True)
    def setup_headers(self):
        self.headers = get_auth_headers()

    def test_ai_chat_query_rack_b(self):
        """Test POST /ai/chat matching prompt example: 'How much steel is in Rack B?'"""
        resp = client.post(
            f"{PREFIX}/ai/chat",
            json={"query": "How much steel is in Rack B?"},
            headers=self.headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0

    def test_ai_chat_query_low_stock(self):
        resp = client.post(
            f"{PREFIX}/ai/chat",
            json={"query": "What items are low on stock?"},
            headers=self.headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data

    def test_ai_chat_requires_auth(self):
        resp = client.post(
            f"{PREFIX}/ai/chat",
            json={"query": "How much steel is in Rack B?"},
        )
        assert resp.status_code in (401, 403)


class TestDocumentOCRAPI:

    @pytest.fixture(autouse=True)
    def setup_headers(self):
        self.headers = get_auth_headers()

    def test_ocr_scan_document(self):
        """Test POST /ocr/scan with packing slip file upload."""
        sample_slip = (
            "Supplier: Global Industrial Supply\n"
            "Invoice Ref: INV-2026-99\n"
            "Items:\n"
            "Steel Rods - 50 units\n"
            "Industrial Bolts - 200 units\n"
        )
        files = {"file": ("packing_slip.txt", io.BytesIO(sample_slip.encode("utf-8")), "text/plain")}

        resp = client.post(
            f"{PREFIX}/ocr/scan",
            files=files,
            headers=self.headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert len(data["items"]) >= 1

    def test_ocr_create_draft_receipt(self):
        """Test POST /ocr/receipt auto-creating draft receipt from document scan."""
        sample_slip = (
            "Supplier: Acme Steel Corp\n"
            "Steel Rods - 42 units\n"
        )
        files = {"file": ("invoice.txt", io.BytesIO(sample_slip.encode("utf-8")), "text/plain")}

        resp = client.post(
            f"{PREFIX}/ocr/receipt",
            files=files,
            headers=self.headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "receipt_id" in data
        assert "receipt_number" in data
        assert data["status"] == "Draft"
