import os
import pandas as pd

def load_data(data_dir):
    # 读取所有CSV文件并合并
    all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    dfs = []

    for file in all_files:
        file_path = os.path.join(data_dir, file)
        df = pd.read_csv(file_path)
        dfs.append(df)

    # 合并所有数据
    combined_df = pd.concat(dfs, ignore_index=True)

    # 将时间戳转换为datetime格式
    combined_df['open_time'] = pd.to_datetime(combined_df['open_time'], unit='ms')
    combined_df['close_time'] = pd.to_datetime(combined_df['close_time'], unit='ms')

    # 设置时间戳为索引
    combined_df.set_index('open_time', inplace=True)

    return combined_df