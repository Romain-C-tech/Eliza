<template>
  <div class="h-fit bg-forge-steel text-white flex flex-col">
    <Navbar />
    <router-view ></router-view>
    <Business  />
    <Footer />
  </div>
</template>

<script setup>
import Navbar from './components/navbar.vue'
import Business from './components/BusinessSection.vue'
import Footer from './components/Footer.vue'
</script>