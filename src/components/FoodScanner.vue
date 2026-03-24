<template>
  <div class="scanner-container">

    <div class="beta-banner">
      <span class="beta-pill">BETA</span>
      <span>Aplikasi ini masih dalam tahap uji coba — data dan analisis bersifat demonstratif</span>
    </div>

    <header class="app-header">
      <div class="header-glow"></div>
      <div class="header-top">
        <div class="logo-3d">
          <div class="logo-face logo-front">🥗</div>
          <div class="logo-face logo-bottom"></div>
          <div class="logo-face logo-right"></div>
        </div>
        <div class="header-text">
          <h1>AI Food<br><span class="h1-accent">Scanner</span></h1>
        </div>
      </div>
      <p class="header-sub">Analisis nutrisi cerdas berbasis AI</p>
    </header>

    <main class="main-content">

      <div class="input-card card-3d">
        <div class="card-3d-face card-3d-top"></div>
        <div class="card-3d-face card-3d-right"></div>
        <div class="card-content">
          <div class="search-label">
            <span class="label-dot"></span>
            Scan Produk
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
            {{ isCameraOpen ? '✕  Tutup Kamera' : 'Buka kamera untuk scan barcode kemasan' }}
          </button>
        </div>
      </div>

      <Transition name="fade">
        <div v-if="isCameraOpen" class="camera-wrapper card-3d mt-3">
          <div class="card-3d-face card-3d-top"></div>
          <div class="card-3d-face card-3d-right"></div>
          <div class="card-content">
            <div id="reader" class="scanner-box"></div>
          </div>
        </div>
      </Transition>

      <div v-if="isLoading" class="loading-box card-3d mt-3">
        <div class="card-3d-face card-3d-top"></div>
        <div class="card-3d-face card-3d-right"></div>
        <div class="card-content loading-content">
          <div class="brain-orbit">
            <div class="brain-core">🧠</div>
            <div class="orbit-ring ring-1"></div>
            <div class="orbit-ring ring-2"></div>
          </div>
          <p>AI sedang menganalisis kandungan gizi...</p>
        </div>
      </div>

      <div v-if="errorMessage" class="error-toast mt-3">
        <span class="error-icon">⚠</span> {{ errorMessage }}
      </div>

      <Transition name="slide-up">
        <div v-if="result && !isLoading" class="result-card card-3d mt-3">
          <div class="card-3d-face card-3d-top"></div>
          <div class="card-3d-face card-3d-right"></div>
          <div class="card-content">

            <div class="result-header">
              <div class="product-meta">
                <div class="product-category">{{ result.kategori || 'Produk Pangan' }}</div>
                <div class="product-name">{{ result.nama_produk }}</div>
              </div>
              <div class="score-badge-wrap">
                <div class="score-badge" :class="scoreClass">
                  <div class="score-badge-inner">
                    <div class="score-number">{{ result.analisis_ai.health_score }}</div>
                    <div class="score-text">HEALTH</div>
                  </div>
                  <div class="score-glow" :class="scoreClass"></div>
                </div>
              </div>
            </div>

            <div class="status-bar" :class="statusBarClass">
              <div class="status-dot-wrap">
                <div class="status-dot"></div>
                <div class="status-dot-ring"></div>
              </div>
              <div class="status-text">{{ result.analisis_ai.status }}</div>
              <div class="status-sep">·</div>
              <div class="status-sub">{{ result.analisis_ai.frekuensi }}</div>
            </div>

            <div class="nutri-section">
              <div class="nutri-title">Nilai gizi per 100g</div>
              <div class="nutri-grid">
                <div class="nutri-item" v-for="(item, i) in nutriItems" :key="i" :style="{'--accent': item.color}">
                  <div class="nutri-icon">{{ item.icon }}</div>
                  <div class="nutri-val">{{ item.value }}</div>
                  <div class="nutri-label">{{ item.label }}</div>
                </div>
              </div>
            </div>

            <div class="ai-section">
              <div class="ai-header">
                <div class="ai-label-wrap">
                  <span class="ai-label">Analisis AI</span>
                </div>
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
                  v-for="(msg, i) in result.analisis_ai.pesan_rekomendasi"
                  :key="msg"
                  class="advice-item"
                  :style="{'--i': i}"
                >
                  <div class="advice-num">{{ String(i+1).padStart(2,'0') }}</div>
                  <div>{{ msg }}</div>
                </li>
              </ul>
            </div>

          </div>
        </div>
      </Transition>

      <div class="edu-card card-3d mt-3">
        <div class="card-3d-face card-3d-top"></div>
        <div class="card-3d-face card-3d-right"></div>
        <div class="card-content">
          <div class="edu-header">
            <div class="edu-icon-wrap">
              <div class="edu-icon">📚</div>
            </div>
            <div class="edu-title">Cara membaca label nutrisi</div>
          </div>
          <div class="edu-items">
            <div class="edu-item" v-for="(item, i) in eduItems" :key="i">
              <div class="edu-num-3d">
                <span>{{ i + 1 }}</span>
              </div>
              <div>
                <div class="edu-text-title">{{ item.title }}</div>
                <div class="edu-text-body">{{ item.body }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </main>

    <footer class="app-footer">
      <div class="footer-author">
        <div class="author-avatar">
          <img src="https://ui-avatars.com/api/?name=Ali+Sinaga&background=16a34a&color=fff&size=64&bold=true&font-size=0.4" alt="Ali Sinaga" />
          <div class="avatar-ring"></div>
        </div>
        <div class="author-info">
          <div class="author-name">Ali Sinaga</div>
          <div class="author-role">Developer</div>
        </div>
      </div>
      <div class="footer-divider"></div>
      <p class="footer-copy">© 2026 AI Food Scanner</p>
      <div class="tech-stack">
        <span class="tech-chip">Vue JS</span>
        <span class="tech-dot">·</span>
        <span class="tech-chip">FastAPI</span>
        <span class="tech-dot">·</span>
        <span class="tech-chip">AI</span>
      </div>
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

// Computed Nutrisi
const nutriItems = computed(() => {
  if (!result.value) return [];
  return [
    { icon: '⚡', value: result.value.nutrisi_per_100g.kalori, label: 'Kkal', color: '#f59e0b' },
    { icon: '🍬', value: result.value.nutrisi_per_100g.gula + 'g', label: 'Gula', color: '#ef4444' },
    { icon: '🫧', value: result.value.nutrisi_per_100g.lemak + 'g', label: 'Lemak', color: '#8b5cf6' },
    { icon: '💪', value: result.value.nutrisi_per_100g.protein + 'g', label: 'Protein', color: '#16a34a' },
  ];
});

// Simulasi Data Mockup (Agar UI bisa di-test tanpa backend)
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
            "Imbangi dengan minum air putih yang banyak setelah mengonsumsi produk ini.",
            "Bukan pengganti sumber karbohidrat utama."
          ]
        }
      });
    }, 1500); // Simulasi loading 1.5 detik
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
    // Mencoba fetch ke API asli
    const response = await fetch(`/api/scan/${barcode.value}`);
    if (!response.ok) throw new Error('API_NOT_FOUND');
    const data = await response.json();
    result.value = data;
  } catch (error) {
    // Jika API gagal (karena backend belum dibuat), gunakan mock data agar UI tetap jalan
    console.warn("Backend API tidak ditemukan, menggunakan data simulasi.");
    result.value = await getMockData(barcode.value);
  } finally {
    isLoading.value = false;
  }
};

const toggleCamera = async () => {
  isCameraOpen.value = !isCameraOpen.value;
  
  if (isCameraOpen.value) {
    // Menggunakan nextTick memastikan div #reader sudah dirender di DOM (v-if) sebelum scanner dipanggil
    await nextTick();
    startScanner();
  } else {
    stopScanner();
  }
};

const startScanner = () => {
  html5QrcodeScanner = new Html5QrcodeScanner(
    'reader',
    { fps: 10, qrbox: { width: 250, height: 100 }, videoConstraints: { facingMode: 'environment' } },
    false
  );
  html5QrcodeScanner.render(onScanSuccess, () => {});
};

const onScanSuccess = (decodedText) => {
  barcode.value = decodedText;
  toggleCamera(); // Tutup kamera otomatis
  scanBarcode();  // Langsung tembak API
};

const stopScanner = () => {
  if (html5QrcodeScanner) {
    html5QrcodeScanner.clear().catch(e => console.error(e));
    html5QrcodeScanner = null;
  }
};

// Pastikan kamera mati saat pindah halaman
onBeforeUnmount(() => {
  stopScanner();
});

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
