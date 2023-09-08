# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 10:43:08 2023

@author: kanr8
"""

import pandas as pd
import numpy as np

# 初始化参数和常量
capital = 1000000
tau = 0.2
idm = 1
fx_rate = 1
multiplier = 1

sigma = {
    'COPPER': 0.0294,
    'CRUDE_W': 0.0186,
    'GAS_US': 0.0159,
    "GOLD": 0.49,
    'SP500': 0.0072,
    'US20': 0.1159,
    'EUR': 0.3221
}

# 从指定路径加载CSV数据
data = pd.read_csv('D:\\2022-2023\\thesis\\bottomup\\0905\\plots\\combined\\combined_forecast.csv')

for i, row in data.iterrows():
    daily_profit_loss = 0
    for instrument, weight_i in sigma.items():
        capped_combined_forecast = row[instrument]
        position_size = (capped_combined_forecast * capital * idm * weight_i * tau) / (10 * multiplier * row[instrument] * fx_rate * sigma[instrument])
        buffer_width = 0.1 * (capital * idm * weight_i * tau) / (10 * multiplier * row[instrument] * fx_rate * sigma[instrument])
        
        position_size = 0 if np.isnan(position_size) else position_size
        buffer_width = 0 if np.isnan(buffer_width) else buffer_width

        # 保存每天的position_size到相应的列中
        data.at[i, f'position_size_{instrument}'] = position_size
        
        buffer_lower = position_size - buffer_width
        buffer_upper = position_size + buffer_width

        if 'position_' + instrument not in data.columns:
            data['position_' + instrument] = 0

        if buffer_lower < data.at[i, 'position_' + instrument] < buffer_upper:
            data.at[i, f'trade_{instrument}'] = 0
        elif data.at[i, 'position_' + instrument] < buffer_lower:
            data.at[i, f'trade_{instrument}'] = buffer_lower - data.at[i, 'position_' + instrument]
        elif data.at[i, 'position_' + instrument] > buffer_upper:
            data.at[i, f'trade_{instrument}'] = buffer_upper - data.at[i, 'position_' + instrument] 
        
        data.at[i, 'position_' + instrument] += data.at[i, f'trade_{instrument}']

        # 如果不是数据的第一行，则计算该金融工具的盈亏
        if i > 0:
            data.at[i, f'profit_loss_{instrument}'] = data.at[i, f'trade_{instrument}'] * (data.at[i, instrument] - data.at[i-1, instrument])
            daily_profit_loss += data.at[i, f'profit_loss_{instrument}']

    data.at[i, 'overall_daily_profit_loss'] = daily_profit_loss

# 将处理后的数据保存到新的CSV文件中
data.to_csv('D:\\2022-2023\\thesis\\bottomup\\0905\\plots\\trend\\combined\\output.csv', index=False)
