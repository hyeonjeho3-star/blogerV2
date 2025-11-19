"""
전체 분석 결과 모델
"""
from typing import List, Optional
from datetime import datetime
try:
    from pydantic import BaseModel, Field
except ImportError:
    class BaseModel:
        pass
    def Field(*args, **kwargs):
        return None

from backend.models.keyword_trend import KeywordTrend

class AnalysisResult(BaseModel):
    """전체 분석 결과"""

    # 입력
    input_keywords: List[str] = Field(..., description="입력 키워드")

    # 결과
    trends: List[KeywordTrend] = Field(default_factory=list, description="트렌드 분석 결과")
    best_keyword: Optional[KeywordTrend] = Field(None, description="최고 점수 키워드")

    # 통계
    total_analyzed: int = Field(default=0, ge=0, description="분석된 키워드 수")
    successful: int = Field(default=0, ge=0, description="성공한 분석 수")
    failed: int = Field(default=0, ge=0, description="실패한 분석 수")

    # 메타
    started_at: datetime = Field(default_factory=datetime.now, description="시작 시각")
    completed_at: Optional[datetime] = Field(None, description="완료 시각")

    @property
    def success_rate(self) -> float:
        """성공률 계산"""
        if self.total_analyzed == 0:
            return 0.0
        return (self.successful / self.total_analyzed) * 100

    @property
    def processing_time(self) -> float:
        """총 처리 시간 (초)"""
        if self.completed_at is None:
            return 0.0
        delta = self.completed_at - self.started_at
        return delta.total_seconds()

    def get_top_keywords(self, n: int = 5) -> List[KeywordTrend]:
        """상위 N개 키워드 반환"""
        sorted_trends = sorted(self.trends, key=lambda x: x.total_score, reverse=True)
        return sorted_trends[:n]
