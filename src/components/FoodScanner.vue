<template>
  <div class="scanner-container">

    <div class="beta-banner">
      <span class="beta-pill">BETA</span>
      <span>Aplikasi uji coba — data bersifat demonstratif</span>
    </div>

    <header class="app-header">
      <div class="header-top">
        <div class="logo-clean">🥗</div>
        <div class="header-text">
          <h1>AI Food <span class="h1-accent">Scanner</span></h1>
          <p class="header-sub">Analisis nutrisi cerdas berbasis AI</p>
        </div>
      </div>
    </header>

    <main class="main-content">

      <div class="clean-card">
        <div class="search-label">
          <span class="label-dot"></span> Scan Produk
        </div>
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
            <span v-if="!isLoading" class="btn-scan-inner">Scan <span class="arrow">→</span></span>
            <span v-else class="loader-mini"></span>
          </button>
        </div>
        <button @click="toggleCamera" :disabled="isLoading" class="btn-camera">
          <span class="camera-icon">📷</span>
          {{ isCameraOpen ? '✕ Tutup Kamera' : 'Buka kamera untuk scan barcode' }}
        </button>
      </div>

      <Transition name="fade">
        <div v-if="isCameraOpen" class="clean-card mt-3 p-2">
          <div id="reader" class="scanner-box"></div>
        </div>
      </Transition>

      <div v-if="isLoading" class="clean-card mt-3 loading-content">
        <div class="brain-icon">🧠</div>
        <p>AI sedang menganalisis kandungan gizi...</p>
      </div>

      <div v-if="errorMessage" class="error-toast mt-3">
        <span class="error-icon">⚠</span> {{ errorMessage }}
      </div>

      <Transition name="slide-up">
        <div v-if="result && !isLoading" class="clean-card mt-3 p-0 overflow-hidden">
          
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

          <div class="status-bar" :class="statusBarClass">
            <div class="status-dot-wrap"><div class="status-dot"></div></div>
            <div class="status-text">{{ result.analisis_ai.status }}</div>
            <div class="status-sep">·</div>
            <div class="status-sub">{{ result.analisis_ai.frekuensi }}</div>
          </div>

          <div class="p-4 border-b border-gray">
            <div class="section-title">Nilai gizi per 100g</div>
            <div class="nutri-grid">
              <div class="nutri-item" v-for="(item, i) in nutriItems" :key="i" :style="{'--accent': item.color}">
                <div class="nutri-icon">{{ item.icon }}</div>
                <div class="nutri-val">{{ item.value }}</div>
                <div class="nutri-label">{{ item.label }}</div>
              </div>
            </div>
          </div>

          <div class="p-4 bg-slate-50">
            <div class="section-title text-green">✨ Analisis AI</div>
            <div class="tag-row">
              <span v-for="tag in result.analisis_ai.kategori_cocok" :key="tag" class="tag">{{ tag }}</span>
            </div>
            <ul class="advice-list">
              <li v-for="(msg, i) in result.analisis_ai.pesan_rekomendasi" :key="msg" class="advice-item">
                <div class="advice-num">{{ String(i+1).padStart(2,'0') }}</div>
                <div>{{ msg }}</div>
              </li>
            </ul>
          </div>
        </div>
      </Transition>

      <div class="clean-card mt-3 p-0 overflow-hidden">
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

    <footer class="app-footer">
      <div class="footer-author">
        <img class="author-avatar" src="https://ui-avatars.com/api/?name=Ali+Sinaga&background=16a34a&color=fff&size=64&bold=true" alt="Ali Sinaga" />
        <div class="author-info">
          <div class="author-name">Ali Sinaga</div>
          <div class="author-role">Developer</div>
        </div>
      </div>
      <p class="footer-copy">© 2026 AI Food Scanner</p>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount, nextTick } from 'vue';
import { Html5QrcodeScanner } from 'html5-qrcode';

const barcode = ref('');
const result = ref(null);
const isLoading = ref(false);
const errorMessage = ref('');
const isCameraOpen = ref(false);
let html5QrcodeScanner = null;

// Edu Data
const eduItems = [
  { title: 'Perhatikan "Takaran Saji"', body: 'Semua angka nutrisi berlaku per takaran saji, bukan per kemasan penuh.' },
  { title: '%AKG — Angka Kecukupan Gizi', body: 'Di atas 20% berarti tinggi, di bawah 5% berarti rendah.' },
  { title: 'Waspadai 3 hal ini', body: 'Gula tambahan, natrium (sodium), dan lemak jenuh perlu dibatasi.' },
  { title: 'Health Score AI', body: 'Skor AI bersifat panduan, konsultasikan dengan ahli gizi untuk hasil terbaik.' }
];

const nutriItems = computed(() => {
  if (!result.value) return [];
  return [
    { icon: '⚡', value: result.value.nutrisi_per_100g.kalori, label: 'Kkal', color: '#f59e0b' },
    { icon: '🍬', value: result.value.nutrisi_per_100g.gula + 'g', label: 'Gula', color: '#ef4444' },
    { icon: '🫧', value: result.value.nutrisi_per_100g.lemak + 'g', label: 'Lemak', color: '#8b5cf6' },
    { icon: '💪', value: result.value.nutrisi_per_100g.protein + 'g', label: 'Protein', color: '#16a34a' },
  ];
});

// Mock Data
const getMockData = (code) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        nama_produk: "Cemilan Kentang Simulasi " + (code || "123"),
        kategori: "Makanan Ringan",
        nutrisi_per_100g: { kalori: 450, gula: 12, lemak: 22, protein: 4 },
        analisis_ai: {
          health_score: 42,
          status: "Kurang Sehat",
          frekuensi: "Batasi Konsumsi",
          kategori_cocok: ["Tinggi Garam", "Tinggi Kalori", "Ultra-Proses"],
          pesan_rekomendasi: [
            "Kandungan natrium cukup tinggi, tidak disarankan untuk konsumsi harian.",
            "Imbangi dengan minum air putih yang banyak setelah mengonsumsi produk ini."
          ]
        }
      });
    }, 1500);
  });
};

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
    if (!response.ok) throw new Error('API_NOT_FOUND');
    result.value = await response.json();
  } catch (error) {
    result.value = await getMockData(barcode.value);
  } finally {
    isLoading.value = false;
  }
};

const toggleCamera = async () => {
  isCameraOpen.value = !isCameraOpen.value;
  if (isCameraOpen.value) {
    await nextTick();
    startScanner();
  } else {
    stopScanner();
  }
};

const startScanner = () => {
  html5QrcodeScanner = new Html5QrcodeScanner(
    'reader', { fps: 10, qrbox: { width: 250, height: 100 }, videoConstraints: { facingMode: 'environment' } }, false
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

