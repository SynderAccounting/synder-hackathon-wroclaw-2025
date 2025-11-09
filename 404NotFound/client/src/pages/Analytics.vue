<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between mb-4">
          <div>
            <div class="d-flex align-center ga-2 mb-2">
              <v-btn
                icon="mdi-arrow-left"
                variant="text"
                size="small"
                to="/"
              />
              <h1 class="text-h4 font-weight-bold">Analytics Dashboard</h1>
            </div>
            <p class="text-subtitle-1 text-medium-emphasis">
              Performance metrics and insights across all platforms
            </p>
          </div>
          <v-btn
            color="primary"
            prepend-icon="mdi-refresh"
            @click="refreshData"
            :loading="loading"
          >
            Refresh Data
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-if="loading && !analyticsData">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate size="64" color="primary" />
        <p class="text-h6 mt-4">Loading analytics...</p>
      </v-col>
    </v-row>

    <!-- Error State -->
    <v-row v-else-if="error">
      <v-col cols="12">
        <v-alert type="error" variant="tonal" prominent>
          <v-alert-title>Error Loading Analytics</v-alert-title>
          {{ error }}
        </v-alert>
      </v-col>
    </v-row>

    <!-- Main Content -->
    <template v-else-if="analyticsData">
      <!-- Key Metrics Cards -->
      <v-row>
        <v-col cols="12" sm="6" lg="3">
          <v-card>
            <v-card-text>
              <div class="d-flex align-center justify-space-between">
                <div>
                  <p class="text-caption text-medium-emphasis mb-1">Total Sales</p>
                  <h2 class="text-h4 font-weight-bold">
                    {{ formatCurrency(analyticsData.totalSales) }}
                  </h2>
                  <p class="text-caption text-success mt-1">
                    <v-icon size="small">mdi-trending-up</v-icon>
                    +{{ analyticsData.salesGrowth }}% from last month
                  </p>
                </div>
                <v-avatar color="primary" size="56">
                  <v-icon size="32">mdi-currency-usd</v-icon>
                </v-avatar>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" lg="3">
          <v-card>
            <v-card-text>
              <div class="d-flex align-center justify-space-between">
                <div>
                  <p class="text-caption text-medium-emphasis mb-1">Average Order</p>
                  <h2 class="text-h4 font-weight-bold">
                    {{ formatCurrency(analyticsData.averageOrder) }}
                  </h2>
                  <p class="text-caption text-medium-emphasis mt-1">
                    {{ analyticsData.totalOrders }} orders
                  </p>
                </div>
                <v-avatar color="success" size="56">
                  <v-icon size="32">mdi-cart</v-icon>
                </v-avatar>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" lg="3">
          <v-card>
            <v-card-text>
              <div class="d-flex align-center justify-space-between">
                <div>
                  <p class="text-caption text-medium-emphasis mb-1">Conversion Rate</p>
                  <h2 class="text-h4 font-weight-bold">
                    {{ analyticsData.conversionRate.toFixed(1) }}%
                  </h2>
                  <p class="text-caption text-medium-emphasis mt-1">
                    {{ analyticsData.totalVisitors }} visitors
                  </p>
                </div>
                <v-avatar color="info" size="56">
                  <v-icon size="32">mdi-chart-line</v-icon>
                </v-avatar>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" lg="3">
          <v-card>
            <v-card-text>
              <div class="d-flex align-center justify-space-between">
                <div>
                  <p class="text-caption text-medium-emphasis mb-1">Low Stock Items</p>
                  <h2 class="text-h4 font-weight-bold">
                    {{ analyticsData.lowStockCount }}
                  </h2>
                  <p class="text-caption text-warning mt-1">
                    <v-icon size="small">mdi-alert</v-icon>
                    Requires attention
                  </p>
                </div>
                <v-avatar color="warning" size="56">
                  <v-icon size="32">mdi-package-variant</v-icon>
                </v-avatar>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Charts Row 1 -->
      <v-row class="mt-4">
        <!-- Sales by Platform -->
        <v-col cols="12" lg="8">
          <v-card>
            <v-card-title class="d-flex align-center justify-space-between">
              <span>Sales by Platform</span>
              <v-btn-toggle
                v-model="salesPeriod"
                density="compact"
                mandatory
                variant="outlined"
                color="primary"
              >
                <v-btn value="7d" size="small">7D</v-btn>
                <v-btn value="30d" size="small">30D</v-btn>
                <v-btn value="90d" size="small">90D</v-btn>
              </v-btn-toggle>
            </v-card-title>
            <v-card-text style="height: 400px">
              <Line :data="salesChartData" :options="salesChartOptions" />
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Platform Distribution -->
        <v-col cols="12" lg="4">
          <v-card>
            <v-card-title>Platform Distribution</v-card-title>
            <v-card-text style="height: 400px">
              <Doughnut :data="platformChartData" :options="platformChartOptions" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Charts Row 2 -->
      <v-row class="mt-4">
        <!-- Conversion Rate Trend -->
        <v-col cols="12" lg="6">
          <v-card>
            <v-card-title>Conversion Rate Trend</v-card-title>
            <v-card-text style="height: 350px">
              <Line :data="conversionChartData" :options="conversionChartOptions" />
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Average Order Value -->
        <v-col cols="12" lg="6">
          <v-card>
            <v-card-title>Average Order Value</v-card-title>
            <v-card-text style="height: 350px">
              <Bar :data="aovChartData" :options="aovChartOptions" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Top 10 Low Stock Products -->
      <v-row class="mt-4">
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center justify-space-between">
              <span>Top 10 Low Stock Products</span>
              <v-chip color="warning" variant="tonal">
                <v-icon start>mdi-alert</v-icon>
                {{ analyticsData.lowStockCount }} items need restock
              </v-chip>
            </v-card-title>
            <v-card-text>
              <v-data-table
                :headers="lowStockHeaders"
                :items="analyticsData.lowStockProducts"
                :items-per-page="10"
                class="elevation-0"
              >
                <template v-slot:item.product="{ item }">
                  <div class="d-flex align-center py-2">
                    <v-avatar size="40" class="mr-3" rounded>
                      <v-img
                        v-if="item.image"
                        :src="item.image"
                        :alt="item.name"
                      />
                      <v-icon v-else>mdi-image-off</v-icon>
                    </v-avatar>
                    <div>
                      <div class="font-weight-medium">{{ item.name }}</div>
                      <div class="text-caption text-medium-emphasis">
                        SKU: {{ item.sku }}
                      </div>
                    </div>
                  </div>
                </template>

                <template v-slot:item.platform="{ item }">
                  <v-chip size="small" variant="tonal" :color="getPlatformColor(item.platform)">
                    {{ item.platform }}
                  </v-chip>
                </template>

                <template v-slot:item.stock="{ item }">
                  <div class="d-flex align-center">
                    <v-progress-linear
                      :model-value="(item.stock / item.threshold) * 100"
                      :color="getStockColor(item.stock, item.threshold)"
                      height="8"
                      rounded
                      class="mr-3"
                      style="max-width: 100px"
                    />
                    <span class="font-weight-bold">{{ item.stock }}</span>
                  </div>
                </template>

                <template v-slot:item.status="{ item }">
                  <v-chip
                    size="small"
                    :color="item.stock === 0 ? 'error' : item.stock < item.threshold / 2 ? 'warning' : 'orange'"
                    variant="tonal"
                  >
                    {{ item.stock === 0 ? 'Out of Stock' : 'Low Stock' }}
                  </v-chip>
                </template>

                <template v-slot:item.actions="{ item }">
                  <v-btn
                    size="small"
                    variant="text"
                    color="primary"
                    :href="item.productUrl"
                    target="_blank"
                  >
                    View Product
                    <v-icon end>mdi-open-in-new</v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import axios from 'axios'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line, Doughnut, Bar } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface AnalyticsData {
  totalSales: number
  salesGrowth: number
  averageOrder: number
  totalOrders: number
  conversionRate: number
  totalVisitors: number
  lowStockCount: number
  lowStockProducts: LowStockProduct[]
  salesByPlatform: { platform: string; sales: number; orders: number }[]
  salesTrend: { date: string; sales: number }[]
  conversionTrend: { date: string; rate: number }[]
  aovTrend: { platform: string; aov: number }[]
}

interface LowStockProduct {
  id: string
  name: string
  sku: string
  platform: string
  stock: number
  threshold: number
  image?: string
  productUrl: string
}

const salesPeriod = ref<string>('30d')
const loading = ref(false)
const error = ref<string | null>(null)

// Fetch analytics data
const { data: analyticsData, refetch } = useQuery({
  queryKey: ['analytics', salesPeriod],
  queryFn: async () => {
    const response = await axios.get<AnalyticsData>('/api/analytics', {
      params: { period: salesPeriod.value }
    })
    return response.data
  }
})

// Refresh data function
const refreshData = async () => {
  loading.value = true
  error.value = null
  try {
    await refetch()
  } catch (err: any) {
    error.value = err.message || 'Failed to load analytics data'
  } finally {
    loading.value = false
  }
}

// Watch for period changes
watch(salesPeriod, () => {
  refreshData()
})

onMounted(() => {
  refreshData()
})

// Chart Data
const salesChartData = computed(() => {
  if (!analyticsData.value) return { labels: [], datasets: [] }

  return {
    labels: analyticsData.value.salesTrend.map(d => d.date),
    datasets: [
      {
        label: 'Sales',
        data: analyticsData.value.salesTrend.map(d => d.sales),
        borderColor: 'rgb(99, 102, 241)',
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }
})

const salesChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context: any) => `Sales: $${context.parsed.y.toLocaleString()}`
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value: any) => '$' + value.toLocaleString()
      }
    }
  }
}

const platformChartData = computed(() => {
  if (!analyticsData.value) return { labels: [], datasets: [] }

  return {
    labels: analyticsData.value.salesByPlatform.map(p => p.platform),
    datasets: [
      {
        data: analyticsData.value.salesByPlatform.map(p => p.sales),
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(251, 146, 60, 0.8)',
          'rgba(236, 72, 153, 0.8)',
          'rgba(59, 130, 246, 0.8)'
        ],
        borderWidth: 0
      }
    ]
  }
})

const platformChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const
    },
    tooltip: {
      callbacks: {
        label: (context: any) => {
          const label = context.label || ''
          const value = context.parsed || 0
          return `${label}: $${value.toLocaleString()}`
        }
      }
    }
  }
}

const conversionChartData = computed(() => {
  if (!analyticsData.value) return { labels: [], datasets: [] }

  return {
    labels: analyticsData.value.conversionTrend.map(d => d.date),
    datasets: [
      {
        label: 'Conversion Rate %',
        data: analyticsData.value.conversionTrend.map(d => d.rate),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }
})

const conversionChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value: any) => value + '%'
      }
    }
  }
}

const aovChartData = computed(() => {
  if (!analyticsData.value) return { labels: [], datasets: [] }

  return {
    labels: analyticsData.value.aovTrend.map(d => d.platform),
    datasets: [
      {
        label: 'Average Order Value',
        data: analyticsData.value.aovTrend.map(d => d.aov),
        backgroundColor: 'rgba(99, 102, 241, 0.8)',
        borderRadius: 8
      }
    ]
  }
})

const aovChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context: any) => `AOV: $${context.parsed.y.toLocaleString()}`
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value: any) => '$' + value.toLocaleString()
      }
    }
  }
}

// Table headers
const lowStockHeaders = [
  { title: 'Product', key: 'product', sortable: false },
  { title: 'Platform', key: 'platform' },
  { title: 'Current Stock', key: 'stock' },
  { title: 'Threshold', key: 'threshold' },
  { title: 'Status', key: 'status' },
  { title: 'Actions', key: 'actions', sortable: false }
]

// Helper functions
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

const getPlatformColor = (platform: string): string => {
  const colors: Record<string, string> = {
    Shopify: 'success',
    Square: 'primary',
    Amazon: 'orange',
    WooCommerce: 'purple',
    eBay: 'blue'
  }
  return colors[platform] || 'grey'
}

const getStockColor = (stock: number, threshold: number): string => {
  if (stock === 0) return 'error'
  if (stock < threshold / 2) return 'warning'
  if (stock < threshold) return 'orange'
  return 'success'
}
</script>

<style scoped>
.v-card {
  height: 100%;
}
</style>
