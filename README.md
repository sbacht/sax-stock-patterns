# Stock Market Pattern Detection using SAX

This repository contains a Python script that demonstrates how to use Symbolic Aggregate approXimation (SAX) to identify specific patterns in stock market index data. It includes a simulated API call to fetch historical stock prices, applies SAX to transform the numerical data into symbolic strings, and then searches for predefined symbolic patterns.

## 📊 Project Overview

The core idea is to simplify complex, high-dimensional time series data (like stock prices) into a more manageable, lower-dimensional symbolic representation. This allows for efficient pattern recognition, especially useful in scenarios involving large datasets or streaming data where traditional numerical analysis can be computationally expensive.

## ✨ Features

* **Simulated API Data Fetching:** Includes a function `fetch_stock_data` that simulates fetching daily closing prices for a given stock symbol from a hypothetical API. This function is designed to be easily adaptable to real stock data APIs (e.g., Alpha Vantage, Finnhub).
* **Symbolic Aggregate approXimation (SAX):** Utilizes the `pyts` library to convert numerical stock price data into a sequence of symbols. This process involves:
    * **Piecewise Aggregate Approximation (PAA):** Reducing the dimensionality of the time series by averaging segments.
    * **Symbolic Conversion:** Mapping the aggregated values to discrete symbols (e.g., 'a', 'b', 'c', 'd') based on a Gaussian distribution strategy.
* **Pattern Definition and Search:** Allows for defining specific "trend" patterns (e.g., a "bullish trend" like 'ccd') in symbolic form and efficiently searching for these patterns within the SAX-transformed stock data.

## 🚀 Getting Started

### Prerequisites

* Python 3.x
* `pandas`
* `numpy`
* `pyts`
* `requests` (for actual API calls, though simulated in this example)

You can install the required libraries using pip:

```bash
pip install pandas numpy pyts requests

### Usage

1.  **Clone the repository (or copy the code):**
    ```bash
    git clone [your-repo-name]
    cd [your-repo-name]
    ```
    *(Note: If you're running this directly in a Canvas environment, you can just use the provided code.)*

2.  **Obtain an API Key (for real data):**
    * If you wish to use real stock data, you'll need an API key from a stock data provider. Popular choices include:
        * [Alpha Vantage](https://www.alphavantage.co/) (offers a free tier)
        * [Finnhub](https://finnhub.io/)
        * [Quandl](https://www.quandl.com/)
    * Once you have an API key, **replace `"YOUR_ACTUAL_API_KEY_HERE"`** in the `API_KEY` variable within the Python script (`main.py` or similar).
    * **Uncomment the `requests.get(API_URL)` block** and update `API_URL` to the actual endpoint for your chosen service.

3.  **Run the script:**
    ```bash
    python your_script_name.py
    ```
    (Replace `your_script_name.py` with the actual name of your Python file).

### Customization

* **`STOCK_SYMBOL`**: Change `"SPY"` to any other stock ticker (e.g., `"AAPL"`, `"GOOGL"`) to analyze different assets.
* **`window_size`**: Adjust the size of the sliding window (e.g., `12` days for a fortnight, `20` for a month of trading days) to define the length of the segments you want to analyze.
* **`n_segments`**: Modify how many sub-segments each `window_size` period is broken into for PAA. This affects the length of your SAX symbol string.
* **`n_bins`**: Change the number of symbols in your alphabet (e.g., `4` for 'a', 'b', 'c', 'd'; `5` for 'a' through 'e'). A higher number of bins provides more granularity but less compression.
* **`target_pattern`**: Define your own symbolic patterns to search for. Experiment with different sequences of 'a', 'b', 'c', 'd' (or more if you increase `n_bins`) to represent various market trends (e.g., 'abd' for a dip and recovery, 'aaa' for a stable period).

## ⚠️ Disclaimer

This script is provided for **educational and demonstration purposes only**. It uses simplified models for stock price trends and does not constitute financial advice. Stock market analysis is complex and involves many factors not covered by this basic example. Always conduct thorough research and consult with financial professionals before making any investment decisions.