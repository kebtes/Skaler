from unittest.mock import AsyncMock, patch

import httpx
import pytest

from skaler import Requester


@pytest.mark.asyncio
async def test_send_basic_request():
    """
    Test the Requester.send performs a basic GET request without headers,
    JSON payload, or proxy, and returns the expected response.
    """

    requester = Requester()

    with patch.object(
        requester.client,
        "request",
        new_callable=AsyncMock
    ) as mock_request:
        mock_response = httpx.Response(200, json={"message": "ok"})
        mock_request.return_value = mock_response

        response = await requester.send("GET", "https://example.com")

        mock_request.assert_awaited_once_with(
            method="GET",
            url="https://example.com",
            headers=None,
            json=None,
            timeout=10,
            proxies=None
        )

        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

@pytest.mark.asyncio
async def test_send_with_headers_and_json():
    """
    Test that Requester.send correctly sends a POST request with custom headers
    and a JSON payload, and returns the expected response.
    """
    requester = Requester()

    with patch.object(
        requester.client,
        "request",
        new_callable=AsyncMock
    ) as mock_request:
        mock_response = httpx.Response(201, json={"created": True})
        mock_request.return_value = mock_response

        headers = {"Authorization": "Bearer token"}
        json_payload = {"key": "value"}

        response = await requester.send(
            "POST",
            "https://example.com/api",
            headers=headers,
            json=json_payload
        )

        mock_request.assert_awaited_once_with(
            method="POST",
            url="https://example.com/api",
            headers=headers,
            json=json_payload,
            timeout=10,
            proxies=None,
        )
        assert response.status_code == 201
        assert response.json() == {"created": True}

@pytest.mark.asyncio
async def test_send_with_proxy():
    """
    Test that Requester.send sends a GET request using a specified HTTP proxy,
    and returns the expected response.
    """
    requester = Requester()

    with patch.object(
        requester.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response = httpx.Response(200)
        mock_request.return_value = mock_response

        proxy_url = "http://127.0.0.1:8080"
        response = await requester.send(
            "GET", "https://example.com", proxy=proxy_url
        )

        mock_request.assert_awaited_once_with(
            method="GET",
            url="https://example.com",
            headers=None,
            json=None,
            timeout=10,
            proxies={"http": proxy_url, "https": proxy_url},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_send_raises_request_error():
    """
    Test that Requester.send properly raises an httpx.RequestError exception
    when the underlying request fails (e.g., connection error).
    """
    requester = Requester()

    with patch.object(
        requester.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_request.side_effect = httpx.RequestError("Connection error")

        with pytest.raises(httpx.RequestError):
            await requester.send("GET", "https://example.com")
