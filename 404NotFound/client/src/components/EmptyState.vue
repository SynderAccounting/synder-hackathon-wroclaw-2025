<template>
  <v-card class="empty-state text-center py-12">
    <v-card-text>
      <div class="icon-wrapper mx-auto mb-6">
        <v-icon size="64" color="primary" class="icon-animate">mdi-package-variant-closed</v-icon>
      </div>
      <p class="text-h6 text-medium-emphasis">{{ message }}</p>
      <p class="text-caption text-disabled mt-2">Connect your store to start monitoring it</p>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
defineProps<{
  message: string
}>()
</script>

<style lang="scss" scoped>
.empty-state {
  border: 2px dashed rgba(0, 200, 83, 0.2);
  background: rgba(var(--v-theme-surface-variant), 0.2);

  .icon-wrapper {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: rgba(0, 200, 83, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .icon-animate {
    animation: pulse 2s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 0.5;
    }
    50% {
      opacity: 1;
    }
  }
}
</style>
