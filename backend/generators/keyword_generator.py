"""
키워드 생성기
롱테일 키워드 자동 생성 및 확장
"""
from typing import List, Set, Dict
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class LongTailGenerator:
    """롱테일 키워드 자동 생성기"""

    # 카테고리별 수식어
    MODIFIERS: Dict[str, List[str]] = {
        'how_to': ['방법', '하는법', '하기', '팁', '가이드', '노하우', '비법', '요령'],
        'review': ['후기', '리뷰', '사용법', '장단점', '솔직', '실사용', '경험담'],
        'comparison': ['VS', '비교', '차이', '추천', '순위', '베스트', '랭킹'],
        'problem': ['해결', '오류', '안될때', '문제', '고장', '수리', '해결법'],
        'timing': ['시기', '타이밍', '언제', '시즌', '계절', '시점'],
        'price': ['가격', '저렴한', '할인', '세일', '싼', '가성비', '최저가'],
        'quality': ['좋은', '인기', '유명한', '추천', '인기있는', '믿을만한'],
        'location': ['추천', '베스트', '인기', '유명한', '근처', '주변'],
        'diy': ['DIY', '직접', '셀프', '만들기', '홈메이드', '수제'],
        'beginner': ['초보', '입문', '처음', '기초', '쉬운', '간단한']
    }

    def __init__(self, max_variants: int = 30):
        """
        초기화

        Args:
            max_variants: 최대 생성 개수
        """
        self.max_variants = max_variants
        logger.info(f"LongTailGenerator 초기화 (max_variants={max_variants})")

    def generate(self, base_keyword: str) -> List[str]:
        """
        기본 키워드로부터 롱테일 변형 생성

        Args:
            base_keyword: "롱패딩"

        Returns:
            ['롱패딩', '롱패딩 방법', '롱패딩 후기', ...]
        """
        if not base_keyword or not base_keyword.strip():
            raise ValueError("기본 키워드가 비어있습니다")

        base_keyword = base_keyword.strip()
        logger.info(f"롱테일 생성 시작: '{base_keyword}'")

        variants: Set[str] = {base_keyword}  # 중복 제거용 Set

        # 카테고리별 변형 생성
        for category, modifiers in self.MODIFIERS.items():
            for modifier in modifiers:
                # 앞에 붙이기
                front_variant = f"{modifier} {base_keyword}"
                variants.add(front_variant)

                # 뒤에 붙이기
                back_variant = f"{base_keyword} {modifier}"
                variants.add(back_variant)

                if len(variants) >= self.max_variants:
                    break

            if len(variants) >= self.max_variants:
                break

        result = list(variants)[:self.max_variants]

        logger.info(f"롱테일 생성 완료: {len(result)}개")
        logger.debug(f"생성된 키워드 샘플: {result[:5]}")

        return result

    def generate_from_multiple(self, base_keywords: List[str]) -> List[str]:
        """
        여러 기본 키워드로부터 롱테일 생성

        Args:
            base_keywords: ["롱패딩", "발열내의"]

        Returns:
            모든 키워드의 롱테일 변형
        """
        if not base_keywords:
            raise ValueError("기본 키워드 리스트가 비어있습니다")

        logger.info(f"다중 롱테일 생성 시작: {len(base_keywords)}개 키워드")

        all_variants: Set[str] = set()

        for base in base_keywords:
            variants = self.generate(base)
            all_variants.update(variants)

        result = list(all_variants)

        logger.info(f"다중 롱테일 생성 완료: {len(result)}개")

        return result

    def filter_by_quality(self, keywords: List[str], min_length: int = 3) -> List[str]:
        """
        품질 기반 필터링

        Args:
            keywords: 필터링할 키워드 리스트
            min_length: 최소 글자 수

        Returns:
            필터링된 키워드
        """
        filtered = [
            kw for kw in keywords
            if len(kw) >= min_length and kw.strip()
        ]

        logger.info(f"품질 필터링: {len(keywords)}개 → {len(filtered)}개")

        return filtered
