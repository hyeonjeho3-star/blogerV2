"""
API 클라이언트 유틸리티
v1.0.3의 requests를 httpx로 업그레이드하여 비동기 지원 (임시로 requests 사용)
"""
from typing import Dict, Any, Optional
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    """범용 API 클라이언트 (임시 구현 - httpx 미설치)"""

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        API 클라이언트 초기화

        Args:
            base_url: API 기본 URL
            headers: 기본 헤더
        """
        self.base_url = base_url
        self.headers = headers or {}

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST 요청

        Args:
            endpoint: API 엔드포인트
            data: 요청 데이터

        Returns:
            응답 JSON 데이터
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.info(f"POST 요청: {url}")

            # TODO: httpx 설치 후 실제 구현
            # import httpx
            # response = self.client.post(url, json=data, headers=self.headers)
            # response.raise_for_status()
            # return response.json()

            logger.warning("httpx 미설치 - 더미 응답 반환")
            return {"status": "dummy_response"}

        except Exception as e:
            logger.error(f"요청 실패: {str(e)}")
            raise

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        GET 요청

        Args:
            endpoint: API 엔드포인트
            params: 쿼리 파라미터

        Returns:
            응답 JSON 데이터
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.info(f"GET 요청: {url}")

            # TODO: httpx 설치 후 실제 구현
            # import httpx
            # response = self.client.get(url, params=params, headers=self.headers)
            # response.raise_for_status()
            # return response.json()

            logger.warning("httpx 미설치 - 더미 응답 반환")
            return {"status": "dummy_response"}

        except Exception as e:
            logger.error(f"요청 실패: {str(e)}")
            raise
