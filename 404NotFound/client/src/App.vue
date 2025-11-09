<template>
  <v-app>
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="top right"
    >
      <div class="d-flex align-center">
        <v-icon class="mr-2">{{ snackbar.icon }}</v-icon>
        <div>
          <div class="font-weight-bold">{{ snackbar.title }}</div>
          <div class="text-caption">{{ snackbar.description }}</div>
        </div>
      </div>
    </v-snackbar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, provide } from 'vue'
import { useTheme } from 'vuetify'

const theme = useTheme()

const toggleTheme = () => {
  theme.global.name.value = theme.global.current.value.dark ? 'lightTheme' : 'darkTheme'
}

interface SnackbarState {
  show: boolean
  title: string
  description: string
  color: string
  icon: string
}

const snackbar = ref<SnackbarState>({
  show: false,
  title: '',
  description: '',
  color: 'success',
  icon: 'mdi-check-circle',
})

const showToast = (options: {
  title: string
  description: string
  variant?: 'success' | 'destructive' | 'default'
}) => {
  const colorMap = {
    success: 'success',
    destructive: 'error',
    default: 'info',
  }

  const iconMap = {
    success: 'mdi-check-circle',
    destructive: 'mdi-alert-circle',
    default: 'mdi-information',
  }

  const variant = options.variant || 'default'

  snackbar.value = {
    show: true,
    title: options.title,
    description: options.description,
    color: colorMap[variant],
    icon: iconMap[variant],
  }
}

provide('toast', showToast)
provide('toggleTheme', toggleTheme)
provide('theme', theme)
</script>

<style scoped>
.v-main {
  background-color: rgb(var(--v-theme-background));
}
</style>