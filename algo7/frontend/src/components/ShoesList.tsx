import { useEffect, useState, useMemo } from 'react';
import { getAllShoes } from '../api/shoes';
import type { ShoesDTO } from '../api/shoes';

type SortField = 'id' | 'type' | 'size' | 'price' | 'productionPrice' | 'profitMargin';
type SortDirection = 'asc' | 'desc';

export function ShoesList() {
  const [shoes, setShoes] = useState<ShoesDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortField, setSortField] = useState<SortField>('id');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  useEffect(() => {
    const fetchShoes = async () => {
      try {
        setLoading(true);
        const response = await getAllShoes();
        setShoes(response.shoes);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load shoes');
        console.error('Error fetching shoes:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchShoes();
  }, []);

  // Handle column header click for sorting
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Toggle direction if same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to ascending
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Sort shoes based on current sort field and direction
  const sortedShoes = useMemo(() => {
    const sorted = [...shoes].sort((a, b) => {
      let aValue: number | string;
      let bValue: number | string;

      if (sortField === 'profitMargin') {
        aValue = a.price - a.productionPrice;
        bValue = b.price - b.productionPrice;
      } else {
        aValue = a[sortField];
        bValue = b[sortField];
      }

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      return sortDirection === 'asc'
        ? (aValue as number) - (bValue as number)
        : (bValue as number) - (aValue as number);
    });

    return sorted;
  }, [shoes, sortField, sortDirection]);

  // Render sort indicator
  const SortIndicator = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return (
      <span className="ml-1" style={{ color: 'var(--primary)' }}>
        {sortDirection === 'asc' ? '↑' : '↓'}
      </span>
    );
  };

  if (loading) {
    return (
      <div
        className="rounded-lg shadow-lg border p-6"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        <p style={{ color: 'var(--text-muted)' }}>Loading shoes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="rounded-lg shadow-lg border p-6"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        <p style={{ color: 'var(--text-error)' }}>Error: {error}</p>
      </div>
    );
  }

  if (shoes.length === 0) {
    return (
      <div
        className="rounded-lg shadow-lg border p-6"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        <p style={{ color: 'var(--text-muted)' }}>No shoes found in inventory.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div
        className="rounded-lg shadow-lg border p-6"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold" style={{ color: 'var(--text)' }}>
            Shoes Inventory ({sortedShoes.length} items)
          </h2>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Click column headers to sort
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr
                className="border-b"
                style={{
                  borderColor: 'var(--border)',
                }}
              >
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('id')}
                >
                  ID
                  <SortIndicator field="id" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('type')}
                >
                  Type
                  <SortIndicator field="type" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('size')}
                >
                  Size
                  <SortIndicator field="size" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('price')}
                >
                  Price
                  <SortIndicator field="price" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('productionPrice')}
                >
                  Production Price
                  <SortIndicator field="productionPrice" />
                </th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:opacity-80"
                  style={{ color: 'var(--text)' }}
                  onClick={() => handleSort('profitMargin')}
                >
                  Profit Margin
                  <SortIndicator field="profitMargin" />
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedShoes.map((shoe) => {
                const profitMargin = shoe.price - shoe.productionPrice;
                const profitPercentage = ((profitMargin / shoe.productionPrice) * 100).toFixed(1);

                return (
                  <tr
                    key={shoe.id}
                    className="border-b hover:bg-opacity-50"
                    style={{
                      borderColor: 'var(--border)',
                    }}
                  >
                    <td className="py-3 px-4" style={{ color: 'var(--text-muted)' }}>
                      #{shoe.id}
                    </td>
                    <td className="py-3 px-4 font-medium" style={{ color: 'var(--text)' }}>
                      {shoe.type}
                    </td>
                    <td className="py-3 px-4" style={{ color: 'var(--text)' }}>
                      {shoe.size}
                    </td>
                    <td className="py-3 px-4 font-semibold" style={{ color: 'var(--primary)' }}>
                      ${shoe.price}
                    </td>
                    <td className="py-3 px-4" style={{ color: 'var(--text-muted)' }}>
                      ${shoe.productionPrice}
                    </td>
                    <td
                      className="py-3 px-4 font-medium"
                      style={{ color: profitMargin > 0 ? 'var(--success)' : 'var(--text-error)' }}
                    >
                      ${profitMargin} ({profitPercentage}%)
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          className="rounded-lg shadow border p-4"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Total Items
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: 'var(--text)' }}>
            {sortedShoes.length}
          </p>
        </div>

        <div
          className="rounded-lg shadow border p-4"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Total Inventory Value
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: 'var(--primary)' }}>
            ${sortedShoes.reduce((sum, shoe) => sum + shoe.price, 0)}
          </p>
        </div>

        <div
          className="rounded-lg shadow border p-4"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Avg. Profit Margin
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: 'var(--success)' }}>
            {sortedShoes.length > 0
              ? (
                  (sortedShoes.reduce((sum, shoe) => sum + (shoe.price - shoe.productionPrice), 0) /
                    sortedShoes.reduce((sum, shoe) => sum + shoe.productionPrice, 0)) *
                  100
                ).toFixed(1)
              : 0}
            %
          </p>
        </div>
      </div>
    </div>
  );
}
