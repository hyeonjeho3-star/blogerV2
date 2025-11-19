"""
로깅 시스템
v1.0.3의 logging을 loguru로 업그레이드하여 더 나은 DX 제공
"""
import sys
from pathlib import Path
from typing import Optional

# 임시로 기본 logging 사용 (loguru 미설치)
import logging


def setup_logger():
    """로거 초기화 (임시 버전 - loguru 미설치)"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('data/logs/blog_mate.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)


def get_logger(name: str):
    """모듈별 로거 인스턴스 반환"""
    return logging.getLogger(name)


# 앱 시작 시 초기화
setup_logger()
