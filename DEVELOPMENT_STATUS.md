# Blog Mate v2.0 - 개발 현황 보고서

> 최종 업데이트: 2025-11-19
> 현재 상태: **Phase 3 완료** ✅

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [프로젝트 구조](#프로젝트-구조)
3. [Phase 1: Project Bootstrap](#phase-1-project-bootstrap)
4. [Phase 2: Keyword Generation Engine](#phase-2-keyword-generation-engine)
5. [Phase 3: Smart Discovery Service](#phase-3-smart-discovery-service)
6. [테스트 현황](#테스트-현황)
7. [기술 스택](#기술-스택)
8. [다음 단계](#다음-단계)

---

## 🎯 프로젝트 개요

**Blog Mate v2.0**은 AI 기반 스마트 키워드 발굴 및 블로그 컨텐츠 생성 플랫폼입니다.

### 핵심 기능
- 🔍 **Smart Discovery**: 키워드 자동 발굴 및 기회 점수 분석
- 📊 **Trend Analysis**: 네이버 DataLab 기반 트렌드 분석
- 🤖 **AI Content Generation**: Google Gemini 기반 컨텐츠 자동 생성 (Phase 4 예정)
- 📈 **Performance Dashboard**: 실시간 분석 및 리포팅 (Phase 5 예정)

### 개발 로드맵
```
✅ Phase 1: Project Bootstrap (완료)
✅ Phase 2: Keyword Generation Engine (완료)
✅ Phase 3: Smart Discovery Service (완료)
⏳ Phase 4: AI Content Generation Engine (예정)
⏳ Phase 5: Performance & Dashboard (예정)
```

---

## 📁 프로젝트 구조

```
blog-mate2/
├── app/                          # Streamlit UI
│   ├── pages/
│   │   ├── 1_🔍_smart_discovery.py   # Smart Discovery UI (Phase 3)
│   │   ├── 2_📝_content_gen.py       # Content Generation (Phase 4 예정)
│   │   └── 3_📊_comparison.py        # Comparison (Phase 2 기반)
│   └── main.py                   # 메인 앱
│
├── backend/                      # 백엔드 로직
│   ├── models/                   # 데이터 모델
│   │   ├── keyword_trend.py          # 키워드 트렌드 모델
│   │   ├── keyword_batch.py          # 배치 처리 모델
│   │   ├── analysis_result.py        # 분석 결과 모델
│   │   ├── opportunity_score.py      # 기회 점수 모델 (Phase 3)
│   │   └── discovery_result.py       # 발굴 결과 모델 (Phase 3)
│   │
│   ├── analyzers/                # 분석기
│   │   ├── base_analyzer.py          # 추상 베이스 클래스
│   │   └── datalab_analyzer.py       # 네이버 DataLab 분석기 v2.0
│   │
│   ├── generators/               # 키워드 생성기
│   │   ├── base_generator.py         # 추상 베이스 클래스
│   │   ├── keyword_generator.py      # 롱테일 키워드 생성기
│   │   └── autocomplete_generator.py # 네이버 자동완성 크롤러
│   │
│   ├── services/                 # 비즈니스 로직
│   │   ├── keyword_comparison_service.py  # 키워드 비교 서비스
│   │   ├── batch_processor.py             # 배치 분석 프로세서
│   │   ├── opportunity_scorer.py          # 기회 점수 계산 (Phase 3)
│   │   └── smart_discovery_service.py     # 스마트 발굴 서비스 (Phase 3)
│   │
│   └── utils/                    # 유틸리티
│       ├── logger.py                 # 로깅 (loguru 폴백)
│       ├── api_client.py             # HTTP 클라이언트 (httpx 폴백)
│       ├── file_handler.py           # 파일 I/O
│       ├── cache_manager.py          # 캐시 관리 시스템 (Phase 3)
│       └── progress_tracker.py       # 진행률 추적 (Phase 3)
│
├── config/                       # 설정
│   └── settings.py               # Pydantic Settings (폴백 포함)
│
├── tests/                        # 테스트
│   ├── unit/                     # 단위 테스트 (80개)
│   │   ├── test_models.py
│   │   ├── test_analyzers.py
│   │   ├── test_generators.py
│   │   ├── test_opportunity_scorer.py     (16 tests)
│   │   ├── test_cache_manager.py          (17 tests)
│   │   ├── test_smart_discovery_service.py (20 tests)
│   │   └── test_progress_tracker.py       (27 tests)
│   └── integration/              # 통합 테스트 (Phase 3.6 예정)
│
├── .env.example                  # 환경 변수 템플릿
├── requirements.txt              # 의존성 (Python 3.14 호환)
└── pytest.ini                    # Pytest 설정
```

---

## ✅ Phase 1: Project Bootstrap

**목표**: 프로젝트 기본 구조 및 인프라 구축

### 구현 내용

#### 1.1 디렉토리 구조 생성
- 전체 프로젝트 디렉토리 생성
- `__init__.py` 파일 자동 생성
- `.gitkeep` 파일로 빈 디렉토리 유지

#### 1.2 의존성 관리
```python
# requirements.txt (주요 패키지)
streamlit>=1.28.0
pydantic>=2.0.0
httpx>=0.24.0
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0
pytest>=7.4.0
loguru>=0.7.0
```

**Python 3.14 호환성 문제 해결**:
- 사전 빌드된 wheel 우선 설치
- 버전 제약 완화 (>= 방식 사용)
- 누락된 패키지 폴백 처리

#### 1.3 핵심 유틸리티
```python
# backend/utils/logger.py
- loguru 기반 로깅 (폴백: 표준 logging)
- 모듈별 로거 생성: get_logger(__name__)

# backend/utils/api_client.py
- httpx 기반 HTTP 클라이언트 (폴백: 더미 구현)
- POST/GET 메서드 지원

# backend/utils/file_handler.py
- JSON/Text 파일 I/O
- 타임스탬프 파일명 생성
```

#### 1.4 설정 관리
```python
# config/settings.py
- Pydantic Settings 기반 (폴백 포함)
- 환경 변수 자동 로드 (.env)
- API 키 관리
- 경로 설정 (base_dir, cache_dir, log_dir)
```

#### 1.5 Git 설정
```bash
# .gitignore
- Python 바이트코드, 캐시
- 환경 변수 (.env)
- IDE 설정 (.vscode, .idea)
- 데이터 디렉토리
```

### 테스트 결과
- 8/8 기본 검증 테스트 통과 ✅
- GitHub 저장소 초기화 완료 ✅

---

## ✅ Phase 2: Keyword Generation Engine

**목표**: 키워드 자동 생성 및 트렌드 분석 엔진 구축

### 구현 내용

#### 2.1 데이터 모델

**KeywordTrend** (`backend/models/keyword_trend.py`)
```python
class KeywordTrend(BaseModel):
    keyword: str
    average_ratio: float      # 전체 평균 검색 비율
    recent_ratio: float       # 최근 7일 평균
    momentum: float           # 성장 모멘텀 (%)
    trend_direction: Literal['rising', 'stable', 'falling']
    velocity: float           # 변화 속도
    total_score: float        # 종합 점수
    trend_data: List[TrendDataPoint]
```

**KeywordBatch** (`backend/models/keyword_batch.py`)
```python
class KeywordBatch(BaseModel):
    keywords: List[str]       # 최대 5개 (네이버 API 제한)
    batch_number: int
    total_batches: int
```

**AnalysisResult** (`backend/models/analysis_result.py`)
```python
class AnalysisResult(BaseModel):
    input_keywords: List[str]
    trends: List[KeywordTrend]
    best_keyword: Optional[KeywordTrend]
    total_analyzed: int
    successful: int
    failed: int
    started_at: datetime
    completed_at: datetime

    @property
    def success_rate(self) -> float
    @property
    def processing_time(self) -> float
```

#### 2.2 DataLab Analyzer v2.0

**`backend/analyzers/datalab_analyzer.py`**

핵심 개선사항:
- **모멘텀 계산**: `((최근7일 - 이전7일) / 이전7일) * 100`
- **트렌드 방향 판정**:
  - Rising: momentum > 10%
  - Falling: momentum < -10%
  - Stable: -10% ≤ momentum ≤ 10%
- **속도(Velocity) 계산**: 일별 변화율 평균
- **하락 패널티**: falling 추세 시 점수 × 0.7

```python
def _calculate_momentum(self, trend_data: List[TrendDataPoint]) -> float:
    recent_7 = trend_data[-7:]
    previous_7 = trend_data[-14:-7]

    recent_avg = sum(p.ratio for p in recent_7) / 7
    previous_avg = sum(p.ratio for p in previous_7) / 7

    return ((recent_avg - previous_avg) / previous_avg) * 100
```

#### 2.3 키워드 생성기

**LongTailGenerator** (`backend/generators/keyword_generator.py`)

10개 카테고리, 70+ 수식어:
```python
MODIFIERS = {
    'how_to': ['방법', '하는법', '팁', '가이드', '노하우'],
    'review': ['후기', '리뷰', '사용법', '장단점'],
    'comparison': ['VS', '비교', '차이', '추천', '순위'],
    'problem': ['해결', '오류', '문제', '수리'],
    'timing': ['시기', '타이밍', '언제', '시즌'],
    'price': ['가격', '저렴한', '할인', '가성비'],
    'quality': ['좋은', '인기', '유명한', '추천'],
    'location': ['추천', '베스트', '근처', '주변'],
    'diy': ['DIY', '직접', '셀프', '만들기'],
    'beginner': ['초보', '입문', '처음', '기초']
}
```

최대 30개 변형 생성

**AutocompleteGenerator** (`backend/generators/autocomplete_generator.py`)

네이버 자동완성 API 활용:
```python
API_URL = "https://ac.search.naver.com/nx/ac"

def generate(seed_keyword: str) -> List[str]:
    # 네이버 검색창 자동완성 결과 크롤링
    # httpx 미설치 시 더미 결과 반환
```

#### 2.4 배치 프로세서

**BatchProcessor** (`backend/services/batch_processor.py`)

네이버 API 제한(5개) 대응:
```python
class BatchProcessor:
    def __init__(
        self,
        analyzer: DataLabAnalyzer,
        batch_size: int = 5,           # 네이버 제한
        delay_seconds: float = 1.0,    # Rate limiting
        progress_callback: Optional[Callable] = None
    )

    def process(keywords: List[str]) -> List[KeywordTrend]:
        # 키워드를 5개씩 분할
        # 배치 간 1초 대기
        # 진행률 콜백 호출
```

#### 2.5 키워드 비교 서비스

**KeywordComparisonService** (`backend/services/keyword_comparison_service.py`)

```python
def compare(keywords: List[str]) -> AnalysisResult:
    # 1-5개 키워드 비교
    # 최고 키워드 자동 선정
    # 순위별 정렬

def get_ranking(result: AnalysisResult) -> List[tuple]:
    # [(순위, KeywordTrend), ...] 반환

def get_comparison_summary(result: AnalysisResult) -> str:
    # 텍스트 요약 생성
```

### 테스트 결과
- Phase 2 관련 테스트 전체 통과 ✅
- GitHub 푸시 완료 ✅

---

## ✅ Phase 3: Smart Discovery Service

**목표**: 키워드 자동 발굴 및 기회 점수 분석 시스템 구축

### 구현 내용

#### 3.1 OpportunityScore 시스템

**OpportunityScore Model** (`backend/models/opportunity_score.py`)

```python
class OpportunityScore(BaseModel):
    keyword: str

    # 개별 점수 (0-100)
    search_demand: float      # 검색 수요 (30%)
    momentum: float           # 성장 추세 (35%)
    competition_gap: float    # 경쟁 공백 (20%)
    suitability: float        # 블로그 적합도 (15%)

    @computed_field
    @property
    def total_score(self) -> float:
        return (
            self.search_demand * 0.30 +
            self.momentum * 0.35 +
            self.competition_gap * 0.20 +
            self.suitability * 0.15
        )

    @computed_field
    @property
    def grade(self) -> Literal['S', 'A', 'B', 'C', 'D']:
        score = self.total_score
        if score >= 80: return 'S'
        elif score >= 65: return 'A'
        elif score >= 50: return 'B'
        elif score >= 35: return 'C'
        else: return 'D'
```

**OpportunityScorer** (`backend/services/opportunity_scorer.py`)

점수 계산 로직:
```python
def _calculate_search_demand(trend: KeywordTrend) -> float:
    # average_ratio를 0-100 스케일로
    return min(100.0, max(0.0, trend.average_ratio))

def _calculate_momentum_score(trend: KeywordTrend) -> float:
    # momentum (-100~+100)을 0-100으로 정규화
    # 0% → 50점, +50% → 75점, +100% → 100점
    # -50% → 25점, -100% → 0점

def _calculate_competition_gap(trend: KeywordTrend) -> float:
    # recent_ratio의 80%를 경쟁 공백으로 간주
    return min(100.0, trend.recent_ratio * 0.8)

def _calculate_suitability(trend: KeywordTrend) -> float:
    score = 50.0  # 기본 점수
    # 길이 점수 (5-15자: +20점)
    # 공백 포함 (롱테일): +15점
    # 블로그 친화 수식어: +15점
    return min(100.0, score)
```

**테스트**: 16 tests passed ✅

#### 3.2 CacheManager

**`backend/utils/cache_manager.py`**

파일 기반 JSON 캐싱:
```python
class CacheManager:
    def __init__(
        self,
        cache_dir: str = ".cache",
        ttl_hours: int = 24,           # 24시간 TTL
        index_file: str = "cache_index.json"
    )

    def save_result(
        seed_keyword: str,
        result_data: Dict,
        metadata: Optional[Dict] = None
    ) -> str:
        # JSON 파일로 저장
        # 인덱스 업데이트
        # 타임스탬프 파일명

    def load_result(seed_keyword: str) -> Optional[Dict]:
        # 인덱스에서 검색
        # 만료 확인
        # 데이터 로드

    def clear_expired() -> int:
        # 만료된 캐시 자동 삭제
```

캐시 구조:
```json
{
  "seed_keyword": "롱패딩",
  "cached_at": "2025-11-19T10:00:00",
  "expires_at": "2025-11-20T10:00:00",
  "metadata": {
    "processing_time": 5.2,
    "success_rate": 100.0
  },
  "result": { ... }
}
```

**테스트**: 17 tests passed ✅

#### 3.3 SmartDiscoveryService

**DiscoveryResult Model** (`backend/models/discovery_result.py`)

```python
class DiscoveryResult(BaseModel):
    seed_keyword: str
    generated_count: int          # 생성된 키워드 수
    analyzed_count: int           # 분석된 키워드 수
    opportunities: List[OpportunityScore]
    cache_hit: bool              # 캐시 히트 여부

    @computed_field
    @property
    def grade_distribution(self) -> Dict[str, int]:
        # {'S': 3, 'A': 5, 'B': 10, 'C': 7, 'D': 5}

    @computed_field
    @property
    def best_opportunity(self) -> OpportunityScore:
        # 최고 점수 키워드
```

**SmartDiscoveryService** (`backend/services/smart_discovery_service.py`)

5단계 파이프라인:
```python
def discover(
    seed_keyword: str,
    use_autocomplete: bool = True,
    min_grade: str = 'C',
    progress_callback: Optional[Callable] = None
) -> DiscoveryResult:

    # Stage 1: 캐시 확인
    if use_cache and cached := self._check_cache(seed_keyword):
        return cached

    # Stage 2: 키워드 생성 (롱테일 + 자동완성)
    keywords = self._generate_keywords(seed_keyword, use_autocomplete)

    # Stage 3: 배치 분석 (네이버 DataLab)
    trends = self._analyze_keywords(keywords)

    # Stage 4: 기회 점수 계산
    opportunities = self._calculate_scores(trends)

    # Stage 5: 등급 필터링
    filtered = self.scorer.filter_by_grade(opportunities, min_grade)

    # 결과 생성 및 캐시 저장
    result = DiscoveryResult(...)
    self._save_to_cache(seed_keyword, result)

    return result
```

**테스트**: 20 tests passed ✅

#### 3.4 ProgressTracker

**`backend/utils/progress_tracker.py`**

단일 작업 추적:
```python
class ProgressTracker:
    def update(current: int, message: str):
        # 진행률 업데이트
        # 콜백 실행
        # Streamlit 위젯 업데이트

    def complete(message: str):
        # 완료 처리

    # 컨텍스트 매니저 지원
    with ProgressTracker(total_steps=100) as tracker:
        tracker.update(50, "진행 중")
```

다단계 작업 추적:
```python
class MultiStageProgressTracker:
    def __init__(stages: List[str]):
        # 5단계: ["캐시 확인", "키워드 생성", ...]

    @property
    def overall_progress(self) -> float:
        # 전체 진행률 (가중치 반영)

    def next_stage(message: str):
        # 다음 단계로 이동
```

Streamlit 통합:
```python
progress_widget = st.empty()
tracker = ProgressTracker(
    total_steps=100,
    streamlit_widget=progress_widget
)
# 자동으로 st.progress() 업데이트
```

**테스트**: 27 tests passed ✅

#### 3.5 Smart Discovery UI

**`app/pages/1_🔍_smart_discovery.py`**

전체 기능 구현:

**입력 섹션**:
- 시드 키워드 입력
- 최소 등급 선택 (S/A/B/C/D)
- 네이버 자동완성 사용 여부
- 캐시 사용 여부

**진행률 표시**:
```python
def progress_callback(stage_name, current, total, overall_progress):
    st.progress(
        overall_progress / 100,
        text=f"[{current}/{total}] {stage_name}"
    )
```

**결과 표시**:
- 요약 메트릭 (4개 카드)
- 등급 분포 차트
- 최고 기회 키워드 상세
- 상위 20개 기회 목록 (등급별 색상)

**Excel 다운로드**:
```python
def create_excel_export(result) -> bytes:
    # Sheet 1: 요약
    # Sheet 2: 기회 키워드 (전체 데이터)
    # Sheet 3: 등급 분포
```

**캐시 관리** (사이드바):
- 캐시 통계 (개수, 크기)
- 만료 삭제 버튼
- 전체 삭제 버튼

---

## 📊 테스트 현황

### 전체 테스트 통과율: 100% ✅

```
총 80개 단위 테스트
├── OpportunityScorer      : 16 tests ✅
├── CacheManager           : 17 tests ✅
├── SmartDiscoveryService  : 20 tests ✅
└── ProgressTracker        : 27 tests ✅
```

### 테스트 커버리지

**Phase 1 테스트**:
- 기본 유틸리티 검증: 8/8 ✅

**Phase 2 테스트**:
- DataLab Analyzer v2.0 검증
- 키워드 생성기 검증
- 배치 프로세서 검증

**Phase 3 테스트**:
```bash
# 전체 실행
pytest tests/unit/ -v

# Phase 3만 실행
pytest tests/unit/test_opportunity_scorer.py \
       tests/unit/test_cache_manager.py \
       tests/unit/test_smart_discovery_service.py \
       tests/unit/test_progress_tracker.py -v
```

### 주요 테스트 케이스

**OpportunityScorer**:
- 점수 계산 정확성
- 등급 판정 로직
- 가중치 검증
- 배치 처리

**CacheManager**:
- 저장/로드 기능
- TTL 만료 처리
- 인덱스 관리
- 파일명 안전화

**SmartDiscoveryService**:
- 5단계 파이프라인
- 캐시 히트/미스
- 진행률 콜백
- 등급 필터링

**ProgressTracker**:
- 단일/다단계 추적
- 컨텍스트 매니저
- Streamlit 통합
- 가중치 계산

---

## 🛠 기술 스택

### Backend
- **Python**: 3.14 (호환성 폴백 처리)
- **Pydantic**: 데이터 검증 및 설정 관리
- **httpx**: HTTP 클라이언트 (폴백: 더미)
- **loguru**: 로깅 (폴백: 표준 logging)

### Frontend
- **Streamlit**: 웹 UI 프레임워크
- **Pandas**: 데이터 처리 및 Excel 생성
- **openpyxl**: Excel 파일 생성

### API
- **Naver DataLab API**: 키워드 트렌드 분석
- **Naver Autocomplete API**: 자동완성 키워드
- **Google Gemini API**: AI 컨텐츠 생성 (Phase 4)

### Testing
- **pytest**: 단위/통합 테스트
- **pytest-cov**: 테스트 커버리지
- **pytest-mock**: 모킹

### 개발 도구
- **Git**: 버전 관리
- **GitHub**: 원격 저장소

---

## 🎯 다음 단계

### Phase 4: AI Content Generation Engine (예정)

**목표**: Google Gemini 기반 블로그 컨텐츠 자동 생성

구현 예정:
1. **Step 4.1**: Gemini API 통합
   - API 클라이언트 구현
   - 프롬프트 엔지니어링

2. **Step 4.2**: 컨텐츠 생성 서비스
   - 템플릿 시스템
   - 섹션별 생성 (제목, 도입, 본문, 결론)

3. **Step 4.3**: UI 페이지
   - 키워드 선택
   - 생성 옵션 설정
   - 결과 미리보기 및 편집
   - Markdown/HTML 다운로드

### Phase 5: Performance & Dashboard (예정)

**목표**: 성능 최적화 및 대시보드

구현 예정:
1. **Performance Optimization**
   - Redis 캐싱 (선택적)
   - 비동기 처리
   - 배치 크기 최적화

2. **Dashboard**
   - 전체 통계 대시보드
   - 트렌드 차트
   - 히스토리 관리

---

## 📝 사용 방법

### 환경 설정

1. **환경 변수 설정** (`.env`)
```bash
NAVER_DATALAB_CLIENT_ID=your_client_id
NAVER_DATALAB_CLIENT_SECRET=your_client_secret
GOOGLE_GEMINI_API_KEY=your_api_key
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **테스트 실행**
```bash
pytest tests/unit/ -v
```

### Smart Discovery 사용

**CLI 방식** (개발/테스트):
```python
from backend.services.smart_discovery_service import SmartDiscoveryService

service = SmartDiscoveryService(use_cache=True)

result = service.discover(
    seed_keyword="롱패딩",
    use_autocomplete=True,
    min_grade='B'
)

print(f"발견 기회: {len(result.opportunities)}개")
print(f"최고 키워드: {result.best_opportunity.keyword}")
print(f"등급: {result.best_opportunity.grade}")
```

**Streamlit UI 방식**:
```bash
streamlit run app/pages/1_🔍_smart_discovery.py
```

UI 사용법:
1. 시드 키워드 입력 (예: "롱패딩")
2. 최소 등급 선택 (S/A/B/C/D)
3. 옵션 설정 (자동완성, 캐시)
4. "분석 시작" 버튼 클릭
5. 결과 확인 및 Excel 다운로드

---

## 🔧 트러블슈팅

### Python 3.14 호환성 문제

**증상**: 패키지 빌드 실패 (numpy, pandas, streamlit)

**해결**:
```bash
# 1. 사전 빌드 wheel 설치
pip install numpy pandas --only-binary :all:

# 2. requirements.txt 버전 제약 완화
numpy>=1.24.0  # 특정 버전 고정 X
```

### pydantic_settings 미설치

**증상**: `ModuleNotFoundError: No module named 'pydantic_settings'`

**해결**: 폴백 처리 구현됨
```python
# config/settings.py
try:
    from pydantic_settings import BaseSettings
except ImportError:
    class BaseSettings:
        def __init__(self, **data):
            # 폴백 구현
```

### Streamlit 미설치

**증상**: UI 페이지 실행 불가

**해결**: 모든 UI 파일에 폴백 처리
```python
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None
```

---

## 📌 중요 노트

### 의존성 폴백 전략
모든 선택적 의존성에 대해 폴백 구현:
- **loguru** → 표준 `logging`
- **httpx** → 더미 구현 (Phase 4 필수)
- **streamlit** → None 처리
- **pydantic_settings** → 기본 클래스

### 네이버 API 제한
- **DataLab API**: 최대 5개 키워드/요청
- **Rate Limit**: 배치 간 1초 대기 권장
- **BatchProcessor**가 자동 처리

### 캐시 관리
- 기본 TTL: 24시간
- 파일 기반: `.cache/` 디렉토리
- 자동 만료 삭제: 컨텍스트 매니저 종료 시

---

## 📈 프로젝트 메트릭

### 코드 통계
- **총 Python 파일**: 30+
- **총 코드 라인**: ~5,000 lines
- **테스트 파일**: 10+
- **테스트 케이스**: 80+

### 커밋 히스토리
- **Phase 1**: 초기 구조 생성
- **Phase 2**: 키워드 생성 엔진
- **Phase 3**: 스마트 발굴 서비스

### GitHub 저장소
```
https://github.com/hyeonjeho3-star/blogerV2.git
```

---

## 🤝 기여자

- **Developer**: 사용자
- **AI Assistant**: Claude (Anthropic)
- **Tool**: Claude Code

---

## 📄 라이선스

이 프로젝트는 개인 프로젝트입니다.

---

**최종 업데이트**: 2025-11-19
**버전**: Phase 3 완료
**다음 마일스톤**: Phase 4 - AI Content Generation Engine
