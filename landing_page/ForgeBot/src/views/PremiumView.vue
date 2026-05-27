<template>
    <section class="bg-forge-steel text-white flex flex-col items-center pt-20 ">
        <header class="bg-gradient-to-br from-black via-zinc-800 to-orange-600 w-[65vw] h-fit rounded-lg m-12 p-6 border-t-4 border-forge-spark">
            <div class="flex items-center justify-center gap-4 mb-6">
                <span class="text-forge-ember text-2xl">🔥</span>
                <h1 class="text-4xl font-bold font-title text-forge-spark">Passez au Premium !</h1>
                <span class="text-forge-ember text-2xl">🔥</span>
            </div>
            <div class="mt-6 flex flex-col md:flex-row gap-6">
                <div
                    v-for="(premium, name) in premiums"
                    :key="name"
                    class="rounded-lg p-6  border-y-forge-ash flex-1 flex flex-col"
                    :class="premium.color + ' ' + premium.borderside"
                >
                    <h3 class="text-2xl font-bold mb-4 font-title">{{ name }}</h3>
                    <div class="w-[30%] h-1 bg-forge-spark mb-4"></div>
                    <p class="text-forge-ash mb-6 font-sans">{{ premium.price }}</p>
                    <ul class="space-y-3 text-forge-ash mb-6">
                        <li v-for="feature in premium.features" :key="feature" class="flex items-start gap-3 py-1">
                            <span class="text-forge-spark mt-1">✓</span>
                            <span>{{ feature }}</span>
                        </li>
                    </ul>
                    <button
                        class="mt-auto w-full py-2 rounded-lg  font-bold text-white hover:shadow-lg"
                        :class="premium.buttonColor + ' ' + premium.buttonanimation"
                    >
                        {{  name === 'Gratuit' ? 'Par défaut' : 'Passer au Premium' }}
                    </button>
                </div>
            </div>
        </header>

    </section>
</template>

<script setup>
const premiums = {
    'Gratuit': {
        price: '0€',
        color: 'bg-forge-black',
        buttonColor: 'bg-gradient-to-br from-forge-spark to-forge-fire cursor-not-allowed',
        borderside: 'border-l-4 border-forge-spark',
        buttonanimation: 'animate-none',
        features: [
            'Accès aux commandes de base',
            'Personnalisation limitée du bot',
            'Support communautaire',
        ],
    },
    'Premium': {
        price: '3.49€ / mois',
        color: 'bg-gradient-to-b from-orange-400 to-orange-600',
        buttonColor: 'bg-gradient-to-br from-forge-spark to-forge-fire hover:bg-forge-grey-800',
        borderside: 'border-r-4 border-forge-spark',
        buttonanimation: 'animate-bounce',
        features: [
            'Accès à des commandes exclusives',
            'Personnalisation avancée du bot',
            'Support prioritaire',
            'Statistiques détaillées sur votre serveur',
        ],
    }
} 
</script>