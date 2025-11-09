import React from 'react';

interface PricePredictionData {
  month: string;
  predictedPrice: number;
  confidenceLow?: number;
  confidenceHigh?: number;
}

interface PricePredictionGraphProps {
  product: string | null;
  predictions: PricePredictionData[];
  isLoading: boolean;
}

const PricePredictionGraph: React.FC<PricePredictionGraphProps> = ({ 
  product, 
  predictions, 
  isLoading 
}) => {
  if (isLoading) {
    return (
      <div className="prediction-graph loading">
        <p>Loading price predictions...</p>
      </div>
    );
  }

  if (!product || predictions.length === 0) {
    return (
      <div className="prediction-graph empty">
        <p>Select a product to see price predictions</p>
      </div>
    );
  }

  // Find min and max values for scaling the graph
  const allPrices = predictions.flatMap(p => [
    p.predictedPrice,
    p.confidenceLow || p.predictedPrice,
    p.confidenceHigh || p.predictedPrice
  ]);
  const minPrice = Math.min(...allPrices);
  const maxPrice = Math.max(...allPrices);
  const priceRange = maxPrice - minPrice || 1; // Avoid division by zero
  
  // Graph dimensions
  const graphHeight = 300;
  const graphWidth = 600;
  const padding = 40;
  const chartWidth = graphWidth - (padding * 2);
  const chartHeight = graphHeight - (padding * 2);
  
  // Calculate points for the prediction line
  const points = predictions.map((prediction, index) => {
    const x = padding + (index * chartWidth) / (predictions.length - 1);
    const y = graphHeight - padding - ((prediction.predictedPrice - minPrice) / priceRange) * chartHeight;
    return `${x},${y}`;
  }).join(' ');

  // Calculate points for the confidence area
  const confidenceAreaPoints = predictions.map((prediction, index) => {
    const x = padding + (index * chartWidth) / (predictions.length - 1);
    const y = graphHeight - padding - ((prediction.confidenceLow! - minPrice) / priceRange) * chartHeight;
    return `${x},${y}`;
  }).reverse().concat(
    predictions.map((prediction, index) => {
      const x = padding + (index * chartWidth) / (predictions.length - 1);
      const y = graphHeight - padding - ((prediction.confidenceHigh! - minPrice) / priceRange) * chartHeight;
      return `${x},${y}`;
    })
  ).join(' ');

  return (
    <div className="prediction-graph">
      <h3>Price Prediction for Next 5 Months</h3>
      <div className="graph-container">
        <svg 
          width={graphWidth} 
          height={graphHeight} 
          viewBox={`0 0 ${graphWidth} ${graphHeight}`}
        >
          {/* Background grid */}
          <g stroke="#e0e0e0" strokeWidth="1">
            {[0, 1, 2, 3, 4].map(i => (
              <line 
                key={`h-grid-${i}`}
                x1={padding} 
                y1={padding + (i * chartHeight/4)} 
                x2={graphWidth - padding} 
                y2={padding + (i * chartHeight/4)} 
              />
            ))}
            {predictions.map((_, i) => (
              <line 
                key={`v-grid-${i}`}
                x1={padding + (i * chartWidth/(predictions.length-1 || 1))} 
                y1={padding} 
                x2={padding + (i * chartWidth/(predictions.length-1 || 1))} 
                y2={graphHeight - padding} 
              />
            ))}
          </g>
          
          {/* Confidence area */}
          <polygon 
            points={confidenceAreaPoints} 
            fill="#e3f2fd" 
            opacity="0.5"
          />
          
          {/* Prediction line */}
          <polyline
            fill="none"
            stroke="#1976d2"
            strokeWidth="2"
            points={points}
          />
          
          {/* Data points */}
          {predictions.map((prediction, index) => {
            const x = padding + (index * chartWidth) / (predictions.length - 1 || 1);
            const y = graphHeight - padding - ((prediction.predictedPrice - minPrice) / priceRange) * chartHeight;
            return (
              <circle
                key={`point-${index}`}
                cx={x}
                cy={y}
                r="4"
                fill="#1976d2"
              />
            );
          })}
          
          {/* X-axis labels */}
          {predictions.map((prediction, index) => {
            const x = padding + (index * chartWidth) / (predictions.length - 1 || 1);
            const y = graphHeight - 10;
            return (
              <text
                key={`label-${index}`}
                x={x}
                y={y}
                textAnchor="middle"
                fontSize="12"
                fill="#666"
              >
                {prediction.month}
              </text>
            );
          })}
          
          {/* Y-axis labels */}
          {[0, 1, 2, 3, 4].map(i => {
            const value = minPrice + (i * priceRange / 4);
            const y = graphHeight - padding - (i * chartHeight / 4);
            return (
              <text
                key={`y-label-${i}`}
                x={padding - 10}
                y={y + 4}
                textAnchor="end"
                fontSize="12"
                fill="#666"
              >
                ${value.toFixed(2)}
              </text>
            );
          })}
        </svg>
      </div>
      
      <div className="legend">
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#1976d2' }}></div>
          <span>Predicted Price</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#e3f2fd' }}></div>
          <span>Confidence Interval</span>
        </div>
      </div>
    </div>
  );
};

export default PricePredictionGraph;