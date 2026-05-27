<template>
    <ul class="flex gap-1 overflow-x-auto">
      <li v-for="cmd in commands" :key="cmd.name">
        <router-link :to="cmd.path" v-slot="{ isExactActive }" custom>
          <button
            @click="$router.push(cmd.path)"
            class="px-4 py-3 font-title text-sm transition whitespace-nowrap border-b-2"
            :class="isExactActive
              ? 'border-forge-spark text-forge-spark'
              : 'border-transparent text-forge-ash hover:text-white hover:border-forge-ember'"
          >
            {{ cmd.name }}
          </button>
        </router-link>
      </li>
    </ul>
  </template>

<script setup>
const commands = [
  { name: 'Accueil', path: '/docs/commandes' },
  { name: 'Setup', path: '/docs/commandes/setup' },
  { name: 'Cancel', path: '/docs/commandes/cancel' },
]
</script>
