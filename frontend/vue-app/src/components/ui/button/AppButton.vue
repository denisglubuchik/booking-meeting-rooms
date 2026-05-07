<template>
  <button :class="buttonClass" :type="type" :disabled="disabled">
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { cn } from "@/lib/utils";

type Variant = "outline" | "dark";

const props = withDefaults(
  defineProps<{
    type?: "button" | "submit" | "reset";
    variant?: Variant;
    disabled?: boolean;
  }>(),
  {
    type: "button",
    variant: "outline",
    disabled: false,
  }
);

const buttonClass = computed(() =>
  cn(
    "button",
    props.variant === "dark" && "button-dark",
    "disabled:cursor-not-allowed disabled:opacity-60"
  )
);
</script>
