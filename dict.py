import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import warnings

# Load the data from Excel with error handling
try:
    df = pd.read_excel(r"C:\Users\harsh\Downloads\AIP_structuredfragmented) (1) (1).xlsx", header=None)
except FileNotFoundError:
    print("File not found. Please check the file path.")
    exit(1)
except Exception as e:
    print("An error occurred while loading the data:", e)
    exit(1)

# Validate and extract the headers (dates) and all line items for forecasting
if df.shape[0] < 14 or df.shape[1] < 2:  # Expecting 15 rows and at least 2 columns
    print("Invalid data format. Expected at least 15 rows and 2 columns.")
    exit(1)

# Extract dates from the first row
dates = df.iloc[0, 1:].values.tolist()

# Extract line items and their values from the remaining rows
line_items = []
for i in range(1, 14):  # Loop through 15 rows (indexes 1 to 15)
    line_item = df.iloc[i, 0]
    values = df.iloc[i, 1:].values.tolist()
    line_items.append((line_item, values))

print("Extracted Line Items:")
for item, _ in line_items:
    print(item)

# Create a DataFrame for each line item
data_frames = []
for line_item, values in line_items:
    data = pd.DataFrame({
        'ds': dates,
        'y': values,
        'line_item': line_item  # Add line_item column
    })
    data['ds'] = pd.to_datetime(data['ds'], dayfirst=True)

    # Handling missing values
    data['y'] = data['y'].interpolate(method='linear', limit_direction='both')  # Interpolation
    # Or use ffill method:
    # data['y'] = data['y'].fillna(method='ffill')  # Forward fill (ffill)

    # Custom imputation based on linear regression
    if line_item == 'Interest Expense':
        # Assuming 'revenue_data' is the DataFrame for 'Revenue'
        revenue_data = next((df for df in data_frames if df['line_item'].iloc[0] == 'Revenue'), None)

        if revenue_data is not None and not revenue_data.empty:
            valid_data = data.dropna(subset=['y']).merge(revenue_data.dropna(subset=['y']), on='ds', suffixes=('_interest', '_revenue'))

            if not valid_data.empty:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = LinearRegression()
                    model.fit(valid_data[['y_revenue']], valid_data['y_interest'])

                    missing_indices = data['y'].isnull()
                    if any(missing_indices):
                        data.loc[missing_indices, 'y'] = model.predict(revenue_data.loc[missing_indices, 'y'].values.reshape(-1, 1))

    # Skip line items where all values are NaN
    if not all(pd.isnull(data['y'])):
        data_frames.append(data)

# Create Prophet models for each line item with adjusted parameters and custom holidays
models = []
for data in data_frames:
    model = Prophet(
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10.0,
        holidays_prior_scale=20.0
    )
    model.add_country_holidays(country_name='US')
    models.append(model)

# Fit each model to the respective data with error handling
for i, model in enumerate(models):
    try:
        model.fit(data_frames[i])
    except Exception as e:
        print(f"An error occurred while fitting the model for {line_items[i][0]}:", e)
        exit(1)

# Create a DataFrame for future dates (next 5 years starting from 2024)
future_dates = pd.date_range(start='2024-01-01', periods=5*4, freq='Q')  # Quarterly for 5 years
future_dates = pd.DataFrame({'ds': future_dates})

# Forecast future values for each line item
forecast_results = []  # List to store forecasts for each line item

for i, model in enumerate(models):
    forecast = model.predict(future_dates)
    
    # Create a dictionary for each line item's forecasted data
    forecast_dict = {
        'line_item': line_items[i][0],
        'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    }
    
    # Append the forecast dictionary to the list
    forecast_results.append(forecast_dict)

# Print the forecasted values for the next 5 years (quarterly) for each line item
print("\nForecasted Line Items for the Next 5 Years (Quarterly):\n")
for result in forecast_results:
    line_item = result['line_item']
    forecast_df = result['forecast']
    print(f"{line_item} Forecast:")
    print(forecast_df.tail(20))

# Plot historical and forecasted values for each line item
for result in forecast_results:
    line_item = result['line_item']
    forecast_df = result['forecast']
    data = next(data for data in data_frames if data['line_item'].iloc[0] == line_item)
    plt.figure(figsize=(10, 6))
    
    # Plot historical data with blue color, lines, and markers
    plt.plot(data['ds'], data['y'], label='Historical ' + line_item, color='blue', marker='o', linestyle='-')

    # Plot forecasted data with orange color, lines, and markers
    plt.plot(forecast_df['ds'], forecast_df['yhat'], label='Forecasted ' + line_item, color='orange', marker='o', linestyle='--')
    
    plt.title(f'{line_item} Historical and Forecast for Next 5 Years (Quarterly)')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()  # Adjust layout for better spacing
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.show()
