# FXSwap - Foreign Exchange Swap Library

A Python library for managing FX (Foreign Exchange) swaps, trades, and related payment operations.

## Overview

FXSwap provides a comprehensive set of tools and classes for working with foreign exchange transactions, including:

- **Currency Management**: Support for 70+ currencies with standardized enums
- **Currency Pairs**: Pre-defined and custom currency pair handling
- **FX Trades**: Complete FX trade representation with direction, rates, and payment tracking
- **FX Swaps**: Composite trades representing simultaneous buy/sell operations at different value dates
- **Payment Tracking**: Structured payment objects with currency, amount, and direction

## Project Structure

```
repo-root/
├── src/fxswap/                 # Main package directory
│   ├── __init__.py            # Package initialization and exports
│   ├── classes/               # Core financial classes
│   │   ├── currency.py        # Currency enum (70+ currencies)
│   │   ├── currency_pair.py   # Currency pair definitions
│   │   ├── direction.py       # Trade and payment direction enums
│   │   ├── FXTrade.py         # FXTrade class for single trades
│   │   ├── FXSwap.py          # FXSwap class for swap operations
│   │   ├── FXrate.py          # FXrate class for rate management
│   │   └── payment.py         # Payment class for payment tracking
│   ├── excel_addin.py         # Excel add-in for position reporting
│   └── outlook_addin.py       # Outlook add-in for email organization
├── tests/                      # Test suite
│   ├── test_placeholder.py    # Placeholder test file
│   └── (Jupyter notebooks for testing)
├── docs/                       # Documentation directory
├── requirements.txt            # Project dependencies
├── pyproject.toml             # Project configuration
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fxswap.git
cd fxswap
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Install development dependencies (optional):
```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from fxswap import Currency, CurrencyPair, FXTrade, TradeDirection
from datetime import date

# Create a currency pair
pair = CurrencyPair.EUR_USD

# Create an FX trade
trade = FXTrade(
    currency_pair=pair,
    giv_amount=1_000_000,
    value_date=date(2024, 3, 28),
    giv_direction=TradeDirection.BUY,
    rate=1.0950
)

print(f"Bought {trade.giv_amount} EUR at rate {trade.rate}")
print(f"Paying {trade.alt_amount} USD")
```

### Working with FX Swaps

```python
from fxswap import FXSwap, TradeDirection

# Create two trades for near and far legs
near_trade = FXTrade(
    currency_pair=CurrencyPair.EUR_USD,
    giv_amount=1_000_000,
    value_date=date(2024, 3, 28),
    giv_direction=TradeDirection.BUY,
    rate=1.0950
)

far_trade = FXTrade(
    currency_pair=CurrencyPair.EUR_USD,
    giv_amount=1_000_000,
    value_date=date(2024, 4, 25),
    giv_direction=TradeDirection.SELL,
    rate=1.0965
)

# Create swap
swap = FXSwap(near_trade, far_trade)
print(f"Swap price: {swap.price}")  # 0.0015 (difference between far and near rates)
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

Format code with Black:
```bash
black src/ tests/
```

Check code style:
```bash
flake8 src/ tests/
```

Type checking:
```bash
mypy src/
```

## Workflow

Work is organized using GitHub Issues and Projects. When contributing:

1. Check existing issues to avoid duplicates
2. Create an issue for your planned work
3. Reference the issue number in your commits
4. Submit pull requests with clear descriptions
5. Ensure all tests pass before merging

## Core Classes

### Currency
Enum of 70+ supported currencies (USD, EUR, GBP, JPY, etc.)

### CurrencyPair
Pre-defined currency pairs with helper methods for accessing foreign and domestic currencies.

### FXTrade
Represents a single FX trade with:
- Currency pair and amounts
- Trade direction (BUY/SELL)
- Exchange rate calculation
- Payment tracking (giv_payment and alt_payment)

### FXSwap
Composite object representing two FXTrade objects:
- Near leg and far leg trades
- Automatic swap price calculation
- Direction tracking (BUY_SELL or SELL_BUY)

### Payment
Represents a single payment:
- Date, currency, amount
- Payment direction (PAY/RECEIVE)
- Optional USD conversion

## Dependencies

- **xlwings** (>=0.28.0): Excel integration for add-ins
- **pywin32** (>=305): Windows COM interface for Outlook integration

### Optional Dependencies (Development)

- **pytest**: Testing framework
- **black**: Code formatter
- **flake8**: Style checker
- **mypy**: Type checker

## Future Enhancements

- Add more payment calculation features
- Implement rate history tracking
- Add portfolio-level analytics
- Create REST API for trade management
- Enhance Excel add-in functionality
- Add GUI for trade entry

## License

MIT License - See LICENSE file for details

## Contact

For questions or suggestions, please open an issue on GitHub or contact the development team.

---

**Last Updated**: March 28, 2024  
**Version**: 0.1.0  
**Status**: In Active Development
