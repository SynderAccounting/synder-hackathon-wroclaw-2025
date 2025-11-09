// Mock service for loading product data from CSV and making predictions
// In a real application, this would interface with the actual CSV file and model

interface ProductData {
  id: string;
  name: string;
  category: string;
  prices: number[]; // Historical prices
}

interface PredictionResult {
  productId: string;
  productName: string;
  predictions: {
    month: string;
    predictedPrice: number;
    confidenceLow: number;
    confidenceHigh: number;
  }[];
}

// Mock data that simulates what would come from Retail_Prices_of_Products.csv
const mockProductData: ProductData[] = [
  {
    id: '1',
    name: 'Laptop Pro',
    category: 'Electronics',
    prices: [1250, 1260, 1270, 1280, 1290, 1299.99] // Last 6 months of prices
  },
  {
    id: '2',
    name: 'Wireless Headphones',
    category: 'Electronics',
    prices: [180, 185, 188, 190, 195, 199.99] // Last 6 months of prices
  },
  {
    id: '3',
    name: 'Smart Watch',
    category: 'Electronics',
    prices: [280, 285, 290, 292, 295, 299.99] // Last 6 months of prices
  },
  {
    id: '4',
    name: 'Coffee Maker',
    category: 'Home Appliance',
    prices: [80, 82, 84, 86, 88, 89.99] // Last 6 months of prices
  },
  {
    id: '5',
    name: 'Blender',
    category: 'Home Appliance',
    prices: [50, 52, 54, 56, 58, 59.99] // Last 6 months of prices
  },
  {
    id: '6',
    name: 'Desk Chair',
    category: 'Furniture',
    prices: [180, 185, 190, 192, 195, 199.99] // Last 6 months of prices
  },
  {
    id: '7',
    name: 'Office Desk',
    category: 'Furniture',
    prices: [320, 330, 335, 340, 345, 349.99] // Last 6 months of prices
  }
];

// Function to simulate loading products from CSV
export const loadProductsFromCSV = async (): Promise<ProductData[]> => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Return mock data - in a real app, this would parse the CSV
  return mockProductData;
};

// Function to simulate price prediction using a model
// In a real app, this would load the model from product_model
export const predictPrices = async (productId: string): Promise<PredictionResult> => {
  // Simulate model loading and prediction time
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const product = mockProductData.find(p => p.id === productId);
  
  if (!product) {
    throw new Error(`Product with id ${productId} not found`);
  }
  
  // Generate mock predictions for next 5 months
  const currentPrice = product.prices[product.prices.length - 1];
  const predictions = [];
  
  // Get the next 5 months
  const months = [];
  const now = new Date();
  for (let i = 1; i <= 5; i++) {
    const nextMonth = new Date(now.getFullYear(), now.getMonth() + i, 1);
    months.push(nextMonth.toLocaleString('default', { month: 'short' }));
  }
  
  // Generate predictions with some random variation based on recent trend
  let lastPrice = currentPrice;
  for (let i = 0; i < 5; i++) {
    // Calculate a trend factor based on recent price changes
    const recentChange = 
      product.prices.length > 1 
        ? (product.prices[product.prices.length - 1] - product.prices[product.prices.length - 2]) / product.prices.length
        : 0;
    
    // Add some random fluctuation
    const fluctuation = (Math.random() - 0.5) * 0.1; // ±5% fluctuation
    const predictedChange = recentChange * (1 + fluctuation);
    const predictedPrice = lastPrice + predictedChange;
    
    // Calculate confidence interval (±5% of predicted price)
    const confidenceInterval = predictedPrice * 0.05;
    
    predictions.push({
      month: months[i],
      predictedPrice: parseFloat(predictedPrice.toFixed(2)),
      confidenceLow: parseFloat((predictedPrice - confidenceInterval).toFixed(2)),
      confidenceHigh: parseFloat((predictedPrice + confidenceInterval).toFixed(2))
    });
    
    lastPrice = predictedPrice;
  }
  
  return {
    productId: product.id,
    productName: product.name,
    predictions
  };
};