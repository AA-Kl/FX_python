"""
Interest rate curve with day count conventions and interpolation.
"""

import calendar as _calendar_mod
from datetime import date
from enum import Enum
import math

try:
    import numpy as np
    from scipy.interpolate import CubicSpline
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False


class DayCountConvention(Enum):
    ACT_360 = "ACT/360"
    ACT_365 = "ACT/365"
    ACT_ACT = "ACT/ACT"
    THIRTY_360 = "30/360"


class InterpolationMethod(Enum):
    LINEAR = "LINEAR"
    LOG_LINEAR = "LOG_LINEAR"
    CUBIC_SPLINE = "CUBIC_SPLINE"


class InterestRateCurve:
    """
    Zero-coupon interest rate curve supporting multiple day count conventions
    and interpolation methods.
    """

    def __init__(
        self,
        reference_date: date,
        pillar_dates: list,
        zero_rates: list,
        day_count: DayCountConvention = DayCountConvention.ACT_365,
        interpolation: InterpolationMethod = InterpolationMethod.LOG_LINEAR,
        calendar=None,
    ):
        """
        Construct an InterestRateCurve.

        Args:
            reference_date: The curve's valuation date.
            pillar_dates: Ordered list of dates at which zero rates are known.
            zero_rates: Zero rates (annualised, as decimals) at pillar_dates.
            day_count: Day count convention for year fraction calculation.
            interpolation: Interpolation method between pillars.
            calendar: Optional Calendar for business day adjustments.
        """
        if len(pillar_dates) != len(zero_rates):
            raise ValueError("pillar_dates and zero_rates must have the same length")
        if len(pillar_dates) == 0:
            raise ValueError("At least one pillar is required")

        self.reference_date = reference_date
        self.day_count = day_count
        self.interpolation = interpolation
        self.calendar = calendar

        # Sort pillars by date
        pairs = sorted(zip(pillar_dates, zero_rates), key=lambda x: x[0])
        self._pillar_dates = [p[0] for p in pairs]
        self._zero_rates = [p[1] for p in pairs]

        # Pre-compute year fractions at pillar dates
        self._pillar_t = [self.year_fraction(reference_date, d) for d in self._pillar_dates]

        # Pre-compute log discount factors for LOG_LINEAR
        self._log_dfs = [-r * t for r, t in zip(self._zero_rates, self._pillar_t)]

        # Build cubic spline if needed
        self._spline = None
        if interpolation == InterpolationMethod.CUBIC_SPLINE and len(self._pillar_t) >= 2:
            if _HAS_SCIPY:
                self._spline = CubicSpline(self._pillar_t, self._zero_rates, bc_type='natural')
            # else: fallback to linear

    def year_fraction(self, start: date, end: date) -> float:
        """
        Calculate year fraction between two dates.

        Args:
            start: Start date.
            end: End date.

        Returns:
            Year fraction as a float.
        """
        if self.day_count == DayCountConvention.ACT_360:
            return (end - start).days / 360.0
        elif self.day_count == DayCountConvention.ACT_365:
            return (end - start).days / 365.0
        elif self.day_count == DayCountConvention.ACT_ACT:
            # ISDA Act/Act: split across year boundaries
            if start.year == end.year:
                year_days = 366.0 if _is_leap_year(start.year) else 365.0
                return (end - start).days / year_days
            # Split at year boundaries
            frac = 0.0
            current = start
            while current.year < end.year:
                year_end = date(current.year + 1, 1, 1)
                year_days = 366.0 if _is_leap_year(current.year) else 365.0
                frac += (year_end - current).days / year_days
                current = year_end
            year_days = 366.0 if _is_leap_year(end.year) else 365.0
            frac += (end - current).days / year_days
            return frac
        elif self.day_count == DayCountConvention.THIRTY_360:
            d1, m1, y1 = start.day, start.month, start.year
            d2, m2, y2 = end.day, end.month, end.year
            d1 = min(d1, 30)
            if d1 == 30:
                d2 = min(d2, 30)
            return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)) / 360.0
        return (end - start).days / 365.0

    def zero_rate(self, target_date: date) -> float:
        """
        Interpolated zero rate at target_date.

        Args:
            target_date: The date to interpolate.

        Returns:
            Zero rate as a decimal.
        """
        if target_date == self.reference_date:
            return self._zero_rates[0]
        t = self.year_fraction(self.reference_date, target_date)
        return self._interpolate_zero_rate(t)

    def _interpolate_zero_rate(self, t: float) -> float:
        """Interpolate zero rate at time t (year fraction from reference)."""
        ts = self._pillar_t
        rs = self._zero_rates
        lds = self._log_dfs

        # Extrapolate flat outside pillar range
        if t <= ts[0]:
            return rs[0]
        if t >= ts[-1]:
            return rs[-1]

        # Find surrounding pillars
        idx = _searchsorted(ts, t)
        t0, t1 = ts[idx - 1], ts[idx]
        alpha = (t - t0) / (t1 - t0)

        if self.interpolation == InterpolationMethod.LINEAR:
            return rs[idx - 1] + alpha * (rs[idx] - rs[idx - 1])

        elif self.interpolation == InterpolationMethod.LOG_LINEAR:
            ld0, ld1 = lds[idx - 1], lds[idx]
            log_df = ld0 + alpha * (ld1 - ld0)
            if t == 0:
                return 0.0
            return -log_df / t

        elif self.interpolation == InterpolationMethod.CUBIC_SPLINE:
            if self._spline is not None:
                return float(self._spline(t))
            # Fallback to linear
            return rs[idx - 1] + alpha * (rs[idx] - rs[idx - 1])

        return rs[idx - 1] + alpha * (rs[idx] - rs[idx - 1])

    def discount_factor(self, target_date: date) -> float:
        """
        Discount factor at target_date: df = exp(-r * t).

        Args:
            target_date: The date to compute the discount factor for.

        Returns:
            Discount factor as a float in (0, 1].
        """
        if target_date == self.reference_date:
            return 1.0
        t = self.year_fraction(self.reference_date, target_date)
        if t <= 0:
            return 1.0

        if self.interpolation == InterpolationMethod.LOG_LINEAR:
            ts = self._pillar_t
            lds = self._log_dfs
            rs = self._zero_rates
            if t <= ts[0]:
                r = rs[0]
                return math.exp(-r * t)
            if t >= ts[-1]:
                # Flat extrapolation of zero rate
                r = self._zero_rates[-1]
                return math.exp(-r * t)
            idx = _searchsorted(ts, t)
            t0, t1 = ts[idx - 1], ts[idx]
            alpha = (t - t0) / (t1 - t0)
            log_df = lds[idx - 1] + alpha * (lds[idx] - lds[idx - 1])
            return math.exp(log_df)

        r = self.zero_rate(target_date)
        return math.exp(-r * t)

    def forward_rate(self, start_date: date, end_date: date) -> float:
        """
        Simply-compounded forward rate between start_date and end_date.

        f(t1,t2) derived from: df(t2) = df(t1) * (1 + f * tau)
        where tau = year_fraction(t1, t2).

        Args:
            start_date: Start of the forward period.
            end_date: End of the forward period.

        Returns:
            Forward rate as a decimal.
        """
        tau = self.year_fraction(start_date, end_date)
        if tau <= 0:
            raise ValueError("end_date must be after start_date")
        df1 = self.discount_factor(start_date)
        df2 = self.discount_factor(end_date)
        return (df1 / df2 - 1.0) / tau

    @classmethod
    def from_deposits(
        cls,
        reference_date: date,
        instruments: list,
        calendar=None,
        day_count: DayCountConvention = DayCountConvention.ACT_365,
        interpolation: InterpolationMethod = InterpolationMethod.LOG_LINEAR,
    ) -> "InterestRateCurve":
        """
        Build a curve from deposit instruments.

        Args:
            reference_date: Curve valuation date.
            instruments: List of dicts with keys 'maturity_date' and 'rate'.
            calendar: Optional Calendar instance.
            day_count: Day count convention.
            interpolation: Interpolation method.

        Returns:
            An InterestRateCurve instance.
        """
        pillar_dates = [inst["maturity_date"] for inst in instruments]
        zero_rates = [inst["rate"] for inst in instruments]
        return cls(reference_date, pillar_dates, zero_rates, day_count, interpolation, calendar)

    @classmethod
    def from_swaps(
        cls,
        reference_date: date,
        instruments: list,
        calendar=None,
        day_count: DayCountConvention = DayCountConvention.ACT_365,
        interpolation: InterpolationMethod = InterpolationMethod.LOG_LINEAR,
    ) -> "InterestRateCurve":
        """
        Build a curve by bootstrapping from par swap rates.

        Args:
            reference_date: Curve valuation date.
            instruments: List of dicts with keys 'maturity_date', 'fixed_rate',
                         and 'frequency' ('annual' or 'semi-annual').
            calendar: Optional Calendar instance.
            day_count: Day count convention.
            interpolation: Interpolation method.

        Returns:
            An InterestRateCurve instance.
        """
        return cls.bootstrap(
            reference_date=reference_date,
            deposits=[],
            fras=[],
            swaps=instruments,
            calendar=calendar,
            day_count=day_count,
            interpolation=interpolation,
        )

    @classmethod
    def bootstrap(
        cls,
        reference_date: date,
        deposits: list,
        fras: list,
        swaps: list,
        calendar=None,
        day_count: DayCountConvention = DayCountConvention.ACT_365,
        interpolation: InterpolationMethod = InterpolationMethod.LOG_LINEAR,
    ) -> "InterestRateCurve":
        """
        Bootstrap a zero curve from deposits, FRAs, and par swaps.

        Args:
            reference_date: Curve valuation date.
            deposits: List of dicts with keys 'maturity_date', 'rate'.
            fras: List of dicts with keys 'start_date', 'end_date', 'rate'.
            swaps: List of dicts with keys 'maturity_date', 'fixed_rate',
                   'frequency' ('annual' or 'semi-annual').
            calendar: Optional Calendar instance.
            day_count: Day count convention.
            interpolation: Interpolation method.

        Returns:
            An InterestRateCurve instance.
        """
        pillar_dates = []
        zero_rates = []

        # Helper to compute year fraction
        def yf(d1, d2):
            temp = cls.__new__(cls)
            temp.day_count = day_count
            return temp.year_fraction(d1, d2)

        # Helper discount factor from current pillars
        def df(target):
            if not pillar_dates:
                return 1.0
            t = yf(reference_date, target)
            if t <= 0:
                return 1.0
            curve = cls(reference_date, pillar_dates, zero_rates, day_count, interpolation)
            return curve.discount_factor(target)

        # 1. Deposits — directly give zero rates
        for dep in sorted(deposits, key=lambda x: x["maturity_date"]):
            mat = dep["maturity_date"]
            rate = dep["rate"]
            t = yf(reference_date, mat)
            if t > 0:
                pillar_dates.append(mat)
                zero_rates.append(rate)

        # 2. FRAs — imply discount factors
        for fra in sorted(fras, key=lambda x: x["end_date"]):
            start = fra["start_date"]
            end = fra["end_date"]
            rate = fra["rate"]
            tau = yf(start, end)
            df_start = df(start)
            df_end = df_start / (1.0 + rate * tau)
            t_end = yf(reference_date, end)
            if t_end > 0 and df_end > 0:
                z = -math.log(df_end) / t_end
                pillar_dates.append(end)
                zero_rates.append(z)

        # 3. Par swaps — bootstrap sequentially
        for swap in sorted(swaps, key=lambda x: x["maturity_date"]):
            mat = swap["maturity_date"]
            fixed_rate = swap["fixed_rate"]
            freq = swap.get("frequency", "annual")

            # Build coupon schedule
            coupon_dates = _build_coupon_schedule(reference_date, mat, freq)
            tau_coupon = freq_to_fraction(freq)

            # Sum of df * tau for all coupons except the last
            annuity = 0.0
            for cpn_date in coupon_dates[:-1]:
                annuity += df(cpn_date) * tau_coupon

            # Solve for df at maturity:
            # fixed_rate * annuity + fixed_rate * df_mat * tau_coupon + df_mat = 1
            # df_mat * (1 + fixed_rate * tau_coupon) = 1 - fixed_rate * annuity
            t_mat = yf(reference_date, mat)
            numerator = 1.0 - fixed_rate * annuity
            denominator = 1.0 + fixed_rate * tau_coupon
            if denominator <= 0 or numerator <= 0:
                continue
            df_mat = numerator / denominator
            z_mat = -math.log(df_mat) / t_mat if t_mat > 0 and df_mat > 0 else 0.0
            pillar_dates.append(mat)
            zero_rates.append(z_mat)

        if not pillar_dates:
            raise ValueError("No instruments provided for bootstrapping")

        return cls(reference_date, pillar_dates, zero_rates, day_count, interpolation, calendar)


def _is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def _searchsorted(lst: list, val: float) -> int:
    """Find insertion index (right) in a sorted list."""
    lo, hi = 0, len(lst)
    while lo < hi:
        mid = (lo + hi) // 2
        if lst[mid] <= val:
            lo = mid + 1
        else:
            hi = mid
    return lo


def freq_to_fraction(freq: str) -> float:
    """Convert frequency string to year fraction per coupon period."""
    if freq in ("semi-annual", "semiannual", "semi_annual"):
        return 0.5
    elif freq in ("quarterly",):
        return 0.25
    elif freq in ("monthly",):
        return 1.0 / 12.0
    return 1.0  # annual


def _build_coupon_schedule(reference_date: date, maturity: date, freq: str) -> list:
    """Build coupon payment dates from reference to maturity."""
    tau = freq_to_fraction(freq)
    from datetime import timedelta

    dates = []
    # Work backwards from maturity
    current = maturity
    while current > reference_date:
        dates.append(current)
        # Subtract roughly tau years
        months_back = round(tau * 12)
        y = current.year
        m = current.month - months_back
        while m <= 0:
            m += 12
            y -= 1
        try:
            current = date(y, m, current.day)
        except ValueError:
            last_day = _calendar_mod.monthrange(y, m)[1]
            current = date(y, m, last_day)

    return sorted(dates)
