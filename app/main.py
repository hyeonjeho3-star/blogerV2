"""
Blog Mate v2.0 - 메인 엔트리 포인트
"""
# import streamlit as st  # Streamlit 미설치로 주석 처리
from pathlib import Path

# 임시 메시지
print("""
========================================
Blog Mate v2.0 - Smart Keyword Discovery Platform
========================================

⚠️ Streamlit이 아직 설치되지 않았습니다.

설치 방법:
1. Python 3.10-3.12 버전 사용 권장
2. pip install streamlit

실행 방법:
streamlit run app/main.py

========================================
""")

# 아래는 Streamlit 설치 후 사용할 코드입니다:
"""
# 페이지 설정 (반드시 최상단)
st.set_page_config(
    page_title="Blog Mate v2.0",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown('''
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
</style>
''', unsafe_allow_html=True)

# 메인 페이지
st.markdown('<div class="main-header">📝 Blog Mate v2.0</div>', unsafe_allow_html=True)

st.markdown('''
### 🚀 블로그 성공을 위한 스마트 키워드 플랫폼

네이버 데이터랩과 AI를 활용하여 당신의 블로그가 성공할 수 있도록 돕습니다.
''')

# 기능 소개
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('''
    <div class="feature-card">
        <h3>🔍 스마트 발굴</h3>
        <p>관심 분야만 입력하면<br>S급 키워드를 자동으로 발견</p>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown('''
    <div class="feature-card">
        <h3>⚖️ 키워드 비교</h3>
        <p>여러 키워드를 비교하여<br>최적의 선택 지원</p>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown('''
    <div class="feature-card">
        <h3>🎯 전략 수립</h3>
        <p>데이터 기반 블로그<br>발행 전략 제시</p>
    </div>
    ''', unsafe_allow_html=True)

# 시작하기
st.markdown("---")
st.markdown("### 👉 왼쪽 사이드바에서 원하는 기능을 선택하세요!")

# 푸터
st.markdown("---")
st.markdown('''
<div style='text-align: center; color: gray;'>
    <small>Blog Mate v2.0 | Powered by Naver DataLab & Google Gemini</small>
</div>
''', unsafe_allow_html=True)
"""
