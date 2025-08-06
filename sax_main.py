import pandas as pd
import numpy as np
from pyts.approximation import SymbolicAggregateApproximation
import requests
import time # Used for exponential backoff in real API calls

# --- Configuration for Stock Data API ---
# IMPORTANT: Replace "YOUR_ACTUAL_API_KEY_HERE" with your valid API key
# from a stock data provider (e.g., Alpha Vantage, Finnhub).
# This key is essential for fetching real data.
API_KEY = "YOUR_ACTUAL_API_KEY_HERE" 

# Define the stock symbol you want to analyze (e.g., S&P 500 ETF)
STOCK_SYMBOL = "SPY" 

# Define the base URL for your chosen stock data API.
# This is a placeholder; consult your API provider's documentation for the correct URL.
# Example for Alpha Vantage (replace YOUR_API_KEY with your actual key):
# API_URL = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={STOCK_SYMBOL}&outputsize=full&apikey={API_KEY}"
API_URL = f"https://api.example.com/stock/{STOCK_SYMBOL}/daily?apikey={API_KEY}" # Placeholder URL

# --- Function to Fetch Stock Data from API ---
def fetch_stock_data(symbol: str, api_key: str, api_base_url: str, retries: int = 5, backoff_factor: float = 1.0) -> pd.DataFrame | None:
    """
    Fetches daily stock data from a specified API endpoint.
    Implements exponential backoff for robust API calls.

    Args:
        symbol (str): The stock symbol (e.g., "SPY").
        api_key (str): Your API key for the stock data service.
        api_base_url (str): The base URL for the API endpoint.
        retries (int): Number of retries for the API call in case of failure.
        backoff_factor (float): Factor to increase delay between retries.

    Returns:
        pd.DataFrame: A DataFrame with 'day' (sequential integer) and 'index_price' (closing price) columns,
                      or None if data fetching fails after retries.
    """
    url = api_base_url.format(symbol=symbol, api_key=api_key) # Format the URL with symbol and key

    for i in range(retries):
        try:
            # Make the actual HTTP request to the API
            response = requests.get(url)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            # Process the API response to extract daily closing prices
            # This part is highly dependent on the specific API's JSON structure.
            # Below is an example for Alpha Vantage's 'Time Series (Daily)' structure.
            if "Time Series (Daily)" in data:
                time_series_data = data["Time Series (Daily)"]
                
                # Convert to DataFrame, ensuring index is datetime and sorted chronologically
                df_raw = pd.DataFrame.from_dict(time_series_data, orient='index')
                df_raw.index = pd.to_datetime(df_raw.index)
                df_raw = df_raw.sort_index(ascending=True) # Sort by date from oldest to newest

                # Extract '4. close' (or '5. adjusted close' for Alpha Vantage) and convert to float
                # Rename 'day' to be sequential integer for SAX processing consistency
                df_processed = pd.DataFrame({
                    'day': np.arange(1, len(df_raw) + 1),
                    'index_price': df_raw['4. close'].astype(float).values # Use '5. adjusted close' for Alpha Vantage
                })
                return df_processed
            else:
                print(f"Error: 'Time Series (Daily)' key not found in API response for {symbol}.")
                print(f"API Response (first 200 chars): {str(data)[:200]}")
                return None # Return None if expected data structure is missing

        except requests.exceptions.RequestException as e:
            print(f"API call attempt {i+1}/{retries} failed for {symbol}: {e}")
            if i < retries - 1:
                # Exponential backoff: wait longer before the next retry
                sleep_time = backoff_factor * (2 ** i)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"Max retries reached for {symbol}. Failed to fetch data.")
                return None
        except Exception as e:
            print(f"An unexpected error occurred while processing API response for {symbol}: {e}")
            return None
    return None # Should not be reached if retries are handled

# --- Core SAX Pattern Detection Logic ---
def analyze_stock_patterns(df: pd.DataFrame, target_pattern: str, window_size: int, n_segments: int, n_bins: int) -> list[str]:
    """
    Applies SAX to stock price data in sliding windows and searches for a target symbolic pattern.

    Args:
        df (pd.DataFrame): DataFrame with 'day' and 'index_price' columns.
        target_pattern (str): The symbolic pattern to search for (e.g., "ccd").
        window_size (int): The number of days in each sliding window (e.g., 12 for a fortnight).
        n_segments (int): Number of segments for PAA within each window.
        n_bins (int): Number of symbols in the SAX alphabet (e.g., 4 for 'a' to 'd').

    Returns:
        list[str]: A list of strings indicating the start day of windows where the pattern was found.
    """
    if df is None or df.empty:
        print("No data to analyze.")
        return []

    sax_patterns_per_window = []
    start_days = []
    
    # Iterate through the data using a sliding window.
    # We step by 'window_size' to get non-overlapping segments for pattern analysis.
    for i in range(0, len(df) - window_size + 1, window_size):
        window_data = df['index_price'][i : i + window_size].values
        
        # Initialize SAX transformer with specified parameters.
        # 'strategy=normal' ensures equiprobable bins based on Gaussian distribution.
        sax_transformer = SymbolicAggregateApproximation(n_bins=n_bins, n_segments=n_segments, strategy='normal')
        
        # Apply SAX to the current window data.
        # .reshape(1, -1) is necessary as fit_transform expects a 2D array (even for a single time series).
        # [0] extracts the 1D array of symbols from the result.
        sax_result = sax_transformer.fit_transform(window_data.reshape(1, -1))[0]
        
        # Join the symbols to form a single symbolic string for the window.
        current_sax_pattern = "".join(sax_result)
        sax_patterns_per_window.append(current_sax_pattern)
        start_days.append(df['day'][i])

    # Search for the target pattern in the generated SAX representations
    found_matches = []
    for i, pattern in enumerate(sax_patterns_per_window):
        if pattern == target_pattern:
            found_matches.append(f"Window starting on Day {start_days[i]} (SAX: '{pattern}')")
            
    return found_matches

# --- Example Usage (How to call these functions) ---
# This section demonstrates how to use the functions defined above.
# In a production environment, you might call these functions from a larger application,
# or schedule them to run periodically.

if __name__ == "__main__":
    # 1. Fetch stock data
    # Ensure API_KEY and API_URL are correctly configured above.
    stock_data_df = fetch_stock_data(STOCK_SYMBOL, API_KEY, API_URL)

    if stock_data_df is not None:
        print(f"\n--- Analysis for {STOCK_SYMBOL} ---")
        print("First 5 rows of fetched data:")
        print(stock_data_df.head())
        print(f"Total {len(stock_data_df)} days of data fetched.")

        # 2. Define SAX parameters and target pattern
        # A "bullish trend" pattern: prices generally moderate-to-high, then high, then very high.
        TARGET_PATTERN = "ccd" 
        WINDOW_SIZE = 12    # Analyze in 12-day periods
        N_SEGMENTS = 3      # Break each 12-day window into 3 segments for SAX
        N_BINS = 4          # Use 4 symbols ('a', 'b', 'c', 'd')

        # 3. Analyze patterns
        matching_windows = analyze_stock_patterns(stock_data_df, TARGET_PATTERN, WINDOW_SIZE, N_SEGMENTS, N_BINS)

        # 4. Print results
        if matching_windows:
            print(f"\nFound '{TARGET_PATTERN}' pattern in the following windows:")
            for match in matching_windows:
                print(f"- {match}")
        else:
            print(f"\nPattern '{TARGET_PATTERN}' not found in any window.")
    else:
        print("\nCould not perform analysis due to data fetching failure.")