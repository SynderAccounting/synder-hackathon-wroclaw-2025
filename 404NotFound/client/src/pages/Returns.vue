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
              <h1 class="text-h4 font-weight-bold">Returns & Refunds</h1>
            </div>
            <p class="text-subtitle-1 text-medium-emphasis">
              Track and manage product returns across all platforms
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
    <v-row v-if="loading && !returnsData">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate size="64" color="primary" />
        <p class="text-h6 mt-4">Loading returns data...</p>
      </v-col>
    </v-row>

    <!-- Error State -->
    <v-row v-else-if="error">
      <v-col cols="12">
        <v-alert type="error" variant="tonal" prominent>
          <v-alert-title>Error Loading Returns Data</v-alert-title>
          {{ error }}
        </v-alert>
      </v-col>
    </v-row>

    <!-- Main Content -->
    <template v-else-if="returnsData">
      <!-- Key Metrics Cards -->
      <v-row>
        <v-col cols="12" sm="6" lg="3">
          <v-card>
            <v-card-text>
              <div class="d-flex align-center justify-space-between">
                <div>
                  <p class="text-caption text-medium-emphasis mb-1">Total Returns</p>
                  <h2 class="text-h4 font-weight-bold">
                    {{ returnsData.totalReturns }}
                  </h2>
                  <p :class="['text-caption mt-1', getGrowthColor(returnsData.returnsGrowth)]">
                    <v-icon size="small">{{ getGrowthIcon(returnsData.returnsGrowth) }}</v-icon>
                    {{ Math.abs(parseFloat(returnsData.returnsGrowth)) }}% from last period
                  </p>
                </div>
                <v-avatar color="error" size="56">
                  <v-icon size="32">mdi-package-variant-closed-remove</v-icon>
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
                  <p class="text-caption text-medium-emphasis mb-1">Total Refunds</p>
                  <h2 class="text-h4 font-weight-bold">
                    {{ formatCurrency(returnsData.totalRefundAmount) }}
                  </h2>
                  <p :class="['text-caption mt-1', getGrowthColor(returnsData.refundAmountGrowth)]">
                    <v-icon size="small">{{ getGrowthIcon(returnsData.refundAmountGrowth) }}</v-icon>
                    {{ Math.abs(parseFloat(returnsData.refundAmountGrowth)) }}% from last period
                  </p>
                </div>
                <v-avatar color="warning" size="56">
                  <v-icon size="32">mdi-cash-refund</v-icon>
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
                  <p class="text-caption text-medium-emphasis mb-1">Return Rate</p>
                  <h2 class="text-h4 font-weight-bold">
                    {{ returnsData.returnRate }}%
                  </h2>
                  <p class="text-caption text-medium-emphasis mt-1">
                    {{ returnsData.totalReturnedItems }} items returned
                  </p>
                </div>
                <v-avatar color="info" size="56">
                  <v-icon size="32">mdi-percent</v-icon>
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
                  <p class="text-caption text-medium-emphasis mb-1">Avg Refund</p>
                  <h2 class="text-h4 font-weight-bold">
                    {{ formatCurrency(returnsData.avgRefundAmount) }}
                  </h2>
                  <p class="text-caption text-medium-emphasis mt-1">
                    Per return
                  </p>
                </div>
                <v-avatar color="success" size="56">
                  <v-icon size="32">mdi-calculator</v-icon>
                </v-avatar>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Period Selector -->
      <v-row class="mt-2">
        <v-col cols="12">
          <v-btn-toggle
            v-model="period"
            density="compact"
            mandatory
            variant="outlined"
            color="primary"
          >
            <v-btn value="7d">Last 7 Days</v-btn>
            <v-btn value="30d">Last 30 Days</v-btn>
            <v-btn value="90d">Last 90 Days</v-btn>
          </v-btn-toggle>
        </v-col>
      </v-row>

      <!-- Charts Row 1 -->
      <v-row class="mt-4">
        <!-- Returns Trend -->
        <v-col cols="12" lg="8">
          <v-card>
            <v-card-title>Returns & Refunds Trend</v-card-title>
            <v-card-text style="height: 400px">
              <Line :data="returnsTrendChartData" :options="returnsTrendChartOptions" />
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Return Reasons -->
        <v-col cols="12" lg="4">
          <v-card>
            <v-card-title>Return Reasons</v-card-title>
            <v-card-text style="height: 400px">
              <Doughnut :data="returnReasonsChartData" :options="returnReasonsChartOptions" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Charts Row 2 -->
      <v-row class="mt-4">
        <!-- Returns by Platform -->
        <v-col cols="12" lg="6">
          <v-card>
            <v-card-title>Returns by Platform</v-card-title>
            <v-card-text style="height: 350px">
              <Bar :data="returnsByPlatformChartData" :options="returnsByPlatformChartOptions" />
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Refund Status Breakdown -->
        <v-col cols="12" lg="6">
          <v-card>
            <v-card-title>Refund Status</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item
                  v-for="(count, status) in returnsData.refundStatusBreakdown"
                  :key="status"
                >
                  <template v-slot:prepend>
                    <v-avatar :color="getStatusColor(status)" size="40">
                      <v-icon>{{ getStatusIcon(status) }}</v-icon>
                    </v-avatar>
                  </template>
                  <v-list-item-title class="font-weight-bold">
                    {{ capitalizeFirst(status) }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ count }} returns ({{ ((count / returnsData.totalReturns) * 100).toFixed(1) }}%)
                  </v-list-item-subtitle>
                  <template v-slot:append>
                    <v-chip :color="getStatusColor(status)" size="small" variant="tonal">
                      {{ count }}
                    </v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Recent Returns Table -->
      <v-row class="mt-4">
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center justify-space-between">
              <span>Recent Returns</span>
              <v-chip color="primary" variant="tonal">
                <v-icon start>mdi-package-variant-closed</v-icon>
                {{ returnsData.recentReturns.length }} recent returns
              </v-chip>
            </v-card-title>
            <v-card-text>
              <v-data-table
                :headers="returnsTableHeaders"
                :items="returnsData.recentReturns"
                :items-per-page="10"
                class="elevation-0"
              >
                <template v-slot:item.id="{ item }">
                  <span class="font-weight-bold text-primary">{{ item.id }}</span>
                </template>

                <template v-slot:item.productName="{ item }">
                  <div>
                    <div class="font-weight-medium">{{ item.productName }}</div>
                    <div class="text-caption text-medium-emphasis">
                      Order: {{ item.orderId }}
                    </div>
                  </div>
                </template>

                <template v-slot:item.platform="{ item }">
                  <v-chip size="small" variant="tonal" :color="getPlatformColor(item.platform)">
                    {{ item.platform }}
                  </v-chip>
                </template>

                <template v-slot:item.status="{ item }">
                  <v-chip
                    size="small"
                    :color="getStatusColor(item.status.toLowerCase())"
                    variant="tonal"
                  >
                    {{ item.status }}
                  </v-chip>
                </template>

                <template v-slot:item.refundAmount="{ item }">
                  <span class="font-weight-bold">{{ formatCurrency(item.refundAmount) }}</span>
                </template>

                <template v-slot:item.reason="{ item }">
                  <v-tooltip location="top">
                    <template v-slot:activator="{ props }">
                      <span v-bind="props" class="text-truncate" style="max-width: 200px; display: inline-block;">
                        {{ item.reason }}
                      </span>
                    </template>
                    {{ item.reason }}
                  </v-tooltip>
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

interface ReturnsData {
  totalReturns: number
  totalRefundAmount: number
  totalReturnedItems: number
  returnRate: number
  avgRefundAmount: number
  returnsTrend: { date: string; returns: number; refundAmount: number }[]
  returnsByPlatform: { platform: string; returns: number; refundAmount: number; returnRate: string }[]
  returnReasons: { reason: string; count: number; percentage: number }[]
  recentReturns: RecentReturn[]
  refundStatusBreakdown: {
    pending: number
    approved: number
    refunded: number
    rejected: number
    processing: number
  }
  returnsGrowth: string
  refundAmountGrowth: string
}

interface RecentReturn {
  id: string
  orderId: string
  productName: string
  platform: string
  reason: string
  status: string
  refundAmount: number
  returnDate: string
  customerName: string
  sku: string
}

const period = ref<string>('30d')
const loading = ref(false)
const error = ref<string | null>(null)

// Fetch returns data
const { data: returnsData, refetch } = useQuery({
  queryKey: ['returns', period],
  queryFn: async () => {
    const response = await axios.get<ReturnsData>('/api/analytics/returns', {
      params: { period: period.value }
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
    error.value = err.message || 'Failed to load returns data'
  } finally {
    loading.value = false
  }
}

// Watch for period changes
watch(period, () => {
  refreshData()
})

onMounted(() => {
  refreshData()
})

// Chart Data
const returnsTrendChartData = computed(() => {
  if (!returnsData.value) return { labels: [], datasets: [] }

  return {
    labels: returnsData.value.returnsTrend.map(d => d.date),
    datasets: [
      {
        label: 'Returns Count',
        data: returnsData.value.returnsTrend.map(d => d.returns),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y'
      },
      {
        label: 'Refund Amount',
        data: returnsData.value.returnsTrend.map(d => d.refundAmount),
        borderColor: 'rgb(251, 146, 60)',
        backgroundColor: 'rgba(251, 146, 60, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y1'
      }
    ]
  }
})

const returnsTrendChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false
  },
  plugins: {
    legend: {
      position: 'top' as const
    },
    tooltip: {
      callbacks: {
        label: (context: any) => {
          if (context.datasetIndex === 0) {
            return `Returns: ${context.parsed.y}`
          } else {
            return `Refund: $${context.parsed.y.toLocaleString()}`
          }
        }
      }
    }
  },
  scales: {
    y: {
      type: 'linear' as const,
      display: true,
      position: 'left' as const,
      beginAtZero: true,
      title: {
        display: true,
        text: 'Returns Count'
      }
    },
    y1: {
      type: 'linear' as const,
      display: true,
      position: 'right' as const,
      beginAtZero: true,
      title: {
        display: true,
        text: 'Refund Amount ($)'
      },
      grid: {
        drawOnChartArea: false
      },
      ticks: {
        callback: (value: any) => '$' + value.toLocaleString()
      }
    }
  }
}

const returnReasonsChartData = computed(() => {
  if (!returnsData.value) return { labels: [], datasets: [] }

  return {
    labels: returnsData.value.returnReasons.map(r => r.reason),
    datasets: [
      {
        data: returnsData.value.returnReasons.map(r => r.count),
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(251, 146, 60, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(99, 102, 241, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(156, 163, 175, 0.8)'
        ],
        borderWidth: 0
      }
    ]
  }
})

const returnReasonsChartOptions = {
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
          const percentage = returnsData.value?.returnReasons[context.dataIndex]?.percentage || 0
          return `${label}: ${value} (${percentage}%)`
        }
      }
    }
  }
}

const returnsByPlatformChartData = computed(() => {
  if (!returnsData.value) return { labels: [], datasets: [] }

  return {
    labels: returnsData.value.returnsByPlatform.map(p => p.platform),
    datasets: [
      {
        label: 'Returns',
        data: returnsData.value.returnsByPlatform.map(p => p.returns),
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderRadius: 8
      }
    ]
  }
})

const returnsByPlatformChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context: any) => {
          const platform = returnsData.value?.returnsByPlatform[context.dataIndex]
          return [
            `Returns: ${context.parsed.y}`,
            `Refunds: $${platform?.refundAmount.toLocaleString()}`,
            `Return Rate: ${platform?.returnRate}%`
          ]
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

// Table headers
const returnsTableHeaders = [
  { title: 'Return ID', key: 'id' },
  { title: 'Product', key: 'productName' },
  { title: 'Platform', key: 'platform' },
  { title: 'Customer', key: 'customerName' },
  { title: 'Reason', key: 'reason' },
  { title: 'Status', key: 'status' },
  { title: 'Refund Amount', key: 'refundAmount' },
  { title: 'Date', key: 'returnDate' }
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

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    pending: 'warning',
    approved: 'info',
    refunded: 'success',
    rejected: 'error',
    processing: 'primary'
  }
  return colors[status.toLowerCase()] || 'grey'
}

const getStatusIcon = (status: string): string => {
  const icons: Record<string, string> = {
    pending: 'mdi-clock-outline',
    approved: 'mdi-check-circle',
    refunded: 'mdi-cash-check',
    rejected: 'mdi-close-circle',
    processing: 'mdi-refresh'
  }
  return icons[status.toLowerCase()] || 'mdi-help-circle'
}

const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

const getGrowthColor = (growth: string): string => {
  const growthNum = parseFloat(growth)
  // For returns, negative growth is good (fewer returns)
  return growthNum < 0 ? 'text-success' : 'text-error'
}

const getGrowthIcon = (growth: string): string => {
  const growthNum = parseFloat(growth)
  return growthNum < 0 ? 'mdi-trending-down' : 'mdi-trending-up'
}
</script>

<style scoped>
.v-card {
  height: 100%;
}

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
