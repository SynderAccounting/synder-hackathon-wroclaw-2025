<template>
  <v-container fluid class="pa-0 fill-height dashboard">
    <!-- Unified Header -->
    <v-app-bar class="app-header" elevation="1">
      <v-container class="d-flex align-center justify-space-between pa-0">
        <!-- Left: Logo, Title, and Navigation Buttons -->
        <div class="d-flex align-center ga-3">
          <v-icon size="32" color="primary">mdi-bell-ring</v-icon>
          <h1 class="text-h6 font-weight-medium">
            Backoffice Assistant
          </h1>

          <!-- Analytics Button -->
          <v-btn
            variant="tonal"
            color="primary"
            size="small"
            to="/analytics"
          >
            <v-icon start>mdi-chart-line</v-icon>
            Analytics
          </v-btn>

          <!-- Returns Button -->
          <v-btn
            variant="tonal"
            color="warning"
            size="small"
            to="/returns"
          >
            <v-icon start>mdi-package-variant-closed-remove</v-icon>
            Returns
          </v-btn>
        </div>

        <!-- Right: Actions and Status -->
        <div class="d-flex align-center ga-2">
          <!-- Telegram Status Badge -->
          <v-chip
            v-if="telegramStatus"
            :color="telegramStatus.connected ? 'success' : 'error'"
            variant="flat"
            size="small"
          >
            <v-icon start size="16">
              {{ telegramStatus.connected ? 'mdi-check-circle' : 'mdi-alert-circle' }}
            </v-icon>
            {{ telegramStatus.connected ? 'Connected' : 'Disconnected' }}
          </v-chip>

          <!-- Test Telegram Button -->
          <v-btn
            v-if="telegramStatus?.connected"
            variant="tonal"
            color="primary"
            size="small"
            :loading="testTelegramMutation.isPending.value"
            @click="testTelegramMutation.mutate()"
            data-testid="button-test-telegram"
          >
            <v-icon start>mdi-send</v-icon>
            Test Telegram
          </v-btn>

          <!-- Configure Telegram Button -->
          <v-btn
            variant="outlined"
            color="primary"
            size="small"
            @click="showTelegramDialog = true"
          >
            <v-icon start>mdi-cog</v-icon>
            Configure
          </v-btn>

          <!-- Theme Toggle -->
          <v-btn
            :icon="theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
            variant="text"
            size="small"
            @click="toggleTheme"
            aria-label="Toggle theme"
          />
        </div>
      </v-container>
    </v-app-bar>

    <!-- Main Content -->
    <v-main>
      <v-container class="py-8">
        <!-- Available Platforms Section -->
        <section class="mb-12">
          <div class="d-flex align-center ga-2 mb-6">
            <v-icon color="primary">mdi-storefront</v-icon>
            <h2 class="text-h6 font-weight-medium">Available Platforms</h2>
          </div>

          <v-slide-group show-arrows class="platform-carousel">
            <v-slide-item
              v-for="platform in availablePlatforms"
              :key="platform.name"
              class="carousel-item"
            >
              <platform-card
                :name="platform.name"
                :description="platform.description"
                :available="platform.available"
                @add="() => handleAddPlatform(platform.name)"
              />
            </v-slide-item>
          </v-slide-group>
        </section>

        <!-- Connected Platforms Section -->
        <section class="mb-12">
          <div class="d-flex align-center ga-2 mb-6">
            <v-icon color="primary">mdi-link-variant</v-icon>
            <h2 class="text-h6 font-weight-medium">Connected Platforms</h2>
          </div>

          <v-progress-circular
            v-if="isLoading"
            indeterminate
            color="primary"
            class="d-block mx-auto"
          />

          <empty-state
            v-else-if="!platforms || platforms.length === 0"
            message="No platforms added yet"
          />

          <v-row v-else-if="platforms">
            <v-col
              v-for="platform in platforms"
              :key="platform.id"
              cols="12"
            >
              <connected-platform-panel
                :id="platform.id"
                :type="platform.type as any"
                :name="platform.name"
                :settings="platform.settings"
                @update-settings="(settings: PlatformSettings) => updateSettingsMutation.mutate({ id: platform.id, settings })"
                @delete="deletePlatformMutation.mutate(platform.id)"
                @generate-summary="generateSummaryMutation.mutate(platform.id)"
              />
            </v-col>
          </v-row>
        </section>

        <!-- Run Check Button -->
        <section v-if="platforms && platforms.length > 0">
          <div class="d-flex flex-column align-center ga-4 py-8">
            <v-btn
              size="large"
              color="primary"
              :loading="runCheckMutation.isPending.value"
              @click="runCheckMutation.mutate()"
              data-testid="button-run-check"
              class="px-8"
            >
              <v-icon start>mdi-play-circle</v-icon>
              {{ runCheckMutation.isPending.value ? 'Checking...' : 'Run Check' }}
            </v-btn>
            <p class="text-caption text-medium-emphasis">
              Manually trigger alert checks for all platforms
            </p>
          </div>
        </section>
      </v-container>
    </v-main>

    <!-- Add Platform Dialog -->
    <add-platform-dialog
      v-model="isDialogOpen"
      :platform-type="selectedPlatformType as any"
      @add-platform="handleSubmitPlatform"
    />

    <!-- Telegram Connection Dialog -->
    <telegram-connection-dialog
      v-model="showTelegramDialog"
    />
  </v-container>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import type { PlatformSettings, PlatformPublic } from '@shared/schema'
import { apiRequest } from '@/lib/queryClient'
import PlatformCard from '@/components/PlatformCard.vue'
import AddPlatformDialog from '@/components/AddPlatformDialog.vue'
import ConnectedPlatformPanel from '@/components/ConnectedPlatformPanel.vue'
import EmptyState from '@/components/EmptyState.vue'
import TelegramConnectionDialog from '@/components/TelegramConnectionDialog.vue'

const toast = inject('toast') as any
const toggleTheme = inject('toggleTheme') as () => void
const theme = inject('theme') as any

const queryClient = useQueryClient()

const isDialogOpen = ref(false)
const selectedPlatformType = ref('')
const showTelegramDialog = ref(false)

// Available platforms (includes coming-soon items)
const availablePlatforms = [
  {
    name: 'Shopify',
    description: 'Monitor inventory levels and chargebacks in Shopify stores',
    available: true,
  },
  {
    name: 'Square',
    description: 'Monitor orders, returns and inventory levels on Square',
    available: true,
  },
  {
    name: 'Amazon',
    description: 'Marketplace integration for Amazon stores',
    available: false,
  },
  {
    name: 'WooCommerce',
    description: 'Monitor WooCommerce stores (self-hosted)',
    available: false,
  },
  {
    name: 'eBay',
    description: 'Marketplace integration for eBay stores',
    available: false,
  },
]

// Queries
const { data: platforms = [], isLoading } = useQuery<PlatformPublic[]>({
  queryKey: ['platforms'],
  queryFn: () => apiRequest('GET', '/api/platforms'),
})

const { data: telegramStatus } = useQuery<{ connected: boolean }>({
  queryKey: ['telegram-status'],
  queryFn: () => apiRequest('GET', '/api/telegram/status'),
})

// Mutations
const addPlatformMutation = useMutation({
  mutationFn: async (data: { type: string; name: string; credentials: any }) => {
    console.log('Sending platform data:', data)
    return await apiRequest('POST', '/api/platforms', data)
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['platforms'] })
    isDialogOpen.value = false
    toast({
      title: 'Success',
      description: 'Platform added successfully',
      variant: 'success',
    })
  },
  onError: (error: any) => {
    console.error('Failed to add platform:', error)
    toast({
      title: 'Error',
      description: error.message || 'Failed to add platform',
      variant: 'destructive',
    })
  },
})

const updateSettingsMutation = useMutation({
  mutationFn: async ({ id, settings }: { id: string; settings: PlatformSettings }) => {
    return await apiRequest('POST', `/api/platforms/${id}/settings`, settings)
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['platforms'] })
    toast({
      title: 'Success',
      description: 'Settings updated successfully',
      variant: 'success',
    })
  },
})

const deletePlatformMutation = useMutation({
  mutationFn: async (id: string) => {
    return await apiRequest('DELETE', `/api/platforms/${id}`)
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['platforms'] })
    toast({
      title: 'Success',
      description: 'Platform removed',
      variant: 'success',
    })
  },
})

const runCheckMutation = useMutation({
  mutationFn: async () => {
    return await apiRequest('POST', '/api/check/run')
  },
  onSuccess: () => {
    toast({
      title: 'Check started',
      description: 'Alerts will appear on Telegram',
      variant: 'success',
    })
  },
  onError: () => {
    toast({
      title: 'Error',
      description: 'Failed to run check',
      variant: 'destructive',
    })
  },
})

const testTelegramMutation = useMutation({
  mutationFn: async () => {
    return await apiRequest('POST', '/api/test/telegram')
  },
  onSuccess: () => {
    toast({
      title: 'Message sent',
      description: 'Check your Telegram inbox',
      variant: 'success',
    })
  },
  onError: () => {
    toast({
      title: 'Error',
      description: 'Failed to send test message',
      variant: 'destructive',
    })
  },
})

const generateSummaryMutation = useMutation({
  mutationFn: async (platformId: string) => {
    return await apiRequest('POST', `/api/generate-summary/${platformId}`)
  },
  onSuccess: (data: any) => {
    toast({
      title: 'Success',
      description: 'AI summary generated and sent to Telegram',
      variant: 'success',
    })
  },
  onError: (error: any) => {
    toast({
      title: 'AI Error',
      description: `Failed to generate summary: ${error.message}`,
      variant: 'destructive',
    })
  },
})

// Methods
const handleAddPlatform = (platformType: string) => {
  selectedPlatformType.value = platformType
  isDialogOpen.value = true
}

const handleSubmitPlatform = (data: {
  type: string
  name: string
  credentials: any
}) => {
  console.log('Platform data received from dialog:', data)
  addPlatformMutation.mutate({
    type: data.type,
    name: data.name,
    credentials: data.credentials,
  })
}
</script>

<style lang="scss" scoped>
.dashboard {
  background: linear-gradient(to bottom, rgba(0, 200, 83, 0.03), transparent 300px);
}

.app-header {
  border-bottom: 1px solid rgba(0, 200, 83, 0.1);
  
  :deep(.v-toolbar__content) {
    padding: 0 !important;
  }
}

section {
  h2 {
    color: rgb(var(--v-theme-on-surface));
    letter-spacing: 0.5px;
  }
}

.platform-carousel {
   overflow: hidden;
   --gap: 24px;
}

.platform-carousel ::v-deep .v-slide-group__content,
.platform-carousel ::v-deep .v-slide-group__items {
  /* Use deep selector so scoped styles apply to Vuetify internal elements */
  display: flex;
  gap: var(--gap);
  align-items: stretch;
}

.platform-carousel .carousel-item {
  /* Show three cards at once. Subtract total gaps (2 gaps between 3 items) before dividing */
  flex: 0 0 calc((100% - (var(--gap) * 2)) / 4);
  max-width: calc((100% - (var(--gap) * 2)) / 4);
  box-sizing: border-box;
}

@media (max-width: 1100px) {
  /* Medium screens: show two cards */
  .platform-carousel .carousel-item {
    flex: 0 0 calc((100% - var(--gap)) / 2);
    max-width: calc((100% - var(--gap)) / 2);
  }
}

@media (max-width: 800px) {
  /* Mobile: show one card at a time */
  .platform-carousel .carousel-item {
    flex: 0 0 100%;
    max-width: 100%;
  }
}
</style>
