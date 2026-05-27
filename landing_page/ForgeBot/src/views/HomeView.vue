<template>
    <div class="flex bg-gradient-to-t from-forge-steel to-forge-fire pt-24 h-screen items-center">
        
        <div class="w-1/2 flex items-center justify-center">
            <div class="bg-forge-black bg-opacity-80 backdrop-blur-md rounded-lg shadow-lg max-w-md text-center p-12">
                <img src="/logo.png" alt="ForgeBot Logo" class="h-24 w-auto mx-auto mb-12">
                <p class="text-lg text-gray-200 mb-12">Le bot ultime pour créer et booster votre serveur Discord avec des fonctionnalités avancées et une communauté active !</p>
                <a href="https://discord.com/oauth2/authorize?client_id=1493228941517783050" target="_blank" rel="noopener noreferrer">
                    <button class="bg-forge-fire hover:bg-forge-ember text-white font-bold py-3 px-6 rounded-3xl transition duration-300">Ajouter à Discord</button>
                </a>
            </div>
        </div>

        <div class="w-1/2 h-full flex items-start justify-center">
            <DotLottieVue
                style="width: auto; height: 100vh;"
                autoplay
                loop
                src="https://lottie.host/47871d7d-4ad4-4f5a-a517-9a50d0e32be4/WkiSSj1qij.lottie"
            />
        </div>
    </div>
</template>

<script setup>
import { DotLottieVue } from '@lottiefiles/dotlottie-vue'
</script>