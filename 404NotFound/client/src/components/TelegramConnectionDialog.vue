<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="600">
    <v-card class="telegram-dialog">
      <v-card-title class="d-flex align-center ga-2 pb-4">
        <v-icon color="primary" size="28">mdi-telegram</v-icon>
        <span>Telegram Configuration</span>
      </v-card-title>

      <v-card-text>
        <div class="mb-6">
          <p class="text-body-2 text-medium-emphasis mb-4">
            Configure connection to Telegram Bot API to receive alert notifications from platforms.
          </p>
        </div>

        <v-form ref="formRef" @submit.prevent="handleSubmit">
          <!-- Bot Token (read-only, shown for reference) -->
          <v-text-field
            :model-value="botToken"
            label="Bot Token"
            readonly
            variant="outlined"
            density="comfortable"
            class="mb-4"
            prepend-inner-icon="mdi-key"
            hint="Bot token is fixed and configured in the system"
            persistent-hint
          />

          <!-- Chat ID (editable) -->
          <v-text-field
            v-model="chatId"
            label="Chat ID"
            variant="outlined"
            density="comfortable"
            class="mb-2"
            prepend-inner-icon="mdi-message-text"
            :rules="[rules.required, rules.chatId]"
            hint="Telegram conversation ID (e.g. -1003218510854)"
            persistent-hint
            placeholder="-1003218510854"
          />

          <v-alert
            type="info"
            variant="tonal"
            density="compact"
            class="mt-4 mb-2"
          >
            <div class="text-caption">
              <strong>How to get Chat ID?</strong>
              <ul class="mt-2 ml-4">
                <li>For group: Add bot to group and use @userinfobot or @RawDataBot</li>
                <li>For user: Send message to @userinfobot</li>
                <li>Group ID usually starts with "-100"</li>
              </ul>
            </div>
          </v-alert>
        </v-form>
      </v-card-text>

      <v-card-actions class="px-6 pb-4">
        <v-spacer />
        <v-btn
          variant="text"
          @click="$emit('update:modelValue', false)"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          :loading="isSaving"
          @click="handleSubmit"
        >
          <v-icon start>mdi-content-save</v-icon>
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, inject, watch } from 'vue'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { apiRequest } from '@/lib/queryClient'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const toast = inject('toast') as any
const queryClient = useQueryClient()

const formRef = ref()
const botToken = ref('8295463965:AAH***************************')
const chatId = ref('-1003218510854')
const isSaving = ref(false)

const rules = {
  required: (v: string) => !!v || 'This field is required',
  chatId: (v: string) => {
    if (!v) return true
    // Chat ID should be a number or start with - for groups/channels
    return /^-?\d+$/.test(v) || 'Chat ID must be a number (e.g. -1003218510854)'
  },
}

// Reset form when dialog opens
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    // Load current chat ID - in production this would come from backend API
    chatId.value = '-1003218510854'
  }
})

const saveTelegramConfigMutation = useMutation({
  mutationFn: async (data: { chatId: string }) => {
    return await apiRequest('POST', '/api/telegram/config', data)
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['telegram-status'] })
    emit('update:modelValue', false)
    toast({
      title: 'Success',
      description: 'Telegram configuration has been saved',
      variant: 'success',
    })
  },
  onError: () => {
    toast({
      title: 'Error',
      description: 'Failed to save configuration',
      variant: 'destructive',
    })
  },
})

const handleSubmit = async () => {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  isSaving.value = true
  saveTelegramConfigMutation.mutate({ chatId: chatId.value })
  isSaving.value = false
}
</script>

<style lang="scss" scoped>
.telegram-dialog {
  :deep(.v-card-title) {
    background: rgba(0, 200, 83, 0.05);
    border-bottom: 1px solid rgba(0, 200, 83, 0.1);
  }

  :deep(.v-text-field) {
    .v-field {
      border-radius: 8px;
    }
  }

  ul {
    list-style-type: disc;

    li {
      margin-bottom: 4px;
    }
  }
}
</style>
