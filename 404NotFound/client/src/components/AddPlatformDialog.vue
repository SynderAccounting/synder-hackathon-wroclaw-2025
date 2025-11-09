<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="600"
  >
    <v-card class="add-platform-dialog">
      <v-card-title class="d-flex align-center ga-2 pb-4">
        <img :src="platformLogo" :alt="platformType" class="dialog-logo" />
        <span>Add {{ platformType }}</span>
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-6">
        <v-form ref="formRef" @submit.prevent="handleSubmit">
          <v-text-field
            v-model="form.name"
            label="Store Name"
            :placeholder="platformPlaceholder.name"
            :hint="platformPlaceholder.hint"
            persistent-hint
            :rules="[(v: string) => !!v || 'Required field']"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-store"
            class="mb-4"
          />

          <!-- Shopify Fields -->
          <template v-if="platformType === 'Shopify'">
            <v-text-field
              v-model="form.apiKey"
              label="Admin API Access Token"
              placeholder="shpat_..."
              type="password"
              :rules="[(v: string) => !!v || 'Required field']"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-key"
              class="mb-4"
            />

            <v-text-field
              v-model="form.apiVersion"
              label="API Version"
              placeholder="2024-04"
              :rules="[(v: string) => !!v || 'Required field']"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-git"
            />
          </template>

          <!-- Square Fields -->
          <template v-if="platformType === 'Square'">
            <v-select
              v-model="form.environment"
              label="Environment"
              :items="['sandbox', 'production']"
              :rules="[(v: string) => !!v || 'Required field']"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-earth"
              class="mb-4"
            />

            <v-text-field
              v-model="form.accessToken"
              label="Access Token"
              placeholder="EAAA..."
              type="password"
              :rules="[(v: string) => !!v || 'Required field']"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-key"
              class="mb-4"
            />

            <v-text-field
              v-model="form.applicationId"
              label="Application ID"
              placeholder="sq0idp-..."
              :rules="[(v: string) => !!v || 'Required field']"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-application"
              class="mb-4"
            />

            <v-text-field
              v-model="form.locationId"
              label="Location ID (Optional)"
              placeholder="L..."
              hint="Square location identifier (if you have multiple)"
              persistent-hint
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-map-marker"
            />
          </template>

          <v-divider class="my-4" />

          <v-card-actions class="pa-0">
            <v-spacer />
            <v-btn
              variant="text"
              @click="$emit('update:modelValue', false)"
            >
              Cancel
            </v-btn>
            <v-btn
              color="primary"
              variant="elevated"
              type="submit"
              :loading="isSubmitting"
            >
              Save Connection
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { VForm } from 'vuetify/components'

type PlatformType = 'Shopify' | 'Square'

const props = defineProps<{
  modelValue: boolean
  platformType: PlatformType
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'add-platform', data: { 
    type: PlatformType; 
    name: string; 
    credentials: {
      api_key?: string;
      api_version?: string;
      environment?: string;
      access_token?: string;
      application_id?: string;
      location_id?: string;
    } 
  }): void
}>()

const formRef = ref<VForm | null>(null)
const isSubmitting = ref(false)
const form = ref({
  name: '',
  apiKey: '',
  apiVersion: '2024-04',
  locationId: '',
  environment: 'sandbox',
  accessToken: '',
  applicationId: '',
})

const platformLogo = computed(() => {
  switch (props.platformType) {
    case 'Shopify':
      return '/public/shopify.png'
    case 'Square':
      return '/public/square.png'
    default:
      return ''
  }
})

const platformPlaceholder = computed(() => {
  switch (props.platformType) {
    case 'Shopify':
      return {
        name: 'e.g. my-shopify-store',
        hint: 'Your store name (without .myshopify.com)',
      }
    case 'Square':
      return {
        name: 'e.g. my-square-business',
        hint: 'Your Square business name',
      }
    default:
      return {
        name: 'e.g. my-store',
        hint: 'Platform name',
      }
  }
})

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    isSubmitting.value = false
    form.value = {
      name: '',
      apiKey: '',
      apiVersion: '2024-04',
      locationId: '',
      environment: 'sandbox',
      accessToken: '',
      applicationId: '',
    }
    formRef.value?.resetValidation()
  }
})

const handleSubmit = async () => {
  if (!formRef.value) return
  const { valid } = await formRef.value.validate()
  if (!valid) return

  isSubmitting.value = true

  const credentials: any = {}

  if (props.platformType === 'Shopify') {
    credentials.api_key = form.value.apiKey
    credentials.api_version = form.value.apiVersion
  } else if (props.platformType === 'Square') {
    credentials.environment = form.value.environment
    credentials.access_token = form.value.accessToken
    credentials.application_id = form.value.applicationId
    if (form.value.locationId) {
      credentials.location_id = form.value.locationId
    }
  }

  const platformData = {
    type: props.platformType,
    name: form.value.name,
    credentials,
  }

  console.log('Submitting platform data:', platformData)

  emit('add-platform', platformData)

  isSubmitting.value = false
}
</script>

<style lang="scss" scoped>
.dialog-logo {
  width: 28px;
  height: 28px;
  object-fit: contain;
}
</style>