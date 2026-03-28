import pytest
from datetime import date
from src.fxswap.classes.calendar import Calendar, RollConvention, _easter
from src.fxswap.classes.currency import Currency


class TestCalendarBasics:
    def setup_method(self):
        # A simple calendar: weekends only, no holidays
        self.cal = Calendar("Test", holidays=set(), weekend_days={5, 6})

    def test_monday_is_business_day(self):
        assert self.cal.is_business_day(date(2024, 1, 8)) is True  # Monday

    def test_saturday_is_not_business_day(self):
        assert self.cal.is_business_day(date(2024, 1, 6)) is False

    def test_sunday_is_not_business_day(self):
        assert self.cal.is_business_day(date(2024, 1, 7)) is False

    def test_holiday_is_not_business_day(self):
        cal = Calendar("Test", holidays={date(2024, 1, 8)})
        assert cal.is_business_day(date(2024, 1, 8)) is False

    def test_add_business_days_simple(self):
        # Friday Jan 5 2024 + 1 bd = Monday Jan 8 2024
        assert self.cal.add_business_days(date(2024, 1, 5), 1) == date(2024, 1, 8)

    def test_add_business_days_zero(self):
        assert self.cal.add_business_days(date(2024, 1, 5), 0) == date(2024, 1, 5)

    def test_add_business_days_across_weekend(self):
        # Friday + 3 bd = Wednesday
        assert self.cal.add_business_days(date(2024, 1, 5), 3) == date(2024, 1, 10)

    def test_subtract_business_days(self):
        # Monday Jan 8 - 1 bd = Friday Jan 5
        assert self.cal.subtract_business_days(date(2024, 1, 8), 1) == date(2024, 1, 5)

    def test_subtract_business_days_across_weekend(self):
        # Wednesday Jan 10 - 3 bd = Friday Jan 5
        assert self.cal.subtract_business_days(date(2024, 1, 10), 3) == date(2024, 1, 5)

    def test_add_negative_business_days(self):
        assert self.cal.add_business_days(date(2024, 1, 8), -1) == date(2024, 1, 5)


class TestRollConventions:
    def setup_method(self):
        self.cal = Calendar("Test", holidays={date(2024, 1, 15)})  # Monday holiday

    def test_unadjusted_returns_original(self):
        # Saturday
        assert self.cal.roll(date(2024, 1, 6), RollConvention.UNADJUSTED) == date(2024, 1, 6)

    def test_following_moves_to_next_bd(self):
        # Saturday Jan 6 -> Monday Jan 8
        assert self.cal.roll(date(2024, 1, 6), RollConvention.FOLLOWING) == date(2024, 1, 8)

    def test_preceding_moves_to_prev_bd(self):
        # Saturday Jan 6 -> Friday Jan 5
        assert self.cal.roll(date(2024, 1, 6), RollConvention.PRECEDING) == date(2024, 1, 5)

    def test_modified_following_same_month(self):
        # Saturday Jan 6 -> Monday Jan 8 (same month, use following)
        assert self.cal.roll(date(2024, 1, 6), RollConvention.MODIFIED_FOLLOWING) == date(2024, 1, 8)

    def test_modified_following_crosses_month(self):
        # Saturday March 30, 2024: following would be April 1
        # Modified following should go back to Friday March 29
        cal = Calendar("Test")
        result = cal.roll(date(2024, 3, 30), RollConvention.MODIFIED_FOLLOWING)
        assert result.month == 3

    def test_modified_preceding_same_month(self):
        assert self.cal.roll(date(2024, 1, 6), RollConvention.MODIFIED_PRECEDING) == date(2024, 1, 5)

    def test_business_day_unchanged_by_any_convention(self):
        bd = date(2024, 1, 8)  # Monday
        for conv in RollConvention:
            assert self.cal.roll(bd, conv) == bd


class TestBusinessDaysBetween:
    def setup_method(self):
        self.cal = Calendar("Test")

    def test_same_date_is_zero(self):
        assert self.cal.business_days_between(date(2024, 1, 8), date(2024, 1, 8)) == 0

    def test_one_business_day(self):
        # Monday to Tuesday
        assert self.cal.business_days_between(date(2024, 1, 8), date(2024, 1, 9)) == 1

    def test_across_weekend(self):
        # Friday to Monday = 1 bd (Friday itself)
        assert self.cal.business_days_between(date(2024, 1, 5), date(2024, 1, 8)) == 1

    def test_full_week(self):
        # Monday to next Monday = 5 bds
        assert self.cal.business_days_between(date(2024, 1, 8), date(2024, 1, 15)) == 5

    def test_reverse_is_negative(self):
        result = self.cal.business_days_between(date(2024, 1, 15), date(2024, 1, 8))
        assert result == -5


class TestLeapYear:
    def test_feb_29_is_business_day(self):
        cal = Calendar("Test")
        assert cal.is_business_day(date(2024, 2, 29)) is True  # 2024 is leap year, Thursday

    def test_add_business_days_around_feb_29(self):
        cal = Calendar("Test")
        # Feb 28 2024 (Wednesday) + 1 = Feb 29 2024 (Thursday)
        assert cal.add_business_days(date(2024, 2, 28), 1) == date(2024, 2, 29)


class TestYearEndEdgeCases:
    def test_new_year_holiday_adjustment(self):
        # Jan 1 2023 is Sunday -> observed Monday Jan 2
        usd_cal = Calendar.for_currency(Currency.USD)
        assert usd_cal.is_business_day(date(2023, 1, 2)) is False

    def test_year_end_add_business_days(self):
        cal = Calendar("Test")
        # Dec 31 2024 is Tuesday, Jan 1 2025 is Wednesday
        # Adding 1 bd from Dec 31 -> Jan 1 (both bds in this calendar)
        result = cal.add_business_days(date(2024, 12, 31), 1)
        assert result == date(2025, 1, 1)


class TestUSDCalendar:
    def setup_method(self):
        self.cal = Calendar.for_currency(Currency.USD)

    def test_thanksgiving_2024(self):
        # 4th Thursday of November 2024 = Nov 28
        assert self.cal.is_business_day(date(2024, 11, 28)) is False

    def test_mlk_day_2024(self):
        # 3rd Monday of January 2024 = Jan 15
        assert self.cal.is_business_day(date(2024, 1, 15)) is False

    def test_independence_day_2024(self):
        # July 4 2024 is Thursday
        assert self.cal.is_business_day(date(2024, 7, 4)) is False

    def test_labor_day_2024(self):
        # 1st Monday of September 2024 = Sep 2
        assert self.cal.is_business_day(date(2024, 9, 2)) is False

    def test_normal_tuesday_is_business_day(self):
        assert self.cal.is_business_day(date(2024, 6, 4)) is True

    def test_get_holidays_returns_set(self):
        holidays = self.cal.get_holidays(2024)
        assert isinstance(holidays, set)
        assert len(holidays) > 0


class TestEURCalendar:
    def setup_method(self):
        self.cal = Calendar.for_currency(Currency.EUR)

    def test_easter_monday_2024(self):
        # Easter Sunday 2024 = March 31, Easter Monday = April 1
        easter = _easter(2024)
        from datetime import timedelta
        easter_monday = easter + timedelta(days=1)
        assert self.cal.is_business_day(easter_monday) is False

    def test_good_friday_2024(self):
        easter = _easter(2024)
        from datetime import timedelta
        good_friday = easter - timedelta(days=2)
        assert self.cal.is_business_day(good_friday) is False

    def test_new_years_day(self):
        assert self.cal.is_business_day(date(2024, 1, 1)) is False

    def test_christmas(self):
        assert self.cal.is_business_day(date(2024, 12, 25)) is False

    def test_normal_business_day(self):
        assert self.cal.is_business_day(date(2024, 6, 3)) is True


class TestForCurrencyFactory:
    def test_usd_calendar(self):
        cal = Calendar.for_currency(Currency.USD)
        assert cal.name == "USD Federal Reserve"

    def test_eur_calendar(self):
        cal = Calendar.for_currency(Currency.EUR)
        assert isinstance(cal, Calendar)

    def test_gbp_calendar(self):
        cal = Calendar.for_currency(Currency.GBP)
        assert isinstance(cal, Calendar)

    def test_jpy_calendar(self):
        cal = Calendar.for_currency(Currency.JPY)
        assert isinstance(cal, Calendar)

    def test_chf_calendar(self):
        cal = Calendar.for_currency(Currency.CHF)
        assert isinstance(cal, Calendar)

    def test_unsupported_currency_raises(self):
        with pytest.raises(ValueError):
            Calendar.for_currency(Currency.AUD)
