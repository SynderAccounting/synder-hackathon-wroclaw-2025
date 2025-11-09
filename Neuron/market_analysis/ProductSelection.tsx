import React, { useState, useEffect } from 'react';

interface Product {
  id: string;
  name: string;
  category: string;
  currentPrice: number;
}

interface ProductSelectionProps {
  onProductSelect: (productId: string) => void;
  selectedProduct: string | null;
}

const ProductSelection: React.FC<ProductSelectionProps> = ({ 
  onProductSelect, 
  selectedProduct 
}) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data loading - in a real app, this would load from CSV
  useEffect(() => {
    const loadProducts = async () => {
      try {
        // Simulate API call or CSV loading
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Mock product data
        const mockProducts: Product[] = [
          { id: '1', name: 'Laptop Pro', category: 'Electronics', currentPrice: 1299.99 },
          { id: '2', name: 'Wireless Headphones', category: 'Electronics', currentPrice: 199.99 },
          { id: '3', name: 'Smart Watch', category: 'Electronics', currentPrice: 299.99 },
          { id: '4', name: 'Coffee Maker', category: 'Home Appliance', currentPrice: 89.99 },
          { id: '5', name: 'Blender', category: 'Home Appliance', currentPrice: 59.99 },
          { id: '6', name: 'Desk Chair', category: 'Furniture', currentPrice: 199.99 },
          { id: '7', name: 'Office Desk', category: 'Furniture', currentPrice: 349.99 },
        ];
        
        setProducts(mockProducts);
        setLoading(false);
      } catch (err) {
        setError('Failed to load products');
        setLoading(false);
      }
    };

    loadProducts();
  }, []);

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="loading">Loading products...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="product-selection">
      <h3>Select Product for Market Analysis</h3>
      <div className="search-container">
        <input
          type="text"
          placeholder="Search products..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>
      
      <div className="product-list">
        {filteredProducts.map(product => (
          <div
            key={product.id}
            className={`product-item ${
              selectedProduct === product.id ? 'selected' : ''
            }`}
            onClick={() => onProductSelect(product.id)}
          >
            <div className="product-info">
              <h4>{product.name}</h4>
              <p>Category: {product.category}</p>
              <p>Current Price: ${product.currentPrice.toFixed(2)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductSelection;