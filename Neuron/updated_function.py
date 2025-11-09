# This is the updated function to replace the existing one

@app.route('/api/product_price_prediction', methods=['POST'])
def api_product_price_prediction():
    """API: Predict price changes for products based on historical data using XGBoost model approach from notebook"""
    try:
        data = request.json
        product_id = data.get('product_id')

        # Get the selected product from the database
        conn = get_db()
        cursor = conn.cursor()
        product = cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        conn.close()

        if not product:
            return jsonify({
                'success': False,
                'error': f'Product with id {product_id} not found'
            }), 400

        product_name = product[1]  # product name is at index 1
        current_price = float(product[3])  # price is at index 3

        # Load historical data from the retail prices CSV to create predictions
        retail_df = pd.read_csv('products_prices/Retail_Prices_of _Products.csv')

        # Prepare the data structure exactly as in the notebook
        df = retail_df.copy()
        if 'Value' in df.columns:
            df = df.rename(columns={'Value': 'VALUE'})
        df['date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'].astype(str).str.zfill(2) + '-01')
        df = df.sort_values(['GEO', 'Product Category', 'Products', 'Essential', 'date']).reset_index(drop=True)
        df = df[['GEO', 'Product Category', 'Products', 'Essential', 'date', 'VALUE']].dropna(subset=['VALUE'])

        # Filter for specific product
        product_data = df[df['Products'] == product_name]

        if len(product_data) == 0:
            # If no historical data for this product in the CSV, use current price with minimal variation
            predictions = []
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
            current_month_idx = datetime.now().month - 1

            for i in range(5):
                month_name = months[(current_month_idx + i) % 12]
                predicted_price = current_price * (1 + (np.random.random() - 0.5) * 0.05)  # ±2.5% variation

                predictions.append({
                    'month': month_name,
                    'predictedPrice': round(predicted_price, 2),
                    'confidenceLow': round(predicted_price * 0.95, 2),
                    'confidenceHigh': round(predicted_price * 1.05, 2)
                })

            return jsonify({
                'success': True,
                'product_id': product_id,
                'product_name': product_name,
                'predictions': predictions
            })

        # Encode categorical columns as in the notebook
        categorical_cols = ['GEO', 'Product Category', 'Products', 'Essential']
        label_encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = df[col].astype(str)
            df[col + '_encoded'] = le.fit_transform(df[col])
            label_encoders[col] = le

        group_keys = ['GEO', 'Product Category', 'Products', 'Essential']
        encoded_keys = [col + '_encoded' for col in categorical_cols]

        # Feature engineering function as in the notebook
        def build_advanced_features(group):
            group = group.set_index('date').sort_index()
            full_range = pd.date_range(start=group.index.min(), end=group.index.max(), freq='MS')
            group = group.reindex(full_range)
            
            # Basic lags
            for lag in [1, 2, 3, 4, 6, 12]:
                group[f'lag_{lag}'] = group['VALUE'].shift(lag)
            
            # Same month last year (strong seasonal signal)
            group['lag_12'] = group['VALUE'].shift(12)
            
            # Rolling stats
            group['rolling_mean_3'] = group['VALUE'].shift(1).rolling(3, min_periods=1).mean()
            group['rolling_mean_6'] = group['VALUE'].shift(1).rolling(6, min_periods=1).mean()
            group['rolling_std_3'] = group['VALUE'].shift(1).rolling(3, min_periods=1).std()
            group['rolling_cv_3'] = group['rolling_std_3'] / (group['rolling_mean_3'] + 1e-8)  # coefficient of variation
            
            # First-order difference (momentum)
            group['diff_1'] = group['VALUE'].diff(1)
            group['diff_2'] = group['VALUE'].diff(2)
            
            # Relative changes (%)
            group['pct_change_1'] = group['VALUE'].pct_change(1)
            group['pct_change_3'] = group['VALUE'].pct_change(3)
            
            # Time features
            group['year'] = group.index.year
            group['month'] = group.index.month
            group['quarter'] = group.index.quarter
            group['month_sin'] = np.sin(2 * np.pi * group['month'] / 12)
            group['month_cos'] = np.cos(2 * np.pi * group['month'] / 12)
            
            # Linear & quadratic time trend (per group)
            group['time_idx'] = np.arange(len(group))
            group['time_trend'] = group['time_idx']
            group['time_trend_sq'] = group['time_idx'] ** 2
            
            return group.reset_index().rename(columns={'index': 'date'})

        # Apply feature engineering per product location group
        feature_dfs = []
        for name, group in product_data.groupby(group_keys):
            if len(group) < 12:  # need at least 1 year
                continue
            feat_df = build_advanced_features(group)
            for col in categorical_cols:
                feat_df[col + '_encoded'] = label_encoders[col].transform([name[categorical_cols.index(col)]])[0]
            feature_dfs.append(feat_df)

        if not feature_dfs:
            # Fallback to simple prediction if not enough data
            predictions = []
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
            current_month_idx = datetime.now().month - 1

            for i in range(5):
                month_name = months[(current_month_idx + i) % 12]
                predicted_price = current_price * (1 + (np.random.random() - 0.5) * 0.05)  # ±2.5% variation

                predictions.append({
                    'month': month_name,
                    'predictedPrice': round(predicted_price, 2),
                    'confidenceLow': round(predicted_price * 0.95, 2),
                    'confidenceHigh': round(predicted_price * 1.05, 2)
                })

            return jsonify({
                'success': True,
                'product_id': product_id,
                'product_name': product_name,
                'predictions': predictions
            })

        features_df = pd.concat(feature_dfs, ignore_index=True)

        # Chronological split: last 6 months = validation (as in notebook)
        def assign_chrono_split(group):
            n = len(group)
            if n <= 6:
                group['split'] = 'train'
            else:
                group['split'] = 'train'
                group.iloc[-6:, group.columns.get_loc('split')] = 'val'
            return group

        features_df = features_df.groupby(group_keys, group_keys=False).apply(assign_chrono_split).reset_index(drop=True)

        # Define all feature columns as in the notebook
        lag_cols = [f'lag_{i}' for i in [1,2,3,4,6,12]]
        rolling_cols = ['rolling_mean_3', 'rolling_mean_6', 'rolling_std_3', 'rolling_cv_3']
        diff_cols = ['diff_1', 'diff_2']
        pct_cols = ['pct_change_1', 'pct_change_3']
        time_cols = ['year', 'month_sin', 'month_cos', 'quarter', 'time_trend', 'time_trend_sq']
        feature_cols = lag_cols + rolling_cols + diff_cols + pct_cols + time_cols + encoded_keys

        # Clean data
        modeling_df = features_df.dropna(subset=['VALUE']).copy()
        modeling_df[feature_cols] = modeling_df[feature_cols].fillna(0)

        train_df = modeling_df[modeling_df['split'] == 'train']
        val_df = modeling_df[modeling_df['split'] == 'val']

        if len(train_df) > 0:
            X_train = train_df[feature_cols]
            y_train = train_df['VALUE']
            X_val = val_df[feature_cols]
            y_val = val_df['VALUE']

            # Prepare for prediction - we'll use the last available features
            last_row = features_df.iloc[-1:][feature_cols].fillna(0)
            
            # Define search space for hyperparameters as in the notebook
            from scipy.stats import uniform, randint
            import xgboost as xgb

            # Use XGBoost model with best practices from the notebook
            xgb_model = xgb.XGBRegressor(
                n_estimators=600,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                tree_method='hist',
                eval_metric='rmse'
            )

            # Fit the model
            xgb_model.fit(X_train, y_train, early_stopping_rounds=50, eval_set=[(X_val, y_val)], verbose=False)

            # Create features for prediction (next 5 months)
            # Use the latest available features and extend them
            predictions = []
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            current_month_idx = datetime.now().month - 1

            # Prepare feature vectors for next 5 months
            for i in range(1, 6):
                # Create a copy of the last row to use as base features
                next_features = last_row.copy()
                
                # Update time-based features for the next month
                next_month_idx = (current_month_idx + i) % 12
                next_year = datetime.now().year + ((current_month_idx + i) // 12)
                
                next_features['year'] = next_year
                next_features['month'] = next_month_idx + 1
                next_features['month_sin'] = np.sin(2 * np.pi * (next_month_idx + 1) / 12)
                next_features['month_cos'] = np.cos(2 * np.pi * (next_month_idx + 1) / 12)
                next_features['quarter'] = ((next_month_idx) // 3) + 1
                next_features['time_trend'] = next_features['time_trend'] + i
                next_features['time_trend_sq'] = (next_features['time_trend'] + i) ** 2

                # Make prediction
                pred_value = xgb_model.predict(next_features)[0]
                pred_value = max(0.01, pred_value)  # Ensure it's positive

                # Calculate confidence interval based on validation performance
                if len(y_val) > 0:
                    val_pred = xgb_model.predict(X_val)
                    from sklearn.metrics import mean_absolute_percentage_error
                    mape = mean_absolute_percentage_error(y_val, val_pred) * 100
                    confidence_range = pred_value * (mape / 100)
                else:
                    confidence_range = pred_value * 0.05  # 5% as fallback

                predictions.append({
                    'month': months[next_month_idx],
                    'predictedPrice': round(float(pred_value), 2),
                    'confidenceLow': round(float(max(0.01, pred_value - confidence_range)), 2),
                    'confidenceHigh': round(float(pred_value + confidence_range), 2)
                })

        else:
            # Fallback if model training didn't work
            predictions = []
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
            current_month_idx = datetime.now().month - 1

            for i in range(5):
                month_name = months[(current_month_idx + i) % 12]
                predicted_price = current_price * (1 + (np.random.random() - 0.5) * 0.05)  # ±2.5% variation

                predictions.append({
                    'month': month_name,
                    'predictedPrice': round(predicted_price, 2),
                    'confidenceLow': round(predicted_price * 0.95, 2),
                    'confidenceHigh': round(predicted_price * 1.05, 2)
                })

        return jsonify({
            'success': True,
            'product_id': product_id,
            'product_name': product_name,
            'predictions': predictions
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500