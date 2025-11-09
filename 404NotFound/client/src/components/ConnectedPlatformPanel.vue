<template>
  <v-card class="platform-panel">
    <v-expansion-panels>
      <v-expansion-panel>
        <v-expansion-panel-title>
          <div class="d-flex align-center ga-3">
            <img :src="platformLogo" :alt="type" class="panel-logo" />
            <div>
              <div class="font-weight-medium">{{ name }}</div>
              <div class="text-caption text-medium-emphasis">{{ type }}</div>
            </div>
          </div>
        </v-expansion-panel-title>

        <v-expansion-panel-text>
          <v-divider class="mb-6" />

          <v-form>
            <div class="text-overline text-primary mb-4">
              <v-icon size="18" class="mr-1">mdi-bell-cog</v-icon>
              Notification Settings
            </div>

            <div class="setting-item mb-6">
              <div class="d-flex align-center justify-space-between mb-4">
                <div class="d-flex align-center ga-2">
                  <v-icon color="warning">mdi-package-variant</v-icon>
                  <div>
                    <div class="font-weight-medium">Low Stock Monitoring</div>
                    <div class="text-caption text-medium-emphasis">
                      Get notified when product reaches low stock level
                    </div>
                  </div>
                </div>
                <v-switch
                  v-model="localSettings.low_stock_enabled"
                  color="primary"
                  density="compact"
                  inset
                  hide-details
                />
              </div>
              <v-slider
                v-model="localSettings.low_stock_threshold"
                :disabled="!localSettings.low_stock_enabled"
                label="Threshold"
                :thumb-label="true"
                min="1"
                max="100"
                step="1"
                color="primary"
                class="ml-2"
                density="compact"
              />
            </div>
            
            <div class="setting-item mb-6">
              <div class="d-flex align-center justify-space-between mb-4">
                <div class="d-flex align-center ga-2">
                  <v-icon color="error">mdi-credit-card-refund-outline</v-icon>
                  <div>
                    <div class="font-weight-medium">Chargeback Alerts</div>
                    <div class="text-caption text-medium-emphasis">
                      Get instant alerts about new disputes
                    </div>
                  </div>
                </div>
                <v-switch
                  v-model="localSettings.chargeback_enabled"
                  color="primary"
                  density="compact"
                  inset
                  hide-details
                />
              </div>
            </div>

            <v-divider class="my-4" />

            <div class="text-overline text-primary mb-4">
              <v-icon size="18" class="mr-1">mdi-robot-outline</v-icon>
              AI Actions (Groq)
            </div>

            <div class="setting-item mb-6">
              <div class="d-flex align-center justify-space-between">
                <div>
                  <div class="font-weight-medium">Daily Sales Summary</div>
                  <div class="text-caption text-medium-emphasis">
                    Generate AI summary of last 24h sales and send to Telegram
                  </div>
                </div>
                <v-btn
                  color="secondary"
                  variant="outlined"
                  :loading="isGeneratingSummary"
                  @click="handleGenerateSummary"
                  v-if="type === 'Shopify'"
                  size="small"
                >
                  <v-icon start>mdi-send</v-icon>
                  Send Now
                </v-btn>
              </div>
            </div>

            <v-divider class="my-4" />
            <v-card-actions class="pa-0">
              <v-btn
                variant="text"
                color="error"
                @click="showDeleteDialog = true"
              >
                Delete
              </v-btn>
              <v-spacer />
              <v-btn
                v-if="type === 'Shopify'"
                variant="outlined"
                color="primary"
                @click="handleViewProducts"
                class="mr-2"
              >
                <v-icon start>mdi-package-variant</v-icon>
                View Products
              </v-btn>
              <v-btn
                color="primary"
                variant="elevated"
                @click="handleUpdate"
              >
                Save Changes
              </v-btn>
            </v-card-actions>
          </v-form>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>

    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h5">Confirm Deletion</v-card-title>
        <v-card-text>
          Are you sure you want to delete platform "{{ name }}"? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="handleDelete">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from 'vue'
import { useRouter } from 'vue-router'

type PlatformType = 'Shopify' | 'Square'

const props = defineProps<{
  id: string
  type: PlatformType
  name: string
  settings: any
}>()

const emit = defineEmits<{
  (e: 'update-settings', settings: any): void
  (e: 'delete'): void
  (e: 'generate-summary'): void
}>()

const router = useRouter()

const showDeleteDialog = ref(false)
const isGeneratingSummary = ref(false)

const localSettings = reactive({
  low_stock_enabled: true,
  low_stock_threshold: 10,
  chargeback_enabled: true,
  ...props.settings
})

watch(() => props.settings, (newSettings) => {
  Object.assign(localSettings, newSettings)
}, { deep: true })

const platformLogo = computed(() => {
  if (props.type === 'Shopify') return '/shopify.png'
  if (props.type === 'Square') return '/square.png'
  return '';
})

const handleUpdate = () => {
  emit('update-settings', { ...localSettings })
}

const handleDelete = () => {
  showDeleteDialog.value = false
  emit('delete')
}

const handleViewProducts = () => {
  router.push({
    name: 'ShopifyProducts',
    params: { platformId: props.id }
  })
}

const handleGenerateSummary = async () => {
  isGeneratingSummary.value = true
  emit('generate-summary')

  // Simulate delay to give backend time to process
  await new Promise(resolve => setTimeout(resolve, 500))
  isGeneratingSummary.value = false
}
</script>

<style lang="scss" scoped>
.platform-panel {
  border: 1px solid rgba(var(--v-theme-primary), 0.1);
  background: rgba(var(--v-theme-surface), 1);

  :deep(.v-expansion-panel-title) {
    &:hover {
      background: rgba(var(--v-theme-primary), 0.05);
    }
  }
}

.panel-logo {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 4px;
}

.setting-item {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
  padding: 16px;
  background: rgba(var(--v-theme-surface-variant), 0.3);
}
</style>