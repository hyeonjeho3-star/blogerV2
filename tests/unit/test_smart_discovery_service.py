"""
SmartDiscoveryService 단위 테스트

v1.0.0 - Phase 3 Step 3.3
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from backend.models.keyword_trend import KeywordTrend
from backend.models.opportunity_score import OpportunityScore
from backend.models.discovery_result import DiscoveryResult
from backend.services.smart_discovery_service import SmartDiscoveryService
from backend.generators.keyword_generator import LongTailGenerator
from backend.services.opportunity_scorer import OpportunityScorer


@pytest.fixture
def mock_longtail_gen():
    """Mock LongTailGenerator"""
    gen = Mock()
    gen.generate.return_value = [
        "롱패딩",
        "롱패딩 추천",
        "롱패딩 세탁",
        "롱패딩 방법"
    ]
    return gen


@pytest.fixture
def mock_autocomplete_gen():
    """Mock AutocompleteGenerator"""
    gen = Mock()
    gen.generate.return_value = [
        "롱패딩 코디",
        "롱패딩 후기"
    ]
    return gen


@pytest.fixture
def mock_batch_processor():
    """Mock BatchProcessor"""
    processor = Mock()
    processor.process.return_value = [
        KeywordTrend(
            keyword="롱패딩",
            average_ratio=75.0,
            recent_ratio=80.0,
            momentum=15.0,
            total_score=77.0
        ),
        KeywordTrend(
            keyword="롱패딩 추천",
            average_ratio=65.0,
            recent_ratio=70.0,
            momentum=10.0,
            total_score=68.0
        )
    ]
    return processor


@pytest.fixture
def mock_cache_manager(tmp_path):
    """Mock CacheManager"""
    cache = Mock()
    cache.load_result.return_value = None  # 기본적으로 캐시 미스
    cache.save_result.return_value = str(tmp_path / "cache.json")
    cache.get_cache_stats.return_value = {
        "total_count": 0,
        "valid_count": 0
    }
    return cache


@pytest.fixture
def discovery_service(
    mock_longtail_gen,
    mock_autocomplete_gen,
    mock_batch_processor,
    mock_cache_manager
):
    """SmartDiscoveryService 인스턴스"""
    scorer = OpportunityScorer()

    service = SmartDiscoveryService(
        longtail_generator=mock_longtail_gen,
        autocomplete_generator=mock_autocomplete_gen,
        batch_processor=mock_batch_processor,
        opportunity_scorer=scorer,
        cache_manager=mock_cache_manager,
        use_cache=True
    )

    return service


def test_service_initialization():
    """서비스 초기화 테스트"""
    service = SmartDiscoveryService(use_cache=False)

    assert service.longtail_gen is not None
    assert service.autocomplete_gen is not None
    assert service.batch_processor is not None
    assert service.scorer is not None
    assert service.use_cache == False


def test_discover_basic(discovery_service):
    """기본 발굴 테스트"""
    result = discovery_service.discover("롱패딩", min_grade='D')

    assert isinstance(result, DiscoveryResult)
    assert result.seed_keyword == "롱패딩"
    assert result.generated_count > 0
    assert result.analyzed_count > 0
    assert len(result.opportunities) > 0


def test_discover_with_autocomplete(
    mock_longtail_gen,
    mock_autocomplete_gen,
    mock_batch_processor,
    mock_cache_manager
):
    """자동완성 포함 발굴 테스트"""
    service = SmartDiscoveryService(
        longtail_generator=mock_longtail_gen,
        autocomplete_generator=mock_autocomplete_gen,
        batch_processor=mock_batch_processor,
        cache_manager=mock_cache_manager,
        use_cache=False
    )

    result = service.discover("롱패딩", use_autocomplete=True)

    # 자동완성 생성기 호출 확인
    mock_autocomplete_gen.generate.assert_called_once_with("롱패딩")


def test_discover_without_autocomplete(
    mock_longtail_gen,
    mock_autocomplete_gen,
    mock_batch_processor,
    mock_cache_manager
):
    """자동완성 없이 발굴 테스트"""
    service = SmartDiscoveryService(
        longtail_generator=mock_longtail_gen,
        autocomplete_generator=mock_autocomplete_gen,
        batch_processor=mock_batch_processor,
        cache_manager=mock_cache_manager,
        use_cache=False
    )

    result = service.discover("롱패딩", use_autocomplete=False)

    # 자동완성 생성기 호출되지 않음
    mock_autocomplete_gen.generate.assert_not_called()


def test_discover_with_grade_filter(discovery_service):
    """등급 필터링 테스트"""
    # A등급 이상만
    result = discovery_service.discover("롱패딩", min_grade='A')

    # 모든 결과가 A등급 이상인지 확인
    for opp in result.opportunities:
        assert opp.grade in ['S', 'A']


def test_discover_with_progress_callback(discovery_service):
    """진행률 콜백 테스트"""
    progress_calls = []

    def progress_callback(stage, current, total):
        progress_calls.append((stage, current, total))

    result = discovery_service.discover(
        "롱패딩",
        progress_callback=progress_callback
    )

    # 5단계 진행
    assert len(progress_calls) == 5
    assert progress_calls[0][1] == 1  # 첫 단계
    assert progress_calls[-1][1] == 5  # 마지막 단계


def test_discover_empty_keyword(discovery_service):
    """빈 키워드 검증"""
    with pytest.raises(ValueError):
        discovery_service.discover("")


def test_cache_hit(
    mock_longtail_gen,
    mock_autocomplete_gen,
    mock_batch_processor,
    mock_cache_manager
):
    """캐시 히트 테스트"""
    # 캐시된 결과 설정
    cached_result_data = {
        'result': {
            'seed_keyword': '롱패딩',
            'generated_count': 10,
            'analyzed_count': 8,
            'opportunities': [
                {
                    'keyword': '롱패딩',
                    'search_demand': 75.0,
                    'momentum': 80.0,
                    'competition_gap': 60.0,
                    'suitability': 70.0,
                    'average_ratio': 50.0,
                    'recent_ratio': 55.0,
                    'momentum_value': 10.0
                }
            ],
            'cache_hit': True,
            'started_at': datetime.now().isoformat(),
            'completed_at': datetime.now().isoformat()
        }
    }

    mock_cache_manager.load_result.return_value = cached_result_data

    service = SmartDiscoveryService(
        longtail_generator=mock_longtail_gen,
        autocomplete_generator=mock_autocomplete_gen,
        batch_processor=mock_batch_processor,
        cache_manager=mock_cache_manager,
        use_cache=True
    )

    result = service.discover("롱패딩")

    # 캐시 히트 확인
    assert result.cache_hit == True

    # 분석 프로세서 호출되지 않음
    mock_batch_processor.process.assert_not_called()


def test_cache_save(discovery_service, mock_cache_manager):
    """캐시 저장 테스트"""
    result = discovery_service.discover("롱패딩")

    # 캐시 저장 호출 확인
    mock_cache_manager.save_result.assert_called_once()


def test_cache_disabled(
    mock_longtail_gen,
    mock_autocomplete_gen,
    mock_batch_processor,
    mock_cache_manager
):
    """캐시 비활성화 테스트"""
    service = SmartDiscoveryService(
        longtail_generator=mock_longtail_gen,
        autocomplete_generator=mock_autocomplete_gen,
        batch_processor=mock_batch_processor,
        cache_manager=mock_cache_manager,
        use_cache=False
    )

    result = service.discover("롱패딩")

    # 캐시 로드/저장 호출되지 않음
    mock_cache_manager.load_result.assert_not_called()
    mock_cache_manager.save_result.assert_not_called()


def test_generate_keywords(discovery_service):
    """키워드 생성 테스트"""
    keywords = discovery_service._generate_keywords("롱패딩", use_autocomplete=True)

    assert len(keywords) > 0
    assert isinstance(keywords, list)


def test_analyze_keywords(discovery_service, mock_batch_processor):
    """키워드 분석 테스트"""
    keywords = ["롱패딩", "롱패딩 추천"]

    trends = discovery_service._analyze_keywords(keywords)

    assert len(trends) > 0
    mock_batch_processor.process.assert_called_once_with(keywords)


def test_calculate_scores(discovery_service):
    """점수 계산 테스트"""
    trends = [
        KeywordTrend(
            keyword="롱패딩",
            average_ratio=75.0,
            recent_ratio=80.0,
            momentum=15.0,
            total_score=77.0
        )
    ]

    scores = discovery_service._calculate_scores(trends)

    assert len(scores) == 1
    assert isinstance(scores[0], OpportunityScore)


def test_get_cache_stats(discovery_service, mock_cache_manager):
    """캐시 통계 조회 테스트"""
    stats = discovery_service.get_cache_stats()

    assert 'total_count' in stats
    mock_cache_manager.get_cache_stats.assert_called_once()


def test_clear_cache(discovery_service, mock_cache_manager):
    """캐시 삭제 테스트"""
    mock_cache_manager.clear_all.return_value = 5

    deleted = discovery_service.clear_cache()

    assert deleted == 5
    mock_cache_manager.clear_all.assert_called_once()


def test_clear_expired_cache(discovery_service, mock_cache_manager):
    """만료 캐시 삭제 테스트"""
    mock_cache_manager.clear_expired.return_value = 3

    deleted = discovery_service.clear_expired_cache()

    assert deleted == 3
    mock_cache_manager.clear_expired.assert_called_once()


def test_discovery_result_properties():
    """DiscoveryResult 속성 테스트"""
    result = DiscoveryResult(
        seed_keyword="롱패딩",
        generated_count=30,
        analyzed_count=28,
        opportunities=[
            OpportunityScore(
                keyword="롱패딩",
                search_demand=80,
                momentum=75,
                competition_gap=70,
                suitability=65
            ),
            OpportunityScore(
                keyword="롱패딩 추천",
                search_demand=60,
                momentum=55,
                competition_gap=50,
                suitability=45
            )
        ]
    )

    # 성공률
    assert result.success_rate > 90.0

    # 평균 점수
    assert result.average_score > 0

    # 최고 기회
    assert result.best_opportunity.keyword == "롱패딩"

    # 등급 분포
    dist = result.grade_distribution
    assert isinstance(dist, dict)


def test_discovery_result_top_opportunities():
    """상위 기회 추출 테스트"""
    opportunities = [
        OpportunityScore(
            keyword=f"키워드{i}",
            search_demand=50 + i * 3,
            momentum=60 + i * 3,
            competition_gap=55,
            suitability=50
        )
        for i in range(10)
    ]

    result = DiscoveryResult(
        seed_keyword="테스트",
        generated_count=10,
        analyzed_count=10,
        opportunities=opportunities
    )

    top_5 = result.get_top_opportunities(top_n=5)

    assert len(top_5) == 5
    # 점수 내림차순 확인
    for i in range(len(top_5) - 1):
        assert top_5[i].total_score >= top_5[i + 1].total_score


def test_discovery_result_filter_by_grade():
    """등급 필터링 테스트"""
    opportunities = [
        OpportunityScore(
            keyword="S급",
            search_demand=90,
            momentum=85,
            competition_gap=80,
            suitability=85
        ),
        OpportunityScore(
            keyword="C급",
            search_demand=40,
            momentum=45,
            competition_gap=35,
            suitability=40
        )
    ]

    result = DiscoveryResult(
        seed_keyword="테스트",
        generated_count=2,
        analyzed_count=2,
        opportunities=opportunities
    )

    filtered = result.filter_by_grade(min_grade='B')

    # C급은 제외되어야 함
    assert len(filtered) == 1
    assert filtered[0].grade == 'S'


def test_discovery_result_summary():
    """결과 요약 테스트"""
    result = DiscoveryResult(
        seed_keyword="롱패딩",
        generated_count=30,
        analyzed_count=28,
        opportunities=[
            OpportunityScore(
                keyword="롱패딩",
                search_demand=80,
                momentum=75,
                competition_gap=70,
                suitability=65
            )
        ]
    )

    summary = result.to_summary()

    assert isinstance(summary, str)
    assert "롱패딩" in summary
    assert "30개" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
