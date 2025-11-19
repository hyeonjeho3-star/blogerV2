"""
캐시 관리 시스템
파일 기반 JSON 캐싱, TTL 지원

v1.0.0 - Phase 3 Step 3.2
"""
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """파일 기반 캐시 관리자"""

    def __init__(
        self,
        cache_dir: str = ".cache",
        ttl_hours: int = 24,
        index_file: str = "cache_index.json"
    ):
        """
        초기화

        Args:
            cache_dir: 캐시 저장 디렉토리
            ttl_hours: 캐시 유효 시간 (시간)
            index_file: 인덱스 파일명
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.index_file = self.cache_dir / index_file

        # 디렉토리 생성
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 인덱스 로드 또는 초기화
        self.index = self._load_index()

        logger.info(
            f"CacheManager 초기화 "
            f"(디렉토리={cache_dir}, TTL={ttl_hours}시간)"
        )

    def save_result(
        self,
        seed_keyword: str,
        result_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        분석 결과 저장

        Args:
            seed_keyword: 시드 키워드
            result_data: 저장할 결과 데이터
            metadata: 추가 메타데이터

        Returns:
            캐시 파일 경로
        """
        # 파일명 생성 (타임스탬프 포함)
        timestamp = int(time.time())
        safe_keyword = self._sanitize_filename(seed_keyword)
        filename = f"{safe_keyword}_{timestamp}.json"
        filepath = self.cache_dir / filename

        # 캐시 데이터 구성
        cache_data = {
            "seed_keyword": seed_keyword,
            "cached_at": datetime.now().isoformat(),
            "expires_at": (
                datetime.now() + timedelta(hours=self.ttl_hours)
            ).isoformat(),
            "metadata": metadata or {},
            "result": result_data
        }

        # 파일 저장
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            # 인덱스 업데이트
            self._update_index(seed_keyword, str(filepath), cache_data)

            logger.info(f"캐시 저장 완료: {seed_keyword} → {filename}")

            return str(filepath)

        except Exception as e:
            logger.error(f"캐시 저장 실패: {str(e)}")
            raise

    def load_result(self, seed_keyword: str) -> Optional[Dict[str, Any]]:
        """
        캐시된 결과 로드

        Args:
            seed_keyword: 시드 키워드

        Returns:
            캐시 데이터 (만료되었거나 없으면 None)
        """
        # 인덱스에서 검색
        cache_info = self.index.get(seed_keyword)

        if not cache_info:
            logger.debug(f"캐시 없음: {seed_keyword}")
            return None

        filepath = Path(cache_info['filepath'])

        # 파일 존재 확인
        if not filepath.exists():
            logger.warning(f"캐시 파일 없음: {filepath}")
            self._remove_from_index(seed_keyword)
            return None

        # 파일 로드
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 만료 확인
            expires_at = datetime.fromisoformat(cache_data['expires_at'])
            if datetime.now() > expires_at:
                logger.info(f"캐시 만료: {seed_keyword}")
                self._delete_cache_file(filepath)
                self._remove_from_index(seed_keyword)
                return None

            logger.info(f"캐시 히트: {seed_keyword}")
            return cache_data

        except Exception as e:
            logger.error(f"캐시 로드 실패: {str(e)}")
            return None

    def find_by_seed(self, seed_keyword: str) -> Optional[Dict[str, Any]]:
        """
        시드 키워드로 캐시 검색 (load_result 별칭)

        Args:
            seed_keyword: 시드 키워드

        Returns:
            캐시 데이터
        """
        return self.load_result(seed_keyword)

    def is_cached(self, seed_keyword: str) -> bool:
        """
        캐시 존재 여부 확인

        Args:
            seed_keyword: 시드 키워드

        Returns:
            캐시 존재 여부
        """
        result = self.load_result(seed_keyword)
        return result is not None

    def clear_expired(self) -> int:
        """
        만료된 캐시 삭제

        Returns:
            삭제된 캐시 개수
        """
        deleted_count = 0

        for seed_keyword in list(self.index.keys()):
            cache_info = self.index[seed_keyword]
            filepath = Path(cache_info['filepath'])

            # 파일 존재 확인
            if not filepath.exists():
                self._remove_from_index(seed_keyword)
                deleted_count += 1
                continue

            # 만료 확인
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                expires_at = datetime.fromisoformat(cache_data['expires_at'])
                if datetime.now() > expires_at:
                    self._delete_cache_file(filepath)
                    self._remove_from_index(seed_keyword)
                    deleted_count += 1

            except Exception as e:
                logger.error(f"만료 확인 실패: {filepath} - {str(e)}")

        logger.info(f"만료 캐시 삭제 완료: {deleted_count}개")

        return deleted_count

    def clear_all(self) -> int:
        """
        모든 캐시 삭제

        Returns:
            삭제된 캐시 개수
        """
        deleted_count = 0

        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file.name != self.index_file.name:
                try:
                    cache_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"파일 삭제 실패: {cache_file} - {str(e)}")

        # 인덱스 초기화
        self.index = {}
        self._save_index()

        logger.info(f"전체 캐시 삭제 완료: {deleted_count}개")

        return deleted_count

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        캐시 통계 반환

        Returns:
            통계 딕셔너리
        """
        total_count = len(self.index)
        expired_count = 0
        valid_count = 0

        for seed_keyword in self.index.keys():
            if self.is_cached(seed_keyword):
                valid_count += 1
            else:
                expired_count += 1

        cache_size = sum(
            f.stat().st_size
            for f in self.cache_dir.glob("*.json")
            if f.name != self.index_file.name
        )

        return {
            "total_count": total_count,
            "valid_count": valid_count,
            "expired_count": expired_count,
            "cache_size_bytes": cache_size,
            "cache_dir": str(self.cache_dir)
        }

    def list_cached_keywords(self) -> List[str]:
        """
        캐시된 키워드 목록 반환

        Returns:
            키워드 리스트
        """
        return list(self.index.keys())

    def _load_index(self) -> Dict[str, Any]:
        """인덱스 파일 로드"""
        if not self.index_file.exists():
            logger.debug("인덱스 파일 없음, 새로 생성")
            return {}

        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
            logger.debug(f"인덱스 로드 완료: {len(index)}개")
            return index

        except Exception as e:
            logger.error(f"인덱스 로드 실패: {str(e)}")
            return {}

    def _save_index(self) -> None:
        """인덱스 파일 저장"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
            logger.debug("인덱스 저장 완료")

        except Exception as e:
            logger.error(f"인덱스 저장 실패: {str(e)}")

    def _update_index(
        self,
        seed_keyword: str,
        filepath: str,
        cache_data: Dict[str, Any]
    ) -> None:
        """인덱스 업데이트"""
        self.index[seed_keyword] = {
            "filepath": filepath,
            "cached_at": cache_data['cached_at'],
            "expires_at": cache_data['expires_at']
        }
        self._save_index()

    def _remove_from_index(self, seed_keyword: str) -> None:
        """인덱스에서 제거"""
        if seed_keyword in self.index:
            del self.index[seed_keyword]
            self._save_index()

    def _delete_cache_file(self, filepath: Path) -> None:
        """캐시 파일 삭제"""
        try:
            filepath.unlink()
            logger.debug(f"캐시 파일 삭제: {filepath}")
        except Exception as e:
            logger.error(f"파일 삭제 실패: {filepath} - {str(e)}")

    def _sanitize_filename(self, keyword: str) -> str:
        """
        파일명 안전 문자열 변환

        Args:
            keyword: 원본 키워드

        Returns:
            안전한 파일명
        """
        # 윈도우/리눅스 모두 금지 문자 제거
        invalid_chars = '<>:"/\\|?*'
        safe = keyword

        for char in invalid_chars:
            safe = safe.replace(char, '_')

        # 공백을 언더스코어로
        safe = safe.replace(' ', '_')

        # 최대 길이 제한
        max_length = 50
        if len(safe) > max_length:
            safe = safe[:max_length]

        return safe

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        # 만료 캐시 정리
        self.clear_expired()
        return False
