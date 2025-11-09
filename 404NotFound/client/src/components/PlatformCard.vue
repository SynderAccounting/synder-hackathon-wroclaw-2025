<template>
  <v-card class="platform-card">
    <v-card-text class="pa-6">
      <div class="d-flex align-start ga-4">
        <div class="icon-wrapper">
          <img :src="platformLogo" :alt="name" class="platform-logo" />
        </div>

        <div class="flex-grow-1">
          <h3 class="text-h6 mb-2 font-weight-medium">{{ name }}</h3>
          <p class="text-body-2 text-medium-emphasis mb-2">{{ description }}</p>
          <v-btn
            color="primary"
            variant="tonal"
            @click="$emit('add')"
            :disabled="!available || (name !== 'Shopify' && name !== 'Square')"
          >
            <v-icon start>mdi-plus-circle</v-icon>
            Connect store
          </v-btn>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const { name, description, available = true } = defineProps<{
  name: string
  description: string
  available?: boolean
}>()

defineEmits<{
  add: []
}>()

const platformLogo = computed(() => {
  if (name === 'Shopify') return '/shopify.png'
  if (name === 'Square') return '/square.png'
  if (name === 'Amazon') return '/amazon.png'
  if (name === 'WooCommerce') return '/woo.webp'
  if (name === 'eBay') return '/ebay.png'
  return '/favicon.png'
})
</script>

<style lang="scss" scoped>
.platform-card {
  border: 1px solid rgba(var(--v-theme-primary), 0.15);
  background: rgba(var(--v-theme-surface), 0.5);
  backdrop-filter: blur(10px);
}

.platform-logo {
  width: 48px;
  height: 48px;
  object-fit: contain;
  border-radius: 4px;
}

.platform-unavailable {
  display: inline-block;
  margin-top: 6px;
  color: rgba(var(--v-theme-on-surface), 0.6);
  font-size: 0.85rem;
}
</style>