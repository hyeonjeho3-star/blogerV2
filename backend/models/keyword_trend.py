"""
키워드 트렌드 데이터 모델
v1.0.3의 dataclass를 Pydantic으로 업그레이드하여 타입 안전성 강화
"""
from typing import List, Literal
from datetime import datetime
try:
    from pydantic import BaseModel, Field, field_validator
except ImportError:
    # Pydantic 미설치 시 임시 대체
    class BaseModel:
        pass
    def Field(*args, **kwargs):
        return None
    def field_validator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

class TrendDataPoint(BaseModel):
    """개별 트렌드 데이터 포인트"""
    period: str = Field(..., description="기간 (YYYY-MM-DD)")
    ratio: float = Field(..., ge=0, le=100, description="검색 비율 (0-100)")

class KeywordTrend(BaseModel):
    """키워드 트렌드 분석 결과"""

    # 기본 정보
    keyword: str = Field(..., min_length=1, max_length=100, description="분석 키워드")

    # 기본 지표 (v1.0.3)
    average_ratio: float = Field(..., ge=0, le=100, description="전체 기간 평균 비율")
    recent_ratio: float = Field(..., ge=0, le=100, description="최근 7일 평균 비율")

    # 신규 지표 (Phase 2)
    momentum: float = Field(default=0.0, ge=-100, le=100, description="모멘텀 (-100 ~ +100)")
    trend_direction: Literal['rising', 'stable', 'falling'] = Field(
        default='stable',
        description="트렌드 방향"
    )
    velocity: float = Field(default=0.0, description="추세 가속도")

    # 점수
    total_score: float = Field(..., ge=0, le=100, description="종합 점수")

    # 원본 데이터
    trend_data: List[TrendDataPoint] = Field(default_factory=list, description="시계열 데이터")

    # 메타 정보
    analyzed_at: datetime = Field(default_factory=datetime.now, description="분석 시각")

    @field_validator('keyword')
    @classmethod
    def keyword_must_not_be_empty(cls, v: str) -> str:
        """키워드 공백 검증"""
        if not v.strip():
            raise ValueError('키워드는 공백일 수 없습니다')
        return v.strip()

    def get_urgency_message(self) -> str:
        """발행 긴급도 메시지"""
        if self.momentum > 50 and self.trend_direction == 'rising':
            return '🔥 지금 당장 발행 권장! (급상승 트렌드)'
        elif self.momentum > 20 and self.trend_direction == 'rising':
            return '⚡ 이번 주 안에 발행 권장 (상승세)'
        elif self.trend_direction == 'stable':
            return '✅ 여유있게 발행 가능 (안정적)'
        else:
            return '⏳ 다음 기회 대기 권장 (하락세)'

    def get_grade(self) -> str:
        """등급 판정 (Phase 3에서 활용)"""
        if self.total_score >= 80:
            return 'S'
        elif self.total_score >= 65:
            return 'A'
        elif self.total_score >= 50:
            return 'B'
        elif self.total_score >= 35:
            return 'C'
        else:
            return 'D'

    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "롱패딩 세탁법",
                "average_ratio": 45.3,
                "recent_ratio": 68.7,
                "momentum": 51.6,
                "trend_direction": "rising",
                "velocity": 2.3,
                "total_score": 72.5,
                "trend_data": [
                    {"period": "2024-11-01", "ratio": 35.2},
                    {"period": "2024-11-02", "ratio": 42.8}
                ]
            }
        }
