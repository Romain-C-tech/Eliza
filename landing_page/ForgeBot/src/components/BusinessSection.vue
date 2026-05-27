<template>
    <section class="bg-gradient-to-t from-black via-forge-ember to-black p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mx-12 rounded-lg">
        <div
            v-for="stat in stats"
            :key="stat.title"
            class="bg-forge-steel rounded-lg p-6 border border-forge-steel"
        >
            <h1 class="text-4xl font-bold mb-4 font-title text-forge-spark">{{ stat.title }}</h1>
            <p class="text-forge-ash mb-6 font-sans">{{ stat.description }}</p>
            <ul class="space-y-3 text-forge-ash">
                <li v-for="point in stat.points" :key="point" class="flex items-start gap-3">
                    <span class="text-forge-ember mt-1">✓</span>
                    <span>{{ point }}</span>
                </li>
            </ul>
        </div>
    </section>
</template>

<script setup>
const stats = [
    {
        title: ' + 540 000 utilisateurs actifs',
        description: 'ForgeBot scale rapidement et s\'adapte à des communautés de toutes tailles.',
        points: [
            'Jusqu\'à 24 000 serveurs en 6 mois.',
            'Adoption rapide par les communautés Discord.',
        ],
    },
    {
        title: '+1000 serveurs / semaine',
        description: 'Une croissance rapide grâce à une forte visibilité et au bouche-à-oreille.',
        points: [
            'Promotion sur plateformes de bots Discord.',
            'Adoption dans les communautés gaming et pro.',
        ],
    },
    {
        title: '5.4M commandes / jour',
        description: 'Un engagement élevé grâce aux fonctionnalités interactives.',
        points: [
            '3 à 10 commandes par utilisateur / jour.',
            'Communautés plus actives et dynamiques.',
        ],
    },
    {
        title: '60% de rétention',
        description: 'ForgeBot devient un outil essentiel pour la gestion des serveurs.',
        points: [
            'Automatisation des tâches administratives.',
            'Réduction du travail des modérateurs.',
        ],
    },
    {
        title: '+282% ROI',
        description: 'Un potentiel de rentabilité élevé en cas de forte adoption.',
        points: [
            'Jusqu\'à 12 096€ générés en 6 mois.',
            'Monétisation via abonnement premium.',
        ],
    },
    {
        title: '~2 mois',
        description: 'Temps estimé pour atteindre la rentabilité dans un scénario de forte croissance.',
        points: [
            'Revenus mensuels estimés : ~2000€.',
            'ROI rapide grâce à une forte adoption.',
        ],
        },
]
</script>