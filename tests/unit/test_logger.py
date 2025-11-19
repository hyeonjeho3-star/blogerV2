"""
Logger 테스트
"""
from backend.utils.logger import get_logger


def test_logger_basic():
    """기본 로거 동작 테스트"""
    logger = get_logger("test")

    # 로그 메시지 출력 (에러 없이 실행되어야 함)
    logger.info("테스트 정보 메시지")
    logger.debug("테스트 디버그 메시지")
    logger.warning("테스트 경고 메시지")

    assert True  # 에러 없이 통과하면 성공


def test_logger_name():
    """로거 이름 테스트"""
    logger = get_logger("test_module")

    assert logger.name == "test_module"
