"""
배치 분석 프로세서
네이버 API 제한(5개)을 고려한 배치 처리 시스템
"""
import time
from typing import List, Callable, Optional
from backend.models.keyword_batch import KeywordBatch, BatchAnalysisResult
from backend.models.keyword_trend import KeywordTrend
from backend.analyzers.datalab_analyzer import DataLabAnalyzer
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class BatchProcessor:
    """키워드 배치 분석 프로세서"""

    def __init__(
        self,
        analyzer: DataLabAnalyzer,
        batch_size: int = 5,
        delay_seconds: float = 1.0,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ):
        """
        초기화

        Args:
            analyzer: DataLabAnalyzer 인스턴스
            batch_size: 배치 크기 (네이버 제한: 5)
            delay_seconds: 배치 간 대기 시간
            progress_callback: 진행률 콜백 함수 (current, total)
        """
        if batch_size > 5:
            logger.warning(f"배치 크기 {batch_size}는 5로 제한됩니다")
            batch_size = 5

        self.analyzer = analyzer
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
        self.progress_callback = progress_callback

        logger.info(f"BatchProcessor 초기화 (배치 크기={batch_size}, 대기={delay_seconds}초)")

    def process(self, keywords: List[str]) -> List[KeywordTrend]:
        """
        키워드 리스트를 배치로 나눠 분석

        Args:
            keywords: 분석할 키워드 리스트

        Returns:
            전체 KeywordTrend 리스트
        """
        if not keywords:
            raise ValueError("키워드 리스트가 비어있습니다")

        logger.info(f"배치 분석 시작: {len(keywords)}개 키워드")

        # 배치 생성
        batches = self._create_batches(keywords)
        total_batches = len(batches)

        logger.info(f"총 {total_batches}개 배치 생성")

        all_trends: List[KeywordTrend] = []

        # 배치 처리
        for idx, batch in enumerate(batches, 1):
            logger.info(f"배치 {idx}/{total_batches} 처리 중...")

            # 진행률 콜백
            if self.progress_callback:
                self.progress_callback(idx, total_batches)

            # 분석 실행
            result = self._process_single_batch(batch, idx, total_batches)

            if result.success:
                all_trends.extend(result.results)
                logger.info(f"배치 {idx} 완료: {len(result.results)}개 키워드 분석")
            else:
                logger.error(f"배치 {idx} 실패: {result.error_message}")

            # Rate Limiting (마지막 배치 제외)
            if idx < total_batches:
                logger.debug(f"{self.delay_seconds}초 대기 중...")
                time.sleep(self.delay_seconds)

        logger.info(f"배치 분석 완료: 총 {len(all_trends)}개 키워드")

        return all_trends

    def _create_batches(self, keywords: List[str]) -> List[KeywordBatch]:
        """키워드 리스트를 배치로 분할"""
        batches = []
        total_batches = (len(keywords) + self.batch_size - 1) // self.batch_size

        for i in range(0, len(keywords), self.batch_size):
            batch_keywords = keywords[i:i + self.batch_size]
            batch_number = (i // self.batch_size) + 1

            batch = KeywordBatch(
                keywords=batch_keywords,
                batch_number=batch_number,
                total_batches=total_batches
            )

            batches.append(batch)

        return batches

    def _process_single_batch(
        self,
        batch: KeywordBatch,
        current: int,
        total: int
    ) -> BatchAnalysisResult:
        """단일 배치 처리"""
        start_time = time.time()

        try:
            logger.debug(f"배치 키워드: {batch.keywords}")

            # 분석 실행
            trends = self.analyzer.analyze(batch.keywords)

            processing_time = time.time() - start_time

            return BatchAnalysisResult(
                batch=batch,
                results=trends,
                success=True,
                processing_time=processing_time
            )

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"배치 분석 실패: {str(e)}"

            logger.error(error_msg)

            return BatchAnalysisResult(
                batch=batch,
                results=[],
                success=False,
                error_message=error_msg,
                processing_time=processing_time
            )
