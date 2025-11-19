"""
키워드 비교 서비스
v1.0.3 BlogService의 비교 기능만 추출 및 개선
"""
from typing import List, Optional
from datetime import datetime
from backend.analyzers.datalab_analyzer import DataLabAnalyzer
from backend.models.keyword_trend import KeywordTrend
from backend.models.analysis_result import AnalysisResult
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class KeywordComparisonService:
    """키워드 트렌드 비교 서비스"""

    def __init__(self, analyzer: Optional[DataLabAnalyzer] = None):
        """
        초기화

        Args:
            analyzer: DataLabAnalyzer 인스턴스 (None이면 자동 생성)
        """
        self.analyzer = analyzer or DataLabAnalyzer()
        logger.info("KeywordComparisonService 초기화 완료")

    def compare(self, keywords: List[str]) -> AnalysisResult:
        """
        키워드 비교 분석

        Args:
            keywords: 비교할 키워드 리스트 (1-5개)

        Returns:
            AnalysisResult 객체

        Raises:
            ValueError: 키워드가 없거나 5개 초과 시
        """
        # 입력 검증
        if not keywords:
            raise ValueError("키워드가 비어있습니다")

        if len(keywords) > 5:
            raise ValueError("키워드는 최대 5개까지 가능합니다")

        logger.info(f"키워드 비교 시작: {keywords}")

        # AnalysisResult 초기화
        result = AnalysisResult(
            input_keywords=keywords,
            started_at=datetime.now()
        )

        try:
            # 트렌드 분석 실행
            trends = self.analyzer.analyze(keywords)

            result.trends = trends
            result.total_analyzed = len(keywords)
            result.successful = len(trends)
            result.failed = len(keywords) - len(trends)

            # 최고 점수 키워드 선정
            if trends:
                result.best_keyword = max(trends, key=lambda x: x.total_score)
                logger.info(f"최고 키워드: {result.best_keyword.keyword} ({result.best_keyword.total_score:.1f}점)")

            result.completed_at = datetime.now()

            logger.info(f"비교 완료: 성공률 {result.success_rate:.1f}%")

            return result

        except Exception as e:
            result.completed_at = datetime.now()
            result.failed = len(keywords)

            logger.error(f"비교 실패: {str(e)}")
            raise

    def get_ranking(self, result: AnalysisResult) -> List[tuple]:
        """
        순위별 키워드 반환

        Args:
            result: AnalysisResult 객체

        Returns:
            [(순위, KeywordTrend), ...] 리스트
        """
        sorted_trends = sorted(result.trends, key=lambda x: x.total_score, reverse=True)
        return list(enumerate(sorted_trends, 1))

    def get_comparison_summary(self, result: AnalysisResult) -> str:
        """
        비교 결과 요약 텍스트 생성

        Args:
            result: AnalysisResult 객체

        Returns:
            요약 텍스트
        """
        if not result.trends:
            return "분석 결과가 없습니다."

        best = result.best_keyword
        if not best:
            return "최고 키워드를 찾을 수 없습니다."

        summary_lines = [
            "=" * 60,
            "분석 결과 요약",
            "=" * 60,
            "",
            f"분석 키워드: {len(result.input_keywords)}개",
            f"성공: {result.successful}개",
            f"실패: {result.failed}개",
            f"소요 시간: {result.processing_time:.1f}초",
            "",
            "=" * 60,
            "최고 키워드",
            "=" * 60,
            "",
            f"키워드: {best.keyword}",
            f"종합 점수: {best.total_score:.1f}/100 (등급: {best.get_grade()})",
            f"전체 평균: {best.average_ratio:.1f}",
            f"최근 추세: {best.recent_ratio:.1f}",
            f"모멘텀: {best.momentum:+.1f}%",
            f"트렌드: {best.trend_direction}",
            f"긴급도: {best.get_urgency_message()}",
            "",
            "=" * 60,
        ]

        return "\n".join(summary_lines)
