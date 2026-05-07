<template>
  <div class="panel">
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead v-for="column in columns" :key="column">{{ column }}</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <slot />
      </TableBody>
    </Table>
  </div>
</template>

<script setup lang="ts">
import { Table, TableBody, TableHead, TableHeader, TableRow } from "../ui/table";

defineProps<{
  columns: string[];
}>();
</script>
