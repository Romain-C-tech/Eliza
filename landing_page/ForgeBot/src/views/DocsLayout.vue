<template>
  <div class="h-fit bg-gradient-to-br from-forge-coal to-forge-steel text-white flex flex-col" style="padding-top: 96px;">
    <header class="border-b border-forge-steel text-center py-8 flex-shrink-0">
      <div class="max-w-6xl mx-auto px-4">
        <h1 class="text-4xl font-bold mb-2 font-title text-forge-spark">La Documentation de ForgeBot</h1>
        <p class="text-forge-ash font-sans">Guide complet pour utiliser ForgeBot sur ton propre serveur Discord</p>
      </div>
    </header>
    <nav class="mb-2 border-b border-forge-steel bg-forge-black/50">
      <div class="mx-auto px-4 justify-center flex">
        <DocsSidebar />
      </div>
    </nav>

    <nav v-if="$route.path.startsWith('/docs/commandes')" class="border-b border-forge-steel bg-forge-black/50">
      <div class="mx-auto px-4 justify-center flex">
        <CommandsSidebar />
      </div>
    </nav>  

    <div class="mx-auto px-12 py-8 flex-1 overflow-hidden w-full">
      <main class="overflow-y-auto">
    <router-view />
  </main>
</div>
  </div>
</template>

<script>
import DocsSidebar from '../components/DocsSidebar.vue'
import CommandsSidebar from '../components/CommandsSidebar.vue'

export default {
  name: 'DocsLayout',
  components: {
    DocsSidebar,
    CommandsSidebar,
  },
}
</script>