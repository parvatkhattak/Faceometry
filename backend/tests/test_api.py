"""API integration tests (httpx ASGI transport)."""

import io

import cv2
import numpy as np
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _png_bytes(img: np.ndarray, ext: str = ".png") -> bytes:
    ok, buf = cv2.imencode(ext, img)
    assert ok
    return buf.tobytes()


@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_health(client):
    async with client as c:
        r = await c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_invalid_file_type(client):
    async with client as c:
        r = await c.post("/api/analyze", files={"image": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_corrupt_image(client):
    async with client as c:
        r = await c.post("/api/analyze", files={"image": ("a.jpg", b"not-an-image", "image/jpeg")})
    assert r.status_code in (400, 422)


@pytest.mark.asyncio
async def test_no_face(client):
    rng = np.random.default_rng(0)
    img = rng.integers(0, 255, (480, 480, 3), dtype=np.uint8)
    async with client as c:
        r = await c.post("/api/analyze", files={"image": ("a.png", _png_bytes(img), "image/png")})
    assert r.status_code == 422
    assert r.json()["detail"]["success"] is False


@pytest.mark.asyncio
async def test_oversized_file(client):
    big = b"\0" * (11 * 1024 * 1024)
    async with client as c:
        r = await c.post("/api/analyze", files={"image": ("a.jpg", big, "image/jpeg")})
    assert r.status_code == 413
