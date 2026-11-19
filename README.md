# Maybank (1155) stock tracker

A one-page dashboard for Malayan Banking Berhad (Maybank, Bursa Malaysia code 1155).
It reads a monthly price history exported from Investing.com.
It shows the latest close, the 3-month and 10-month moving averages, the 14-month RSI, and a buy/sell signal from two fixed rules.

The signal comes from past prices only. It is not financial advice.

## Files

- `index.html` – Start page. It loads the dashboard page, the stand-in runtime and the data.
- `dashboard/page.html` – The dashboard page: layout, styles, data loader, calculations and charts. This is the same page that runs as a Claude dashboard.
- `dashboard/dash-shim.js` – A small stand-in for the Claude dashboard runtime, so the page also runs in a normal browser.
- `dashboard/theme.css` – Colours, fonts and sizes for use outside Claude. It has a light and a dark theme.
- `data/maybank_monthly.csv` – The Investing.com monthly price history (Dec 2024 to Nov 2026).
- `scripts/check_indicators.py` – A separate Python calculation of the averages, the RSI and the signals. Use it to check the dashboard numbers.

## Run it on your computer

The browser cannot read the data file when you open `index.html` directly from the disk. Use a small web server:

```
cd maybank-stock-tracker
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

The page loads the d3 chart library from cdn.jsdelivr.net, so the computer needs internet access.

## Publish it with GitHub Pages

1. Push the folder to a GitHub repository.
2. In the repository, open Settings, then Pages.
3. Set the source to "Deploy from a branch". Select the `main` branch and the `/ (root)` folder.
4. Save. GitHub shows the page address after the first deployment.

## Update the data

1. Open https://www.investing.com/equities/malayan-banking-bhd-historical-data.
2. Set the time frame to Monthly and select the date range.
3. Download the CSV file.
4. Replace `data/maybank_monthly.csv` with the new file. Keep the same file name.

The loader expects the Investing.com columns `Date, Price, Open, High, Low, Vol., Change %` and dates in the form MM/DD/YYYY.

## How the signal works

The trend rule uses the 10-month average of the monthly close. A close above the average means the trend is up. A close below the average means the trend is down. A buy signal is the month when the close crosses from below to above the average. A sell signal is the month when the close crosses from above to below the average.

The momentum rule uses the RSI (Relative Strength Index) over 14 months, with the Wilder method. Above 70 means overbought. Below 30 means oversold.

The two rules give one of four zones for the latest month.

- Buy / hold zone: close above the 10-month average and RSI 70 or lower.
- Hold, do not add: close above the 10-month average and RSI above 70.
- Wait, oversold: close below the 10-month average and RSI below 30.
- Sell / avoid zone: close below the 10-month average and RSI 30 or higher.

The last month in the file is not complete until the month ends. Read the signal at the end of the month.

## Check the numbers

```
python scripts/check_indicators.py
```

The script prints each month with the close, the averages, the RSI and the crossings, and then the zone for the latest month. It rounds and adds numbers in the same way as the dashboard code, so the two give the same values.

## Change the rules

The rule settings are at the top of the `indicators` calculation in `dashboard/page.html`: `SHORT = 3`, `LONG = 10` and `RSI_N = 14`. The zone limits (30 and 70) are in the `latest` calculation. If you change them, also change the same values in `scripts/check_indicators.py` and the words on the page.
