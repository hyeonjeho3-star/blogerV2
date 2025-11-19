"""
기회 점수 모델
키워드의 블로그 작성 기회를 점수화

v1.0.0 - Phase 3 Step 3.1
"""
from typing import Literal

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

GradeType = Literal['S', 'A', 'B', 'C', 'D']


class OpportunityScore(BaseModel):
    """
    키워드 기회 점수 모델

    점수 구성:
    - search_demand (30%): 검색 수요 점수
    - momentum (35%): 성장 추세 점수
    - competition_gap (20%): 경쟁 공백 점수
    - suitability (15%): 블로그 적합도 점수

    등급 기준:
    - S: 80점 이상 (최고 기회)
    - A: 65~79점 (높은 기회)
    - B: 50~64점 (중간 기회)
    - C: 35~49점 (낮은 기회)
    - D: 35점 미만 (기회 없음)
    """

    keyword: str = Field(description="분석 키워드")

    # 개별 점수 (0-100)
    search_demand: float = Field(
        ge=0,
        le=100,
        description="검색 수요 점수 (네이버 검색량 기준)"
    )
    momentum: float = Field(
        ge=0,
        le=100,
        description="성장 추세 점수 (최근 7일 vs 이전 7일)"
    )
    competition_gap: float = Field(
        ge=0,
        le=100,
        description="경쟁 공백 점수 (검색량 대비 블로그 글 수)"
    )
    suitability: float = Field(
        ge=0,
        le=100,
        description="블로그 적합도 점수 (키워드 특성)"
    )

    # 메타 정보
    average_ratio: float = Field(default=0.0, description="전체 평균 검색 비율")
    recent_ratio: float = Field(default=0.0, description="최근 평균 검색 비율")
    momentum_value: float = Field(default=0.0, description="모멘텀 값 (%)")

    @computed_field
    @property
    def total_score(self) -> float:
        """
        종합 점수 계산

        Returns:
            가중 평균 점수 (0-100)
        """
        return (
            self.search_demand * 0.30 +
            self.momentum * 0.35 +
            self.competition_gap * 0.20 +
            self.suitability * 0.15
        )

    @computed_field
    @property
    def grade(self) -> GradeType:
        """
        등급 자동 판정

        Returns:
            S/A/B/C/D 등급
        """
        score = self.total_score

        if score >= 80:
            return 'S'
        elif score >= 65:
            return 'A'
        elif score >= 50:
            return 'B'
        elif score >= 35:
            return 'C'
        else:
            return 'D'

    @computed_field
    @property
    def grade_reason(self) -> str:
        """
        등급 판정 이유

        Returns:
            등급 설명 텍스트
        """
        grade = self.grade

        reasons = {
            'S': f"최고 등급! 검색 수요({self.search_demand:.1f}), 성장세({self.momentum:.1f}), 경쟁 공백({self.competition_gap:.1f}) 모두 우수합니다.",
            'A': f"높은 기회입니다. 특히 {'성장세' if self.momentum >= 70 else '검색 수요'}가 강점입니다.",
            'B': f"중간 수준의 기회입니다. {'성장세' if self.momentum < 50 else '경쟁 공백'}를 개선하면 좋습니다.",
            'C': f"낮은 기회입니다. 검색 수요({self.search_demand:.1f})나 성장세({self.momentum:.1f})가 부족합니다.",
            'D': f"기회가 거의 없습니다. 다른 키워드를 고려하세요."
        }

        return reasons.get(grade, "등급 미정")

    def get_strongest_factor(self) -> tuple[str, float]:
        """
        가장 강한 요인 찾기

        Returns:
            (요인명, 점수) 튜플
        """
        factors = {
            '검색 수요': self.search_demand,
            '성장 추세': self.momentum,
            '경쟁 공백': self.competition_gap,
            '블로그 적합도': self.suitability
        }

        strongest = max(factors.items(), key=lambda x: x[1])
        return strongest

    def get_weakest_factor(self) -> tuple[str, float]:
        """
        가장 약한 요인 찾기

        Returns:
            (요인명, 점수) 튜플
        """
        factors = {
            '검색 수요': self.search_demand,
            '성장 추세': self.momentum,
            '경쟁 공백': self.competition_gap,
            '블로그 적합도': self.suitability
        }

        weakest = min(factors.items(), key=lambda x: x[1])
        return weakest

    def to_summary(self) -> str:
        """
        요약 텍스트 생성

        Returns:
            점수 요약 문자열
        """
        strongest = self.get_strongest_factor()

        return (
            f"[{self.grade}등급] {self.keyword}\n"
            f"종합: {self.total_score:.1f}점 | "
            f"수요: {self.search_demand:.0f} | "
            f"추세: {self.momentum:.0f} | "
            f"공백: {self.competition_gap:.0f} | "
            f"적합: {self.suitability:.0f}\n"
            f"강점: {strongest[0]} ({strongest[1]:.1f}점)"
        )

    class Config:
        """Pydantic 설정"""
        json_schema_extra = {
            "example": {
                "keyword": "겨울 롱패딩 추천",
                "search_demand": 75.0,
                "momentum": 85.0,
                "competition_gap": 60.0,
                "suitability": 70.0,
                "average_ratio": 45.2,
                "recent_ratio": 52.8,
                "momentum_value": 16.8
            }
        }
