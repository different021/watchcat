from datetime import datetime, time, timedelta, timezone

class MarketClock:
    def __init__(self):
        self.KST = timezone(timedelta(hours=9))
        self._market_open = self._parse_time("09:00")
        self._market_close = self._parse_time("15:30")
        self._market_final = self._parse_time("15:31")  # 장 종료 알림 시점

    def now(self) -> datetime:
        """현재 시각 (datetime, KST 기준)"""
        return datetime.now(self.KST)
    
    def formatted_now(self) -> str:
        """표준 출력용 현재 시각 문자열 ('YYYY-MM-DD HH:MM:SS')"""
        return self.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def time_now(self) -> time:
        """현재 시각 (time only, KST 기준)"""
        return self.now().time()

    def today_str(self) -> str:
        """오늘 날짜 문자열 ('YYYY-MM-DD')"""
        return self.now().strftime("%Y-%m-%d")

    def is_market_open_time(self) -> bool:
        """지금이 장중인가? (09:00 ~ 15:30 포함)"""
        now = self.time_now()
        return self._market_open <= now <= self._market_close

    def is_before_market(self) -> bool:
        """지금이 장 시작 전인가? (09:00 이전)"""
        return self.time_now() < self._market_open

    def is_after_close(self) -> bool:
        """지금이 장 종료 이후인가? (15:31 이후)"""
        return self.time_now() >= self._market_final

    def market_open_time(self) -> time:
        """장 시작 시각 (time)"""
        return self._market_open

    def market_close_time(self) -> time:
        """장 종료 시각 (time)"""
        return self._market_close

    def market_final_cutoff_time(self) -> time:
        """장 종료 알림 기준 시각 (15:31)"""
        return self._market_final

    @staticmethod
    def _parse_time(tstr: str) -> time:
        """'HH:MM' 문자열을 time 객체로 변환"""
        return datetime.strptime(tstr, "%H:%M").time()
