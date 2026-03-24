from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from groq import Groq
import json
import os

# Inisialisasi FastAPI
app = FastAPI(title="AI Food Scanner API by Ali Sinaga", version="2.0")

# Middleware CORS agar Vue bisa memanggil API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inisialisasi Groq Client (Mengambil API KEY dari Environment Variable Vercel)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def analisis_nutrisi_groq(nama, gula, lemak, kalori, protein):
    """
    Mengirim data ke Groq (Llama 3) untuk analisis gizi profesional dalam format JSON.
    """
    prompt = f"""
    Bertindaklah sebagai ahli gizi profesional dan analitis.
    Analisis produk "{nama}" dengan komposisi per 100g: 
    Kalori: {kalori} kcal, Gula: {gula}g, Lemak: {lemak}g, Protein: {protein}g.

    Tujuan: Berikan edukasi kesehatan yang jujur dan ringkas.
    
    WAJIB Kembalikan HANYA format JSON valid:
    {{
      "status": "Kategori keamanan (misal: Sangat Aman, Perlu Perhatian, Kurang Sehat)",
      "health_score": (Angka 0-100),
      "kategori_cocok": ["Contoh: Diet Rendah Gula", "Contoh: Bulking Otot"],
      "pesan_rekomendasi": [
        "Kalimat saran 1", 
        "Kalimat saran 2"
      ]
    }}
    """
    
    try:
        # Panggil Groq API dengan Mode JSON
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional nutritionist that only responds in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        # Ambil konten teks dan ubah ke Dictionary
        ai_response = chat_completion.choices[0].message.content
        return json.loads(ai_response)
        
    except Exception as e:
        print(f"Error Groq API: {e}")
        return {
            "status": "Sistem Sedang Sibuk",
            "health_score": 0,
            "kategori_cocok": ["Gagal Menganalisis"],
            "pesan_rekomendasi": ["Mohon maaf, ahli gizi AI sedang tidak tersedia. Coba lagi nanti."]
        }

# --- ENDPOINT ---

@app.get("/api/scan/{barcode}")
async def scan_barcode(barcode: str):
    # Endpoint Open Food Facts
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    headers = {"User-Agent": "AliFoodScanner/2.0"}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                product = data.get("product", {})
                nutriments = product.get("nutriments", {})
                
                nama_produk = product.get("product_name", "Produk Tanpa Nama")
                
                # Ekstraksi nutrisi dengan nilai default 0 jika tidak ada
                gula = nutriments.get("sugars_100g", 0)
                lemak = nutriments.get("fat_100g", 0)
                kalori = nutriments.get("energy-kcal_100g", 0)
                protein = nutriments.get("proteins_100g", 0)
                
                # Proses Analisis menggunakan Groq AI
                hasil_ai = analisis_nutrisi_groq(nama_produk, gula, lemak, kalori, protein)
                
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
                raise HTTPException(status_code=404, detail="Barcode tidak terdaftar di database global.")
        else:
            raise HTTPException(status_code=response.status_code, detail="Server OpenFoodFacts bermasalah.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))