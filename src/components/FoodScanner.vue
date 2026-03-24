<template>
  <div class="scanner-container">
    <header class="app-header-3d">
      <div class="logo-3d">
        <span class="emoji">🥗</span>
      </div>
      <div class="brand-text">
        <h1>AI Food Scanner</h1>
        <p>Advanced Nutrition Intelligence by <strong>Ali Sinaga</strong></p>
      </div>
    </header>

    <main class="main-content">
      <div class="control-card-3d">
        <div class="search-label">Input Barcode</div>
        <div class="search-row">
          <input
            v-model="barcode"
            type="text"
            placeholder="Ketik angka barcode..."
            @keyup.enter="scanBarcode"
            :disabled="isLoading"
          />
          <button @click="scanBarcode" :disabled="isLoading" class="btn-3d-dark">
            <span v-if="!isLoading">SCAN</span>
            <div v-else class="loader-mini"></div>
          </button>
        </div>

        <div class="camera-controls">
          <button @click="toggleCamera" :disabled="isLoading" class="btn-3d-primary">
            {{ isCameraOpen ? '✕ Tutup' : '📷 Buka Kamera' }}
          </button>
          
          <button 
            v-if="isCameraOpen" 
            @click="switchCamera" 
            class="btn-3d-secondary"
          >
            🔄 Putar
          </button>
        </div>
      </div>

      <Transition name="zoom">
        <div v-show="isCameraOpen" class="camera-canvas">
          <div id="reader"></div>
          <div class="camera-overlay">
            <div class="corner tl"></div><div class="corner tr"></div>
            <div class="corner bl"></div><div class="corner br"></div>
          </div>
        </div>
      </Transition>

      <div v-if="isLoading" class="ai-loading-3d">
        <div class="floating-brain">🧠</div>
        <div class="loading-text">Ali AI sedang memproses data...</div>
      </div>

      <Transition name="flip-3d">
        <div v-if="result && !isLoading" class="result-card-3d">
          <div class="card-inner" :class="scoreClass">
            
            <div class="top-row">
              <div class="product-info">
                <span class="chip">ALI AI ANALYSIS</span>
                <h2>{{ result.nama_produk }}</h2>
              </div>
              <div class="score-3d-ball">
                <span class="num">{{ result.analisis_ai.health_score }}</span>
                <span class="lab">HEALTH</span>
              </div>
            </div>

            <div class="status-banner">
              <strong>{{ result.analisis_ai.status }}</strong>
            </div>

            <div class="grid-3d">
              <div class="grid-item"><strong>{{ result.nutrisi_per_100g.kalori }}</strong><p>Kkal</p></div>
              <div class="grid-item"><strong>{{ result.nutrisi_per_100g.gula }}g</strong><p>Gula</p></div>
              <div class="grid-item"><strong>{{ result.nutrisi_per_100g.lemak }}g</strong><p>Lemak</p></div>
              <div class="grid-item"><strong>{{ result.nutrisi_per_100g.protein }}g</strong><p>Protein</p></div>
            </div>

            <div class="advice-box-3d">
              <div class="advice-tags">
                <span v-for="tag in result.analisis_ai.kategori_cocok" :key="tag" class="tag-3d">{{ tag }}</span>
              </div>
              <ul class="advice-list-3d">
                <li v-for="msg in result.analisis_ai.pesan_rekomendasi" :key="msg">{{ msg }}</li>
              </ul>
            </div>
          </div>
        </div>
      </Transition>
    </main>

    <footer class="footer-3d">
      <p>© 2026 Developed by <strong>Ali Sinaga</strong></p>
      <div class="stack">VUE 3 • FASTAPI • DEEP LEARNING</div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue';
import { Html5QrcodeScanner } from 'html5-qrcode';

const barcode = ref('');
const result = ref(null);
const isLoading = ref(false);
const errorMessage = ref('');
const isCameraOpen = ref(false);
const currentFacingMode = ref('environment'); // environment = belakang, user = depan
let html5QrcodeScanner = null;

const scanBarcode = async () => {
  if (!barcode.value.trim()) return;
  isLoading.value = true;
  result.value = null;
  try {
    const response = await fetch(`/api/scan/${barcode.value}`);
    const data = await response.json();
    result.value = data;
  } catch (e) {
    errorMessage.value = "Produk tidak ditemukan.";
  } finally {
    isLoading.value = false;
  }
};

const toggleCamera = () => {
  isCameraOpen.value = !isCameraOpen.value;
  if (isCameraOpen.value) setTimeout(() => startScanner(), 100);
  else stopScanner();
};

const switchCamera = () => {
  // Ganti mode kamera
  currentFacingMode.value = currentFacingMode.value === 'environment' ? 'user' : 'environment';
  stopScanner();
  setTimeout(() => startScanner(), 200);
};

const startScanner = () => {
  html5QrcodeScanner = new Html5QrcodeScanner(
    "reader",
    { 
      fps: 15, 
      qrbox: { width: 250, height: 120 },
      videoConstraints: { facingMode: currentFacingMode.value } 
    },
    false
  );
  html5QrcodeScanner.render((txt) => {
    barcode.value = txt;
    toggleCamera();
    scanBarcode();
  }, () => {});
};

const stopScanner = () => {
  if (html5QrcodeScanner) {
    html5QrcodeScanner.clear();
    html5QrcodeScanner = null;
  }
};

onBeforeUnmount(() => stopScanner());

const scoreClass = computed(() => {
  if (!result.value) return '';
  const s = result.value.analisis_ai.health_score;
  return s >= 80 ? 'is-good' : s >= 50 ? 'is-warn' : 'is-bad';
});
</script>