# Sistem Penentuan Risiko Diabetes — Fuzzy Mamdani

Aplikasi desktop (GUI) untuk skrining awal risiko diabetes menggunakan **logika fuzzy metode Mamdani**, tanpa memerlukan pemeriksaan laboratorium lengkap. Dibangun dengan Python murni + Tkinter (tanpa dependensi eksternal).

> Studi kasus: Puskesmas ingin membantu tenaga kesehatan melakukan skrining awal risiko diabetes berdasarkan empat indikator yang mudah diperoleh: **umur, BMI, kadar gula darah, dan aktivitas fisik.**

![Python](https://img.shields.io/badge/Python-3.x-blue)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange)
![Method](https://img.shields.io/badge/Method-Fuzzy%20Mamdani-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Daftar Isi

- [Tentang Sistem](#tentang-sistem)
- [Fitur](#fitur)
- [Variabel & Himpunan Fuzzy](#variabel--himpunan-fuzzy)
- [Fungsi Keanggotaan](#fungsi-keanggotaan)
- [Basis Aturan (Rule Base)](#basis-aturan-rule-base)
- [Alur Perhitungan](#alur-perhitungan)
- [Cara Menjalankan](#cara-menjalankan)
- [Struktur Proyek](#struktur-proyek)
- [Contoh Kasus](#contoh-kasus)
- [Pemenuhan Requirement Tugas](#pemenuhan-requirement-tugas)
- [Pengembangan Lebih Lanjut](#pengembangan-lebih-lanjut)
- [Lisensi](#lisensi)

---

## Tentang Sistem

| | |
|---|---|
| **Input** | Umur, BMI, Kadar Gula Darah, Aktivitas Fisik |
| **Output** | Risiko Diabetes — `Rendah` / `Sedang` / `Tinggi` |
| **Metode** | Fuzzy Mamdani (Min–Max) |
| **Defuzzifikasi** | Centroid (Center of Area), 500 titik sampling |
| **Jumlah Rule** | 16 rule (minimum tugas: 9) |
| **Bahasa** | Python 3.x |
| **GUI** | Tkinter + ttk (Notebook 3 tab) |
| **Dependensi eksternal** | Tidak ada — hanya pustaka standar Python |

---

## Fitur

- **Dashboard interaktif** — slider real-time untuk 4 variabel input, langsung menghitung ulang risiko (dengan debounce, tanpa lag/flicker) setiap nilai berubah.
- **Visualisasi fungsi keanggotaan** — grafik kurva Zmf / Trimf / Smf untuk tiap variabel, dengan garis penunjuk nilai input saat ini.
- **Grafik agregasi & defuzzifikasi** — visualisasi hasil agregasi MAX dan titik centroid hasil akhir.
- **Panel Rules Aktif** — daftar rule yang menyala (α > 0.001) beserta nilai firing strength-nya, diurutkan dari tertinggi.
- **Tab Perhitungan Manual** — laporan step-by-step otomatis (fuzzifikasi → inferensi → defuzzifikasi) untuk nilai input yang sedang aktif, sehingga proses fuzzy bisa ditelusuri secara transparan.
- **Interpretasi klinis** — rekomendasi singkat sesuai kategori risiko yang dihasilkan.

---

## Variabel & Himpunan Fuzzy

| Variabel | Tipe | Domain | Himpunan Fuzzy |
|---|---|---|---|
| Umur | Input | 10 – 80 tahun | Muda, ParuhBaya, Tua |
| BMI | Input | 10 – 50 kg/m² | Normal, Overweight, Obesitas |
| Gula Darah | Input | 70 – 300 mg/dL | Normal, Prediabetes, Diabetes |
| Aktivitas Fisik | Input | 0 – 100 (skor) | Rendah, Sedang, Tinggi |
| **Risiko Diabetes** | **Output** | 0 – 100 (skor) | Rendah, Sedang, Tinggi |

---

## Fungsi Keanggotaan

Tiga bentuk kurva digunakan: **Zmf** (kurva-Z, turun), **Trimf** (segitiga), **Smf** (kurva-S, naik). Parameter dirancang agar saling beririsan kontinu di sepanjang domain (tidak ada celah nilai yang menghasilkan keanggotaan nol di semua himpunan).

```text
Umur              Muda        = zmf(x, 25, 40)
                  ParuhBaya   = trimf(x, 30, 45, 60)
                  Tua         = smf(x, 50, 65)

BMI               Normal      = zmf(x, 18, 25)
                  Overweight  = trimf(x, 22, 27, 32)
                  Obesitas    = smf(x, 27, 37)

Gula Darah        Normal      = zmf(x, 90, 130)
                  Prediabetes = trimf(x, 100, 150, 200)
                  Diabetes    = smf(x, 160, 220)

Aktivitas Fisik   Rendah      = zmf(x, 15, 40)
                  Sedang      = trimf(x, 25, 52, 75)
                  Tinggi      = smf(x, 60, 80)

Risiko Diabetes   Rendah      = trimf(x, 0, 20, 40)
                  Sedang      = trimf(x, 30, 50, 70)
                  Tinggi      = trimf(x, 60, 80, 100)
```

---

## Basis Aturan (Rule Base)

16 rule, terdiri dari **9 rule inti** berupa matriks penuh BMI × Gula Darah (menjamin selalu ada rule yang aktif untuk kombinasi BMI/Gula berapa pun) dan **7 rule modifier** dari Umur & Aktivitas Fisik untuk menghaluskan/menegaskan hasil.

| No. | IF (Anteseden) | THEN |
|---|---|---|
| 1 | BMI Normal AND Gula Normal | Rendah |
| 2 | BMI Normal AND Gula Prediabetes | Sedang |
| 3 | BMI Normal AND Gula Diabetes | Tinggi |
| 4 | BMI Overweight AND Gula Normal | Sedang |
| 5 | BMI Overweight AND Gula Prediabetes | Sedang |
| 6 | BMI Overweight AND Gula Diabetes | Tinggi |
| 7 | BMI Obesitas AND Gula Normal | Sedang |
| 8 | BMI Obesitas AND Gula Prediabetes | Tinggi |
| 9 | BMI Obesitas AND Gula Diabetes | Tinggi |
| 10 | Umur Tua AND Aktivitas Rendah | Tinggi |
| 11 | Umur Tua AND BMI Obesitas | Tinggi |
| 12 | BMI Obesitas AND Aktivitas Rendah | Tinggi |
| 13 | Umur Tua AND Gula Diabetes | Tinggi |
| 14 | Umur Muda AND BMI Normal AND Aktivitas Tinggi | Rendah |
| 15 | Aktivitas Tinggi AND Gula Normal | Rendah |
| 16 | Umur ParuhBaya AND Gula Prediabetes AND Aktivitas Sedang | Sedang |

> **Catatan desain:** rule base awal (versi 3–4 variabel sekaligus per rule) memiliki celah — beberapa kombinasi input (mis. lansia + obesitas + prediabetes + aktivitas sedang) tidak ter-cover rule manapun sehingga seluruh α = 0 dan hasil keliru jatuh ke "Rendah". Rule base saat ini sudah diuji *exhaustive* di seluruh grid kombinasi umur × BMI × gula × aktivitas dan tidak ditemukan lagi kombinasi yang membuat semua rule tidak aktif.

---

## Alur Perhitungan

1. **Fuzzifikasi** — setiap input crisp dipetakan ke derajat keanggotaan (0–1) pada tiap himpunan fuzzy via `fz_umur()`, `fz_bmi()`, `fz_gula()`, `fz_aktiv()`.
2. **Inferensi (Mamdani)** — tiap rule dievaluasi dengan operator AND = **MIN**, menghasilkan α (firing strength); rule dengan output sama digabung dengan operator **MAX** (`inferensi()`).
3. **Defuzzifikasi (Centroid)** — kurva output hasil agregasi di-sampling pada 500 titik domain [0,100], lalu dihitung titik pusat massa:

   ```
   z* = Σ [ x · μ(x) ] / Σ [ μ(x) ]
   ```

4. **Klasifikasi akhir** berdasarkan ambang nilai crisp `z*` (`hitung()`):

   | Kondisi | Label |
   |---|---|
   | z\* < 35 | RENDAH |
   | 35 ≤ z\* < 60 | SEDANG |
   | z\* ≥ 60 | TINGGI |

---

## Cara Menjalankan

Tidak ada dependensi eksternal — cukup Python 3 dengan Tkinter (sudah termasuk dalam instalasi Python standar di Windows/macOS; di Linux mungkin perlu `sudo apt install python3-tk`).

```bash
# Clone repository
git clone https://github.com/USERNAME/diabetes-risk-fuzzy-mamdani.git
cd diabetes-risk-fuzzy-mamdani

# Jalankan aplikasi
python diabetes_fuzzy.py
```

**Cara pakai:** geser slider Umur, BMI, Gula Darah, dan Aktivitas Fisik di tab **Dashboard** — hasil risiko, nilai alpha, grafik, dan rule aktif akan ter-update otomatis. Buka tab **Fungsi Keanggotaan** untuk melihat kurva tiap variabel, atau tab **Perhitungan Manual** untuk melihat rincian langkah fuzzifikasi sampai defuzzifikasi dari nilai input yang sedang aktif.

---

## Struktur Proyek

```
diabetes-risk-fuzzy-mamdani/
├── diabetes_fuzzy.py     # Seluruh logika fuzzy + GUI Tkinter (single file)
└── README.md
```

Bagian penting dalam `diabetes_fuzzy.py`:

| Fungsi / Kelas | Peran |
|---|---|
| `trimf()`, `zmf()`, `smf()` | Fungsi keanggotaan dasar |
| `fz_umur()`, `fz_bmi()`, `fz_gula()`, `fz_aktiv()` | Fuzzifikasi tiap variabel input |
| `RULES` | Basis aturan (16 rule) |
| `inferensi()` | Evaluasi rule (MIN) + agregasi (MAX) |
| `defuzz_detail()` | Defuzzifikasi centroid |
| `hitung()` | Pipeline lengkap: fuzzifikasi → inferensi → defuzzifikasi → label |
| `class App(tk.Tk)` | GUI: tab Dashboard, Fungsi Keanggotaan, Perhitungan Manual |

---

## Contoh Kasus

| Skenario | Umur | BMI | Gula | Aktivitas | z\* | Hasil |
|---|---|---|---|---|---|---|
| Lansia, obesitas, prediabetes tinggi | 68 | 50.0 | 160 | 56 | 80.00 | **Tinggi** |
| Dewasa muda, sehat, sangat aktif | 22 | 21.0 | 90 | 80 | 20.00 | **Rendah** |
| Paruh baya, overweight, prediabetes, aktif sedang | 45 | 28.0 | 160 | 40 | 54.59 | **Sedang** |
| Lansia, obesitas berat, diabetes, tidak aktif | 60 | 38.0 | 250 | 10 | 80.00 | **Tinggi** |

---

## Pemenuhan Requirement Tugas

- [x] Menentukan sendiri variabel input (Umur, BMI, Gula Darah, Aktivitas Fisik) dan output (Risiko Diabetes)
- [x] Mendesain fungsi keanggotaan (Zmf, Trimf, Smf) untuk tiap variabel
- [x] Mendesain rule fuzzy — **16 rule** (minimum 9)
- [x] Melakukan fuzzifikasi
- [x] Melakukan inferensi — metode **Mamdani**
- [x] Melakukan defuzzifikasi — metode **Centroid**
- [x] Membuat GUI — Tkinter, 3 tab interaktif

---

## Pengembangan Lebih Lanjut

- Validasi parameter fungsi keanggotaan dengan data klinis riil / konsultasi tenaga medis.
- Penambahan variabel lain (riwayat keluarga, lingkar pinggang, tekanan darah).
- Versi web/mobile agar lebih mudah diakses tenaga kesehatan di lapangan.
- Pengujian validitas terhadap diagnosis tenaga medis pada data riil.
