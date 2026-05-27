<template>
    <ul class="flex gap-1 overflow-x-auto">
      <li v-for="link in links" :key="link.name">
        <router-link :to="link.path" v-slot="{ isExactActive }" custom>
          <button
            @click="$router.push(link.path)"
            class="px-4 py-3 font-title text-sm transition whitespace-nowrap border-b-2"
            :class="isExactActive
              ? 'border-forge-spark text-forge-spark'
              : 'border-transparent text-forge-ash hover:text-white hover:border-forge-ember'"
          >
            {{ link.name }}
          </button>
        </router-link>
      </li>
    </ul>
  </template>

<script setup>
const links = [
    { name: 'Accueil', path: '/docs' },
    { name: 'Installation', path: '/docs/installation' },
    { name: 'Commandes', path: '/docs/commandes' },
    { name: 'Fonctionnalités', path: '/docs/feature' },
]
</script>
