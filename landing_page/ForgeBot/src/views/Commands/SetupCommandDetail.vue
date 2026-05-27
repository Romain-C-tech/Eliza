<template>
    <section class="bg-gradient-to-t from-black via-forge-ember to-black rounded-lg p-6">
        <div class="bg-forge-steel rounded-lg p-6 border border-forge-steel">
            <span class="inline-flex items-center gap-1.5 bg-forge-ember/20 text-forge-ember text-xs font-medium px-3 py-1 rounded-md mb-4">
                Commande
            </span>
            <h1 class="text-4xl font-bold mb-4 font-title text-forge-spark">Setup</h1>
            <p class="text-forge-ash mb-6 font-sans">
                Commencer la création de votre propre serveur discord avec la commande /setup .<br>
                Cette commande vous guidera à travers les étapes nécessaires pour configurer votre serveur et le personnaliser selon vos besoins. <br>
                Tout est otpimisé pour que les membres et les modérateurs aient une expérience optimale avec ForgeBot.
            </p>
            <p class="text-lg font-medium text-forge-ash uppercase tracking-widest mb-3">Ce que vous pouvez configurer</p>

            <div class="space-y-3 mb-6">
                <div class="flex items-start gap-3 bg-forge-coal/50 rounded-lg p-3">
                    <div class="w-8 h-8 rounded-lg bg-forge-ember/20 flex items-center justify-center shrink-0 text-forge-ember">🎯</div>
                    <div>
                        <p class="font-medium text-white text-sm">Type du serveur</p>
                        <p class="text-forge-ash text-sm">Choisissez le type de serveur que vous voulez créer (gaming, école, communataire, professionnel).</p>
                    </div>
                </div>
                <div class="flex items-start gap-3 bg-forge-coal/50 rounded-lg p-3">
                    <div class="w-8 h-8 rounded-lg bg-forge-ember/20 flex items-center justify-center shrink-0 text-forge-ember">💬</div>
                    <div>
                        <p class="font-medium text-white text-sm">Salons</p>
                        <p class="text-forge-ash text-sm">Choisissez les salons à faire apparaître sur votre serveur.</p>
                    </div>
                </div>
                <div class="flex items-start gap-3 bg-forge-coal/50 rounded-lg p-3">
                    <div class="w-8 h-8 rounded-lg bg-forge-ember/20 flex items-center justify-center shrink-0 text-forge-ember">⚙️</div>
                    <div>
                        <p class="font-medium text-white text-sm">Taille du serveur</p>
                        <p class="text-forge-ash text-sm">Adaptez la configuration selon le nombre de membres attendus.</p>
                    </div>
                </div>
            </div>

            <p class="text-lg font-medium text-forge-ash uppercase tracking-widest mb-3">Les modes de création</p>

            <div class="space-y-3">
                <div class="flex items-start gap-3 bg-forge-coal/50 rounded-lg p-3">
                    <div class="w-8 h-8 rounded-lg bg-forge-ember/20 flex items-center justify-center shrink-0 text-forge-ember">🏭</div>
                    <div>
                        <p class="font-medium text-white text-sm">Automatique</p>
                        <p class="text-forge-ash text-sm">ForgeBot s'occupe de tout ! Finis les congiguration longue et fatiguante !</p>
                    </div>
                </div>
                <div class="flex items-start gap-3 bg-forge-coal/50 rounded-lg p-3">
                    <div class="w-8 h-8 rounded-lg bg-forge-ember/20 flex items-center justify-center shrink-0 text-forge-ember">🤚</div>
                    <div>
                        <p class="font-medium text-white text-sm">Manuel</p>
                        <p class="text-forge-ash text-sm">ForgeBot vous propose une structure de serveur coincidant avec ce que vous avez demandé.</p>
                    </div>
                </div>
            </div>
            <div class="my-6 font-sans inline-block text-xl border-4 border-forge-fire/50 text-forge-ash rounded-lg p-3">
                Attention ! Si vous choisissez le mode automatique ForgeBot devra accèder au configuration de votre serveur !
            </div>
            
            <p class="text-xl text-center font-medium text-forge-ash uppercase tracking-widest mb-3">Guide step by step</p>

            <p class="text-forge-ash mt-6 font-sans text-center">
                Nous avons préparé un guide détaillé pour vous accompagner à chaque étape du processus de création de votre serveur avec la commande /setup. <br>
                Que vous soyez un novice ou un utilisateur expérimenté, ce guide vous fournira toutes les informations nécessaires pour tirer le meilleur parti de ForgeBot et créer un serveur qui correspond parfaitement à vos besoins.
            </p>
            <div>
                <ul class="text-center mt-6 bg-forge-coal/50 rounded-lg p-3">
                    <li v-for="step in steps" :key="step" class="p-3 my-3">
                        <h2 class="text-2xl text-forge-ash font-title">{{ step.title }}</h2>
                        <div class="h-1 w-16 bg-forge-ember rounded-full mx-auto my-4"></div>
                        <p class="text-lg text-forge-ash mt-2 font-sans">{{ step.description }}</p>
                        <img :src="step.img" alt="Image de l'étape" class="mx-auto mt-4">
                        <div class="text-lg text-forge-ash mt-2 font-sans">
                            Voici à quoi ressemble la réponse de ForgeBot à cette étape :
                            <img :src="step.img_response" alt="Image de la réponse de ForgeBot" class="m-auto">
                        </div>
                    </li>
                </ul>
            </div>

        </div>
    </section>
</template>


<script setup>
const steps = [
    {
        title:'Étape 1 : Lancement de la commande /setup',
        description: 'Apprenez à choisir le type de serveur qui correspond le mieux à vos besoins, que ce soit pour le gaming, l’école, la communauté ou un usage professionnel.',
        img: '/Step1.png',
        img_response: '/Response1.png'
    },
    {
        title:'Étape 2 : Choix du type de serveur',
        description: 'Apprenez à choisir le type de serveur qui correspond le mieux à vos besoins, que ce soit pour le gaming, l’école, la communauté ou un usage professionnel.',
        img: '/Step2.png',
        img_response: '/Response2.png'
    },
    {
        title:'Étape 3 : Configuration des salons et des rôles',
        description: 'Découvrez comment configurer les salons et les rôles de votre serveur pour une organisation optimale et une expérience utilisateur fluide.',
        img: '/Step3.png',
        img_response: '/Response3.png'
    },
    {
        title:'Étape 4 : Personnalisation des paramètres du serveur',
        description: 'Apprenez à personnaliser les paramètres de votre serveur pour qu’il corresponde parfaitement à votre vision et aux besoins de votre communauté.',
        img: '/Step4.png',
        img_response: '/Response4.png'
    },
    {
        title:'Étape 5 : Finalisation et lancement du serveur',
        description: 'Découvrez les dernières étapes pour finaliser la configuration de votre serveur et le lancer avec ForgeBot, prêt à accueillir vos membres et à offrir une expérience exceptionnelle.',
        img: '/Step5.png',
        img_response: '/Response5.png'
    }
]
</script>