"""
진행률 추적 시스템
Streamlit UI 통합을 위한 실시간 진행 상태 관리

v1.0.0 - Phase 3 Step 3.4
"""
from typing import Optional, Callable, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Streamlit 위젯 타입 (실제로는 st.empty() 반환)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None


@dataclass
class ProgressState:
    """진행 상태"""
    current: int = 0
    total: int = 100
    message: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    completed: bool = False

    @property
    def percentage(self) -> float:
        """진행률 (0-100)"""
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100

    @property
    def elapsed_seconds(self) -> float:
        """경과 시간 (초)"""
        return (datetime.now() - self.started_at).total_seconds()


class ProgressTracker:
    """단일 작업 진행률 추적기"""

    def __init__(
        self,
        total_steps: int = 100,
        callback: Optional[Callable[[ProgressState], None]] = None,
        streamlit_widget: Optional[object] = None
    ):
        """
        초기화

        Args:
            total_steps: 전체 단계 수
            callback: 진행 상태 변경 콜백
            streamlit_widget: Streamlit 위젯 (st.empty())
        """
        self.total_steps = total_steps
        self.callback = callback
        self.widget = streamlit_widget

        self.state = ProgressState(total=total_steps)

        logger.debug(f"ProgressTracker 초기화 (총 {total_steps}단계)")

    def update(self, current: int, message: str = "") -> None:
        """
        진행 상태 업데이트

        Args:
            current: 현재 단계
            message: 진행 메시지
        """
        self.state.current = current
        self.state.message = message

        logger.debug(
            f"진행률: {self.state.percentage:.1f}% "
            f"({current}/{self.total_steps}) - {message}"
        )

        # 콜백 실행
        if self.callback:
            try:
                self.callback(self.state)
            except Exception as e:
                logger.error(f"진행률 콜백 오류: {str(e)}")

        # Streamlit 위젯 업데이트
        if self.widget and HAS_STREAMLIT:
            try:
                with self.widget.container():
                    st.progress(
                        self.state.percentage / 100,
                        text=f"{message} ({self.state.percentage:.0f}%)"
                    )
            except Exception as e:
                logger.error(f"Streamlit 위젯 업데이트 오류: {str(e)}")

    def increment(self, message: str = "") -> None:
        """
        1단계 증가

        Args:
            message: 진행 메시지
        """
        self.update(self.state.current + 1, message)

    def complete(self, message: str = "완료") -> None:
        """
        완료 처리

        Args:
            message: 완료 메시지
        """
        self.state.current = self.total_steps
        self.state.completed = True
        self.state.message = message

        logger.info(
            f"작업 완료: {message} "
            f"(소요 시간: {self.state.elapsed_seconds:.1f}초)"
        )

        # 콜백 실행
        if self.callback:
            try:
                self.callback(self.state)
            except Exception as e:
                logger.error(f"완료 콜백 오류: {str(e)}")

        # Streamlit 위젯 업데이트
        if self.widget and HAS_STREAMLIT:
            try:
                with self.widget.container():
                    st.success(
                        f"{message} (소요 시간: {self.state.elapsed_seconds:.1f}초)"
                    )
            except Exception as e:
                logger.error(f"Streamlit 위젯 업데이트 오류: {str(e)}")

    def reset(self) -> None:
        """진행 상태 초기화"""
        self.state = ProgressState(total=self.total_steps)
        logger.debug("진행률 초기화")

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        if not self.state.completed:
            if exc_type:
                logger.error(f"작업 실패: {exc_val}")
            else:
                self.complete()
        return False


@dataclass
class Stage:
    """다단계 작업의 개별 단계"""
    name: str
    weight: float = 1.0  # 가중치 (전체 진행률 계산용)
    completed: bool = False
    message: str = ""


class MultiStageProgressTracker:
    """다단계 작업 진행률 추적기"""

    def __init__(
        self,
        stages: List[str],
        callback: Optional[Callable[[str, int, int, float], None]] = None,
        streamlit_widget: Optional[object] = None
    ):
        """
        초기화

        Args:
            stages: 단계 이름 리스트
            callback: 진행 콜백 (stage_name, current, total, overall_progress)
            streamlit_widget: Streamlit 위젯
        """
        self.stages = [Stage(name=name) for name in stages]
        self.current_stage_idx = 0
        self.callback = callback
        self.widget = streamlit_widget

        self.started_at = datetime.now()

        logger.info(f"MultiStageProgressTracker 초기화 ({len(stages)}단계)")

    @property
    def total_stages(self) -> int:
        """전체 단계 수"""
        return len(self.stages)

    @property
    def current_stage(self) -> Optional[Stage]:
        """현재 단계"""
        if 0 <= self.current_stage_idx < len(self.stages):
            return self.stages[self.current_stage_idx]
        return None

    @property
    def overall_progress(self) -> float:
        """전체 진행률 (0-100)"""
        if not self.stages:
            return 0.0

        total_weight = sum(s.weight for s in self.stages)
        completed_weight = sum(s.weight for s in self.stages if s.completed)

        # 현재 진행 중인 단계도 부분 포함
        if self.current_stage and not self.current_stage.completed:
            completed_weight += self.current_stage.weight * 0.5

        return (completed_weight / total_weight) * 100

    def start_stage(self, stage_idx: int, message: str = "") -> None:
        """
        특정 단계 시작

        Args:
            stage_idx: 단계 인덱스
            message: 진행 메시지
        """
        if 0 <= stage_idx < len(self.stages):
            self.current_stage_idx = stage_idx
            stage = self.stages[stage_idx]
            stage.message = message or f"{stage.name} 시작"

            logger.info(
                f"[{stage_idx + 1}/{self.total_stages}] "
                f"{stage.name} 시작"
            )

            self._notify_progress()

    def complete_stage(self, stage_idx: int, message: str = "") -> None:
        """
        특정 단계 완료

        Args:
            stage_idx: 단계 인덱스
            message: 완료 메시지
        """
        if 0 <= stage_idx < len(self.stages):
            stage = self.stages[stage_idx]
            stage.completed = True
            stage.message = message or f"{stage.name} 완료"

            logger.info(
                f"[{stage_idx + 1}/{self.total_stages}] "
                f"{stage.name} 완료"
            )

            self._notify_progress()

    def next_stage(self, message: str = "") -> None:
        """
        다음 단계로 이동

        Args:
            message: 진행 메시지
        """
        # 현재 단계 완료
        if self.current_stage:
            self.complete_stage(self.current_stage_idx)

        # 다음 단계 시작
        next_idx = self.current_stage_idx + 1
        if next_idx < self.total_stages:
            self.start_stage(next_idx, message)

    def update_stage(self, message: str) -> None:
        """
        현재 단계 메시지 업데이트

        Args:
            message: 진행 메시지
        """
        if self.current_stage:
            self.current_stage.message = message
            self._notify_progress()

    def complete_all(self, message: str = "모든 단계 완료") -> None:
        """
        모든 단계 완료

        Args:
            message: 완료 메시지
        """
        for stage in self.stages:
            stage.completed = True

        elapsed = (datetime.now() - self.started_at).total_seconds()

        logger.info(f"{message} (소요 시간: {elapsed:.1f}초)")

        self._notify_progress(final=True, final_message=message)

    def _notify_progress(
        self,
        final: bool = False,
        final_message: str = ""
    ) -> None:
        """진행 상태 알림"""
        # 콜백 실행
        if self.callback:
            try:
                current_name = self.current_stage.name if self.current_stage else ""
                self.callback(
                    current_name,
                    self.current_stage_idx + 1,
                    self.total_stages,
                    self.overall_progress
                )
            except Exception as e:
                logger.error(f"진행률 콜백 오류: {str(e)}")

        # Streamlit 위젯 업데이트
        if self.widget and HAS_STREAMLIT:
            try:
                with self.widget.container():
                    if final:
                        st.success(final_message)
                    else:
                        # 전체 진행률 바
                        st.progress(
                            self.overall_progress / 100,
                            text=f"전체 진행률: {self.overall_progress:.0f}%"
                        )

                        # 현재 단계 정보
                        if self.current_stage:
                            st.info(
                                f"[{self.current_stage_idx + 1}/{self.total_stages}] "
                                f"{self.current_stage.name}: {self.current_stage.message}"
                            )
            except Exception as e:
                logger.error(f"Streamlit 위젯 업데이트 오류: {str(e)}")

    def get_status_summary(self) -> Dict[str, any]:
        """
        상태 요약 정보

        Returns:
            상태 딕셔너리
        """
        completed_count = sum(1 for s in self.stages if s.completed)

        return {
            "total_stages": self.total_stages,
            "completed_stages": completed_count,
            "current_stage": self.current_stage.name if self.current_stage else None,
            "overall_progress": self.overall_progress,
            "elapsed_seconds": (datetime.now() - self.started_at).total_seconds()
        }

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        if self.stages:
            self.start_stage(0)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        if exc_type:
            logger.error(f"다단계 작업 실패: {exc_val}")
        else:
            # 모든 단계가 완료되지 않았다면 강제 완료
            if not all(s.completed for s in self.stages):
                self.complete_all()
        return False
