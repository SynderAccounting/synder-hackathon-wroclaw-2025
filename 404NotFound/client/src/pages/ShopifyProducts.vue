<template>
  <v-container fluid class="pa-0 fill-height">
    <!-- Header -->
    <v-app-bar class="app-header" elevation="1">
      <v-container class="d-flex align-center justify-space-between pa-0">
        <div class="d-flex align-center ga-3">
          <v-btn
            icon="mdi-arrow-left"
            variant="text"
            @click="$router.push('/')"
          />
          <img src="/shopify.png" alt="Shopify" class="platform-logo" />
          <h1 class="text-h6 font-weight-medium">
            Shopify Products
          </h1>
        </div>

        <v-btn
          variant="outlined"
          color="primary"
          size="small"
          :loading="isLoading || isRefetching"
          @click="refetch()"
        >
          <v-icon start>mdi-refresh</v-icon>
          Refresh
        </v-btn>
      </v-container>
    </v-app-bar>

    <!-- Main Content -->
    <v-main>
      <v-container class="py-8">
        <!-- Loading State -->
        <div v-if="isLoading" class="d-flex justify-center align-center py-12">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
          />
        </div>

        <!-- Error State -->
        <v-alert
          v-else-if="error"
          type="error"
          variant="tonal"
          class="mb-4"
        >
          <div class="d-flex align-center justify-space-between">
            <span>{{ error.message || 'Failed to load products' }}</span>
            <v-btn
              variant="text"
              @click="refetch()"
            >
              Retry
            </v-btn>
          </div>
        </v-alert>

        <!-- Products Data -->
        <div v-else-if="productsData">
          <!-- Summary Card -->
          <v-card class="mb-6" elevation="2">
            <v-card-title class="d-flex align-center ga-2">
              <v-icon color="primary">mdi-chart-box</v-icon>
              Summary
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" sm="4">
                  <div class="stat-item">
                    <div class="text-h4 font-weight-bold text-primary">
                      {{ productsData._summary.total_products }}
                    </div>
                    <div class="text-caption text-medium-emphasis">Total Products</div>
                  </div>
                </v-col>
                <v-col cols="12" sm="4">
                  <div class="stat-item">
                    <div class="text-h4 font-weight-bold text-success">
                      {{ productsData._summary.total_inventory }}
                    </div>
                    <div class="text-caption text-medium-emphasis">Total Inventory</div>
                  </div>
                </v-col>
                <v-col cols="12" sm="4">
                  <div class="stat-item">
                    <div class="text-h4 font-weight-bold text-info">
                      {{ productsData._summary.total_locations }}
                    </div>
                    <div class="text-caption text-medium-emphasis">Locations</div>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Products Table -->
          <v-card elevation="2">
            <v-card-title class="d-flex align-center ga-2">
              <v-icon color="primary">mdi-package-variant</v-icon>
              Products List
            </v-card-title>
            <v-card-text>
              <v-data-table
                :headers="headers"
                :items="productsData.products"
                :items-per-page="10"
                class="elevation-0"
              >
                <!-- Product Column -->
                <template #item.title="{ item }">
                  <div class="d-flex align-center ga-3 py-2">
                    <v-img
                      v-if="item.image?.src"
                      :src="item.image.src"
                      :alt="item.title"
                      width="48"
                      height="48"
                      cover
                      class="rounded"
                    />
                    <div v-else class="product-placeholder">
                      <v-icon>mdi-image-off</v-icon>
                    </div>
                    <div>
                      <div class="font-weight-medium">{{ item.title }}</div>
                      <div class="text-caption text-medium-emphasis">
                        ID: {{ item.id }}
                      </div>
                    </div>
                  </div>
                </template>

                <!-- Variants Column -->
                <template #item.variants="{ item }">
                  <v-chip size="small" color="primary" variant="tonal">
                    {{ item._meta.variants_count }} variant{{ item._meta.variants_count !== 1 ? 's' : '' }}
                  </v-chip>
                </template>

                <!-- Inventory Column -->
                <template #item.inventory="{ item }">
                  <v-chip
                    size="small"
                    :color="getInventoryColor(item._meta.total_inventory)"
                    variant="flat"
                  >
                    {{ item._meta.total_inventory }} in stock
                  </v-chip>
                </template>

                <!-- Status Column -->
                <template #item.status="{ item }">
                  <v-chip
                    size="small"
                    :color="item.status === 'active' ? 'success' : 'default'"
                    variant="tonal"
                  >
                    {{ item.status }}
                  </v-chip>
                </template>

                <!-- Actions Column -->
                <template #item.actions="{ item }">
                  <v-btn
                    icon="mdi-information"
                    variant="text"
                    size="small"
                    @click="selectedProduct = item; showDetailsDialog = true"
                  />
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </div>
      </v-container>
    </v-main>

    <!-- Product Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="800">
      <v-card v-if="selectedProduct">
        <v-card-title class="d-flex align-center justify-space-between">
          <span>{{ selectedProduct.title }}</span>
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="showDetailsDialog = false"
          />
        </v-card-title>
        <v-card-text>
          <div class="mb-4">
            <v-img
              v-if="selectedProduct.image?.src"
              :src="selectedProduct.image.src"
              :alt="selectedProduct.title"
              max-height="200"
              contain
              class="mb-4"
            />
            <div class="text-body-2 mb-2">
              <strong>Product ID:</strong> {{ selectedProduct.id }}
            </div>
            <div class="text-body-2 mb-2">
              <strong>Status:</strong> {{ selectedProduct.status }}
            </div>
            <div class="text-body-2 mb-2">
              <strong>Vendor:</strong> {{ selectedProduct.vendor || 'N/A' }}
            </div>
            <div class="text-body-2 mb-2">
              <strong>Product Type:</strong> {{ selectedProduct.product_type || 'N/A' }}
            </div>
          </div>

          <v-divider class="my-4" />

          <h3 class="text-h6 mb-4">Variants ({{ selectedProduct.variants.length }})</h3>
          <v-list>
            <v-list-item
              v-for="variant in selectedProduct.variants"
              :key="variant.id"
              class="mb-2 border rounded"
            >
              <template #prepend>
                <v-icon>mdi-package-variant</v-icon>
              </template>
              <v-list-item-title>{{ variant.title }}</v-list-item-title>
              <v-list-item-subtitle>
                Price: ${{ variant.price }} | SKU: {{ variant.sku || 'N/A' }}
              </v-list-item-subtitle>

              <template #append>
                <v-chip size="small" color="primary">
                  ID: {{ variant.id }}
                </v-chip>
              </template>

              <!-- Inventory Details -->
              <div v-if="variant.inventory_details?.length" class="mt-2 ml-8">
                <div class="text-caption font-weight-bold mb-1">Inventory by Location:</div>
                <v-chip
                  v-for="inv in variant.inventory_details"
                  :key="inv.location_id"
                  size="small"
                  class="mr-2 mb-1"
                  :color="inv.available > 0 ? 'success' : 'default'"
                  variant="tonal"
                >
                  {{ inv.location_name }}: {{ inv.available }}
                </v-chip>
              </div>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="showDetailsDialog = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { apiRequest } from '@/lib/queryClient'

// Props
const props = defineProps<{
  platformId: string
}>()

// State
const showDetailsDialog = ref(false)
const selectedProduct = ref<any>(null)

// Table headers
const headers = [
  { title: 'Product', key: 'title', sortable: true },
  { title: 'Variants', key: 'variants', sortable: false },
  { title: 'Inventory', key: 'inventory', sortable: false },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' as const },
]

// Fetch products
const { data: productsData, isLoading, isRefetching, error, refetch } = useQuery({
  queryKey: ['shopify-products', props.platformId],
  queryFn: async () => {
    try {
      const response = await apiRequest('GET', `/api/platforms/${props.platformId}/shopify/products?limit=50`)
      console.log('API Response:', response)
      // The API returns {success: true, data: {...}, message: '...'}
      return response.data || response
    } catch (err: any) {
      console.error('Error fetching products:', err)
      throw err
    }
  },
})

// Helper function for inventory color
const getInventoryColor = (inventory: number) => {
  if (inventory === 0) return 'error'
  if (inventory < 10) return 'warning'
  return 'success'
}
</script>

<style lang="scss" scoped>
.app-header {
  border-bottom: 1px solid rgba(0, 200, 83, 0.1);

  :deep(.v-toolbar__content) {
    padding: 0 !important;
  }
}

.platform-logo {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 4px;
}

.stat-item {
  text-align: center;
  padding: 16px;
}

.product-placeholder {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--v-theme-surface-variant), 0.5);
  border-radius: 4px;
}
</style>
