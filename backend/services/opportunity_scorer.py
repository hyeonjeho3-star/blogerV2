"""
기회 점수 계산 서비스
키워드의 기회 점수 자동 산출

v1.0.0 - Phase 3 Step 3.1
"""
from typing import List, Literal
from backend.models.keyword_trend import KeywordTrend
from backend.models.opportunity_score import OpportunityScore, GradeType
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class OpportunityScorer:
    """기회 점수 계산 서비스"""

    def __init__(
        self,
        demand_weight: float = 0.30,
        momentum_weight: float = 0.35,
        gap_weight: float = 0.20,
        suitability_weight: float = 0.15
    ):
        """
        초기화

        Args:
            demand_weight: 검색 수요 가중치 (기본 30%)
            momentum_weight: 성장 추세 가중치 (기본 35%)
            gap_weight: 경쟁 공백 가중치 (기본 20%)
            suitability_weight: 블로그 적합도 가중치 (기본 15%)
        """
        # 가중치 검증
        total = demand_weight + momentum_weight + gap_weight + suitability_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"가중치 합이 1.0이 아닙니다: {total}")

        self.demand_weight = demand_weight
        self.momentum_weight = momentum_weight
        self.gap_weight = gap_weight
        self.suitability_weight = suitability_weight

        logger.info(
            f"OpportunityScorer 초기화 "
            f"(수요:{demand_weight:.0%}, 추세:{momentum_weight:.0%}, "
            f"공백:{gap_weight:.0%}, 적합:{suitability_weight:.0%})"
        )

    def calculate(self, trend: KeywordTrend) -> OpportunityScore:
        """
        단일 키워드의 기회 점수 계산

        Args:
            trend: KeywordTrend 객체

        Returns:
            OpportunityScore 객체
        """
        logger.debug(f"기회 점수 계산 시작: {trend.keyword}")

        # 개별 점수 계산
        search_demand = self._calculate_search_demand(trend)
        momentum = self._calculate_momentum_score(trend)
        competition_gap = self._calculate_competition_gap(trend)
        suitability = self._calculate_suitability(trend)

        score = OpportunityScore(
            keyword=trend.keyword,
            search_demand=search_demand,
            momentum=momentum,
            competition_gap=competition_gap,
            suitability=suitability,
            average_ratio=trend.average_ratio,
            recent_ratio=trend.recent_ratio,
            momentum_value=trend.momentum
        )

        logger.info(
            f"점수 계산 완료: {trend.keyword} = {score.total_score:.1f}점 "
            f"(등급: {score.grade})"
        )

        return score

    def calculate_batch(self, trends: List[KeywordTrend]) -> List[OpportunityScore]:
        """
        여러 키워드의 기회 점수 일괄 계산

        Args:
            trends: KeywordTrend 리스트

        Returns:
            OpportunityScore 리스트
        """
        if not trends:
            logger.warning("빈 트렌드 리스트")
            return []

        logger.info(f"배치 점수 계산 시작: {len(trends)}개 키워드")

        scores = [self.calculate(trend) for trend in trends]

        logger.info(f"배치 점수 계산 완료: {len(scores)}개")

        return scores

    def filter_by_grade(
        self,
        scores: List[OpportunityScore],
        min_grade: GradeType = 'C'
    ) -> List[OpportunityScore]:
        """
        등급 기준으로 필터링

        Args:
            scores: OpportunityScore 리스트
            min_grade: 최소 등급 (기본: C)

        Returns:
            필터링된 OpportunityScore 리스트
        """
        # 등급 순서 정의
        grade_order = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1}
        min_level = grade_order.get(min_grade, 2)

        filtered = [
            score for score in scores
            if grade_order.get(score.grade, 0) >= min_level
        ]

        logger.info(
            f"등급 필터링: {len(scores)}개 → {len(filtered)}개 "
            f"(최소 등급: {min_grade})"
        )

        return filtered

    def _calculate_search_demand(self, trend: KeywordTrend) -> float:
        """
        검색 수요 점수 계산

        Args:
            trend: KeywordTrend 객체

        Returns:
            0-100 점수
        """
        # average_ratio를 0-100 스케일로 변환
        # average_ratio는 보통 0-100 범위
        score = min(100.0, max(0.0, trend.average_ratio))

        logger.debug(f"검색 수요 점수: {score:.1f} (평균 비율: {trend.average_ratio:.1f})")

        return score

    def _calculate_momentum_score(self, trend: KeywordTrend) -> float:
        """
        성장 추세 점수 계산

        Args:
            trend: KeywordTrend 객체

        Returns:
            0-100 점수
        """
        # momentum은 -100 ~ +100 범위
        # 이를 0-100으로 정규화
        momentum_value = trend.momentum

        # 0을 기준으로 스케일링
        if momentum_value >= 0:
            # 상승: 0% → 50점, +50% → 75점, +100% 이상 → 100점
            score = 50 + min(50, momentum_value / 2)
        else:
            # 하락: 0% → 50점, -50% → 25점, -100% 이하 → 0점
            score = 50 + max(-50, momentum_value / 2)

        score = min(100.0, max(0.0, score))

        logger.debug(
            f"추세 점수: {score:.1f} (모멘텀: {momentum_value:+.1f}%)"
        )

        return score

    def _calculate_competition_gap(self, trend: KeywordTrend) -> float:
        """
        경쟁 공백 점수 계산

        현재는 recent_ratio 기반으로 계산
        (실제로는 블로그 글 수 API 필요)

        Args:
            trend: KeywordTrend 객체

        Returns:
            0-100 점수
        """
        # recent_ratio가 높을수록 검색은 많은데
        # 상대적으로 콘텐츠가 적을 가능성
        # 단순화: recent_ratio의 80%를 경쟁 공백으로 간주
        score = min(100.0, trend.recent_ratio * 0.8)

        logger.debug(
            f"경쟁 공백 점수: {score:.1f} (최근 비율: {trend.recent_ratio:.1f})"
        )

        return score

    def _calculate_suitability(self, trend: KeywordTrend) -> float:
        """
        블로그 적합도 점수 계산

        키워드 길이, 구성 등으로 판단

        Args:
            trend: KeywordTrend 객체

        Returns:
            0-100 점수
        """
        keyword = trend.keyword
        score = 50.0  # 기본 점수

        # 길이 점수
        length = len(keyword)
        if 5 <= length <= 15:
            score += 20  # 적절한 길이
        elif 3 <= length <= 20:
            score += 10  # 괜찮은 길이
        else:
            score += 0  # 너무 짧거나 김

        # 공백 포함 여부 (롱테일)
        if ' ' in keyword:
            score += 15

        # 특정 수식어 포함 (블로그 친화적)
        blog_friendly = ['방법', '추천', '후기', '비교', '정리', '가이드', '팁']
        if any(word in keyword for word in blog_friendly):
            score += 15

        score = min(100.0, max(0.0, score))

        logger.debug(f"적합도 점수: {score:.1f} (키워드: '{keyword}')")

        return score

    def get_grade_distribution(self, scores: List[OpportunityScore]) -> dict:
        """
        등급별 분포 통계

        Args:
            scores: OpportunityScore 리스트

        Returns:
            {'S': 3, 'A': 5, 'B': 10, 'C': 7, 'D': 5}
        """
        distribution = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}

        for score in scores:
            distribution[score.grade] = distribution.get(score.grade, 0) + 1

        return distribution

    def get_top_opportunities(
        self,
        scores: List[OpportunityScore],
        top_n: int = 10
    ) -> List[OpportunityScore]:
        """
        상위 N개 기회 키워드 추출

        Args:
            scores: OpportunityScore 리스트
            top_n: 상위 개수

        Returns:
            정렬된 OpportunityScore 리스트
        """
        sorted_scores = sorted(
            scores,
            key=lambda x: x.total_score,
            reverse=True
        )

        return sorted_scores[:top_n]
