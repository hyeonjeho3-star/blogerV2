"""
File Handler 테스트
"""
from pathlib import Path
import tempfile
import shutil
from backend.utils.file_handler import FileHandler


def test_save_and_load_json():
    """JSON 저장 및 로드 테스트"""
    # 임시 디렉토리 생성
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # 테스트 데이터
        test_data = {"name": "Blog Mate", "version": "2.0", "features": ["discovery", "compare"]}
        file_path = temp_dir / "test.json"

        # 저장
        result = FileHandler.save_json(test_data, file_path)
        assert result is True
        assert file_path.exists()

        # 로드
        loaded_data = FileHandler.load_json(file_path)
        assert loaded_data is not None
        assert loaded_data["name"] == "Blog Mate"
        assert loaded_data["version"] == "2.0"
        assert len(loaded_data["features"]) == 2

    finally:
        # 임시 디렉토리 삭제
        shutil.rmtree(temp_dir)


def test_save_and_load_text():
    """텍스트 저장 및 로드 테스트"""
    # 임시 디렉토리 생성
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # 테스트 데이터
        test_text = "Blog Mate v2.0 테스트"
        file_path = temp_dir / "test.txt"

        # 저장
        result = FileHandler.save_text(test_text, file_path)
        assert result is True
        assert file_path.exists()

        # 로드
        loaded_text = FileHandler.load_text(file_path)
        assert loaded_text is not None
        assert loaded_text == test_text

    finally:
        # 임시 디렉토리 삭제
        shutil.rmtree(temp_dir)


def test_generate_filename():
    """파일명 생성 테스트"""
    filename = FileHandler.generate_filename("keyword", "json")

    assert "keyword_" in filename
    assert filename.endswith(".json")
