"""
스마트 발굴 결과 모델
OpportunityScore를 포함한 최종 결과

v1.0.0 - Phase 3 Step 3.3
"""
from typing import List, Dict
from datetime import datetime

try:
    from pydantic import BaseModel, Field, computed_field
except ImportError:
    # Fallback for missing pydantic
    class BaseModel:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)

    def Field(**kwargs):
        return kwargs.get('default', None)

    def computed_field(func):
        return property(func)

from backend.models.opportunity_score import OpportunityScore


class DiscoveryResult(BaseModel):
    """스마트 발굴 결과"""

    seed_keyword: str = Field(description="시드 키워드")
    generated_count: int = Field(description="생성된 키워드 개수")
    analyzed_count: int = Field(description="분석된 키워드 개수")

    opportunities: List[OpportunityScore] = Field(
        default_factory=list,
        description="기회 점수 리스트"
    )

    cache_hit: bool = Field(
        default=False,
        description="캐시 히트 여부"
    )

    started_at: datetime = Field(
        default_factory=datetime.now,
        description="분석 시작 시간"
    )
    completed_at: datetime = Field(
        default_factory=datetime.now,
        description="분석 완료 시간"
    )

    @computed_field
    @property
    def processing_time(self) -> float:
        """
        처리 시간 (초)

        Returns:
            처리 소요 시간
        """
        delta = self.completed_at - self.started_at
        return delta.total_seconds()

    @computed_field
    @property
    def success_rate(self) -> float:
        """
        분석 성공률 (%)

        Returns:
            성공률
        """
        if self.generated_count == 0:
            return 0.0

        return (self.analyzed_count / self.generated_count) * 100

    @computed_field
    @property
    def grade_distribution(self) -> Dict[str, int]:
        """
        등급별 분포

        Returns:
            {'S': 3, 'A': 5, 'B': 10, 'C': 7, 'D': 5}
        """
        distribution = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}

        for opp in self.opportunities:
            grade = opp.grade
            distribution[grade] = distribution.get(grade, 0) + 1

        return distribution

    @computed_field
    @property
    def best_opportunity(self) -> OpportunityScore:
        """
        최고 기회 키워드

        Returns:
            가장 높은 점수의 OpportunityScore
        """
        if not self.opportunities:
            return None

        return max(self.opportunities, key=lambda x: x.total_score)

    @computed_field
    @property
    def average_score(self) -> float:
        """
        평균 점수

        Returns:
            전체 평균 점수
        """
        if not self.opportunities:
            return 0.0

        total = sum(opp.total_score for opp in self.opportunities)
        return total / len(self.opportunities)

    def get_top_opportunities(self, top_n: int = 10) -> List[OpportunityScore]:
        """
        상위 N개 기회 추출

        Args:
            top_n: 상위 개수

        Returns:
            정렬된 OpportunityScore 리스트
        """
        sorted_opps = sorted(
            self.opportunities,
            key=lambda x: x.total_score,
            reverse=True
        )
        return sorted_opps[:top_n]

    def filter_by_grade(
        self,
        min_grade: str = 'C'
    ) -> List[OpportunityScore]:
        """
        등급 기준 필터링

        Args:
            min_grade: 최소 등급 (S/A/B/C/D)

        Returns:
            필터링된 OpportunityScore 리스트
        """
        grade_order = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1}
        min_level = grade_order.get(min_grade, 2)

        filtered = [
            opp for opp in self.opportunities
            if grade_order.get(opp.grade, 0) >= min_level
        ]

        return filtered

    def to_summary(self) -> str:
        """
        결과 요약 텍스트

        Returns:
            요약 문자열
        """
        lines = [
            "=" * 60,
            "Smart Discovery 결과",
            "=" * 60,
            "",
            f"시드 키워드: {self.seed_keyword}",
            f"생성 키워드: {self.generated_count}개",
            f"분석 완료: {self.analyzed_count}개",
            f"성공률: {self.success_rate:.1f}%",
            f"소요 시간: {self.processing_time:.1f}초",
            f"캐시 사용: {'Yes' if self.cache_hit else 'No'}",
            "",
            "=" * 60,
            "등급 분포",
            "=" * 60,
        ]

        dist = self.grade_distribution
        for grade in ['S', 'A', 'B', 'C', 'D']:
            count = dist.get(grade, 0)
            if count > 0:
                lines.append(f"{grade}등급: {count}개")

        if self.best_opportunity:
            best = self.best_opportunity
            lines.extend([
                "",
                "=" * 60,
                "최고 기회 키워드",
                "=" * 60,
                "",
                f"키워드: {best.keyword}",
                f"종합 점수: {best.total_score:.1f}점",
                f"등급: {best.grade}",
                f"수요: {best.search_demand:.0f} | "
                f"추세: {best.momentum:.0f} | "
                f"공백: {best.competition_gap:.0f} | "
                f"적합: {best.suitability:.0f}",
            ])

        lines.append("=" * 60)

        return "\n".join(lines)

    class Config:
        """Pydantic 설정"""
        json_schema_extra = {
            "example": {
                "seed_keyword": "롱패딩",
                "generated_count": 30,
                "analyzed_count": 28,
                "cache_hit": False
            }
        }
