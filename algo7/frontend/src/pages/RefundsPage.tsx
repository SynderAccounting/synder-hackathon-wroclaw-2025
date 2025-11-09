import { useEffect, useState, useMemo } from 'react';
import { getAllRefunds } from '../api/refunds';
import type { RefundDTO } from '../api/refunds';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { GoogleGenerativeAI } from '@google/generative-ai';

interface AIAnalysis {
  summary: string;
  commonReasons: string[];
  improvements: string[];
  totalRefunds: number;
}

interface ChartDataPoint {
  month: string;
  [key: string]: number | string; // Dynamic keys for shoe types
}

// Custom Tooltip component for chart
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div
        className="p-4 rounded-lg shadow-lg border"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        <p className="font-semibold mb-2" style={{ color: 'var(--text)' }}>
          {label}
        </p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }}>
            {entry.name}: <span className="font-bold">{entry.value}</span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export function RefundsPage() {
  const [refunds, setRefunds] = useState<RefundDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [selectedMonth, setSelectedMonth] = useState<string>('all');

  // Load data on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const refundsResponse = await getAllRefunds();
        setRefunds(refundsResponse.refunds);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load refunds data');
        console.error('Error fetching refunds:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Get unique months from refunds
  const availableMonths = useMemo(() => {
    const monthsSet = new Set<string>();
    refunds.forEach((refund) => {
      const date = new Date(refund.date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      monthsSet.add(monthKey);
    });
    return Array.from(monthsSet).sort().reverse(); // Most recent first
  }, [refunds]);

  // Filter refunds by selected month or last 30 days
  const filteredRefunds = useMemo(() => {
    if (selectedMonth === 'all') {
      return refunds;
    }

    if (selectedMonth === 'last-30-days') {
      const now = new Date();
      const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

      return refunds.filter((refund) => {
        const refundDate = new Date(refund.date);
        return refundDate >= thirtyDaysAgo && refundDate <= now;
      });
    }

    return refunds.filter((refund) => {
      const date = new Date(refund.date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      return monthKey === selectedMonth;
    });
  }, [refunds, selectedMonth]);

  // Prepare chart data: group by month and shoe type
  const chartData = useMemo(() => {
    const monthTypeMap = new Map<string, Map<string, number>>();
    const allTypes = new Set<string>();

    filteredRefunds.forEach((refund) => {
      const date = new Date(refund.date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      const monthLabel = new Date(date.getFullYear(), date.getMonth(), 1).toLocaleDateString(
        'en-US',
        { month: 'short', year: 'numeric' }
      );

      if (!monthTypeMap.has(monthLabel)) {
        monthTypeMap.set(monthLabel, new Map());
      }

      const typeMap = monthTypeMap.get(monthLabel)!;
      const currentCount = typeMap.get(refund.shoesType) || 0;
      typeMap.set(refund.shoesType, currentCount + refund.quantity);
      allTypes.add(refund.shoesType);
    });

    // Convert to array format for Recharts
    const data: ChartDataPoint[] = Array.from(monthTypeMap.entries()).map(
      ([month, typeMap]) => {
        const dataPoint: ChartDataPoint = { month };
        allTypes.forEach((type) => {
          dataPoint[type] = typeMap.get(type) || 0;
        });
        return dataPoint;
      }
    );

    return { data, types: Array.from(allTypes) };
  }, [filteredRefunds]);

  // Calculate statistics
  const stats = useMemo(() => {
    const totalRefunds = filteredRefunds.length;
    const totalItems = filteredRefunds.reduce((sum, refund) => sum + refund.quantity, 0);

    // Most returned size
    const sizeMap = new Map<number, number>();
    filteredRefunds.forEach((refund) => {
      const currentCount = sizeMap.get(refund.shoesSize) || 0;
      sizeMap.set(refund.shoesSize, currentCount + 1);
    });
    const mostReturnedSize =
      sizeMap.size > 0
        ? Array.from(sizeMap.entries()).reduce((max, entry) =>
            entry[1] > max[1] ? entry : max
          )[0]
        : 'N/A';

    // Most returned type
    const typeMap = new Map<string, number>();
    filteredRefunds.forEach((refund) => {
      const currentCount = typeMap.get(refund.shoesType) || 0;
      typeMap.set(refund.shoesType, currentCount + 1);
    });
    const mostReturnedType =
      typeMap.size > 0
        ? Array.from(typeMap.entries()).reduce((max, entry) =>
            entry[1] > max[1] ? entry : max
          )[0]
        : 'N/A';

    return { totalRefunds, totalItems, mostReturnedSize, mostReturnedType };
  }, [filteredRefunds]);

  // Check localStorage for cached AI analysis
  useEffect(() => {
    if (refunds.length === 0) return;

    const cachedAnalysis = localStorage.getItem('refundsAiAnalysis');
    const cachedRefundsCount = localStorage.getItem('refundsCount');

    if (cachedAnalysis && cachedRefundsCount) {
      const parsedCount = parseInt(cachedRefundsCount, 10);
      if (parsedCount === refunds.length) {
        // Use cached analysis if count hasn't changed
        setAiAnalysis(JSON.parse(cachedAnalysis));
        return;
      }
    }

    // Fetch new AI analysis if no cache or count changed
    fetchAIAnalysis();
  }, [refunds]);

  const fetchAIAnalysis = async () => {
    if (refunds.length === 0) return;

    try {
      setAiLoading(true);
      setAiError(null);

      // Prepare refund descriptions for AI analysis
      const refundDescriptions = refunds.map((r) => r.description).filter((d) => d && d.trim());

      const prompt = `You are a data analyst specializing in e-commerce returns and customer satisfaction.

Analyze the following product refund descriptions and provide:
1. A brief summary of the main refund trends
2. The 5 most common reasons for refunds
3. 5 practical recommendations to reduce refund rates

Refund descriptions:
${refundDescriptions.join('\n')}

Please respond ONLY with valid JSON in this exact structure (no markdown, no code blocks):
{
  "summary": "Brief summary of refund trends",
  "commonReasons": ["reason 1", "reason 2", "reason 3", "reason 4", "reason 5"],
  "improvements": ["improvement 1", "improvement 2", "improvement 3", "improvement 4", "improvement 5"]
}`;

      // Use Gemini API
      const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });
      const result = await model.generateContent(prompt);
      const response = await result.response;
      const aiResponse = response.text();

      // Clean up response (remove markdown code blocks if present)
      let cleanedResponse = aiResponse.trim();
      if (cleanedResponse.startsWith('```json')) {
        cleanedResponse = cleanedResponse.replace(/```json\n?/g, '').replace(/```\n?/g, '');
      } else if (cleanedResponse.startsWith('```')) {
        cleanedResponse = cleanedResponse.replace(/```\n?/g, '');
      }

      // Parse JSON response
      const analysisData = JSON.parse(cleanedResponse);
      const analysis: AIAnalysis = {
        ...analysisData,
        totalRefunds: refunds.length,
      };

      setAiAnalysis(analysis);

      // Cache the analysis
      localStorage.setItem('refundsAiAnalysis', JSON.stringify(analysis));
      localStorage.setItem('refundsCount', refunds.length.toString());
    } catch (err) {
      setAiError(err instanceof Error ? err.message : 'Failed to fetch AI analysis');
      console.error('Error fetching AI analysis:', err);
    } finally {
      setAiLoading(false);
    }
  };

  // Generate colors for different shoe types
  const getColorForType = (index: number) => {
    const colors = [
      'var(--primary)',
      'var(--info)',
      'var(--success)',
      'var(--warning)',
      '#8884d8',
      '#82ca9d',
      '#ffc658',
      '#ff8042',
      '#a4de6c',
      '#d0ed57',
    ];
    return colors[index % colors.length];
  };

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6" style={{ color: 'var(--text)' }}>
          Refunds Analysis
        </h1>
        <div
          className="rounded-lg shadow-lg border p-6"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <p style={{ color: 'var(--text-muted)' }}>Loading refunds data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6" style={{ color: 'var(--text)' }}>
          Refunds Analysis
        </h1>
        <div
          className="rounded-lg shadow-lg border p-6"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <p style={{ color: 'var(--text-error)' }}>Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6" style={{ color: 'var(--text)' }}>
        Refunds Analysis
      </h1>

      {/* Month Filter */}
      <div
        className="rounded-lg shadow border p-4 mb-6"
        style={{
          backgroundColor: 'var(--bg-light)',
          borderColor: 'var(--border)',
        }}
      >
        <div className="flex flex-wrap items-center gap-3">
          <label className="font-medium" style={{ color: 'var(--text)' }}>
            Filter by Period:
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedMonth('all')}
              className="px-4 py-2 rounded transition-all font-medium"
              style={{
                backgroundColor: selectedMonth === 'all' ? 'var(--info)' : 'var(--bg-light)',
                color: selectedMonth === 'all' ? 'white' : 'var(--text)',
                border: `2px solid ${selectedMonth === 'all' ? 'var(--info)' : 'var(--border)'}`,
              }}
            >
              All Time
            </button>
            <button
              onClick={() => setSelectedMonth('last-30-days')}
              className="px-4 py-2 rounded transition-all font-medium"
              style={{
                backgroundColor:
                  selectedMonth === 'last-30-days' ? 'var(--info)' : 'var(--bg-light)',
                color: selectedMonth === 'last-30-days' ? 'white' : 'var(--text)',
                border: `2px solid ${selectedMonth === 'last-30-days' ? 'var(--info)' : 'var(--border)'}`,
              }}
            >
              Last 30 Days
            </button>
            {availableMonths.map((month) => {
              const [year, monthNum] = month.split('-');
              const monthName = new Date(`${year}-${monthNum}-01`).toLocaleDateString('en-US', {
                month: 'long',
                year: 'numeric',
              });

              return (
                <button
                  key={month}
                  onClick={() => setSelectedMonth(month)}
                  className="px-4 py-2 rounded transition-all font-medium"
                  style={{
                    backgroundColor: selectedMonth === month ? 'var(--info)' : 'var(--bg-light)',
                    color: selectedMonth === month ? 'white' : 'var(--text)',
                    border: `2px solid ${selectedMonth === month ? 'var(--info)' : 'var(--border)'}`,
                  }}
                >
                  {monthName}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Statistics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div
          className="rounded-lg shadow border p-4"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Total Refunds
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: 'var(--text-error)' }}>
            {stats.totalRefunds}
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
            Total Items Returned
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: 'var(--info)' }}>
            {stats.totalItems}
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
            Most Returned Size
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: 'var(--primary)' }}>
            {stats.mostReturnedSize}
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
            Most Returned Type
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: 'var(--success)' }}>
            {stats.mostReturnedType}
          </p>
        </div>
      </div>

      {/* Chart and AI Analysis Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart */}
        <div
          className="rounded-lg shadow-lg border p-6"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text)' }}>
            Refunds by Month and Shoe Type
          </h2>
          {chartData.data.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={chartData.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="month" stroke="var(--text-muted)" />
                <YAxis
                  stroke="var(--text-muted)"
                  label={{ value: 'Quantity', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'var(--bg-light)' }} />
                <Legend />
                {chartData.types.map((type, index) => (
                  <Bar
                    key={type}
                    dataKey={type}
                    stackId="a"
                    fill={getColorForType(index)}
                    radius={index === chartData.types.length - 1 ? [8, 8, 0, 0] : [0, 0, 0, 0]}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>No refund data available for chart.</p>
          )}
        </div>

        {/* AI Analysis */}
        <div
          className="rounded-lg shadow-lg border p-6"
          style={{
            backgroundColor: 'var(--bg-light)',
            borderColor: 'var(--border)',
          }}
        >
          <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text)' }}>
            AI-Powered Refund Analysis
          </h2>

          {aiLoading && (
            <div className="flex items-center justify-center py-8">
              <p style={{ color: 'var(--text-muted)' }}>Analyzing refund patterns...</p>
            </div>
          )}

          {aiError && (
            <div
              className="p-4 rounded border mb-4"
              style={{
                backgroundColor: 'var(--bg-dark)',
                borderColor: 'var(--text-error)',
              }}
            >
              <p style={{ color: 'var(--text-error)' }}>AI Analysis Error: {aiError}</p>
              <p className="text-sm mt-2" style={{ color: 'var(--text-muted)' }}>
                This may be due to API rate limits or network issues. Please try refreshing the page.
              </p>
            </div>
          )}

          {aiAnalysis && !aiLoading && (
            <div className="space-y-6">
              {/* Summary */}
              <div>
                <h3 className="font-semibold mb-2" style={{ color: 'var(--primary)' }}>
                  Summary
                </h3>
                <p style={{ color: 'var(--text)' }}>{aiAnalysis.summary}</p>
              </div>

              {/* Common Reasons */}
              <div>
                <h3 className="font-semibold mb-2" style={{ color: 'var(--info)' }}>
                  Most Common Refund Reasons
                </h3>
                <ul className="space-y-2">
                  {aiAnalysis.commonReasons.map((reason, index) => (
                    <li
                      key={index}
                      className="flex items-start"
                      style={{ color: 'var(--text)' }}
                    >
                      <span className="mr-2" style={{ color: 'var(--text-error)' }}>
                        {index + 1}.
                      </span>
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Improvements */}
              <div>
                <h3 className="font-semibold mb-2" style={{ color: 'var(--success)' }}>
                  Recommended Improvements
                </h3>
                <ul className="space-y-2">
                  {aiAnalysis.improvements.map((improvement, index) => (
                    <li
                      key={index}
                      className="flex items-start"
                      style={{ color: 'var(--text)' }}
                    >
                      <span className="mr-2" style={{ color: 'var(--success)' }}>
                        •
                      </span>
                      <span>{improvement}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="text-xs pt-4 border-t" style={{ borderColor: 'var(--border)' }}>
                <p style={{ color: 'var(--text-muted)' }}>
                  Analysis based on {aiAnalysis.totalRefunds} refund records
                </p>
              </div>
            </div>
          )}

          {!aiAnalysis && !aiLoading && !aiError && (
            <div className="flex items-center justify-center py-8">
              <p style={{ color: 'var(--text-muted)' }}>No AI analysis available yet.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
