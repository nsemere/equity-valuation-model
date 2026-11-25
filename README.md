# Visa/Mastercard Equity Research Valuation Python Program

I've recently built this for an equity research report on Visa and Mastercard. I wrote it in Python instead of Excel because I enjoy coding, and Python is far more flexible. Its libraries go well beyond what a spreadsheet can do, and a script is easy to tweak, reuse and build on over time.

## What it does

1. **Inputs:** loads the data `fetch_data.py` saved
2. **Assumptions:** my growth and risk guesses
3. **Beta:** how jumpy each stock is compared to the market
4. **Discount rate:** the return an investor should want for that risk
5. **DCF:** what all the future cash is worth today
6. **P/E and target:** today's multiple held flat, averaged with the DCF
7. **Price checks:** three quick rules of thumb
8. **Reverse DCF:** what the market is assuming at today's price
9. **Sensitivity:** how much the DCF moves if my guesses are off
10. **Bear, base and bull:** worse and better cases, blended into one value
11. **Monte Carlo:** 20,000 random runs of the DCF

Then it draws the five charts from the report and saves them to `charts/`.

## How to run it

```
pip install -r requirements.txt
python fetch_data.py
jupyter notebook V_MA_Valuation.ipynb
```

Then choose **Run All**. Everything is priced on November 6, 2026, the date of the report.

## Results

| | Visa | Mastercard |
|---|---|---|
| This program (free Yahoo data) | $423 | $673 |
| My report (Bloomberg data) | $419 | $687 |

**Why the numbers are different:** this program uses free data, and my report used Bloomberg. Things like cash flow, debt and share counts are a little different between the two. Beta is also calculated here, not pulled straight from Bloomberg.

**Is that a big deal?** Not really. The targets are only 1 to 2% apart, and the call doesn't change: Visa is priced about right, and Mastercard still has some room to go up. For comparison, nudging the discount rate by one point moves the value about 25%, so this gap is tiny.

**One thing that did move:** the Monte Carlo. Mastercard beats its price in 27% of runs here, vs. 36% in the report, so that number is more sensitive to the data.

## Data

| File | What's in it |
|---|---|
| `data/prices.csv` | 3 years of daily prices, from Yahoo Finance |
| `data/inputs.csv` | Every model input, from Yahoo Finance and FRED |

Analyst estimates are from the day you run the script.
