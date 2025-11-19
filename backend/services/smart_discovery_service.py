"""
스마트 발굴 서비스
키워드 생성 → 분석 → 점수화 통합 오케스트레이션

v1.0.0 - Phase 3 Step 3.3
"""
from typing import List, Optional, Callable
from datetime import datetime

from backend.models.discovery_result import DiscoveryResult
from backend.models.keyword_trend import KeywordTrend
from backend.models.opportunity_score import OpportunityScore

from backend.generators.keyword_generator import LongTailGenerator
from backend.generators.autocomplete_generator import AutocompleteGenerator
from backend.analyzers.datalab_analyzer import DataLabAnalyzer
from backend.services.batch_processor import BatchProcessor
from backend.services.opportunity_scorer import OpportunityScorer
from backend.utils.cache_manager import CacheManager
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class SmartDiscoveryService:
    """스마트 키워드 발굴 서비스"""

    def __init__(
        self,
        longtail_generator: Optional[LongTailGenerator] = None,
        autocomplete_generator: Optional[AutocompleteGenerator] = None,
        datalab_analyzer: Optional[DataLabAnalyzer] = None,
        batch_processor: Optional[BatchProcessor] = None,
        opportunity_scorer: Optional[OpportunityScorer] = None,
        cache_manager: Optional[CacheManager] = None,
        use_cache: bool = True
    ):
        """
        초기화

        Args:
            longtail_generator: 롱테일 생성기
            autocomplete_generator: 자동완성 생성기
            datalab_analyzer: DataLab 분석기
            batch_processor: 배치 프로세서
            opportunity_scorer: 기회 점수 계산기
            cache_manager: 캐시 매니저
            use_cache: 캐시 사용 여부
        """
        # 컴포넌트 초기화
        self.longtail_gen = longtail_generator or LongTailGenerator(max_variants=30)
        self.autocomplete_gen = autocomplete_generator or AutocompleteGenerator(max_results=10)

        analyzer = datalab_analyzer or DataLabAnalyzer()
        self.batch_processor = batch_processor or BatchProcessor(
            analyzer=analyzer,
            batch_size=5,
            delay_seconds=1.0
        )

        self.scorer = opportunity_scorer or OpportunityScorer()
        self.cache = cache_manager or CacheManager(ttl_hours=24)
        self.use_cache = use_cache

        logger.info(
            f"SmartDiscoveryService 초기화 "
            f"(캐시 사용: {use_cache})"
        )

    def discover(
        self,
        seed_keyword: str,
        use_autocomplete: bool = True,
        min_grade: str = 'C',
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> DiscoveryResult:
        """
        스마트 발굴 실행

        5단계 파이프라인:
        1. 캐시 확인
        2. 키워드 생성 (롱테일 + 자동완성)
        3. 배치 분석
        4. 기회 점수 계산
        5. 등급 필터링

        Args:
            seed_keyword: 시드 키워드
            use_autocomplete: 자동완성 사용 여부
            min_grade: 최소 등급 (기본: C)
            progress_callback: 진행률 콜백 (stage, current, total)

        Returns:
            DiscoveryResult 객체
        """
        if not seed_keyword or not seed_keyword.strip():
            raise ValueError("시드 키워드가 비어있습니다")

        seed_keyword = seed_keyword.strip()
        logger.info(f"스마트 발굴 시작: '{seed_keyword}'")

        started_at = datetime.now()

        # Stage 1: 캐시 확인
        self._report_progress(progress_callback, "캐시 확인", 1, 5)

        if self.use_cache:
            cached = self._check_cache(seed_keyword)
            if cached:
                logger.info("캐시 히트 - 저장된 결과 반환")
                return cached

        # Stage 2: 키워드 생성
        self._report_progress(progress_callback, "키워드 생성", 2, 5)

        generated_keywords = self._generate_keywords(
            seed_keyword,
            use_autocomplete
        )

        logger.info(f"생성된 키워드: {len(generated_keywords)}개")

        # Stage 3: 배치 분석
        self._report_progress(progress_callback, "트렌드 분석", 3, 5)

        trends = self._analyze_keywords(generated_keywords)

        logger.info(f"분석 완료: {len(trends)}개")

        # Stage 4: 기회 점수 계산
        self._report_progress(progress_callback, "기회 점수 계산", 4, 5)

        opportunities = self._calculate_scores(trends)

        logger.info(f"점수 계산 완료: {len(opportunities)}개")

        # Stage 5: 등급 필터링
        self._report_progress(progress_callback, "등급 필터링", 5, 5)

        filtered_opps = self.scorer.filter_by_grade(opportunities, min_grade)

        logger.info(
            f"필터링 완료: {len(opportunities)}개 → {len(filtered_opps)}개 "
            f"(최소 등급: {min_grade})"
        )

        # 결과 생성
        result = DiscoveryResult(
            seed_keyword=seed_keyword,
            generated_count=len(generated_keywords),
            analyzed_count=len(trends),
            opportunities=filtered_opps,
            cache_hit=False,
            started_at=started_at,
            completed_at=datetime.now()
        )

        # 캐시 저장
        if self.use_cache:
            self._save_to_cache(seed_keyword, result)

        logger.info(
            f"스마트 발굴 완료: {result.analyzed_count}개 분석, "
            f"{len(result.opportunities)}개 기회 발견 "
            f"({result.processing_time:.1f}초)"
        )

        return result

    def _check_cache(self, seed_keyword: str) -> Optional[DiscoveryResult]:
        """
        캐시 확인 및 로드

        Args:
            seed_keyword: 시드 키워드

        Returns:
            캐시된 DiscoveryResult (없으면 None)
        """
        try:
            cached_data = self.cache.load_result(seed_keyword)

            if not cached_data:
                return None

            # 캐시 데이터를 DiscoveryResult로 복원
            result_data = cached_data.get('result', {})

            # OpportunityScore 리스트 복원
            opportunities = [
                OpportunityScore(**opp_data)
                for opp_data in result_data.get('opportunities', [])
            ]

            result = DiscoveryResult(
                seed_keyword=result_data.get('seed_keyword', seed_keyword),
                generated_count=result_data.get('generated_count', 0),
                analyzed_count=result_data.get('analyzed_count', 0),
                opportunities=opportunities,
                cache_hit=True,
                started_at=datetime.fromisoformat(result_data.get('started_at')),
                completed_at=datetime.fromisoformat(result_data.get('completed_at'))
            )

            return result

        except Exception as e:
            logger.error(f"캐시 로드 실패: {str(e)}")
            return None

    def _save_to_cache(self, seed_keyword: str, result: DiscoveryResult) -> None:
        """
        결과를 캐시에 저장

        Args:
            seed_keyword: 시드 키워드
            result: DiscoveryResult 객체
        """
        try:
            # Pydantic 모델을 딕셔너리로 변환
            if hasattr(result, 'model_dump'):
                result_dict = result.model_dump()
            else:
                # Fallback for non-pydantic
                result_dict = {
                    'seed_keyword': result.seed_keyword,
                    'generated_count': result.generated_count,
                    'analyzed_count': result.analyzed_count,
                    'opportunities': [
                        opp.model_dump() if hasattr(opp, 'model_dump') else vars(opp)
                        for opp in result.opportunities
                    ],
                    'cache_hit': result.cache_hit,
                    'started_at': result.started_at.isoformat(),
                    'completed_at': result.completed_at.isoformat()
                }

            metadata = {
                'processing_time': result.processing_time,
                'success_rate': result.success_rate,
                'average_score': result.average_score
            }

            self.cache.save_result(seed_keyword, result_dict, metadata)

            logger.info(f"캐시 저장 완료: {seed_keyword}")

        except Exception as e:
            logger.error(f"캐시 저장 실패: {str(e)}")

    def _generate_keywords(
        self,
        seed_keyword: str,
        use_autocomplete: bool
    ) -> List[str]:
        """
        키워드 생성 (롱테일 + 자동완성)

        Args:
            seed_keyword: 시드 키워드
            use_autocomplete: 자동완성 사용 여부

        Returns:
            생성된 키워드 리스트
        """
        keywords = set()

        # 롱테일 생성
        try:
            longtail = self.longtail_gen.generate(seed_keyword)
            keywords.update(longtail)
            logger.debug(f"롱테일 생성: {len(longtail)}개")
        except Exception as e:
            logger.error(f"롱테일 생성 실패: {str(e)}")

        # 자동완성 생성
        if use_autocomplete:
            try:
                autocomplete = self.autocomplete_gen.generate(seed_keyword)
                keywords.update(autocomplete)
                logger.debug(f"자동완성 생성: {len(autocomplete)}개")
            except Exception as e:
                logger.error(f"자동완성 생성 실패: {str(e)}")

        return list(keywords)

    def _analyze_keywords(self, keywords: List[str]) -> List[KeywordTrend]:
        """
        키워드 배치 분석

        Args:
            keywords: 분석할 키워드 리스트

        Returns:
            KeywordTrend 리스트
        """
        if not keywords:
            logger.warning("분석할 키워드가 없습니다")
            return []

        try:
            trends = self.batch_processor.process(keywords)
            return trends

        except Exception as e:
            logger.error(f"키워드 분석 실패: {str(e)}")
            return []

    def _calculate_scores(
        self,
        trends: List[KeywordTrend]
    ) -> List[OpportunityScore]:
        """
        기회 점수 계산

        Args:
            trends: KeywordTrend 리스트

        Returns:
            OpportunityScore 리스트
        """
        if not trends:
            logger.warning("점수 계산할 트렌드가 없습니다")
            return []

        try:
            scores = self.scorer.calculate_batch(trends)
            return scores

        except Exception as e:
            logger.error(f"점수 계산 실패: {str(e)}")
            return []

    def _report_progress(
        self,
        callback: Optional[Callable[[str, int, int], None]],
        stage: str,
        current: int,
        total: int
    ) -> None:
        """
        진행률 보고

        Args:
            callback: 콜백 함수
            stage: 현재 단계 이름
            current: 현재 단계 번호
            total: 전체 단계 수
        """
        if callback:
            try:
                callback(stage, current, total)
            except Exception as e:
                logger.error(f"진행률 콜백 실패: {str(e)}")

        logger.info(f"[{current}/{total}] {stage}")

    def get_cache_stats(self) -> dict:
        """
        캐시 통계 반환

        Returns:
            캐시 통계 딕셔너리
        """
        return self.cache.get_cache_stats()

    def clear_cache(self) -> int:
        """
        캐시 전체 삭제

        Returns:
            삭제된 캐시 개수
        """
        return self.cache.clear_all()

    def clear_expired_cache(self) -> int:
        """
        만료된 캐시 삭제

        Returns:
            삭제된 캐시 개수
        """
        return self.cache.clear_expired()
