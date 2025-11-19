"""
분석기 추상 클래스
v1.0.3과 동일한 인터페이스 유지
"""
from abc import ABC, abstractmethod
from typing import List
from backend.models.keyword_trend import KeywordTrend

class BaseAnalyzer(ABC):
    """키워드 트렌드 분석기 추상 클래스"""

    @abstractmethod
    def analyze(self, keywords: List[str]) -> List[KeywordTrend]:
        """
        키워드 트렌드 분석

        Args:
            keywords: 분석할 키워드 리스트 (최대 5개)

        Returns:
            KeywordTrend 리스트
        """
        pass
