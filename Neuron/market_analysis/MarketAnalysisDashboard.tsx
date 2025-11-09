import React, { useState } from 'react';
import ProductSelection from './ProductSelection';
import PricePredictionGraph from './PricePredictionGraph';
import { loadProductsFromCSV, predictPrices } from './dataService';

interface PredictionData {
  month: string;
  predictedPrice: number;
  confidenceLow: number;
  confidenceHigh: number;
}

const MarketAnalysisDashboard: React.FC = () => {
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);
  const [predictions, setPredictions] = useState<PredictionData[]>([]);
  const [loading, setLoading] = useState(false);
  const [predictionError, setPredictionError] = useState<string | null>(null);

  const handleProductSelect = async (productId: string) => {
    setSelectedProduct(productId);
    setLoading(true);
    setPredictionError(null);
    
    try {
      // Get predictions for the selected product
      const result = await predictPrices(productId);
      setPredictions(result.predictions);
    } catch (error) {
      console.error('Error predicting prices:', error);
      setPredictionError(`Failed to predict prices: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="market-analysis-dashboard">
      <h2>Market Analysis & Price Prediction</h2>
      
      <div className="dashboard-content">
        <div className="product-selection-panel">
          <ProductSelection 
            onProductSelect={handleProductSelect} 
            selectedProduct={selectedProduct} 
          />
        </div>
        
        <div className="prediction-panel">
          <PricePredictionGraph 
            product={selectedProduct} 
            predictions={predictions} 
            isLoading={loading} 
          />
          
          {predictionError && (
            <div className="error-message">
              {predictionError}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarketAnalysisDashboard;