<script lang="ts" setup>
import type { ToasterProps } from 'vue-sonner'

import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
  XIcon,
} from 'lucide-vue-next'
import { Toaster as Sonner } from 'vue-sonner'
import { cn } from '@/lib/utils'
import { computed } from 'vue'

const props = defineProps<ToasterProps>()
const forwardedProps = computed(() => {
  const {
    toastOptions: _toastOptions,
    expand: _expand,
    visibleToasts: _visibleToasts,
    gap: _gap,
    ...rest
  } = props
  return rest
})
const mergedToastOptions = computed(() => ({
  ...(props.toastOptions ?? {}),
  classes: {
    ...(props.toastOptions?.classes ?? {}),
    toast: cn('rounded-2xl', props.toastOptions?.classes?.toast),
  },
}))
</script>

<template>
  <Sonner
    :class="cn('toaster group', props.class)"
    :expand="props.expand ?? true"
    :visible-toasts="props.visibleToasts ?? 5"
    :gap="props.gap ?? 10"
    :style="{
      '--normal-bg': '#fffaf2',
      '--normal-text': '#2f241d',
      '--normal-border': '#bfa281',
      '--border-radius': 'var(--radius)',
    }"
    :toast-options="mergedToastOptions"
    v-bind="forwardedProps"
  >
    <template #success-icon>
      <CircleCheckIcon class="size-4" />
    </template>
    <template #info-icon>
      <InfoIcon class="size-4" />
    </template>
    <template #warning-icon>
      <TriangleAlertIcon class="size-4" />
    </template>
    <template #error-icon>
      <OctagonXIcon class="size-4" />
    </template>
    <template #loading-icon>
      <div>
        <Loader2Icon class="size-4 animate-spin" />
      </div>
    </template>
    <template #close-icon>
      <XIcon class="size-4" />
    </template>
  </Sonner>
</template>
