<template>
  <main>
    <FoodScanner />
  </main>
</template>

<script setup>
import FoodScanner from './components/FoodScanner.vue';
</script>

<style>
/* CSS global dasar untuk memastikan background penuh */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  background-color: #f8fafc; /* Warna background abu-abu terang */
}

main {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}
</style>