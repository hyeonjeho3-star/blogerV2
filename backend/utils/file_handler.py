"""
파일 입출력 핸들러
v1.0.3 코드 재사용 (import 경로만 수정)
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class FileHandler:
    """파일 입출력 관리 클래스"""

    @staticmethod
    def save_json(data: Any, file_path: Path, indent: int = 2) -> bool:
        """
        JSON 파일 저장

        Args:
            data: 저장할 데이터
            file_path: 파일 경로
            indent: 들여쓰기 수준

        Returns:
            성공 여부
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)

            logger.info(f"JSON 저장 완료: {file_path}")
            return True

        except Exception as e:
            logger.error(f"JSON 저장 실패: {str(e)}")
            return False

    @staticmethod
    def load_json(file_path: Path) -> Optional[Any]:
        """
        JSON 파일 로드

        Args:
            file_path: 파일 경로

        Returns:
            로드된 데이터 또는 None
        """
        try:
            if not file_path.exists():
                logger.warning(f"파일이 존재하지 않음: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"JSON 로드 완료: {file_path}")
            return data

        except Exception as e:
            logger.error(f"JSON 로드 실패: {str(e)}")
            return None

    @staticmethod
    def save_text(text: str, file_path: Path) -> bool:
        """
        텍스트 파일 저장

        Args:
            text: 저장할 텍스트
            file_path: 파일 경로

        Returns:
            성공 여부
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)

            logger.info(f"텍스트 저장 완료: {file_path}")
            return True

        except Exception as e:
            logger.error(f"텍스트 저장 실패: {str(e)}")
            return False

    @staticmethod
    def load_text(file_path: Path) -> Optional[str]:
        """
        텍스트 파일 로드

        Args:
            file_path: 파일 경로

        Returns:
            로드된 텍스트 또는 None
        """
        try:
            if not file_path.exists():
                logger.warning(f"파일이 존재하지 않음: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            logger.info(f"텍스트 로드 완료: {file_path}")
            return text

        except Exception as e:
            logger.error(f"텍스트 로드 실패: {str(e)}")
            return None

    @staticmethod
    def generate_filename(prefix: str, extension: str = "json") -> str:
        """
        타임스탬프 기반 파일명 생성

        Args:
            prefix: 파일명 접두사
            extension: 파일 확장자

        Returns:
            생성된 파일명
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
