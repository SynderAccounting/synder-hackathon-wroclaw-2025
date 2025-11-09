# Quick Start Guide - AI Predictions Feature

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
cd /home/kimo/Synder
pip3 install -r requirements.txt --break-system-packages
```

Or if you prefer a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Start the Application

```bash
python3 app.py
```

You should see:
```
✓ Loaded model: Sales_day
✓ Loaded model: Sales_week
✓ Loaded model: Sales_month
✓ Loaded model: Customers_day
✓ Loaded model: Customers_week
✓ Loaded model: Customers_month
Successfully loaded 6 prediction models
 * Running on http://127.0.0.1:5000
```

### Step 3: Access the Predictions Dashboard

Open your browser and navigate to:
```
http://127.0.0.1:5000/predictions
```

Or click **"AI Predictions"** in the navigation menu.

## 🎯 Using the Dashboard

### Generate Your First Prediction

1. **Store ID**: Leave as `1` (or enter any store ID 1-1115)
2. **Prediction Target**: Select "Both Sales & Customers"
3. **Forecast Horizon**: Select "All Horizons (Day, Week, Month)"
4. Click **"Generate Predictions"**

You'll see 6 prediction cards showing:
- 💰 Sales forecasts (day, week, month)
- 👥 Customer forecasts (day, week, month)
- Confidence intervals
- Model accuracy metrics

### Understanding the Results

**Main Value**: The predicted sales or customers
- Large number = Monthly prediction
- Medium number = Weekly prediction
- Small number = Daily prediction

**Confidence Range**: Shows the 95% confidence interval
- Green bar with marker shows where the prediction falls

**Metrics Box**:
- **MAPE**: Lower is better (< 10% is excellent)
- **R²**: Higher is better (> 0.95 is excellent)
- **MAE/RMSE**: Absolute error metrics

## 🔧 API Usage Examples

### Using cURL

**Batch Predictions** (all 6 models):
```bash
curl -X POST http://127.0.0.1:5000/api/batch_predict \
  -H "Content-Type: application/json" \
  -d '{"store_id": 1}'
```

**Single Prediction**:
```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"store_id": 1, "target": "Sales", "horizon": "month"}'
```

### Using Python

```python
import requests

# Batch prediction
response = requests.post(
    'http://127.0.0.1:5000/api/batch_predict',
    json={'store_id': 1}
)
data = response.json()

print(f"Sales forecast (month): ${data['predictions']['sales']['month']['value']:,.2f}")
print(f"Customers forecast (week): {data['predictions']['customers']['week']['value']:,.0f}")
```

### Using JavaScript/Fetch

```javascript
// Batch prediction
fetch('http://127.0.0.1:5000/api/batch_predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({store_id: 1})
})
.then(res => res.json())
.then(data => {
  console.log('Sales (month):', data.predictions.sales.month.value);
  console.log('Customers (week):', data.predictions.customers.week.value);
});
```

## 📊 Example Scenarios

### Scenario 1: Daily Revenue Planning
```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"store_id": 1, "target": "Sales", "horizon": "day"}'
```

Use this for:
- Daily cash flow planning
- Staff scheduling for tomorrow
- Inventory needs for the next day

### Scenario 2: Weekly Customer Forecast
```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"store_id": 1, "target": "Customers", "horizon": "week"}'
```

Use this for:
- Weekly staff scheduling
- Marketing campaign planning
- Service capacity planning

### Scenario 3: Monthly Business Planning
```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"store_id": 1, "target": "Sales", "horizon": "month"}'
```

Use this for:
- Monthly budget forecasting
- Inventory procurement
- Financial reporting

## 🎨 Customization Tips

### Change Store ID
Edit the default in the HTML form or pass different store_id in API calls.

### Filter Predictions
Use the dropdowns to show only:
- Sales OR Customers
- Day OR Week OR Month
- Or view all at once

### Export Results
Copy the prediction values or use the API to integrate with Excel, Google Sheets, or your BI tools.

## ⚠️ Important Notes

1. **Demo Data**: Currently uses synthetic historical features
   - For production, connect to your real sales database

2. **Model Accuracy**: Models trained on Rossmann dataset
   - Retrain with your own data for best results

3. **Confidence Intervals**: Based on model MAPE
   - Wider intervals = more uncertainty
   - Narrower intervals = more confident predictions

4. **Store IDs**: Models support stores 1-1115
   - Predictions work best for stores in training data

## 🐛 Common Issues

**Issue**: `Module not found`
```bash
# Solution
pip3 install numpy pandas scikit-learn xgboost --break-system-packages
```

**Issue**: Port 5000 already in use
```bash
# Solution: Change port in app.py
app.run(debug=True, port=5001)
```

**Issue**: Models not loading
```bash
# Solution: Check models directory exists
ls -la models/
# Should show 6 .pkl files
```

## 📚 Next Steps

1. ✅ Try different store IDs
2. ✅ Compare predictions across horizons
3. ✅ Integrate API with your workflow
4. ✅ Read full documentation in PREDICTIONS_README.md
5. ✅ Customize the feature for your needs

## 🎉 Success Indicators

You're ready when you see:
- ✅ All 6 models loaded successfully
- ✅ Predictions page loads with gradient header
- ✅ API returns JSON with predictions
- ✅ Confidence intervals and metrics display correctly

Enjoy your AI-powered predictions! 🚀
