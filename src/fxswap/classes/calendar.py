"""
Calendar and roll convention support for FX operations.
"""

from datetime import date, timedelta
from enum import Enum


class RollConvention(Enum):
    FOLLOWING = "FOLLOWING"
    MODIFIED_FOLLOWING = "MODIFIED_FOLLOWING"
    PRECEDING = "PRECEDING"
    MODIFIED_PRECEDING = "MODIFIED_PRECEDING"
    UNADJUSTED = "UNADJUSTED"


def _easter(year: int) -> date:
    """Compute Easter Sunday using the Meeus/Jones/Butcher algorithm."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """Return the nth occurrence of weekday (0=Mon..6=Sun) in given month/year."""
    first = date(year, month, 1)
    delta = (weekday - first.weekday()) % 7
    first_occurrence = first + timedelta(days=delta)
    return first_occurrence + timedelta(weeks=n - 1)


def _last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    """Return the last occurrence of weekday (0=Mon..6=Sun) in given month/year."""
    if month == 12:
        last = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    delta = (last.weekday() - weekday) % 7
    return last - timedelta(days=delta)


def _adjust_weekend(dt: date) -> date:
    """Move Saturday -> Monday, Sunday -> Monday for US-style weekend adjustments."""
    wd = dt.weekday()
    if wd == 5:  # Saturday
        return dt + timedelta(days=2)
    elif wd == 6:  # Sunday
        return dt + timedelta(days=1)
    return dt


def _adjust_weekend_uk(dt: date) -> date:
    """Move Saturday -> Monday, Sunday -> Monday for UK-style weekend adjustments."""
    return _adjust_weekend(dt)


def _usd_holidays(year: int) -> set:
    """Generate US Federal Reserve holidays for a given year."""
    h = set()
    # New Year's Day
    h.add(_adjust_weekend(date(year, 1, 1)))
    # MLK Day - 3rd Monday in January
    h.add(_nth_weekday_of_month(year, 1, 0, 3))
    # Presidents Day - 3rd Monday in February
    h.add(_nth_weekday_of_month(year, 2, 0, 3))
    # Memorial Day - last Monday in May
    h.add(_last_weekday_of_month(year, 5, 0))
    # Juneteenth - June 19
    h.add(_adjust_weekend(date(year, 6, 19)))
    # Independence Day - July 4
    h.add(_adjust_weekend(date(year, 7, 4)))
    # Labor Day - 1st Monday in September
    h.add(_nth_weekday_of_month(year, 9, 0, 1))
    # Columbus Day - 2nd Monday in October
    h.add(_nth_weekday_of_month(year, 10, 0, 2))
    # Veterans Day - November 11
    h.add(_adjust_weekend(date(year, 11, 11)))
    # Thanksgiving - 4th Thursday in November
    h.add(_nth_weekday_of_month(year, 11, 3, 4))
    # Christmas - December 25
    h.add(_adjust_weekend(date(year, 12, 25)))
    return h


def _eur_holidays(year: int) -> set:
    """Generate TARGET (EUR) holidays for a given year."""
    h = set()
    easter = _easter(year)
    h.add(date(year, 1, 1))   # New Year's Day
    h.add(easter - timedelta(days=2))  # Good Friday
    h.add(easter + timedelta(days=1))  # Easter Monday
    h.add(date(year, 5, 1))   # Labour Day
    h.add(date(year, 12, 25)) # Christmas
    h.add(date(year, 12, 26)) # Boxing Day
    return h


def _gbp_holidays(year: int) -> set:
    """Generate UK bank holidays for a given year."""
    h = set()
    easter = _easter(year)
    # New Year's Day (adjusted)
    h.add(_adjust_weekend_uk(date(year, 1, 1)))
    # Good Friday
    h.add(easter - timedelta(days=2))
    # Easter Monday
    h.add(easter + timedelta(days=1))
    # Early May Bank Holiday - 1st Monday in May
    h.add(_nth_weekday_of_month(year, 5, 0, 1))
    # Spring Bank Holiday - last Monday in May
    h.add(_last_weekday_of_month(year, 5, 0))
    # Summer Bank Holiday - last Monday in August
    h.add(_last_weekday_of_month(year, 8, 0))
    # Christmas (adjusted)
    christmas = date(year, 12, 25)
    boxing = date(year, 12, 26)
    if christmas.weekday() == 5:  # Saturday
        h.add(date(year, 12, 27))  # Monday
        h.add(date(year, 12, 28))  # Tuesday (Boxing Day substitute)
    elif christmas.weekday() == 6:  # Sunday
        h.add(date(year, 12, 26))  # Monday
        h.add(date(year, 12, 27))  # Tuesday (Boxing Day substitute)
    elif boxing.weekday() == 6:  # Boxing Day on Sunday
        h.add(christmas)
        h.add(date(year, 12, 28))
    else:
        h.add(christmas)
        h.add(boxing)
    return h


def _jpy_holidays(year: int) -> set:
    """Generate Japanese public holidays for a given year (approximate)."""
    h = set()
    h.add(date(year, 1, 1))
    h.add(date(year, 1, 2))
    h.add(date(year, 1, 3))
    h.add(_nth_weekday_of_month(year, 1, 0, 2))  # Coming of Age Day
    h.add(_adjust_weekend(date(year, 2, 11)))
    h.add(_adjust_weekend(date(year, 2, 23)))
    h.add(date(year, 3, 20))  # Vernal Equinox (approx)
    h.add(_adjust_weekend(date(year, 4, 29)))
    h.add(_adjust_weekend(date(year, 5, 3)))
    h.add(_adjust_weekend(date(year, 5, 4)))
    h.add(_adjust_weekend(date(year, 5, 5)))
    h.add(_nth_weekday_of_month(year, 7, 0, 3))  # Marine Day
    h.add(_adjust_weekend(date(year, 8, 11)))
    h.add(_nth_weekday_of_month(year, 9, 0, 3))  # Respect for the Aged Day
    h.add(date(year, 9, 23))  # Autumnal Equinox (approx)
    h.add(_nth_weekday_of_month(year, 10, 0, 2))  # Health and Sports Day
    h.add(_adjust_weekend(date(year, 11, 3)))
    h.add(_adjust_weekend(date(year, 11, 23)))
    return h


def _chf_holidays(year: int) -> set:
    """Generate Swiss public holidays for a given year."""
    h = set()
    easter = _easter(year)
    h.add(date(year, 1, 1))   # New Year's Day
    h.add(date(year, 1, 2))   # Berchtoldstag
    h.add(easter - timedelta(days=2))   # Good Friday
    h.add(easter + timedelta(days=1))   # Easter Monday
    h.add(date(year, 5, 1))   # Labour Day
    h.add(easter + timedelta(days=39))  # Ascension Day
    h.add(easter + timedelta(days=50))  # Whit Monday
    h.add(date(year, 8, 1))   # National Day
    h.add(date(year, 12, 25)) # Christmas
    h.add(date(year, 12, 26)) # Boxing Day
    return h


class Calendar:
    """
    Business calendar with holiday management and date rolling.
    
    Supports weekend detection, holiday lookup, business day arithmetic,
    and roll convention application.
    """

    def __init__(self, name: str, holidays: set = None, weekend_days: set = None):
        """
        Initialize a Calendar.
        
        Args:
            name: Human-readable name for the calendar.
            holidays: Set of holiday dates. If None, uses empty set.
            weekend_days: Set of weekday integers (0=Mon..6=Sun) treated as
                          weekend. If None, defaults to {5, 6} (Sat, Sun).
        """
        self.name = name
        self._holidays = set(holidays) if holidays else set()
        self._weekend_days = set(weekend_days) if weekend_days is not None else {5, 6}
        self._holiday_generator = None  # callable(year) -> set[date]
        self._generated_years: set = set()

    def _ensure_year(self, year: int) -> None:
        """Lazily generate holidays for a year if a generator is registered."""
        if self._holiday_generator is not None and year not in self._generated_years:
            self._holidays.update(self._holiday_generator(year))
            self._generated_years.add(year)

    def is_business_day(self, dt: date) -> bool:
        """Return True if dt is a business day (not weekend, not holiday)."""
        self._ensure_year(dt.year)
        return dt.weekday() not in self._weekend_days and dt not in self._holidays

    def add_business_days(self, dt: date, n: int) -> date:
        """Return the date n business days after dt."""
        current = dt
        remaining = n
        step = 1 if n >= 0 else -1
        while remaining != 0:
            current += timedelta(days=step)
            if self.is_business_day(current):
                remaining -= step
        return current

    def subtract_business_days(self, dt: date, n: int) -> date:
        """Return the date n business days before dt."""
        return self.add_business_days(dt, -n)

    def roll(self, dt: date, convention: RollConvention) -> date:
        """
        Adjust dt according to the given roll convention.
        
        Args:
            dt: The date to adjust.
            convention: The roll convention to apply.
            
        Returns:
            The adjusted date.
        """
        if convention == RollConvention.UNADJUSTED:
            return dt
        if self.is_business_day(dt):
            return dt
        if convention == RollConvention.FOLLOWING:
            return self._following(dt)
        if convention == RollConvention.PRECEDING:
            return self._preceding(dt)
        if convention == RollConvention.MODIFIED_FOLLOWING:
            result = self._following(dt)
            if result.month != dt.month:
                return self._preceding(dt)
            return result
        if convention == RollConvention.MODIFIED_PRECEDING:
            result = self._preceding(dt)
            if result.month != dt.month:
                return self._following(dt)
            return result
        return dt

    def _following(self, dt: date) -> date:
        """Move forward to next business day."""
        current = dt + timedelta(days=1)
        while not self.is_business_day(current):
            current += timedelta(days=1)
        return current

    def _preceding(self, dt: date) -> date:
        """Move backward to previous business day."""
        current = dt - timedelta(days=1)
        while not self.is_business_day(current):
            current -= timedelta(days=1)
        return current

    def business_days_between(self, start: date, end: date) -> int:
        """
        Count business days between start (inclusive) and end (exclusive).
        
        Returns a negative number if start > end.
        """
        if start == end:
            return 0
        if start > end:
            return -self.business_days_between(end, start)
        count = 0
        current = start
        while current < end:
            if self.is_business_day(current):
                count += 1
            current += timedelta(days=1)
        return count

    def get_holidays(self, year: int) -> set:
        """Return all holidays for the given year."""
        self._ensure_year(year)
        return {h for h in self._holidays if h.year == year}

    @classmethod
    def for_currency(cls, currency) -> "Calendar":
        """
        Factory method: return a currency-specific calendar.
        
        Args:
            currency: A Currency enum value (USD, EUR, GBP, JPY, CHF).
            
        Returns:
            A Calendar instance with appropriate holidays.
            
        Raises:
            ValueError: If no calendar is defined for the currency.
        """
        # Import here to avoid circular imports
        from .currency import Currency as Cur

        generators = {
            Cur.USD: ("USD Federal Reserve", _usd_holidays),
            Cur.EUR: ("TARGET EUR", _eur_holidays),
            Cur.GBP: ("UK Bank Holidays", _gbp_holidays),
            Cur.JPY: ("Japan Public Holidays", _jpy_holidays),
            Cur.CHF: ("Switzerland Public Holidays", _chf_holidays),
        }
        if currency not in generators:
            raise ValueError(f"No calendar defined for currency: {currency}")
        name, generator = generators[currency]
        cal = cls(name=name)
        cal._holiday_generator = generator
        return cal
