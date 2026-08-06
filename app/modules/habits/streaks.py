from datetime import date, timedelta
from itertools import pairwise
from collections import Counter

class StreakCalculator:

    def __init__(self, today: date):
        self.today = today

    def streak(self, dates: list[date], weekly_frequency: int) -> int:
        dates = sorted(dates, reverse=True) # must be in desc order
        if weekly_frequency == 7:
            return self._daily_scan(dates)
        return self._weekly_scan(dates, weekly_frequency)

    def _daily_scan(self, dates: list[date]) -> int:
        """TODO"""
        if not dates:
            return 0

        # Anchor test: streak is alive is the head is today or yesterday
        if (self.today - dates[0]).days > 1:
            return 0

        # Count consecutive days using pairwise()
        # pairwise() = lazy iterator, no list allocation: O(n) time, O(1) extra space
        # Stil O(n) like zip(seq, seq[1:]) would be
        streak = 1
        for curr, prev in pairwise(dates):
            if (curr - prev).days == 1:
                streak += 1
            else:
                break
        return streak

    def _weekly_scan(self, dates: list[date], weekly_frequency: int) -> int:
        if not dates:
            return 0

        # head week is this week or last week
        # first we need to turn dates -> weeks, anchored on mondays?
        #   so per-week tallies? dict[date, int]
        # in: [Jan 9, Jan 8, Jan 6]
        # we need: {Jan 5: 3}  5 is that week's Monday, 3 days that week
        tally = Counter(d - timedelta(days=d.weekday()) for d in dates)

        # Keep only weeks that hit weekly_frequency
        filtered: list[date] = sorted([k for k, v in tally.items() if v >= weekly_frequency], reverse=True)

        # anchor check
        # Streak is 0 if filtered is empty
        if len(filtered) == 0:
            return 0

        streak = 1
        for curr, prev in pairwise(filtered):
            if (curr - prev).days == 7:
                streak += 1
            else:
                break
        return streak
