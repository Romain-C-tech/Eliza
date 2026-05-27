<template>
    <nav class="fixed top-0 bg-forge-black w-full max-h-24 shadow py-4 z-50 px-6 flex justify-between items-center">
        <div class="left flex items-center">
            <router-link to="/">
                <img src="/logo.png" alt="ForgeBot Logo" class="h-20 w-auto mx-auto">
            </router-link>
        </div>

        <div class="center flex gap-12 dark:text-gray-300 text-xl font-sans">
            <router-link to="/docs">
                <div class="text-xl font-title">Documentations</div>
            </router-link>
            <router-link to="/premium">
                <div class="text-xl font-title">Premium</div>
            </router-link>
        </div>

        <div class="right flex gap-4">
            <button class="bg-forge-spark hover:bg-forge-ember text-white px-6 py-3 rounded-3xl transition font-sans">Communauté</button>
            <a href="https://discord.com/oauth2/authorize?client_id=1493228941517783050" target="_blank" rel="noopener noreferrer">
                <button class="bg-forge-fire hover:bg-forge-ember text-white px-6 py-3 rounded-3xl transition font-sans">Ajouter à Discord</button>
            </a>
            
        </div>
    </nav>
</template>