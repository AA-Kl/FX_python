import xlwings as xw
import sqlite3
from collections import defaultdict
from datetime import datetime
from classes.FXTrade import FXTrade
from classes.currency_pair import CurrencyPair
from classes.direction import TradeDirection

# SQL connection setup
DB_PATH = "c:\\path\\to\\your\\database.db"  # Update with the actual path to your SQL database

def fetch_currency_rates():
    """Fetch currency rates from the SQL table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT base_currency, quote_currency, rate FROM currency_rates")
    rates = {(row[0], row[1]): row[2] for row in cursor.fetchall()}
    conn.close()
    return rates

def generate_position_report():
    """Generate a position report based on FXTrade parameters and currency rates."""
    wb = xw.Book.caller()  # Connect to the calling Excel workbook
    sheet = wb.sheets["FXTrades"]  # Ensure the sheet is named "FXTrades"
    output_sheet = wb.sheets["PositionReport"]  # Ensure the output sheet is named "PositionReport"

    # Fetch FXTrade parameters from Excel
    fx_trades = []
    for row in sheet.range("A2").expand("down").value:
        trade_date = datetime.strptime(row[0], "%Y-%m-%d").date()
        giv_amount = float(row[1])
        currency_pair = CurrencyPair.from_string(row[2])
        rate = float(row[3])
        giv_direction = TradeDirection[row[4].upper()]
        value_date = datetime.strptime(row[5], "%Y-%m-%d").date()
        fx_trades.append(FXTrade(trade_date, giv_amount, currency_pair, rate, giv_direction, value_date))

    # Fetch currency rates from SQL
    currency_rates = fetch_currency_rates()

    # Calculate positions grouped by value date
    positions_by_date = defaultdict(lambda: defaultdict(float))
    for trade in fx_trades:
        value_date = trade.value_date
        if trade.giv_direction == TradeDirection.BUY:
            positions_by_date[value_date][trade.currency_pair.get_domestic_currency()] += trade.giv_amount
            positions_by_date[value_date][trade.currency_pair.get_foreign_currency()] -= trade.giv_amount * trade.rate
        elif trade.giv_direction == TradeDirection.SELL:
            positions_by_date[value_date][trade.currency_pair.get_domestic_currency()] -= trade.giv_amount
            positions_by_date[value_date][trade.currency_pair.get_foreign_currency()] += trade.giv_amount * trade.rate

    # Write the position report to the output sheet
    output_sheet.clear()
    output_sheet.range("A1").value = ["Value Date", "Currency", "Position"]
    row = 2
    for value_date, positions in positions_by_date.items():
        for currency, position in positions.items():
            output_sheet.range(f"A{row}").value = [value_date, currency, position]
            row += 1

# xlwings add-in entry point
@xw.func
def run_position_report():
    generate_position_report()
