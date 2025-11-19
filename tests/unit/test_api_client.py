"""
API Client 테스트
"""
from backend.utils.api_client import APIClient


def test_api_client_init():
    """API 클라이언트 초기화 테스트"""
    client = APIClient(
        base_url="https://example.com",
        headers={"Content-Type": "application/json"}
    )

    assert client.base_url == "https://example.com"
    assert "Content-Type" in client.headers
    assert client.headers["Content-Type"] == "application/json"


def test_api_client_post_dummy():
    """POST 요청 테스트 (더미 응답)"""
    client = APIClient(base_url="https://example.com")

    response = client.post("/test", {"key": "value"})

    # 현재는 더미 응답을 반환하므로 status가 있어야 함
    assert "status" in response


def test_api_client_get_dummy():
    """GET 요청 테스트 (더미 응답)"""
    client = APIClient(base_url="https://example.com")

    response = client.get("/test", {"param": "value"})

    # 현재는 더미 응답을 반환하므로 status가 있어야 함
    assert "status" in response
