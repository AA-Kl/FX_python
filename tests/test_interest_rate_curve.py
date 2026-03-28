import pytest
import math
from datetime import date, timedelta
from src.fxswap.classes.interest_rate_curve import (
    InterestRateCurve,
    DayCountConvention,
    InterpolationMethod,
)


def make_curve(interp=InterpolationMethod.LOG_LINEAR, day_count=DayCountConvention.ACT_365):
    """Helper: build a simple curve with known pillar dates and zero rates."""
    ref = date(2024, 1, 2)
    pillars = [
        date(2024, 4, 2),   # ~3 months
        date(2024, 7, 2),   # ~6 months
        date(2025, 1, 2),   # ~1 year
        date(2026, 1, 2),   # ~2 years
        date(2029, 1, 2),   # ~5 years
    ]
    rates = [0.04, 0.042, 0.045, 0.047, 0.050]
    return InterestRateCurve(ref, pillars, rates, day_count=day_count, interpolation=interp)


class TestCurveConstruction:
    def test_basic_construction(self):
        curve = make_curve()
        assert curve.reference_date == date(2024, 1, 2)

    def test_discount_factor_at_reference_date(self):
        curve = make_curve()
        df = curve.discount_factor(curve.reference_date)
        assert abs(df - 1.0) < 1e-12

    def test_discount_factors_are_decreasing(self):
        curve = make_curve()
        dates = [
            date(2024, 4, 2),
            date(2025, 1, 2),
            date(2026, 1, 2),
            date(2027, 1, 2),
            date(2029, 1, 2),
        ]
        dfs = [curve.discount_factor(d) for d in dates]
        for i in range(len(dfs) - 1):
            assert dfs[i] > dfs[i + 1], f"df[{i}]={dfs[i]} not > df[{i+1}]={dfs[i+1]}"

    def test_discount_factors_less_than_one(self):
        curve = make_curve()
        for d in [date(2024, 6, 1), date(2025, 1, 2), date(2026, 1, 2)]:
            assert curve.discount_factor(d) < 1.0

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            InterestRateCurve(date(2024, 1, 2), [date(2024, 6, 1)], [0.04, 0.05])

    def test_empty_pillars_raises(self):
        with pytest.raises(ValueError):
            InterestRateCurve(date(2024, 1, 2), [], [])


class TestDiscountFactorConsistency:
    def test_df_exp_minus_r_t(self):
        """df(t) must equal exp(-r(t)*t) by construction."""
        curve = make_curve(interp=InterpolationMethod.LINEAR)
        for d in [date(2024, 7, 2), date(2025, 1, 2), date(2026, 1, 2)]:
            t = curve.year_fraction(curve.reference_date, d)
            r = curve.zero_rate(d)
            expected_df = math.exp(-r * t)
            actual_df = curve.discount_factor(d)
            assert abs(actual_df - expected_df) < 1e-10, \
                f"Date {d}: df={actual_df} vs exp(-r*t)={expected_df}"

    def test_df_at_pillars(self):
        """At pillar dates with LOG_LINEAR, df = exp(-r*t) exactly."""
        curve = make_curve(interp=InterpolationMethod.LOG_LINEAR)
        for d, r in zip(curve._pillar_dates, curve._zero_rates):
            t = curve.year_fraction(curve.reference_date, d)
            expected = math.exp(-r * t)
            actual = curve.discount_factor(d)
            assert abs(actual - expected) < 1e-10


class TestForwardRate:
    def test_forward_rate_consistency(self):
        """f(t1,t2) should satisfy df(t2) = df(t1)/(1+f*tau)."""
        curve = make_curve()
        t1 = date(2024, 7, 2)
        t2 = date(2025, 1, 2)
        fwd = curve.forward_rate(t1, t2)
        tau = curve.year_fraction(t1, t2)
        df1 = curve.discount_factor(t1)
        df2 = curve.discount_factor(t2)
        implied_df2 = df1 / (1.0 + fwd * tau)
        assert abs(implied_df2 - df2) < 1e-10

    def test_forward_rate_positive_rates(self):
        curve = make_curve()
        fwd = curve.forward_rate(date(2024, 7, 2), date(2025, 1, 2))
        assert fwd > 0

    def test_forward_rate_invalid_dates_raises(self):
        curve = make_curve()
        with pytest.raises(ValueError):
            curve.forward_rate(date(2025, 1, 2), date(2024, 7, 2))


class TestYearFraction:
    def test_act_365_one_year(self):
        curve = InterestRateCurve(
            date(2024, 1, 2),
            [date(2025, 1, 2)],
            [0.04],
            day_count=DayCountConvention.ACT_365,
        )
        yf = curve.year_fraction(date(2024, 1, 2), date(2025, 1, 2))
        assert abs(yf - 366 / 365.0) < 1e-10  # 2024 is leap year, 366 days

    def test_act_360_one_year(self):
        curve = InterestRateCurve(
            date(2024, 1, 2),
            [date(2025, 1, 2)],
            [0.04],
            day_count=DayCountConvention.ACT_360,
        )
        yf = curve.year_fraction(date(2024, 1, 1), date(2024, 7, 1))
        assert abs(yf - 182 / 360.0) < 1e-10

    def test_thirty_360(self):
        curve = InterestRateCurve(
            date(2024, 1, 2),
            [date(2025, 1, 2)],
            [0.04],
            day_count=DayCountConvention.THIRTY_360,
        )
        yf = curve.year_fraction(date(2024, 1, 1), date(2025, 1, 1))
        assert abs(yf - 1.0) < 1e-10


class TestInterpolationMethods:
    def test_linear_interpolation_between_pillars(self):
        curve = make_curve(interp=InterpolationMethod.LINEAR)
        # Date between 3M and 6M pillar
        d = date(2024, 5, 17)
        r = curve.zero_rate(d)
        assert 0.04 <= r <= 0.042

    def test_log_linear_interpolation(self):
        curve = make_curve(interp=InterpolationMethod.LOG_LINEAR)
        d = date(2024, 5, 17)
        r = curve.zero_rate(d)
        assert 0.04 <= r <= 0.045

    def test_cubic_spline_interpolation(self):
        curve = make_curve(interp=InterpolationMethod.CUBIC_SPLINE)
        d = date(2024, 5, 17)
        r = curve.zero_rate(d)
        # Should return a reasonable rate
        assert 0.03 <= r <= 0.06

    def test_extrapolation_before_first_pillar(self):
        curve = make_curve()
        d = date(2024, 1, 15)  # Before first pillar
        r = curve.zero_rate(d)
        assert r == curve._zero_rates[0]  # Flat extrapolation

    def test_extrapolation_after_last_pillar(self):
        curve = make_curve()
        d = date(2035, 1, 2)  # After last pillar
        r = curve.zero_rate(d)
        assert r == curve._zero_rates[-1]


class TestBootstrapping:
    def test_bootstrap_from_deposits(self):
        ref = date(2024, 1, 2)
        deposits = [
            {"maturity_date": date(2024, 4, 2), "rate": 0.04},
            {"maturity_date": date(2024, 7, 2), "rate": 0.042},
            {"maturity_date": date(2025, 1, 2), "rate": 0.045},
        ]
        curve = InterestRateCurve.from_deposits(ref, deposits)
        assert curve.discount_factor(ref) == 1.0
        # Discount factors should decrease
        df1 = curve.discount_factor(date(2024, 4, 2))
        df2 = curve.discount_factor(date(2024, 7, 2))
        df3 = curve.discount_factor(date(2025, 1, 2))
        assert df1 > df2 > df3

    def test_bootstrap_from_swaps(self):
        ref = date(2024, 1, 2)
        swaps = [
            {"maturity_date": date(2025, 1, 2), "fixed_rate": 0.045, "frequency": "annual"},
            {"maturity_date": date(2026, 1, 2), "fixed_rate": 0.047, "frequency": "annual"},
            {"maturity_date": date(2029, 1, 2), "fixed_rate": 0.050, "frequency": "annual"},
        ]
        curve = InterestRateCurve.from_swaps(ref, swaps)
        assert curve.discount_factor(ref) == 1.0
        df1 = curve.discount_factor(date(2025, 1, 2))
        df2 = curve.discount_factor(date(2026, 1, 2))
        assert df1 > df2

    def test_bootstrap_full(self):
        ref = date(2024, 1, 2)
        deposits = [
            {"maturity_date": date(2024, 4, 2), "rate": 0.04},
        ]
        swaps = [
            {"maturity_date": date(2025, 1, 2), "fixed_rate": 0.045, "frequency": "annual"},
            {"maturity_date": date(2026, 1, 2), "fixed_rate": 0.047, "frequency": "annual"},
        ]
        curve = InterestRateCurve.bootstrap(ref, deposits=deposits, fras=[], swaps=swaps)
        assert curve.discount_factor(ref) == 1.0
        assert curve.discount_factor(date(2026, 1, 2)) < curve.discount_factor(date(2025, 1, 2))

    def test_bootstrap_empty_raises(self):
        ref = date(2024, 1, 2)
        with pytest.raises(ValueError):
            InterestRateCurve.bootstrap(ref, deposits=[], fras=[], swaps=[])
