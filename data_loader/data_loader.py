import os
import pandas as pd

def load_data(data_dir):
    # Read all CSV files and merge them
    all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    dfs = []

    for file in all_files:
        file_path = os.path.join(data_dir, file)
        df = pd.read_csv(file_path)
        dfs.append(df)

    # Merge all data
    combined_df = pd.concat(dfs, ignore_index=True)

    # Convert timestamps to datetime format
    combined_df['open_time'] = pd.to_datetime(combined_df['open_time'], unit='ms')
    combined_df['close_time'] = pd.to_datetime(combined_df['close_time'], unit='ms')

    # Set timestamp as index
    combined_df.set_index('open_time', inplace=True)

    return combined_df