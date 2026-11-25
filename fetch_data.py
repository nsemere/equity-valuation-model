"""
What this does:
This script grabs everything the Visa and Mastercard valuation needs and saves it to the data folder,
creating the folder if it doesn't exist. It pulls 3 years of daily prices to measure risk and draw the
growth chart. It gets each company's free cash flow, debt and cash, which feed the cash flow model.
It gets analysts' earnings estimates for the P/E method. And it gets the 10-year Treasury yield, the
"safe" return every stock gets compared to.

How to run it:
Open a terminal in this folder and type:  python fetch_data.py
Everything is priced on November 6, 2026, the date of the report (temporary, will be updated to allow for users to select the date they want used for pricing)

Sources: Yahoo Finance for prices, financials and estimates 
         FRED for the Treasury yield
Analyst estimates reflect the day you run it.
"""




import os
import pandas as pd
import yfinance as yf

### dates
as_of_date = pd.Timestamp("2026-11-06")                # the report's pricing date
start_date = as_of_date - pd.DateOffset(years=3)       # 3 years of history
os.makedirs("data", exist_ok=True)                     # makes the data folder if it isn't there

### 1. daily prices
tickers = ["V", "MA", "^GSPC", "^SP500TR"]             # Visa, Mastercard, S&P 500, S&P 500 total return
download = yf.download(tickers, start=start_date, end=as_of_date + pd.Timedelta(days=1), auto_adjust=False, progress=False)

prices = pd.DataFrame()
prices["V"] = download["Close"]["V"]                   # plain closing prices
prices["MA"] = download["Close"]["MA"]
prices["SPX"] = download["Close"]["^GSPC"]
prices["V_TR"] = download["Adj Close"]["V"]            # "adjusted" close = dividends reinvested
prices["MA_TR"] = download["Adj Close"]["MA"]
prices["SPX_TR"] = download["Close"]["^SP500TR"]
prices = prices.round(4)
prices.index.name = "date"
prices.to_csv("data/prices.csv")

### 2. 10-year Treasury yield
fred_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"
treasury = pd.read_csv(fred_url, index_col=0, parse_dates=True, na_values=".")
treasury = treasury[treasury.index <= as_of_date].dropna()
risk_free_rate = float(treasury.iloc[-1, 0]) / 100      # FRED gives 4.86, we want 0.0486

### 3. company data
def last_four_quarters(table, row_name):
    """Adds up the last 4 quarters of one line (like free cash flow) up to the as-of date."""
    row = table.loc[row_name]
    row = row[row.index <= as_of_date]                   # only quarters reported by the as-of date
    return float(row.iloc[:4].sum())                     # newest quarters come first

inputs = {}
for ticker in ["V", "MA"]:
    stock = yf.Ticker(ticker)
    close = prices[ticker]
    past_year = close[close.index >= as_of_date - pd.DateOffset(weeks=52)]

    # Balance sheet on or before the as-of date
    balance = stock.quarterly_balance_sheet
    balance = balance.loc[:, balance.columns <= as_of_date].iloc[:, 0]
    debt = float(balance["Total Debt"])
    cash = float(balance["Cash Cash Equivalents And Short Term Investments"])

    # Analyst EPS estimates. Visa's year ends in September and Mastercard's in December, so each company needs its own rule for which years to use.
    estimates = stock.earnings_estimate
    if ticker == "V":
        eps_this = float(estimates.loc["0y", "yearAgoEps"])     # fiscal 2026 (actual)
        eps_next = float(estimates.loc["0y", "avg"])            # fiscal 2027
        eps_two_out = float(estimates.loc["+1y", "avg"])        # fiscal 2028
        eps_years = "fiscal 2026 actual / fiscal 2027 / fiscal 2028"
    else:
        eps_this = float(estimates.loc["0y", "avg"])            # 2026
        eps_next = float(estimates.loc["+1y", "avg"])           # 2027
        eps_two_out = eps_next * (eps_next / eps_this)          # 2028, extended at 2027's growth (no estimate yet)
        eps_years = "2026 / 2027 / 2028 (extended at 2027 growth)"

    inputs[ticker] = {
        "price": float(close.iloc[-1]),
        # Yahoo's "implied" share count includes every share class (matters for Visa), in millions
        "shares": float(stock.info.get("impliedSharesOutstanding") or stock.info["sharesOutstanding"]) / 1e6,
        "fcf0": last_four_quarters(stock.quarterly_cashflow, "Free Cash Flow") / 1e6,
        "net_debt": (debt - cash) / 1e6,
        "eps_this": eps_this,
        "eps_next": eps_next,
        "eps_two_out": eps_two_out,
        "eps_years": eps_years,
        "ebitda": last_four_quarters(stock.quarterly_income_stmt, "Normalized EBITDA") / 1e6,
        "street_target": float(stock.analyst_price_targets["mean"]),
        "low_52w": float(past_year.min()),
        "high_52w": float(past_year.max()),
        "risk_free_rate": risk_free_rate,
        "as_of_date": str(as_of_date.date()),
        "estimates_pulled": str(pd.Timestamp.today().date()),
    }

table = pd.DataFrame(inputs)
table.index.name = "field"
table.to_csv("data/inputs.csv")
print(table)
print(f"\nSaved data/prices.csv ({len(prices)} days) and data/inputs.csv")
