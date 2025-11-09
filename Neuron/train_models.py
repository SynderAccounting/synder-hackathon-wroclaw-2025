#!/usr/bin/env python3
"""
Quick model training script for Rossmann sales prediction
This script trains 6 models and saves them to the models/ directory
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import pickle
import os
import warnings

warnings.filterwarnings('ignore')

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# Configuration
CONTEXT_WINDOWS = [7, 14, 30]  # Reduced for faster training
HORIZONS = {
    'day': 1,
    'week': 7,
    'month': 30
}

print("="*80)
print("QUICK MODEL TRAINING FOR ROSSMANN SALES PREDICTION")
print("="*80)

# Load data
print("\n[1/6] Loading data...")
train = pd.read_csv('rossmann_data/train.csv', parse_dates=['Date'])
store = pd.read_csv('rossmann_data/store.csv')
train_full = train.merge(store, on='Store', how='left')
print(f"Loaded {len(train_full):,} records from {train_full['Store'].nunique()} stores")

# Preprocessing
print("\n[2/6] Preprocessing...")
train_full['CompetitionDistance'].fillna(train_full['CompetitionDistance'].median(), inplace=True)
train_full['CompetitionOpenSinceMonth'].fillna(0, inplace=True)
train_full['CompetitionOpenSinceYear'].fillna(0, inplace=True)
train_full['Promo2SinceWeek'].fillna(0, inplace=True)
train_full['Promo2SinceYear'].fillna(0, inplace=True)
train_full['PromoInterval'].fillna('None', inplace=True)

le_store_type = LabelEncoder()
le_assortment = LabelEncoder()
train_full['StoreType_enc'] = le_store_type.fit_transform(train_full['StoreType'])
train_full['Assortment_enc'] = le_assortment.fit_transform(train_full['Assortment'])

train_full['Year'] = train_full['Date'].dt.year
train_full['Month'] = train_full['Date'].dt.month
train_full['Day'] = train_full['Date'].dt.day
train_full['DayOfWeek_num'] = train_full['Date'].dt.dayofweek
train_full['WeekOfYear'] = train_full['Date'].dt.isocalendar().week
train_full['Quarter'] = train_full['Date'].dt.quarter
train_full = train_full.sort_values(['Store', 'Date']).reset_index(drop=True)

# Feature engineering functions
def create_features(df, context_window, target='Sales'):
    df = df.copy()
    df = df.sort_values(['Store', 'Date']).reset_index(drop=True)

    for lag in [1, 7, 14]:
        if lag <= context_window:
            df[f'{target}_lag_{lag}'] = df.groupby('Store')[target].shift(lag)

    for window in [7, 14]:
        if window <= context_window:
            df[f'{target}_rolling_mean_{window}'] = df.groupby('Store')[target].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean().shift(1)
            )

    return df

def create_targets(df, horizon_days, target='Sales'):
    df = df.copy()
    if horizon_days == 1:
        df[f'{target}_target'] = df.groupby('Store')[target].shift(-1)
    else:
        df[f'{target}_target'] = df.groupby('Store')[target].transform(
            lambda x: x.rolling(window=horizon_days, min_periods=horizon_days).sum().shift(-horizon_days+1)
        )
    return df

base_features = [
    'Store', 'DayOfWeek', 'Open', 'Promo', 'SchoolHoliday',
    'StoreType_enc', 'Assortment_enc', 'CompetitionDistance',
    'Promo2', 'Year', 'Month', 'Day', 'DayOfWeek_num',
    'WeekOfYear', 'Quarter'
]

models_dict = {}
results = {}

print("\n[3/6] Training models...")
model_count = 0
total_models = len(['Sales', 'Customers']) * len(HORIZONS)

for target in ['Sales', 'Customers']:
    for horizon_name, horizon_days in HORIZONS.items():
        model_count += 1
        print(f"\n  [{model_count}/{total_models}] Training {target} - {horizon_name}...")

        best_model = None
        best_metrics = None
        best_context = None
        best_features = None
        best_scaler = None

        for context_window in CONTEXT_WINDOWS:
            df_features = create_features(train_full, context_window, target=target)
            df_with_target = create_targets(df_features, horizon_days, target=target)
            df_model = df_with_target.dropna()

            if len(df_model) < 1000:
                continue

            feature_cols = base_features.copy()
            for col in df_model.columns:
                if (col.startswith(f'{target}_lag_') or
                    col.startswith(f'{target}_rolling_')):
                    feature_cols.append(col)

            X = df_model[feature_cols].copy()
            y = df_model[f'{target}_target'].copy()

            if target == 'Sales':
                valid_indices = df_model['Open'] == 1
                X = X[valid_indices]
                y = y[valid_indices]

            split_idx = int(len(X) * 0.8)
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)

            model = xgb.XGBRegressor(
                n_estimators=200,  # Reduced for speed
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=RANDOM_STATE,
                n_jobs=-1,
                verbosity=0
            )

            model.fit(X_train_scaled, y_train, verbose=False)
            y_pred = model.predict(X_val_scaled)

            mae = mean_absolute_error(y_val, y_pred)
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            r2 = r2_score(y_val, y_pred)
            mape = np.mean(np.abs((y_val - y_pred) / (y_val + 1))) * 100

            metrics = {'MAE': mae, 'RMSE': rmse, 'R2': r2, 'MAPE': mape}

            if best_model is None or mae < best_metrics['MAE']:
                best_model = model
                best_metrics = metrics
                best_context = context_window
                best_features = feature_cols
                best_scaler = scaler

        model_key = f"{target}_{horizon_name}"
        models_dict[model_key] = {
            'model': best_model,
            'scaler': best_scaler,
            'features': best_features,
            'context_window': best_context,
            'metrics': best_metrics
        }

        print(f"      Context: {best_context} days | MAE: {best_metrics['MAE']:.2f} | R²: {best_metrics['R2']:.4f}")

# Save models
print("\n[4/6] Saving models to 'models/' directory...")
os.makedirs('models', exist_ok=True)

for model_key, model_data in models_dict.items():
    filename = f"models/{model_key}_model.pkl"
    with open(filename, 'wb') as f:
        pickle.dump(model_data, f)
    print(f"  ✓ {filename}")

print("\n[5/6] Saving label encoders...")
with open('models/label_encoders.pkl', 'wb') as f:
    pickle.dump({
        'StoreType': le_store_type,
        'Assortment': le_assortment
    }, f)
print("  ✓ models/label_encoders.pkl")

# Summary
print("\n[6/6] Training Summary:")
print("-" * 80)
for model_key, model_data in models_dict.items():
    metrics = model_data['metrics']
    print(f"  {model_key:20s} | MAE: {metrics['MAE']:8.2f} | RMSE: {metrics['RMSE']:8.2f} | R²: {metrics['R2']:.4f} | MAPE: {metrics['MAPE']:6.2f}%")

print("\n" + "="*80)
print("TRAINING COMPLETE! 🎉")
print("="*80)
print("\n✅ All 6 models saved to 'models/' directory")
print("✅ Ready to use with Flask app")
print("\nNext steps:")
print("  1. Start the app: python3 app.py")
print("  2. Open: http://127.0.0.1:5000/predictions")
print("="*80)
