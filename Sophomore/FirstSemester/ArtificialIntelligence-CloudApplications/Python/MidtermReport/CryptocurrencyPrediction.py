import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# 1. 抓資料
df = yf.download('BTC-USD', period='60d', interval='1h')
data = df[['Close']].values

# 2. 正規化
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

# 3. 建立訓練集（例如每60小時預測下一小時）
X, y = [], []
for i in range(60, len(scaled_data)):
    X.append(scaled_data[i-60:i, 0])
    y.append(scaled_data[i, 0])
X, y = np.array(X), np.array(y)
X = np.reshape(X, (X.shape[0], X.shape[1], 1))  # LSTM需要3D輸入

# 4. 建立模型
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
    LSTM(50),
    Dense(1)
])

model.compile(optimizer='adam', loss='mean_squared_error')

# 5. 訓練模型
model.fit(X, y, epochs=10, batch_size=32)

# 6. 預測未來1小時
last_60 = scaled_data[-60:]
pred_input = np.reshape(last_60, (1, 60, 1))
pred_scaled = model.predict(pred_input)
pred_price = scaler.inverse_transform(pred_scaled)
print(f"預測下一小時 BTC 價格約為：{pred_price[0][0]:.2f} 美元")