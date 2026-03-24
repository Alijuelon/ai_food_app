<template>
  <main class="app-wrapper">
    <FoodScanner />
  </main>
</template>

<script setup>
import FoodScanner from './components/FoodScanner.vue';
</script>

<style>
/* CSS global dasar */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  background-color: #f1f5f9; /* Warna abu-abu sangat terang (Slate 100) */
  font-family: 'Syne', sans-serif;
  color: #0f172a;
}

.app-wrapper {
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Menggunakan flex-start agar bisa di-scroll jika konten panjang */
  min-height: 100vh;
  padding: 0;
}

/* Responsif untuk Laptop/Desktop */
@media (min-width: 768px) {
  .app-wrapper {
    padding: 40px 20px; /* Memberikan ruang di atas dan bawah pada layar besar */
    align-items: center;
  }
}
</style>