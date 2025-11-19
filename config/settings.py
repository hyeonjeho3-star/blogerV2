"""
애플리케이션 설정 관리
v1.0.3의 config/settings.py를 Pydantic Settings로 업그레이드
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경 변수 기반 설정"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # API Credentials
    naver_datalab_client_id: str = "dummy_id"
    naver_datalab_client_secret: str = "dummy_secret"
    naver_search_client_id: Optional[str] = None
    naver_search_client_secret: Optional[str] = None
    google_gemini_api_key: str = "dummy_key"

    # Redis (Optional)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Application
    app_name: str = "Blog Mate v2.0"
    log_level: str = "INFO"
    cache_enabled: bool = False
    max_batch_size: int = 5

    # Paths
    @property
    def base_dir(self) -> Path:
        """프로젝트 루트 디렉토리"""
        return Path(__file__).parent.parent

    @property
    def cache_dir(self) -> Path:
        """캐시 디렉토리"""
        path = self.base_dir / "data" / "cache"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def log_dir(self) -> Path:
        """로그 디렉토리"""
        path = self.base_dir / "data" / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def export_dir(self) -> Path:
        """내보내기 디렉토리"""
        path = self.base_dir / "data" / "exports"
        path.mkdir(parents=True, exist_ok=True)
        return path


# 싱글톤 인스턴스
settings = Settings()
