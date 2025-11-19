"""
네이버 데이터랩 분석기 v2.0
v1.0.3 기반 + 모멘텀 분석 추가
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from backend.analyzers.base_analyzer import BaseAnalyzer
from backend.models.keyword_trend import KeywordTrend, TrendDataPoint
from backend.utils.api_client import APIClient
from backend.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

class DataLabAnalyzer(BaseAnalyzer):
    """네이버 데이터랩 트렌드 분석기"""

    BASE_URL = "https://openapi.naver.com"

    def __init__(self):
        """초기화"""
        self.client = APIClient(
            base_url=self.BASE_URL,
            headers={
                "X-Naver-Client-Id": settings.naver_datalab_client_id,
                "X-Naver-Client-Secret": settings.naver_datalab_client_secret,
                "Content-Type": "application/json"
            }
        )
        logger.info("DataLabAnalyzer 초기화 완료")

    def analyze(self, keywords: List[str]) -> List[KeywordTrend]:
        """
        키워드 트렌드 분석

        Args:
            keywords: 분석할 키워드 (최대 5개)

        Returns:
            KeywordTrend 리스트
        """
        if not keywords:
            raise ValueError("키워드가 비어있습니다")

        if len(keywords) > 5:
            raise ValueError("키워드는 최대 5개까지 가능합니다")

        logger.info(f"키워드 분석 시작: {keywords}")

        # API 요청
        request_body = self._build_request_body(keywords)
        response = self.client.post("/v1/datalab/search", data=request_body)

        # 결과 파싱
        trends = self._parse_response(response, keywords)

        logger.info(f"분석 완료: {len(trends)}개 키워드")
        return trends

    def _build_request_body(self, keywords: List[str]) -> Dict[str, Any]:
        """API 요청 바디 생성"""
        # 날짜 범위 설정 (최근 3개월)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        keyword_groups = [
            {
                "groupName": keyword,
                "keywords": [keyword]
            }
            for keyword in keywords
        ]

        return {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "timeUnit": "date",
            "keywordGroups": keyword_groups
        }

    def _parse_response(self, response: Dict[str, Any], keywords: List[str]) -> List[KeywordTrend]:
        """
        API 응답 파싱 및 분석

        Returns:
            KeywordTrend 리스트 (점수순 정렬)
        """
        results = response.get("results", [])
        trends = []

        for result in results:
            keyword = result.get("title")
            data = result.get("data", [])

            if not data:
                logger.warning(f"키워드 '{keyword}' 데이터 없음")
                continue

            # 데이터 포인트 변환
            trend_data = [
                TrendDataPoint(period=point["period"], ratio=float(point["ratio"]))
                for point in data
            ]

            # 기본 지표 계산
            average_ratio = self._calculate_average(trend_data)
            recent_ratio = self._calculate_recent_average(trend_data, days=7)

            # 신규 지표 계산 (Phase 2 개선)
            momentum = self._calculate_momentum(trend_data)
            trend_direction = self._determine_direction(momentum)
            velocity = self._calculate_velocity(trend_data)

            # 점수 계산 (개선된 공식)
            total_score = self._calculate_score(
                average_ratio, recent_ratio, momentum, trend_direction
            )

            # KeywordTrend 객체 생성
            trend = KeywordTrend(
                keyword=keyword,
                average_ratio=average_ratio,
                recent_ratio=recent_ratio,
                momentum=momentum,
                trend_direction=trend_direction,
                velocity=velocity,
                total_score=total_score,
                trend_data=trend_data
            )

            trends.append(trend)
            logger.debug(f"키워드 '{keyword}' 분석 완료 - 점수: {total_score:.1f}")

        # 점수순 정렬
        trends.sort(key=lambda x: x.total_score, reverse=True)

        return trends

    def _calculate_average(self, data: List[TrendDataPoint]) -> float:
        """전체 기간 평균 계산"""
        if not data:
            return 0.0
        return sum(point.ratio for point in data) / len(data)

    def _calculate_recent_average(self, data: List[TrendDataPoint], days: int = 7) -> float:
        """최근 N일 평균 계산"""
        if not data or len(data) < days:
            return self._calculate_average(data)

        recent_data = data[-days:]
        return sum(point.ratio for point in recent_data) / len(recent_data)

    def _calculate_momentum(self, data: List[TrendDataPoint]) -> float:
        """
        모멘텀 계산
        최근 7일 평균 vs 이전 7일 평균 비교

        Returns:
            -100 ~ +100 (백분율 변화)
        """
        if len(data) < 14:
            return 0.0

        recent_7 = data[-7:]
        previous_7 = data[-14:-7]

        recent_avg = sum(p.ratio for p in recent_7) / len(recent_7)
        previous_avg = sum(p.ratio for p in previous_7) / len(previous_7)

        if previous_avg == 0:
            return 0.0

        momentum = ((recent_avg - previous_avg) / previous_avg) * 100
        return round(momentum, 2)

    def _determine_direction(self, momentum: float) -> str:
        """트렌드 방향 판정"""
        if momentum > 20:
            return 'rising'
        elif momentum < -20:
            return 'falling'
        else:
            return 'stable'

    def _calculate_velocity(self, data: List[TrendDataPoint]) -> float:
        """
        추세 가속도 계산 (선형 회귀 기울기)

        Returns:
            기울기 값
        """
        if len(data) < 3:
            return 0.0

        # 간단한 선형 회귀 (최소제곱법)
        n = len(data)
        x = list(range(n))
        y = [p.ratio for p in data]

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return round(slope, 3)

    def _calculate_score(
        self,
        average_ratio: float,
        recent_ratio: float,
        momentum: float,
        direction: str
    ) -> float:
        """
        종합 점수 계산 (개선된 공식)

        Formula:
            score = (avg * 0.4) + (recent * 0.3) + (momentum_normalized * 0.3)

        하락세 페널티:
            direction == 'falling' → score * 0.7
        """
        # 모멘텀 정규화 (0-100 스케일)
        momentum_normalized = ((momentum + 100) / 2)  # -100~100 → 0~100

        # 기본 점수
        score = (
            average_ratio * 0.4 +
            recent_ratio * 0.3 +
            momentum_normalized * 0.3
        )

        # 하락세 페널티
        if direction == 'falling':
            score *= 0.7
            logger.debug(f"하락세 페널티 적용: {score:.1f}")

        return round(score, 2)
