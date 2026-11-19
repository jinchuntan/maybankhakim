# check_indicators.py
# Checks the dashboard numbers with a separate calculation in Python.
# Reads data/maybank_monthly.csv (Investing.com export) and prints, for each month,
# the close, the 3-month and 10-month averages, the RSI (14, Wilder method),
# the position of the close against the 10-month average, and the buy/sell crossings.
#
# Run from the repository folder:
#   python scripts/check_indicators.py

import csv
import math
import sys
from datetime import datetime

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/maybank_monthly.csv"
SHORT = 3
LONG = 10
RSI_N = 14

with open(CSV_PATH, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
rows.sort(key=lambda r: datetime.strptime(r["Date"], "%m/%d/%Y"))

dates = [datetime.strptime(r["Date"], "%m/%d/%Y").strftime("%Y-%m") for r in rows]
close = [float(r["Price"].replace(",", "")) for r in rows]


def sma(n, i):
    if i < n - 1:
        return None
    # Add left to right, the same way as the dashboard code (Python's sum() uses
    # compensated addition, which can change the last digit after rounding).
    total = 0.0
    for value in close[i - n + 1:i + 1]:
        total += value
    return total / n


rsi = [None] * len(close)
if len(close) > RSI_N:
    gains = [max(close[i] - close[i - 1], 0) for i in range(1, len(close))]
    losses = [max(close[i - 1] - close[i], 0) for i in range(1, len(close))]
    avg_gain = sum(gains[:RSI_N]) / RSI_N
    avg_loss = sum(losses[:RSI_N]) / RSI_N
    rsi[RSI_N] = 100 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss)
    for i in range(RSI_N + 1, len(close)):
        avg_gain = (avg_gain * (RSI_N - 1) + gains[i - 1]) / RSI_N
        avg_loss = (avg_loss * (RSI_N - 1) + losses[i - 1]) / RSI_N
        rsi[i] = 100 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss)


def fmt(value, digits):
    # Round half up, the same way as Math.round() in the dashboard code.
    if value is None:
        return "-"
    scale = 10 ** digits
    return f"{math.floor(value * scale + 0.5) / scale:.{digits}f}"


print(f"{'Month':<8} {'Close':>6} {'MA3':>6} {'MA10':>6} {'RSI14':>6}  {'Trend':<6} Signal")
previous = None
last = None
for i in range(len(close)):
    ma10 = sma(LONG, i)
    above = None if ma10 is None else close[i] > ma10
    signal = ""
    if previous is not None and above is not None and above != previous:
        signal = "BUY (crossed above MA10)" if above else "SELL (crossed below MA10)"
    if above is not None:
        previous = above
    trend = "" if above is None else ("above" if above else "below")
    print(f"{dates[i]:<8} {close[i]:>6.2f} {fmt(sma(SHORT, i), 2):>6} {fmt(ma10, 2):>6} {fmt(rsi[i], 1):>6}  {trend:<6} {signal}")
    last = (dates[i], close[i], ma10, rsi[i], above)

month, last_close, last_ma10, last_rsi, last_above = last
if last_ma10 is None:
    zone = "Not enough data"
elif last_above:
    zone = "Hold, do not add" if last_rsi is not None and last_rsi > 70 else "Buy / hold zone"
else:
    zone = "Wait, oversold" if last_rsi is not None and last_rsi < 30 else "Sell / avoid zone"
print()
print(f"Latest month {month}: close {last_close:.2f}, 10-month average {fmt(last_ma10, 2)}, "
      f"RSI {fmt(last_rsi, 1)}, zone: {zone}")
