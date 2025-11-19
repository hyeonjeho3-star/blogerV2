"""
생성기 추상 클래스
"""
from abc import ABC, abstractmethod
from typing import List

class BaseGenerator(ABC):
    """키워드 생성기 추상 클래스"""

    @abstractmethod
    def generate(self, seed_keyword: str) -> List[str]:
        """
        시드 키워드로부터 변형 생성

        Args:
            seed_keyword: 기본 키워드

        Returns:
            생성된 키워드 리스트
        """
        pass
