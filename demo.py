import pandas as pd
import numpy as np
from pyts.approximation import SymbolicAggregateApproximation
import requests
import time # For simulating delays and exponential backoff

# --- Configuration for API Call ---
# IMPORTANT: In a real application, you would replace this with your actual API key
# obtained from a stock data provider (e.g., Alpha Vantage, Finnhub).
# For this example, we'll simulate the API call.
API_KEY = "YOUR_ACTUAL_API_KEY_HERE" # Replace with your real API key!
STOCK_SYMBOL = "SPY" # Example: S&P 500 ETF
# Hypothetical API endpoint for daily stock prices
# In a real scenario, this URL would be provided by your chosen API service.
API_URL = f"https://www.example.com/api/v1/stock/{STOCK_SYMBOL}/daily?apikey={API_KEY}"

# --- Function to Fetch Stock Data from a (Simulated) API ---
def fetch_stock_data(symbol, api_key, retries=5, backoff_factor=1.0):
    """
    Simulates fetching daily stock data from an API.
    In a real application, this would make an actual HTTP request.
    
    Args:
        symbol (str): The stock symbol (e.g., "SPY").
        api_key (str): Your API key for the stock data service.
        retries (int): Number of retries for API call in case of failure.
        backoff_factor (float): Factor to increase delay between retries.

    Returns:
        pandas.DataFrame: A DataFrame with 'day' and 'index_price' columns,
                          or None if data fetching fails.
    """
    print(f"Attempting to fetch data for {symbol} from API...")
    
    # --- SIMULATED API RESPONSE ---
    # In a real scenario, you would use requests.get(API_URL) here.
    # For demonstration, we'll generate mock data that looks like an API response.
    # This mock data is similar to the original, but structured as if from an API.
    simulated_api_data = {
        "Meta Data": {
            "1. Information": "Daily Prices (open, high, low, close)",
            "2. Symbol": symbol,
            "3. Last Refreshed": "2025-08-06",
            "4. Output Size": "Full size",
            "5. Time Zone": "US/Eastern"
        },
        "Time Series (Daily)": {
            "2025-08-06": {"1. open": "103.00", "2. high": "105.00", "3. low": "102.50", "4. close": "104.50", "5. volume": "1000000"},
            "2025-08-05": {"1. open": "102.00", "2. high": "103.50", "3. low": "101.50", "4. close": "103.00", "5. volume": "950000"},
            "2025-08-04": {"1. open": "101.00", "2. high": "102.00", "3. low": "100.50", "4. close": "102.00", "5. volume": "900000"},
            "2025-08-03": {"1. open": "100.00", "2. high": "101.00", "3. low": "99.50", "4. close": "101.00", "5. volume": "850000"},
            "2025-08-02": {"1. open": "99.00", "2. high": "100.00", "3. low": "98.50", "4. close": "100.00", "5. volume": "800000"},
            "2025-08-01": {"1. open": "98.00", "2. high": "99.00", "3. low": "97.50", "4. close": "99.00", "5. volume": "750000"},
            # ... add more simulated data to match the original 60 days for a full example
            # For brevity, I'll only include a few days here.
            # In a real API call, you'd get historical data.
            # For this example, let's generate 60 days of data dynamically
        }
    }

    # Generate 60 days of simulated data for the 'Time Series (Daily)' part
    # This mimics the original mock data's pattern for SAX analysis
    current_price = 100
    simulated_time_series = {}
    for day_offset in range(60):
        date = (pd.to_datetime("2025-08-06") - pd.Timedelta(days=day_offset)).strftime("%Y-%m-%d")
        
        # Mimic the original data's trends for SAX to work as expected
        if day_offset < 12: # Upward trend
            current_price = 111 - day_offset
        elif day_offset < 24: # Downward trend
            current_price = 101 + (day_offset - 12)
        elif day_offset < 36: # Sideways
            current_price = 100 + (day_offset % 2)
        elif day_offset < 48: # Another upward trend
            current_price = 113 - (day_offset - 36)
        else: # Another downward trend
            current_price = 103 + (day_offset - 48)

        # Reverse the price logic to make it appear as if fetching from oldest to newest
        # For the SAX analysis, we need the data in chronological order (oldest to newest)
        # The original mock data was already in chronological order.
        # Let's re-align the simulated data to match the original mock data's values for consistency
        original_mock_prices = [
            100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, # Days 1-12: Strong upward trend (bullish)
            112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, # Days 13-24: Downward trend (bearish)
            100, 100, 101, 101, 100, 100, 101, 101, 100, 100, 101, 101, # Days 25-36: Sideways/stable trend
            102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, # Days 37-48: Another strong upward trend
            114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103  # Days 49-60: Another downward trend
        ]
        simulated_time_series[date] = {
            "1. open": str(original_mock_prices[59 - day_offset] - 0.5), # Simulate open slightly lower
            "2. high": str(original_mock_prices[59 - day_offset] + 1.0), # Simulate high
            "3. low": str(original_mock_prices[59 - day_offset] - 1.0),  # Simulate low
            "4. close": str(original_mock_prices[59 - day_offset]),     # This is our 'index_price'
            "5. volume": str(1000000 + day_offset * 10000)
        }
    simulated_api_data["Time Series (Daily)"] = simulated_time_series


    # --- REAL API CALL (COMMENTED OUT) ---
    # try:
    #     response = requests.get(API_URL)
    #     response.raise_for_status() # Raise an exception for HTTP errors
    #     data = response.json()
    # except requests.exceptions.RequestException as e:
    #     print(f"API call failed: {e}")
    #     return None

    data = simulated_api_data # Use simulated data for this example

    # Process the API response
    if "Time Series (Daily)" in data:
        time_series_data = data["Time Series (Daily)"]
        
        # Convert to DataFrame
        df_raw = pd.DataFrame.from_dict(time_series_data, orient='index')
        df_raw.index = pd.to_datetime(df_raw.index)
        df_raw = df_raw.sort_index(ascending=True) # Ensure chronological order

        # Extract closing prices and rename for consistency
        df_processed = pd.DataFrame({
            'day': np.arange(1, len(df_raw) + 1),
            'index_price': df_raw['4. close'].astype(float).values
        })
        print(f"Successfully fetched {len(df_processed)} days of data.")
        return df_processed
    else:
        print("Error: 'Time Series (Daily)' key not found in API response.")
        print("API Response (first 200 chars):", str(data)[:200])
        return None

# --- Main execution ---
# Fetch real (simulated) stock data
df = fetch_stock_data(STOCK_SYMBOL, API_KEY)

if df is None:
    print("Failed to fetch stock data. Exiting.")
else:
    print("--- Fetched Stock Index Data (first 15 days): ---")
    print(df.head(15))
    print("\n" + "="*50 + "\n")

    # --- 2. SAX Parameters and Application ---
    # We want to represent each 12-day period (e.g., a trading fortnight) symbolically.
    # Each 12-day segment will be transformed into a string of 3 symbols.
    # We'll use an alphabet of 4 symbols ('a', 'b', 'c', 'd').
    # 'n_segments' defines how many parts each time series window is divided into for PAA.
    # 'n_bins' defines the size of the alphabet (number of unique symbols).
    # 'strategy'='normal' ensures that bin boundaries are chosen based on a normal distribution,
    # making each symbol equiprobable, which is standard for SAX.

    # --- 3. Defining a "Bullish Trend" Pattern and Searching for It ---
    # Let's define a "bullish trend" pattern.
    # A simple bullish trend might be represented by symbols that consistently
    # fall into higher bins, indicating increasing prices over the segment.
    # For a 3-segment window with 4 bins, a strong bullish trend might be 'ccd' or 'cdd'.
    # Let's target a pattern like 'ccd' (moderate-to-high, then high, then very high).

    target_pattern = "ccd"
    window_size = 12  # Size of the sliding window = 12 days
    sax_patterns_per_window = []
    start_days = []

    # Iterate through the data using a sliding window.
    # We'll step by 'window_size' to get non-overlapping segments for simplicity.
    for i in range(0, len(df) - window_size + 1, window_size):
        window_data = df['index_price'][i : i + window_size].values
        
        # Apply SAX to the current window.
        # reshape(1, -1) is needed because fit_transform expects a 2D array.
        sax_transformer = SymbolicAggregateApproximation(n_bins=4, n_segments=3, strategy='normal')
        sax_result = sax_transformer.fit_transform(window_data.reshape(1, -1))[0] # [0] to get the 1D array of symbols
        
        current_sax_pattern = "".join(sax_result)
        sax_patterns_per_window.append(current_sax_pattern)
        start_days.append(df['day'][i])

    print("--- SAX Patterns for each 12-day window: ---")
    for i, pattern in enumerate(sax_patterns_per_window):
        print(f"Window starting on Day {start_days[i]}: '{pattern}'")

    # Now, search for our target pattern in the generated SAX representations
    print(f"\n--- Searching for the target pattern '{target_pattern}': ---")
    found_matches = []
    for i, pattern in enumerate(sax_patterns_per_window):
        if pattern == target_pattern:
            found_matches.append(f"Window starting on Day {start_days[i]}")

    if found_matches:
        print(f"The pattern '{target_pattern}' was found in the following windows:")
        for match in found_matches:
            print(f"- {match}")
    else:
        print(f"The pattern '{target_pattern}' was not found.")

