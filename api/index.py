from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import google.generativeai as genai
import json

# Inisialisasi FastAPI
app = FastAPI(title="AI Food Scanner API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
# Menggunakan model Gemini 1.5 Flash (Sangat cepat dan cocok untuk teks)
model = genai.GenerativeModel('gemini-2.5-flash')

def analisis_nutrisi_dengan_ai_sungguhan(nama, gula, lemak, kalori, protein):
    """
    Mengirim data ke Gemini API dan memintanya menjadi ahli gizi yang merespons dalam format JSON.
    """
    prompt = f"""
    Bertindaklah sebagai ahli gizi profesional dan analitis.
    Analisis produk "{nama}" dengan komposisi per 100g: 
    Kalori: {kalori} kcal, Gula: {gula}g, Lemak: {lemak}g, Protein: {protein}g.

    Kembalikan HANYA format JSON valid tanpa format markdown (tanpa ```json). 
    Struktur JSON harus persis seperti ini:
    {{
      "status": "Kategori keamanan (misal: Sangat Aman, Perlu Perhatian, Kurang Sehat)",
      "health_score": (Angka dari 0 sampai 100 berdasarkan kualitas gizinya),
      "kategori_cocok": ["Kategori diet 1", "Kategori diet 2"],
      "pesan_rekomendasi": [
        "Saran medis/gizi kalimat 1", 
        "Saran medis/gizi kalimat 2"
      ]
    }}
    """
    
    try:
        # Panggil Gemini API
        response = model.generate_content(prompt)
        
        # Bersihkan response jika AI membandel menambahkan markdown ```json
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        
        # Ubah teks JSON menjadi Dictionary Python
        ai_data = json.loads(raw_text)
        return ai_data
        
    except Exception as e:
        # Fallback (Jika API gagal/limit)
        print("Error Gemini API:", e)
        return {
            "status": "Gagal Menganalisis",
            "health_score": 0,
            "kategori_cocok": ["Sistem Sedang Sibuk"],
            "pesan_rekomendasi": ["Gagal terhubung ke server AI Ahli Gizi."]
        }

# ==========================================
# ENDPOINT UTAMA
# ==========================================
@app.get("/api/scan/{barcode}")
async def scan_barcode(barcode: str):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    headers = {"User-Agent": "AplikasiDeteksiMakanan_FastAPI/2.0"}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                product = data.get("product", {})
                nutriments = product.get("nutriments", {})
                
                nama_produk = product.get("product_name", "Produk Tidak Diketahui")
                gula = nutriments.get("sugars_100g", 0)
                lemak = nutriments.get("fat_100g", 0)
                kalori = nutriments.get("energy-kcal_100g", 0)
                protein = nutriments.get("proteins_100g", 0)
                
                # ---> PROSES KE GEMINI AI <---
                hasil_ai = analisis_nutrisi_dengan_ai_sungguhan(nama_produk, gula, lemak, kalori, protein)
                
                return {
                    "success": True,
                    "barcode": barcode,
                    "nama_produk": nama_produk,
                    "nutrisi_per_100g": {
                        "kalori": kalori,
                        "gula": gula,
                        "lemak": lemak,
                        "protein": protein
                    },
                    "analisis_ai": hasil_ai
                }
            else:
                raise HTTPException(status_code=404, detail="Produk tidak ditemukan di Open Food Facts.")
        else:
            raise HTTPException(status_code=response.status_code, detail="Gagal menghubungi API eksternal.")
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan koneksi server: {str(e)}")