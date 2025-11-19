"""
ProgressTracker 단위 테스트

v1.0.0 - Phase 3 Step 3.4
"""
import pytest
import time
from unittest.mock import Mock
from backend.utils.progress_tracker import (
    ProgressTracker,
    MultiStageProgressTracker,
    ProgressState,
    Stage
)


@pytest.fixture
def progress_callback():
    """진행률 콜백 Mock"""
    return Mock()


@pytest.fixture
def tracker(progress_callback):
    """ProgressTracker 인스턴스"""
    return ProgressTracker(
        total_steps=100,
        callback=progress_callback
    )


@pytest.fixture
def multi_tracker(progress_callback):
    """MultiStageProgressTracker 인스턴스"""
    stages = ["캐시 확인", "키워드 생성", "트렌드 분석", "점수 계산", "결과 저장"]
    return MultiStageProgressTracker(
        stages=stages,
        callback=progress_callback
    )


def test_progress_state_initialization():
    """ProgressState 초기화 테스트"""
    state = ProgressState(total=100)

    assert state.current == 0
    assert state.total == 100
    assert state.message == ""
    assert state.completed == False
    assert state.percentage == 0.0


def test_progress_state_percentage():
    """진행률 계산 테스트"""
    state = ProgressState(current=50, total=100)
    assert state.percentage == 50.0

    state = ProgressState(current=75, total=100)
    assert state.percentage == 75.0

    # 0으로 나누기 방지
    state = ProgressState(current=10, total=0)
    assert state.percentage == 0.0


def test_progress_state_elapsed_time():
    """경과 시간 테스트"""
    state = ProgressState()
    time.sleep(0.1)

    elapsed = state.elapsed_seconds
    assert elapsed >= 0.1


def test_tracker_initialization(tracker):
    """ProgressTracker 초기화 테스트"""
    assert tracker.total_steps == 100
    assert tracker.state.total == 100
    assert tracker.state.current == 0


def test_tracker_update(tracker, progress_callback):
    """진행률 업데이트 테스트"""
    tracker.update(50, "절반 완료")

    assert tracker.state.current == 50
    assert tracker.state.message == "절반 완료"
    assert tracker.state.percentage == 50.0

    # 콜백 호출 확인
    progress_callback.assert_called_once()


def test_tracker_increment(tracker):
    """1단계 증가 테스트"""
    assert tracker.state.current == 0

    tracker.increment("단계 1")
    assert tracker.state.current == 1

    tracker.increment("단계 2")
    assert tracker.state.current == 2


def test_tracker_complete(tracker, progress_callback):
    """완료 처리 테스트"""
    tracker.complete("작업 완료")

    assert tracker.state.current == 100
    assert tracker.state.completed == True
    assert tracker.state.message == "작업 완료"


def test_tracker_reset(tracker):
    """초기화 테스트"""
    tracker.update(50, "진행 중")
    tracker.reset()

    assert tracker.state.current == 0
    assert tracker.state.message == ""
    assert tracker.state.completed == False


def test_tracker_context_manager():
    """컨텍스트 매니저 테스트"""
    with ProgressTracker(total_steps=10) as t:
        t.update(5, "진행 중")
        assert t.state.current == 5

    # 자동 완료
    assert t.state.completed == True


def test_tracker_context_manager_exception():
    """예외 발생 시 컨텍스트 매니저 테스트"""
    tracker = ProgressTracker(total_steps=10)

    try:
        with tracker:
            tracker.update(5, "진행 중")
            raise ValueError("테스트 오류")
    except ValueError:
        pass

    # 완료되지 않아야 함
    assert tracker.state.completed == False


def test_stage_initialization():
    """Stage 초기화 테스트"""
    stage = Stage(name="테스트 단계")

    assert stage.name == "테스트 단계"
    assert stage.weight == 1.0
    assert stage.completed == False
    assert stage.message == ""


def test_multi_tracker_initialization(multi_tracker):
    """MultiStageProgressTracker 초기화 테스트"""
    assert multi_tracker.total_stages == 5
    assert len(multi_tracker.stages) == 5
    assert multi_tracker.current_stage_idx == 0


def test_multi_tracker_current_stage(multi_tracker):
    """현재 단계 테스트"""
    stage = multi_tracker.current_stage

    assert stage is not None
    assert stage.name == "캐시 확인"


def test_multi_tracker_overall_progress(multi_tracker):
    """전체 진행률 계산 테스트"""
    # 초기 상태
    assert multi_tracker.overall_progress >= 0

    # 첫 단계 완료
    multi_tracker.complete_stage(0)
    progress1 = multi_tracker.overall_progress

    # 두 번째 단계 완료
    multi_tracker.complete_stage(1)
    progress2 = multi_tracker.overall_progress

    # 진행률이 증가해야 함
    assert progress2 > progress1


def test_multi_tracker_start_stage(multi_tracker, progress_callback):
    """단계 시작 테스트"""
    multi_tracker.start_stage(1, "키워드 생성 중")

    assert multi_tracker.current_stage_idx == 1
    assert multi_tracker.current_stage.name == "키워드 생성"
    assert multi_tracker.current_stage.message == "키워드 생성 중"

    # 콜백 호출 확인
    progress_callback.assert_called()


def test_multi_tracker_complete_stage(multi_tracker):
    """단계 완료 테스트"""
    multi_tracker.complete_stage(0, "캐시 확인 완료")

    stage = multi_tracker.stages[0]
    assert stage.completed == True
    assert stage.message == "캐시 확인 완료"


def test_multi_tracker_next_stage(multi_tracker):
    """다음 단계 이동 테스트"""
    # 초기: 0번 단계
    assert multi_tracker.current_stage_idx == 0

    # 다음 단계로
    multi_tracker.next_stage()

    # 0번 완료, 1번으로 이동
    assert multi_tracker.stages[0].completed == True
    assert multi_tracker.current_stage_idx == 1


def test_multi_tracker_update_stage(multi_tracker):
    """단계 메시지 업데이트 테스트"""
    multi_tracker.update_stage("캐시 조회 중...")

    assert multi_tracker.current_stage.message == "캐시 조회 중..."


def test_multi_tracker_complete_all(multi_tracker):
    """전체 완료 테스트"""
    multi_tracker.complete_all("모든 작업 완료")

    # 모든 단계가 완료되어야 함
    for stage in multi_tracker.stages:
        assert stage.completed == True

    assert multi_tracker.overall_progress == 100.0


def test_multi_tracker_status_summary(multi_tracker):
    """상태 요약 테스트"""
    multi_tracker.complete_stage(0)
    multi_tracker.start_stage(1)

    summary = multi_tracker.get_status_summary()

    assert summary['total_stages'] == 5
    assert summary['completed_stages'] == 1
    assert summary['current_stage'] == "키워드 생성"
    assert 'overall_progress' in summary
    assert 'elapsed_seconds' in summary


def test_multi_tracker_context_manager():
    """MultiStageProgressTracker 컨텍스트 매니저 테스트"""
    stages = ["단계1", "단계2", "단계3"]

    with MultiStageProgressTracker(stages=stages) as mt:
        # 첫 단계가 자동 시작되어야 함
        assert mt.current_stage_idx == 0

        mt.next_stage()
        assert mt.current_stage_idx == 1

    # 자동 완료
    assert all(s.completed for s in mt.stages)


def test_multi_tracker_weighted_stages():
    """가중치가 있는 단계 진행률 테스트"""
    mt = MultiStageProgressTracker(stages=["단계1", "단계2"])

    # 첫 단계는 가중치 2
    mt.stages[0].weight = 2.0
    mt.stages[1].weight = 1.0

    # 첫 단계 완료
    mt.complete_stage(0)

    # 가중치 반영된 진행률
    # (2 / 3) * 100 = 66.67%
    assert mt.overall_progress > 60


def test_tracker_callback_error_handling():
    """콜백 오류 처리 테스트"""
    def error_callback(state):
        raise RuntimeError("콜백 오류")

    tracker = ProgressTracker(total_steps=10, callback=error_callback)

    # 오류가 발생해도 진행은 계속되어야 함
    tracker.update(5, "진행 중")
    assert tracker.state.current == 5


def test_multi_tracker_callback_format(progress_callback):
    """MultiStageProgressTracker 콜백 형식 테스트"""
    mt = MultiStageProgressTracker(
        stages=["단계1", "단계2"],
        callback=progress_callback
    )

    mt.start_stage(0, "시작")

    # 콜백이 (stage_name, current, total, progress) 형식으로 호출되어야 함
    call_args = progress_callback.call_args[0]
    assert len(call_args) == 4
    assert isinstance(call_args[0], str)  # stage_name
    assert isinstance(call_args[1], int)  # current
    assert isinstance(call_args[2], int)  # total
    assert isinstance(call_args[3], float)  # overall_progress


def test_tracker_no_callback():
    """콜백 없이 동작 테스트"""
    tracker = ProgressTracker(total_steps=10)

    # 콜백 없어도 정상 동작
    tracker.update(5, "진행 중")
    tracker.complete("완료")

    assert tracker.state.completed == True


def test_multi_tracker_no_callback():
    """MultiStageProgressTracker 콜백 없이 동작 테스트"""
    mt = MultiStageProgressTracker(stages=["단계1", "단계2"])

    # 콜백 없어도 정상 동작
    mt.start_stage(0)
    mt.complete_stage(0)
    mt.next_stage()

    assert mt.stages[0].completed == True


def test_tracker_multiple_updates(tracker, progress_callback):
    """여러 번 업데이트 테스트"""
    for i in range(1, 11):
        tracker.update(i * 10, f"{i * 10}% 완료")

    # 10번 호출되어야 함
    assert progress_callback.call_count == 10

    # 최종 상태
    assert tracker.state.current == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
