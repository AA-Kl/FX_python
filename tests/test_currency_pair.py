import pytest
from src.fxswap.classes.currency import Currency
from src.fxswap.classes.currency_pair import CurrencyPair


class TestCurrencyPairBasicAccess:
    def test_get_base_currency(self):
        assert CurrencyPair.EUR_USD.get_base_currency() == Currency.EUR

    def test_get_quote_currency(self):
        assert CurrencyPair.EUR_USD.get_quote_currency() == Currency.USD

    def test_get_base_currency_usd_jpy(self):
        assert CurrencyPair.USD_JPY.get_base_currency() == Currency.USD

    def test_get_quote_currency_usd_jpy(self):
        assert CurrencyPair.USD_JPY.get_quote_currency() == Currency.JPY

    def test_str(self):
        assert str(CurrencyPair.EUR_USD) == "EUR/USD"

    def test_str_gbp_usd(self):
        assert str(CurrencyPair.GBP_USD) == "GBP/USD"

    def test_repr(self):
        assert repr(CurrencyPair.EUR_USD) == "CurrencyPair(EUR/USD)"

    def test_repr_usd_jpy(self):
        assert repr(CurrencyPair.USD_JPY) == "CurrencyPair(USD/JPY)"

    def test_repr_does_not_affect_str(self):
        pair = CurrencyPair.GBP_USD
        assert str(pair) == "GBP/USD"
        assert repr(pair) == "CurrencyPair(GBP/USD)"


class TestCurrencyPairFromString:
    def test_from_string_slash_format(self):
        assert CurrencyPair.from_string("EUR/USD") == CurrencyPair.EUR_USD

    def test_from_string_no_slash_format(self):
        assert CurrencyPair.from_string("EURUSD") == CurrencyPair.EUR_USD

    def test_from_string_two_string_args(self):
        assert CurrencyPair.from_string("EUR", "USD") == CurrencyPair.EUR_USD

    def test_from_string_two_currency_args(self):
        assert CurrencyPair.from_string(Currency.EUR, Currency.USD) == CurrencyPair.EUR_USD

    def test_from_string_inverted_pair(self):
        # Looking up USD/EUR should still return EUR_USD (inverted match)
        assert CurrencyPair.from_string("USD/EUR") == CurrencyPair.EUR_USD

    def test_from_string_invalid_format_raises(self):
        with pytest.raises((ValueError, KeyError)):
            CurrencyPair.from_string("EU/USD")

    def test_from_string_unknown_pair_raises(self):
        with pytest.raises((ValueError, KeyError)):
            CurrencyPair.from_string("ZZZ/YYY")

    def test_from_string_invalid_arg_count_raises(self):
        with pytest.raises(ValueError):
            CurrencyPair.from_string("EUR", "USD", "GBP")

    def test_from_string_invalid_first_arg_type_raises(self):
        with pytest.raises(ValueError):
            CurrencyPair.from_string(123, "USD")

    def test_from_string_invalid_second_arg_type_raises(self):
        with pytest.raises(ValueError):
            CurrencyPair.from_string("EUR", 456)
