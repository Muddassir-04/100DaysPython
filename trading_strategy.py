import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# List of ticker symbols
tickers = ["GME"]  # Example: GameStop

# Function to fetch stock data
def fetch_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date, timeout=15)  # Increased timeout
    return data

# Function to calculate Moving Averages
def calculate_moving_averages(data):
    data['Short_MA'] = data['Close'].rolling(window=50).mean()  # Short MA (50 days)
    data['Long_MA'] = data['Close'].rolling(window=200).mean()  # Long MA (200 days)
    return data.dropna()  # Drop NaNs from the initial rows due to moving averages

# Function to generate buy/sell signals and calculate profits
def generate_signals(data):
    signals = []
    entry_price = None
    all_time_high = 0  # Track the all-time high price
    bottom_height = float('inf')  # Track the lowest price after buying

    # Start at index 200 to avoid NaN values in moving average columns
    for i in range(200, len(data)):
        # Update the all-time high
        if data['Close'].iloc[i] > all_time_high:
            all_time_high = data['Close'].iloc[i]

        # Buy condition: Close price touches the Short MA
        if data['Close'].iloc[i] <= data['Short_MA'].iloc[i] and entry_price is None:
            entry_price = data['Close'].iloc[i]  # Buy
            bottom_height = entry_price  # Set the bottom height to entry price
            signals.append(('Buy', data.index[i], entry_price))
        
        # Update bottom height if the current close price is lower
        if entry_price is not None:
            if data['Close'].iloc[i] < bottom_height:
                bottom_height = data['Close'].iloc[i]

            # Sell condition: Close price reaches all-time high or if current price is less than bottom height
            if data['Close'].iloc[i] >= all_time_high or (data['Close'].iloc[i] < bottom_height):
                exit_price = data['Close'].iloc[i]  # Sell
                profit = exit_price - entry_price
                profit_percentage = (profit / entry_price) * 100  # Calculate profit percentage
                signals.append(('Sell', data.index[i], exit_price, profit, profit_percentage))
                entry_price = None  # Reset entry price for next buy
                bottom_height = float('inf')  # Reset bottom height

    return signals

# Main Execution
start_date = '2024-01-01'  # Start date
end_date = '2024-12-31'    # End date

for ticker in tickers:
    print(f"\nProcessing ticker: {ticker}")
    data = fetch_data(ticker, start_date, end_date)

    # Check if data is available
    if data.empty:
        print(f"No data found for {ticker} in the given date range.")
    else:
        data = calculate_moving_averages(data)
        trade_signals = generate_signals(data)

        # Print trade signals and results
        for signal in trade_signals:
            if signal[0] == 'Buy':
                print(f"{signal[0]} on {signal[1].date()}: ${signal[2]:.2f}")
            else:
                print(f"{signal[0]} on {signal[1].date()}: ${signal[2]:.2f}, Profit: ${signal[3]:.2f}, Profit Percentage: {signal[4]:.2f}%")

        # Plot results with entry and exit points
        plt.figure(figsize=(14, 7))
        plt.plot(data['Close'], label='Close Price', color='blue', alpha=0.5)  # Close Price

        # Plot Short and Long Moving Averages
        plt.plot(data['Short_MA'], label='Short MA (50 Days)', color='orange', alpha=0.75)
        plt.plot(data['Long_MA'], label='Long MA (200 Days)', color='green', alpha=0.75)

        # Mark entry and exit points
        for signal in trade_signals:
            if signal[0] == 'Buy':
                plt.scatter(signal[1], signal[2], marker='^', color='green', s=100, label='Buy Signal' if 'Buy Signal' not in plt.gca().get_legend_handles_labels()[1] else "")
            else:
                plt.scatter(signal[1], signal[2], marker='v', color='red', s=100, label='Sell Signal' if 'Sell Signal' not in plt.gca().get_legend_handles_labels()[1] else "")

        plt.title(f'{ticker} Price and Moving Averages Since 01/01/2024')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid()
        plt.show()

