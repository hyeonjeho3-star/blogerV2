"""
CacheManager 단위 테스트

v1.0.0 - Phase 3 Step 3.2
"""
import pytest
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from backend.utils.cache_manager import CacheManager


@pytest.fixture
def temp_cache_dir(tmp_path):
    """임시 캐시 디렉토리"""
    return str(tmp_path / "test_cache")


@pytest.fixture
def cache_manager(temp_cache_dir):
    """테스트용 CacheManager"""
    return CacheManager(cache_dir=temp_cache_dir, ttl_hours=24)


@pytest.fixture
def short_ttl_manager(temp_cache_dir):
    """짧은 TTL을 가진 CacheManager (테스트용)"""
    # 1초 TTL (실제로는 hours지만 테스트를 위해)
    return CacheManager(cache_dir=temp_cache_dir, ttl_hours=0.0003)  # ~1초


@pytest.fixture
def sample_result():
    """샘플 분석 결과"""
    return {
        "keywords": ["롱패딩", "롱패딩 추천", "롱패딩 세탁"],
        "scores": [85.0, 78.0, 65.0],
        "best_keyword": "롱패딩"
    }


def test_cache_manager_initialization(cache_manager, temp_cache_dir):
    """CacheManager 초기화 테스트"""
    assert cache_manager.cache_dir == Path(temp_cache_dir)
    assert cache_manager.ttl_hours == 24
    assert cache_manager.cache_dir.exists()
    assert isinstance(cache_manager.index, dict)


def test_save_and_load_result(cache_manager, sample_result):
    """결과 저장 및 로드 테스트"""
    seed = "롱패딩"

    # 저장
    filepath = cache_manager.save_result(seed, sample_result)
    assert filepath is not None
    assert Path(filepath).exists()

    # 로드
    cached = cache_manager.load_result(seed)
    assert cached is not None
    assert cached['seed_keyword'] == seed
    assert cached['result'] == sample_result


def test_save_with_metadata(cache_manager, sample_result):
    """메타데이터 포함 저장 테스트"""
    seed = "롱패딩"
    metadata = {
        "total_analyzed": 30,
        "success_rate": 100.0,
        "processing_time": 5.2
    }

    filepath = cache_manager.save_result(seed, sample_result, metadata)

    # 로드 및 검증
    cached = cache_manager.load_result(seed)
    assert cached['metadata'] == metadata


def test_is_cached(cache_manager, sample_result):
    """캐시 존재 여부 확인 테스트"""
    seed = "롱패딩"

    # 저장 전
    assert not cache_manager.is_cached(seed)

    # 저장 후
    cache_manager.save_result(seed, sample_result)
    assert cache_manager.is_cached(seed)


def test_find_by_seed(cache_manager, sample_result):
    """시드로 캐시 검색 테스트"""
    seed = "롱패딩"

    cache_manager.save_result(seed, sample_result)

    # find_by_seed는 load_result 별칭
    cached = cache_manager.find_by_seed(seed)
    assert cached is not None
    assert cached['seed_keyword'] == seed


def test_cache_expiration(short_ttl_manager, sample_result):
    """캐시 만료 테스트"""
    seed = "롱패딩"

    # 저장
    short_ttl_manager.save_result(seed, sample_result)
    assert short_ttl_manager.is_cached(seed)

    # 2초 대기 (TTL 초과)
    time.sleep(2)

    # 만료 확인
    cached = short_ttl_manager.load_result(seed)
    assert cached is None
    assert not short_ttl_manager.is_cached(seed)


def test_clear_expired(cache_manager, sample_result, short_ttl_manager):
    """만료 캐시 삭제 테스트"""
    # 일반 캐시 (만료 안 됨)
    cache_manager.save_result("롱패딩", sample_result)

    # 짧은 TTL 캐시
    short_ttl_manager.save_result("테스트", sample_result)
    time.sleep(2)  # 만료 대기

    # 만료 캐시 삭제
    deleted = short_ttl_manager.clear_expired()
    assert deleted >= 1


def test_clear_all(cache_manager, sample_result):
    """전체 캐시 삭제 테스트"""
    # 여러 캐시 저장
    keywords = ["롱패딩", "발열내의", "겨울코트"]
    for kw in keywords:
        cache_manager.save_result(kw, sample_result)

    # 전체 삭제
    deleted = cache_manager.clear_all()
    assert deleted == len(keywords)

    # 캐시 없음 확인
    for kw in keywords:
        assert not cache_manager.is_cached(kw)


def test_cache_stats(cache_manager, sample_result):
    """캐시 통계 테스트"""
    # 캐시 저장
    cache_manager.save_result("롱패딩", sample_result)
    cache_manager.save_result("발열내의", sample_result)

    stats = cache_manager.get_cache_stats()

    assert stats['total_count'] >= 2
    assert stats['valid_count'] >= 2
    assert stats['cache_size_bytes'] > 0
    assert 'cache_dir' in stats


def test_list_cached_keywords(cache_manager, sample_result):
    """캐시된 키워드 목록 테스트"""
    keywords = ["롱패딩", "발열내의", "겨울코트"]

    for kw in keywords:
        cache_manager.save_result(kw, sample_result)

    cached_list = cache_manager.list_cached_keywords()

    assert len(cached_list) == len(keywords)
    for kw in keywords:
        assert kw in cached_list


def test_sanitize_filename(cache_manager):
    """파일명 안전화 테스트"""
    # 특수 문자 포함 키워드
    dangerous = "롱패딩/추천<>:\"?*|"
    safe = cache_manager._sanitize_filename(dangerous)

    # 금지 문자가 모두 제거/변환되었는지
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        assert char not in safe

    # 공백 처리
    with_space = "롱패딩 추천"
    safe_space = cache_manager._sanitize_filename(with_space)
    assert ' ' not in safe_space


def test_multiple_saves_same_keyword(cache_manager, sample_result):
    """같은 키워드 여러 번 저장 테스트"""
    seed = "롱패딩"

    # 첫 번째 저장
    filepath1 = cache_manager.save_result(seed, sample_result)

    # 약간 대기 (타임스탬프 달라지게)
    time.sleep(0.1)

    # 두 번째 저장 (덮어쓰기)
    updated_result = {**sample_result, "updated": True}
    filepath2 = cache_manager.save_result(seed, updated_result)

    # 최신 결과만 로드되어야 함
    cached = cache_manager.load_result(seed)
    assert cached['result'].get('updated') == True


def test_context_manager(temp_cache_dir, sample_result):
    """컨텍스트 매니저 테스트"""
    with CacheManager(cache_dir=temp_cache_dir, ttl_hours=24) as cm:
        cm.save_result("롱패딩", sample_result)
        assert cm.is_cached("롱패딩")

    # 컨텍스트 종료 후에도 캐시 유지
    cm2 = CacheManager(cache_dir=temp_cache_dir, ttl_hours=24)
    assert cm2.is_cached("롱패딩")


def test_missing_cache_file(cache_manager, sample_result):
    """캐시 파일 누락 처리 테스트"""
    seed = "롱패딩"

    # 저장
    filepath = cache_manager.save_result(seed, sample_result)

    # 파일 직접 삭제
    Path(filepath).unlink()

    # 로드 시도 - None 반환되어야 함
    cached = cache_manager.load_result(seed)
    assert cached is None


def test_index_persistence(temp_cache_dir, sample_result):
    """인덱스 영속성 테스트"""
    # 첫 번째 매니저로 저장
    cm1 = CacheManager(cache_dir=temp_cache_dir, ttl_hours=24)
    cm1.save_result("롱패딩", sample_result)

    # 두 번째 매니저로 로드 (인덱스 복원)
    cm2 = CacheManager(cache_dir=temp_cache_dir, ttl_hours=24)
    cached = cm2.load_result("롱패딩")

    assert cached is not None
    assert cached['result'] == sample_result


def test_cache_timestamps(cache_manager, sample_result):
    """캐시 타임스탬프 검증"""
    seed = "롱패딩"
    cache_manager.save_result(seed, sample_result)

    cached = cache_manager.load_result(seed)

    # 타임스탬프 필드 존재
    assert 'cached_at' in cached
    assert 'expires_at' in cached

    # 파싱 가능한 ISO 형식
    cached_at = datetime.fromisoformat(cached['cached_at'])
    expires_at = datetime.fromisoformat(cached['expires_at'])

    # expires_at > cached_at
    assert expires_at > cached_at


def test_empty_result_data(cache_manager):
    """빈 결과 저장 테스트"""
    seed = "빈키워드"
    empty_result = {}

    filepath = cache_manager.save_result(seed, empty_result)
    assert filepath is not None

    cached = cache_manager.load_result(seed)
    assert cached['result'] == empty_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
