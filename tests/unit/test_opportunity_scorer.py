"""
OpportunityScorer 단위 테스트

v1.0.0 - Phase 3 Step 3.1
"""
import pytest
from backend.models.keyword_trend import KeywordTrend
from backend.models.opportunity_score import OpportunityScore
from backend.services.opportunity_scorer import OpportunityScorer


@pytest.fixture
def scorer():
    """기본 OpportunityScorer 인스턴스"""
    return OpportunityScorer()


@pytest.fixture
def high_quality_trend():
    """높은 품질의 트렌드 데이터"""
    return KeywordTrend(
        keyword="겨울 롱패딩 추천",
        average_ratio=75.0,
        recent_ratio=85.0,
        momentum=20.0,
        trend_direction='rising',
        velocity=5.0,
        total_score=80.0
    )


@pytest.fixture
def low_quality_trend():
    """낮은 품질의 트렌드 데이터"""
    return KeywordTrend(
        keyword="abc",
        average_ratio=10.0,
        recent_ratio=8.0,
        momentum=-30.0,
        trend_direction='falling',
        velocity=-5.0,
        total_score=15.0
    )


@pytest.fixture
def medium_trend():
    """중간 품질의 트렌드 데이터"""
    return KeywordTrend(
        keyword="노트북 구매",
        average_ratio=50.0,
        recent_ratio=55.0,
        momentum=5.0,
        trend_direction='stable',
        velocity=1.0,
        total_score=52.0
    )


def test_scorer_initialization():
    """Scorer 초기화 테스트"""
    scorer = OpportunityScorer()

    assert scorer.demand_weight == 0.30
    assert scorer.momentum_weight == 0.35
    assert scorer.gap_weight == 0.20
    assert scorer.suitability_weight == 0.15


def test_scorer_custom_weights():
    """커스텀 가중치 설정 테스트"""
    scorer = OpportunityScorer(
        demand_weight=0.40,
        momentum_weight=0.30,
        gap_weight=0.20,
        suitability_weight=0.10
    )

    assert scorer.demand_weight == 0.40
    assert scorer.momentum_weight == 0.30


def test_scorer_invalid_weights():
    """잘못된 가중치 검증"""
    with pytest.raises(ValueError):
        OpportunityScorer(
            demand_weight=0.50,
            momentum_weight=0.30,
            gap_weight=0.10,
            suitability_weight=0.05  # 합계 0.95
        )


def test_calculate_high_quality(scorer, high_quality_trend):
    """높은 품질 키워드 점수 계산"""
    score = scorer.calculate(high_quality_trend)

    assert isinstance(score, OpportunityScore)
    assert score.keyword == "겨울 롱패딩 추천"
    assert score.total_score >= 60.0  # 높은 점수 기대
    assert score.grade in ['S', 'A', 'B']


def test_calculate_low_quality(scorer, low_quality_trend):
    """낮은 품질 키워드 점수 계산"""
    score = scorer.calculate(low_quality_trend)

    assert isinstance(score, OpportunityScore)
    assert score.total_score < 50.0  # 낮은 점수 기대
    assert score.grade in ['C', 'D']


def test_search_demand_calculation(scorer, high_quality_trend):
    """검색 수요 점수 계산 테스트"""
    demand = scorer._calculate_search_demand(high_quality_trend)

    assert 0 <= demand <= 100
    assert demand == 75.0  # average_ratio와 동일


def test_momentum_score_calculation(scorer):
    """모멘텀 점수 계산 테스트"""
    # 상승 추세
    rising_trend = KeywordTrend(
        keyword="test",
        average_ratio=50,
        recent_ratio=60,
        momentum=50.0,
        total_score=60
    )
    rising_score = scorer._calculate_momentum_score(rising_trend)
    assert rising_score >= 50  # 상승은 50점 이상

    # 하락 추세
    falling_trend = KeywordTrend(
        keyword="test",
        average_ratio=50,
        recent_ratio=30,
        momentum=-40.0,
        total_score=40
    )
    falling_score = scorer._calculate_momentum_score(falling_trend)
    assert falling_score <= 50  # 하락은 50점 이하


def test_competition_gap_calculation(scorer, medium_trend):
    """경쟁 공백 점수 계산 테스트"""
    gap = scorer._calculate_competition_gap(medium_trend)

    assert 0 <= gap <= 100
    # recent_ratio의 80%
    expected = medium_trend.recent_ratio * 0.8
    assert abs(gap - expected) < 0.1


def test_suitability_calculation(scorer):
    """적합도 점수 계산 테스트"""
    # 블로그 친화적 키워드
    blog_friendly = KeywordTrend(
        keyword="겨울 롱패딩 추천",
        average_ratio=50,
        recent_ratio=50,
        total_score=50
    )
    friendly_score = scorer._calculate_suitability(blog_friendly)

    # 비친화적 키워드
    unfriendly = KeywordTrend(
        keyword="a",
        average_ratio=50,
        recent_ratio=50,
        total_score=50
    )
    unfriendly_score = scorer._calculate_suitability(unfriendly)

    assert friendly_score > unfriendly_score


def test_calculate_batch(scorer):
    """배치 계산 테스트"""
    trends = [
        KeywordTrend(
            keyword=f"키워드{i}",
            average_ratio=50 + i * 10,
            recent_ratio=60 + i * 5,
            momentum=i * 5,
            total_score=50 + i * 5
        )
        for i in range(5)
    ]

    scores = scorer.calculate_batch(trends)

    assert len(scores) == 5
    assert all(isinstance(s, OpportunityScore) for s in scores)


def test_filter_by_grade(scorer):
    """등급 필터링 테스트"""
    scores = [
        OpportunityScore(
            keyword=f"키워드{i}",
            search_demand=50 + i * 10,
            momentum=60 + i * 10,
            competition_gap=40,
            suitability=50
        )
        for i in range(5)
    ]

    # C 등급 이상 필터링
    filtered = scorer.filter_by_grade(scores, min_grade='C')

    assert len(filtered) <= len(scores)
    assert all(s.grade in ['S', 'A', 'B', 'C'] for s in filtered)


def test_grade_distribution(scorer):
    """등급 분포 통계 테스트"""
    scores = [
        OpportunityScore(
            keyword="S급",
            search_demand=90,
            momentum=90,
            competition_gap=80,
            suitability=85
        ),
        OpportunityScore(
            keyword="A급",
            search_demand=70,
            momentum=75,
            competition_gap=65,
            suitability=60
        ),
        OpportunityScore(
            keyword="D급",
            search_demand=20,
            momentum=25,
            competition_gap=15,
            suitability=30
        )
    ]

    distribution = scorer.get_grade_distribution(scores)

    assert distribution['S'] >= 1
    assert distribution['A'] >= 1
    assert distribution['D'] >= 1
    assert sum(distribution.values()) == 3


def test_get_top_opportunities(scorer):
    """상위 기회 추출 테스트"""
    scores = [
        OpportunityScore(
            keyword=f"키워드{i}",
            search_demand=30 + i * 5,
            momentum=40 + i * 5,
            competition_gap=35 + i * 3,
            suitability=45 + i * 2
        )
        for i in range(10)
    ]

    top_5 = scorer.get_top_opportunities(scores, top_n=5)

    assert len(top_5) == 5
    # 점수 내림차순 확인
    for i in range(len(top_5) - 1):
        assert top_5[i].total_score >= top_5[i + 1].total_score


def test_opportunity_score_properties():
    """OpportunityScore 속성 테스트"""
    score = OpportunityScore(
        keyword="테스트 키워드",
        search_demand=70,
        momentum=80,
        competition_gap=60,
        suitability=65,
        average_ratio=50.0,
        recent_ratio=55.0,
        momentum_value=10.0
    )

    # 종합 점수 계산 확인
    expected = 70 * 0.30 + 80 * 0.35 + 60 * 0.20 + 65 * 0.15
    assert abs(score.total_score - expected) < 0.01

    # 등급 확인
    assert score.grade in ['S', 'A', 'B', 'C', 'D']

    # 등급 이유
    assert isinstance(score.grade_reason, str)
    assert len(score.grade_reason) > 0


def test_strongest_weakest_factors():
    """최강/최약 요인 테스트"""
    score = OpportunityScore(
        keyword="테스트",
        search_demand=90,  # 최강
        momentum=50,
        competition_gap=60,
        suitability=40  # 최약
    )

    strongest = score.get_strongest_factor()
    weakest = score.get_weakest_factor()

    assert strongest[0] == '검색 수요'
    assert strongest[1] == 90

    assert weakest[0] == '블로그 적합도'
    assert weakest[1] == 40


def test_score_summary():
    """점수 요약 테스트"""
    score = OpportunityScore(
        keyword="겨울 패션",
        search_demand=75,
        momentum=70,
        competition_gap=65,
        suitability=80
    )

    summary = score.to_summary()

    assert isinstance(summary, str)
    assert "겨울 패션" in summary
    assert score.grade in summary
    assert "점" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
