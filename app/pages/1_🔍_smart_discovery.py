"""
Smart Discovery 페이지
키워드 자동 발굴 및 기회 분석

v2.0.0 - Phase 3 Step 3.5
"""
try:
    import streamlit as st
    import pandas as pd
    from datetime import datetime
    import io
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None

from backend.services.smart_discovery_service import SmartDiscoveryService
from backend.utils.progress_tracker import MultiStageProgressTracker
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def create_discovery_service() -> SmartDiscoveryService:
    """SmartDiscoveryService 인스턴스 생성"""
    if 'discovery_service' not in st.session_state:
        st.session_state.discovery_service = SmartDiscoveryService(use_cache=True)
    return st.session_state.discovery_service


def render_input_section() -> dict:
    """입력 섹션 렌더링"""
    st.header("🎯 키워드 입력")

    col1, col2 = st.columns([2, 1])

    with col1:
        seed_keyword = st.text_input(
            "시드 키워드",
            placeholder="예: 롱패딩, 발열내의, 겨울코디",
            help="분석할 기본 키워드를 입력하세요"
        )

    with col2:
        min_grade = st.selectbox(
            "최소 등급",
            options=['S', 'A', 'B', 'C', 'D'],
            index=2,  # 기본값: B
            help="이 등급 이상의 결과만 표시합니다"
        )

    col3, col4 = st.columns(2)

    with col3:
        use_autocomplete = st.checkbox(
            "네이버 자동완성 사용",
            value=True,
            help="네이버 검색 자동완성 API를 사용하여 추가 키워드를 생성합니다"
        )

    with col4:
        use_cache = st.checkbox(
            "캐시 사용",
            value=True,
            help="이전 분석 결과를 재사용하여 빠르게 조회합니다"
        )

    return {
        'seed_keyword': seed_keyword,
        'min_grade': min_grade,
        'use_autocomplete': use_autocomplete,
        'use_cache': use_cache
    }


def render_progress_section() -> object:
    """진행률 섹션 렌더링"""
    st.header("⏳ 분석 진행률")
    progress_container = st.empty()
    return progress_container


def render_results_section(result):
    """결과 섹션 렌더링"""
    st.header("📊 분석 결과")

    # 요약 카드
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "생성 키워드",
            f"{result.generated_count}개"
        )

    with col2:
        st.metric(
            "분석 완료",
            f"{result.analyzed_count}개",
            delta=f"{result.success_rate:.0f}%"
        )

    with col3:
        st.metric(
            "발견 기회",
            f"{len(result.opportunities)}개"
        )

    with col4:
        st.metric(
            "소요 시간",
            f"{result.processing_time:.1f}초"
        )

    # 등급 분포
    st.subheader("📈 등급 분포")

    dist = result.grade_distribution
    dist_df = pd.DataFrame([
        {"등급": grade, "개수": count}
        for grade, count in dist.items()
        if count > 0
    ])

    if not dist_df.empty:
        st.bar_chart(dist_df.set_index("등급"))
    else:
        st.info("등급 분포 데이터가 없습니다.")

    # 최고 기회 키워드
    if result.best_opportunity:
        st.subheader("🏆 최고 기회 키워드")

        best = result.best_opportunity

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(f"### {best.keyword}")
            st.markdown(f"**등급: {best.grade}**")
            st.markdown(f"**종합 점수: {best.total_score:.1f}점**")

        with col2:
            # 점수 상세
            score_data = {
                "요인": ["검색 수요", "성장 추세", "경쟁 공백", "블로그 적합도"],
                "점수": [
                    best.search_demand,
                    best.momentum,
                    best.competition_gap,
                    best.suitability
                ]
            }
            score_df = pd.DataFrame(score_data)
            st.bar_chart(score_df.set_index("요인"))

        st.info(best.grade_reason)

    # 상위 기회 목록
    st.subheader("🎯 상위 기회 목록 (Top 20)")

    top_opportunities = result.get_top_opportunities(top_n=20)

    if top_opportunities:
        opportunities_data = []

        for idx, opp in enumerate(top_opportunities, 1):
            opportunities_data.append({
                "순위": idx,
                "키워드": opp.keyword,
                "등급": opp.grade,
                "종합 점수": f"{opp.total_score:.1f}",
                "수요": f"{opp.search_demand:.0f}",
                "추세": f"{opp.momentum:.0f}",
                "공백": f"{opp.competition_gap:.0f}",
                "적합": f"{opp.suitability:.0f}"
            })

        df = pd.DataFrame(opportunities_data)

        # 등급별 색상 강조
        def highlight_grade(row):
            grade_colors = {
                'S': 'background-color: #ffcccc',
                'A': 'background-color: #ffe6cc',
                'B': 'background-color: #ffffcc',
                'C': 'background-color: #e6f3ff',
                'D': 'background-color: #f0f0f0'
            }
            color = grade_colors.get(row['등급'], '')
            return [color] * len(row)

        st.dataframe(
            df.style.apply(highlight_grade, axis=1),
            use_container_width=True,
            height=600
        )

        # Excel 다운로드
        render_download_section(result)

    else:
        st.warning("표시할 기회 키워드가 없습니다.")


def render_download_section(result):
    """다운로드 섹션 렌더링"""
    st.subheader("💾 결과 다운로드")

    # Excel 파일 생성
    excel_data = create_excel_export(result)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"smart_discovery_{result.seed_keyword}_{timestamp}.xlsx"

    st.download_button(
        label="📥 Excel 다운로드",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def create_excel_export(result) -> bytes:
    """Excel 파일 생성"""
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: 요약
        summary_data = {
            "항목": [
                "시드 키워드",
                "생성 키워드",
                "분석 완료",
                "성공률",
                "발견 기회",
                "평균 점수",
                "소요 시간",
                "캐시 사용"
            ],
            "값": [
                result.seed_keyword,
                result.generated_count,
                result.analyzed_count,
                f"{result.success_rate:.1f}%",
                len(result.opportunities),
                f"{result.average_score:.1f}",
                f"{result.processing_time:.1f}초",
                "Yes" if result.cache_hit else "No"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="요약", index=False)

        # Sheet 2: 기회 키워드
        opportunities_data = []
        for idx, opp in enumerate(result.opportunities, 1):
            opportunities_data.append({
                "순위": idx,
                "키워드": opp.keyword,
                "등급": opp.grade,
                "종합 점수": opp.total_score,
                "검색 수요": opp.search_demand,
                "성장 추세": opp.momentum,
                "경쟁 공백": opp.competition_gap,
                "블로그 적합도": opp.suitability,
                "평균 검색 비율": opp.average_ratio,
                "최근 검색 비율": opp.recent_ratio,
                "모멘텀": opp.momentum_value
            })

        if opportunities_data:
            opp_df = pd.DataFrame(opportunities_data)
            opp_df.to_excel(writer, sheet_name="기회 키워드", index=False)

        # Sheet 3: 등급 분포
        dist = result.grade_distribution
        dist_data = [
            {"등급": grade, "개수": count}
            for grade, count in dist.items()
        ]
        dist_df = pd.DataFrame(dist_data)
        dist_df.to_excel(writer, sheet_name="등급 분포", index=False)

    output.seek(0)
    return output.read()


def render_cache_management():
    """캐시 관리 섹션"""
    st.sidebar.header("🗄️ 캐시 관리")

    service = create_discovery_service()
    stats = service.get_cache_stats()

    st.sidebar.metric("캐시 개수", stats.get('total_count', 0))
    st.sidebar.metric("유효 캐시", stats.get('valid_count', 0))

    cache_size_mb = stats.get('cache_size_bytes', 0) / (1024 * 1024)
    st.sidebar.metric("캐시 크기", f"{cache_size_mb:.2f} MB")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("만료 삭제", use_container_width=True):
            deleted = service.clear_expired_cache()
            st.success(f"{deleted}개 삭제됨")

    with col2:
        if st.button("전체 삭제", use_container_width=True):
            deleted = service.clear_cache()
            st.success(f"{deleted}개 삭제됨")


def main():
    """메인 함수"""
    if not HAS_STREAMLIT:
        print("Streamlit이 설치되지 않았습니다.")
        return

    st.set_page_config(
        page_title="Smart Discovery - Blog Mate",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🔍 Smart Discovery")
    st.markdown("**AI 기반 스마트 키워드 발굴 시스템**")

    # 사이드바
    render_cache_management()

    st.sidebar.markdown("---")
    st.sidebar.info(
        "시드 키워드를 입력하면 자동으로\n"
        "관련 키워드를 생성하고 분석하여\n"
        "블로그 작성 기회를 발굴합니다."
    )

    # 입력 섹션
    inputs = render_input_section()

    # 분석 버튼
    if st.button("🚀 분석 시작", type="primary", use_container_width=True):
        if not inputs['seed_keyword']:
            st.error("시드 키워드를 입력하세요.")
            return

        # 진행률 섹션
        progress_container = render_progress_section()

        try:
            # SmartDiscoveryService 생성
            service = create_discovery_service()
            service.use_cache = inputs['use_cache']

            # 진행률 콜백
            def progress_callback(stage_name, current, total, overall_progress):
                with progress_container.container():
                    st.progress(
                        overall_progress / 100,
                        text=f"[{current}/{total}] {stage_name} ({overall_progress:.0f}%)"
                    )

            # 분석 실행
            result = service.discover(
                seed_keyword=inputs['seed_keyword'],
                use_autocomplete=inputs['use_autocomplete'],
                min_grade=inputs['min_grade'],
                progress_callback=progress_callback
            )

            # 진행률 완료
            with progress_container.container():
                st.success(f"분석 완료! (소요 시간: {result.processing_time:.1f}초)")

            # 결과 표시
            st.session_state.last_result = result

        except Exception as e:
            logger.error(f"분석 실패: {str(e)}")
            st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
            return

    # 이전 결과 표시
    if 'last_result' in st.session_state:
        render_results_section(st.session_state.last_result)


if __name__ == "__main__":
    if HAS_STREAMLIT:
        main()
    else:
        print("이 파일은 Streamlit 앱으로 실행되어야 합니다.")
        print("실행 방법: streamlit run app/pages/1_🔍_smart_discovery.py")
