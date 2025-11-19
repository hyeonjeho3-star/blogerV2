"""
키워드 배치 처리 모델
"""
from typing import List
try:
    from pydantic import BaseModel, Field
except ImportError:
    class BaseModel:
        pass
    def Field(*args, **kwargs):
        return None

from backend.models.keyword_trend import KeywordTrend

class KeywordBatch(BaseModel):
    """키워드 배치"""
    keywords: List[str] = Field(..., min_length=1, max_length=5, description="배치 키워드 (최대 5개)")
    batch_number: int = Field(..., ge=1, description="배치 번호")
    total_batches: int = Field(..., ge=1, description="전체 배치 수")

    @property
    def progress_percentage(self) -> float:
        """진행률 계산"""
        return (self.batch_number / self.total_batches) * 100

class BatchAnalysisResult(BaseModel):
    """배치 분석 결과"""
    batch: KeywordBatch
    results: List[KeywordTrend] = Field(default_factory=list, description="분석 결과")
    success: bool = Field(default=True, description="성공 여부")
    error_message: str = Field(default="", description="에러 메시지")
    processing_time: float = Field(default=0.0, ge=0, description="처리 시간 (초)")
