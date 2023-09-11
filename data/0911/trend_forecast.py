import pandas as pd
import numpy as np
import os

folder_path = "D:\\2022-2023\\thesis\\regression\\data\\data"
output_folder = "D:\\2022-2023\\thesis\\bottomup\\0911\\data\\individual_instr\\indivudual_trendcarry\\trend"  # Assuming you want outputs in the same directory

n_values = [2, 4, 8, 16, 32, 64]

forecast_scalars = {
    2: 12.1,
    4: 8.53,
    8: 5.95,
    16: 4.10,
    32: 2.79,
    64: 1.91
}

csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

for csv_file in csv_files:
    data = pd.read_csv(os.path.join(folder_path, csv_file), parse_dates=['DATETIME'])

    results = {"DATETIME": data["DATETIME"].iloc[1000:].tolist()}

    # Replace missing or 0 values with recent ewma
    for col in data.columns[1:]:
        for i in range(len(data)):
            if data[col].iloc[i] == 0 or np.isnan(data[col].iloc[i]):
                data[col].iloc[i] = data[col].iloc[max(0, i-30):i].ewm(span=30, adjust=False).mean().iloc[-1]

    for n in n_values:
        forecast_col_name = f'forecast_{n}'
        results[forecast_col_name] = []
        
        for i in range(1000, len(data)):
            prices = data["price"]
            ewma_4n = prices.ewm(span=4*n, adjust=False).mean()
            ewma_n = prices.ewm(span=n, adjust=False).mean()

            ewma_std_dev_32 = prices.iloc[i-32:i].ewm(span=32, adjust=False).std().iloc[-1]
            ewma_std_dev_1000 = prices.iloc[max(i-1000, 0):i].ewm(span=1000, adjust=False).std().iloc[-1]

            sigma = 0.7 * ewma_std_dev_32 + 0.3 * ewma_std_dev_1000
            raw_forecast = (ewma_n.iloc[i] - ewma_4n.iloc[i]) / sigma
            scaled_forecast = raw_forecast * forecast_scalars[n]
            capped_forecast = max(min(scaled_forecast, 20), -20)

            results[forecast_col_name].append(capped_forecast)

    df_results = pd.DataFrame(results)
    output_file_path = os.path.join(output_folder, csv_file)  # Save with the same name in the output folder
    df_results.to_csv(output_file_path, index=False)
