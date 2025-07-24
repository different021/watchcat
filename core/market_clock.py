from datetime import datetime, timedelta, timezone

class MarketClock:
    def __init__(self):
        self.KST = timezone(timedelta(hours=9))
        self.last_open_date = None
        self.last_close_date = None
        self.last_1530_date = None

    def now(self):
        return datetime.now(self.KST)

    def today_str(self):
        return self.now().strftime("%Y-%m-%d")

    def is_market_open(self):
        t = self.now().time()
        return datetime.strptime("09:00", "%H:%M").time() <= t <= datetime.strptime("15:30", "%H:%M").time()

    def should_open(self):
        t = self.now().time()
        return t >= datetime.strptime("09:00", "%H:%M").time() and self.last_open_date != self.today_str()

    def should_close(self):
        t = self.now().time()
        return t >= datetime.strptime("15:31", "%H:%M").time() and self.last_close_date != self.today_str()

    def should_print_1530(self):
        t = self.now().time()
        return t >= datetime.strptime("15:30", "%H:%M").time() and self.last_1530_date != self.today_str()

    def mark_open(self):
        self.last_open_date = self.today_str()

    def mark_close(self):
        self.last_close_date = self.today_str()

    def mark_1530(self):
        self.last_1530_date = self.today_str()
