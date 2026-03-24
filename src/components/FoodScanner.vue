<template>
  <div class="scanner-container">

    <!-- Beta Banner -->
    <div class="beta-banner">
      <span class="beta-pill">BETA</span>
      <span>Aplikasi ini masih dalam tahap uji coba — data dan analisis bersifat demonstratif</span>
    </div>

    <!-- Header -->
    <header class="app-header">
      <div class="header-top">
        <div class="logo-icon">🥗</div>
        <h1>AI Food Scanner</h1>
      </div>
      <p class="header-sub">Analisis nutrisi cerdas berbasis AI · by Ali Sinaga</p>
    </header>

    <main class="main-content">

      <!-- Input Card -->
      <div class="input-card">
        <div class="search-label">Scan Produk</div>
        <div class="search-row">
          <input
            v-model="barcode"
            type="text"
            placeholder="Masukkan nomor barcode..."
            @keyup.enter="scanBarcode"
            :disabled="isLoading"
            class="search-input"
          />
          <button @click="scanBarcode" :disabled="isLoading" class="btn-scan">
            <span v-if="!isLoading">Scan →</span>
            <span v-else class="loader-mini"></span>
          </button>
        </div>
        <button @click="toggleCamera" :disabled="isLoading" class="btn-camera">
          {{ isCameraOpen ? '✕  Tutup Kamera' : '📷  Buka kamera untuk scan barcode kemasan' }}
        </button>
      </div>

      <!-- Camera -->
      <Transition name="fade">
        <div v-show="isCameraOpen" class="camera-wrapper">
          <div id="reader"></div>
        </div>
      </Transition>

      <!-- Loading -->
      <div v-if="isLoading" class="loading-box">
        <div class="brain-pulse">🧠</div>
        <p>Gemini AI sedang menganalisis kandungan gizi...</p>
      </div>

      <!-- Error -->
      <div v-if="errorMessage" class="error-toast">
        <span>⚠</span> {{ errorMessage }}
      </div>

      <!-- Result Card -->
      <Transition name="slide-up">
        <div v-if="result && !isLoading" class="result-card">

          <!-- Product Header -->
          <div class="result-header">
            <div class="product-meta">
              <div class="product-category">{{ result.kategori || 'Produk Pangan' }}</div>
              <div class="product-name">{{ result.nama_produk }}</div>
            </div>
            <div class="score-badge" :class="scoreClass">
              <div class="score-number">{{ result.analisis_ai.health_score }}</div>
              <div class="score-text">HEALTH</div>
            </div>
          </div>

          <!-- Status Bar -->
          <div class="status-bar" :class="statusBarClass">
            <div class="status-dot"></div>
            <div class="status-text">{{ result.analisis_ai.status }}</div>
            <div class="status-sub">{{ result.analisis_ai.frekuensi }}</div>
          </div>

          <!-- Nutrition Grid -->
          <div class="nutri-section">
            <div class="nutri-title">Nilai gizi per 100g</div>
            <div class="nutri-grid">
              <div class="nutri-item">
                <div class="nutri-val">{{ result.nutrisi_per_100g.kalori }}</div>
                <div class="nutri-label">Kkal</div>
              </div>
              <div class="nutri-item">
                <div class="nutri-val">{{ result.nutrisi_per_100g.gula }}g</div>
                <div class="nutri-label">Gula</div>
              </div>
              <div class="nutri-item">
                <div class="nutri-val">{{ result.nutrisi_per_100g.lemak }}g</div>
                <div class="nutri-label">Lemak</div>
              </div>
              <div class="nutri-item">
                <div class="nutri-val">{{ result.nutrisi_per_100g.protein }}g</div>
                <div class="nutri-label">Protein</div>
              </div>
            </div>
          </div>

          <!-- AI Analysis -->
          <div class="ai-section">
            <div class="ai-header">
              <span class="ai-label">Analisis AI</span>
              <span class="ai-badge">GEMINI</span>
            </div>
            <div class="tag-row">
              <span
                v-for="tag in result.analisis_ai.kategori_cocok"
                :key="tag"
                class="tag"
              >{{ tag }}</span>
            </div>
            <ul class="advice-list">
              <li
                v-for="msg in result.analisis_ai.pesan_rekomendasi"
                :key="msg"
                class="advice-item"
              >
                <div class="advice-dot"></div>
                <div>{{ msg }}</div>
              </li>
            </ul>
          </div>

        </div>
      </Transition>

      <!-- Education Section -->
      <div class="edu-card">
        <div class="edu-header">
          <div class="edu-icon">📚</div>
          <div class="edu-title">Cara membaca label nutrisi</div>
        </div>
        <div class="edu-items">
          <div class="edu-item" v-for="(item, i) in eduItems" :key="i">
            <div class="edu-num">{{ i + 1 }}</div>
            <div>
              <div class="edu-text-title">{{ item.title }}</div>
              <div class="edu-text-body">{{ item.body }}</div>
            </div>
          </div>
        </div>
      </div>

    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <p>© 2026 Developed by <strong>Ali Sinaga</strong></p>
      <div class="tech-stack">
        <span>Vue JS</span> · <span>FastAPI</span> · <span>Gemini AI</span>
      </div>
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
let html5QrcodeScanner = null;

// Konten edukasi
const eduItems = [
  {
    title: 'Perhatikan "Takaran Saji"',
    body: 'Semua angka nutrisi berlaku per takaran saji, bukan per kemasan penuh. Satu bungkus bisa berisi 2–3 sajian.'
  },
  {
    title: '%AKG — Angka Kecukupan Gizi',
    body: 'Angka ini menunjukkan berapa % kebutuhan harianmu yang terpenuhi. Di atas 20% berarti tinggi, di bawah 5% berarti rendah.'
  },
  {
    title: 'Waspadai 3 hal ini',
    body: 'Gula tambahan, natrium (sodium), dan lemak jenuh adalah tiga zat yang paling perlu dibatasi dalam diet sehari-hari.'
  },
  {
    title: 'Health Score bukan satu-satunya ukuran',
    body: 'Skor AI bersifat panduan, bukan patokan mutlak. Konsultasikan kebutuhan nutrisimu dengan ahli gizi untuk hasil terbaik.'
  }
];

// --- FUNGSI API ---
const scanBarcode = async () => {
  if (!barcode.value.trim()) {
    errorMessage.value = 'Silakan masukkan nomor barcode terlebih dahulu.';
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';
  result.value = null;

  try {
    const response = await fetch(`/api/scan/${barcode.value}`);
    const data = await response.json();

    if (!response.ok) throw new Error(data.detail || 'Terjadi kesalahan pada server.');

    result.value = data;
  } catch (error) {
    errorMessage.value = 'Gagal terhubung ke server atau produk tidak ditemukan.';
  } finally {
    isLoading.value = false;
  }
};

// --- FUNGSI KAMERA ---
const toggleCamera = () => {
  isCameraOpen.value = !isCameraOpen.value;
  if (isCameraOpen.value) {
    setTimeout(() => startScanner(), 100);
  } else {
    stopScanner();
  }
};

const startScanner = () => {
  html5QrcodeScanner = new Html5QrcodeScanner(
    'reader',
    {
      fps: 10,
      qrbox: { width: 250, height: 100 },
      videoConstraints: { facingMode: 'environment' }
    },
    false
  );
  html5QrcodeScanner.render(onScanSuccess, () => {});
};

const onScanSuccess = (decodedText) => {
  barcode.value = decodedText;
  toggleCamera();
  scanBarcode();
};

const stopScanner = () => {
  if (html5QrcodeScanner) {
    html5QrcodeScanner.clear().catch(e => console.error(e));
    html5QrcodeScanner = null;
  }
};

onBeforeUnmount(() => stopScanner());

// --- COMPUTED ---
const scoreClass = computed(() => {
  if (!result.value) return '';
  const score = result.value.analisis_ai.health_score;
  if (score >= 80) return 'score-good';
  if (score >= 50) return 'score-warn';
  return 'score-bad';
});

const statusBarClass = computed(() => {
  if (!result.value) return '';
  const score = result.value.analisis_ai.health_score;
  if (score >= 80) return 'status-good';
  if (score >= 50) return 'status-warn';
  return 'status-bad';
});
</script>
