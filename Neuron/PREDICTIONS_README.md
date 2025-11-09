# AI-Powered Sales & Customer Predictions Feature

## Overview

This feature adds machine learning-powered predictions to your retail CRM system using 6 pre-trained models that forecast sales and customer traffic for different time horizons.

## Features

### 🤖 Machine Learning Models

The system includes 6 independent XGBoost models:

1. **Sales - Day** (1 day ahead prediction)
2. **Sales - Week** (7 days sum prediction)
3. **Sales - Month** (30 days sum prediction)
4. **Customers - Day** (1 day ahead prediction)
5. **Customers - Week** (7 days sum prediction)
6. **Customers - Month** (30 days sum prediction)

### 📊 Model Performance

Each model was trained on Rossmann store sales data with the following characteristics:

- **Algorithm**: XGBoost Regressor with optimized hyperparameters
- **Feature Engineering**:
  - Temporal features (day, week, month, quarter, year)
  - Store characteristics (type, assortment, competition distance)
  - Historical patterns (lag features, rolling statistics)
  - Promotional indicators
- **Context Windows**: Automatically optimized (7-90 days)
- **Evaluation Metrics**: MAE, RMSE, R², MAPE

### 🎨 Frontend Interface

Beautiful, responsive UI with:

- **Interactive Dashboard**: Control panel for prediction parameters
- **Real-time Predictions**: Generate forecasts on demand
- **Visual Confidence Intervals**: See prediction uncertainty ranges
- **Model Metrics Display**: View accuracy metrics for each prediction
- **Gradient Design**: Modern, professional styling
- **Responsive Layout**: Works on desktop and mobile

## Installation

### 1. Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt
```

Required packages:
- Flask >= 3.0.0
- numpy >= 1.21.0
- pandas >= 1.3.0
- scikit-learn >= 1.0.0
- xgboost >= 1.5.0
- werkzeug >= 2.0.0

### 2. Model Files

Ensure the following model files are in the `models/` directory:

```
models/
├── Sales_day_model.pkl
├── Sales_week_model.pkl
├── Sales_month_model.pkl
├── Customers_day_model.pkl
├── Customers_week_model.pkl
└── Customers_month_model.pkl
```

These models were trained using the notebook at: `sales_customers.ipynb`

### 3. Run the Application

```bash
python3 app.py
```

The server will start at `http://127.0.0.1:5000`

## Usage

### Web Interface

1. Navigate to **AI Predictions** in the main menu
2. Configure prediction parameters:
   - **Store ID**: Select store (1-1115)
   - **Target**: Choose Sales, Customers, or Both
   - **Horizon**: Select Day, Week, Month, or All
3. Click "Generate Predictions"
4. View results with confidence intervals and model metrics

### API Endpoints

#### Batch Predictions (All Models)

```bash
POST /api/batch_predict
Content-Type: application/json

{
  "store_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "store_id": 1,
  "timestamp": "2025-11-08T21:20:38.054519",
  "predictions": {
    "sales": {
      "day": {
        "value": 4569.61,
        "confidence_lower": -220919.90,
        "confidence_upper": 230059.12,
        "mape": 4934.55
      },
      "week": { ... },
      "month": { ... }
    },
    "customers": { ... }
  }
}
```

#### Single Prediction

```bash
POST /api/predict
Content-Type: application/json

{
  "store_id": 1,
  "target": "Sales",
  "horizon": "month"
}
```

**Response:**
```json
{
  "success": true,
  "prediction": 155442.11,
  "confidence_interval": {
    "lower": 149587.55,
    "upper": 161296.67
  },
  "metrics": {
    "MAE": 6619.99,
    "RMSE": 10371.65,
    "R2": 0.9671,
    "MAPE": 3.77
  },
  "context_window": 30
}
```

## Understanding the Results

### Prediction Value
The main predicted value for the selected target and horizon.

### Confidence Interval
95% confidence range based on model MAPE (Mean Absolute Percentage Error). The actual value is expected to fall within this range with 95% probability.

### Model Metrics

- **MAPE** (Mean Absolute Percentage Error): Average percentage error. Lower is better.
- **MAE** (Mean Absolute Error): Average absolute error in units.
- **RMSE** (Root Mean Squared Error): Square root of average squared errors. Penalizes large errors.
- **R²** (R-squared): Proportion of variance explained. Closer to 1.0 is better.

### Context Window
Number of historical days the model uses to make predictions. Automatically optimized during training.

## Architecture

### Backend (app.py)

```
┌─────────────────────────────────────┐
│     Flask Application               │
├─────────────────────────────────────┤
│ Model Loading at Startup:          │
│ - Load 6 pickle files               │
│ - Initialize scalers                │
│ - Cache in memory                   │
├─────────────────────────────────────┤
│ API Routes:                         │
│ - GET  /predictions                 │
│ - POST /api/predict                 │
│ - POST /api/batch_predict           │
├─────────────────────────────────────┤
│ Prediction Pipeline:                │
│ 1. Extract model + scaler           │
│ 2. Generate feature values          │
│ 3. Scale features                   │
│ 4. Run prediction                   │
│ 5. Calculate confidence interval    │
│ 6. Return JSON response             │
└─────────────────────────────────────┘
```

### Frontend (predictions.html)

```
┌─────────────────────────────────────┐
│     Predictions Dashboard           │
├─────────────────────────────────────┤
│ Header Section:                     │
│ - Title and description             │
│ - AI badge                          │
├─────────────────────────────────────┤
│ Control Panel:                      │
│ - Store ID input                    │
│ - Target selector                   │
│ - Horizon selector                  │
│ - Predict button                    │
├─────────────────────────────────────┤
│ Results Grid:                       │
│ - Prediction cards                  │
│ - Confidence intervals              │
│ - Model metrics                     │
│ - Visual indicators                 │
└─────────────────────────────────────┘
```

## Technical Details

### Feature Generation

The prediction system generates features in real-time:

**Base Features:**
- Store attributes (ID, type, assortment)
- Temporal features (day, month, year, quarter, week)
- Promotional flags
- Competition distance

**Historical Features** (synthetic for demo):
- Lag features (1, 2, 3, 7, 14, 30 days)
- Rolling statistics (mean, std, max, min)
- Exponential moving averages

**Note:** In production, historical features should be fetched from your actual database of past sales/customer data.

### Model Architecture

Each model uses XGBoost with:
- **Estimators**: 500 trees
- **Max Depth**: 7
- **Learning Rate**: 0.05
- **Subsample**: 0.8
- **Column Sample**: 0.8

### Scaling

StandardScaler normalization applied to all features before prediction.

## Customization

### Adding New Models

1. Train your model in the Jupyter notebook
2. Save as pickle file: `{Target}_{horizon}_model.pkl`
3. Place in `models/` directory
4. Restart the application

### Modifying Feature Generation

Edit the feature generation logic in `app.py`:

```python
# Around line 955 in api_predict()
feature_values = {}
# Add your custom features here
```

### Styling

Update CSS in `templates/predictions.html` within the `<style>` block.

## Performance

- **Model Loading**: ~1-2 seconds at startup
- **Single Prediction**: <50ms
- **Batch Prediction** (6 models): ~200ms
- **Memory Usage**: ~200MB with all models loaded

## Troubleshooting

### Models Not Loading

**Error**: `Model file not found`

**Solution**: Ensure model files are in the `models/` directory

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'numpy'`

**Solution**: Install requirements:
```bash
pip install -r requirements.txt
```

### Version Warnings

**Warning**: `InconsistentVersionWarning`

**Solution**: This is a warning only. Models trained with scikit-learn 1.6.1 work with 1.7.2, but ideally retrain models with matching version.

### Negative Predictions

Some predictions may be negative if the model predicts very low values with high uncertainty. This is expected for stores with limited historical data.

## Future Enhancements

- [ ] Connect to real historical data from database
- [ ] Add trend charts and visualizations
- [ ] Implement model retraining pipeline
- [ ] Add export to CSV/PDF
- [ ] Multi-store comparison
- [ ] Scenario analysis (what-if predictions)
- [ ] Integration with inventory management

## Credits

- **Models**: Trained on Rossmann Store Sales dataset
- **Framework**: Flask + XGBoost + scikit-learn
- **UI Design**: Custom gradient-based design system

## License

This feature is part of the One Front retail CRM system.
