"""
네이버 자동완성 크롤러
검색창 자동완성 API를 활용한 키워드 발굴
"""
from typing import List, Set
try:
    import httpx
except ImportError:
    httpx = None
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class AutocompleteGenerator:
    """네이버 자동완성 키워드 생성기"""

    # 네이버 자동완성 API
    API_URL = "https://ac.search.naver.com/nx/ac"

    def __init__(self, max_results: int = 10):
        """
        초기화

        Args:
            max_results: 최대 결과 개수
        """
        self.max_results = max_results
        if httpx:
            self.client = httpx.Client(timeout=10.0)
        else:
            self.client = None
        logger.info(f"AutocompleteGenerator 초기화 (max_results={max_results})")

    def generate(self, seed_keyword: str) -> List[str]:
        """
        시드 키워드로부터 자동완성 키워드 추출

        Args:
            seed_keyword: "롱패딩"

        Returns:
            ["롱패딩 세탁", "롱패딩 추천", ...]
        """
        if not seed_keyword or not seed_keyword.strip():
            raise ValueError("시드 키워드가 비어있습니다")

        seed_keyword = seed_keyword.strip()
        logger.info(f"자동완성 생성 시작: '{seed_keyword}'")

        if not self.client:
            logger.warning("httpx 미설치 - 더미 결과 반환")
            return [f"{seed_keyword} {suffix}" for suffix in ["추천", "방법", "후기"]]

        try:
            keywords = self._fetch_autocomplete(seed_keyword)
            logger.info(f"자동완성 생성 완료: {len(keywords)}개")
            return keywords[:self.max_results]

        except Exception as e:
            logger.error(f"자동완성 생성 실패: {str(e)}")
            return []

    def _fetch_autocomplete(self, query: str) -> List[str]:
        """
        네이버 자동완성 API 호출

        Args:
            query: 검색어

        Returns:
            자동완성 키워드 리스트
        """
        params = {
            "q": query,
            "st": 100,
            "r_format": "json",
            "r_enc": "UTF-8",
            "r_unicode": 0,
            "t_koreng": 1
        }

        try:
            response = self.client.get(self.API_URL, params=params)
            response.raise_for_status()

            data = response.json()

            # 결과 파싱
            items = data.get("items", [[]])[0]
            keywords = [item[0] for item in items if len(item) > 0]

            logger.debug(f"자동완성 결과: {len(keywords)}개")

            return keywords

        except Exception as e:
            logger.error(f"자동완성 API 호출 실패: {str(e)}")
            raise

    def __del__(self):
        """클라이언트 종료"""
        if self.client:
            self.client.close()
