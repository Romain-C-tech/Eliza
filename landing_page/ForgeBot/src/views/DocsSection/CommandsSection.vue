<template>
  <section class="bg-gradient-to-t from-black via-forge-ember to-black rounded-lg p-6">
    <div class="bg-forge-steel rounded-lg p-6 border border-forge-steel">
      <h1 class="text-4xl font-bold mb-4 font-title text-forge-spark">Accueil</h1>
      <p class="text-forge-ash mb-6 font-sans">
        Bienvenue sur le guide des commandes de ForgeBot.
        Cette section regroupe les commandes et fonctionnalités.<br>
        Clique sur une commande pour en savoir plus sur son utilisation et ses options.
      </p>
      <ul class="space-y-4 text-forge-ash">
        <li 
          v-for="command in commands" 
          :key="command.name"
          class="bg-forge-ash bg-opacity-10 rounded-lg p-4"
        >
          <router-link :to="`/docs/commandes/${command.name.replace('/', '')}`">
            <h2 class="text-2xl font-sans text-forge-spark">{{ command.name }}</h2>  
            <p class="mt-2">{{ command.description }}</p>
          </router-link>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
const commands = [
  {
    name: '/help',
    description: 'Affiche toutes les commandes disponibles de ForgeBot.',
  },
  {
    name: '/setup',
    description: 'Lance le processus de création du server.',
  },
  {
    name: '/cancel',
    description: 'Annule le processus de création du server.',
  },
]
</script>