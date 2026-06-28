# BUKU PANDUAN PENGGUNAAN (MANUAL PROGRAM)
**Sistem Pendukung Keputusan Geo-SPK: Pemerataan Infrastruktur BTS**

## 1. Navigasi Utama Aplikasi
Saat aplikasi Geo-SPK diakses melalui *browser*, pengguna akan melihat panel **Navigasi Utama** di sebelah kiri layar. Panel ini menyediakan tiga menu utama:
* **Beranda:** Halaman sambutan dan panduan indikator klasifikasi *Tier*.
* **Aplikasi SPK:** Ruang kerja utama untuk mengatur parameter algoritma, mengunggah data, dan melihat visualisasi hasil komputasi.
* **Tentang Sistem:** Informasi pengembang dan latar belakang pengembangan SPK.

## 2. Modul Beranda (Pengenalan Indikator)
Sebelum mengeksekusi sistem, pengguna disarankan membaca panduan pada menu **Beranda**. Halaman ini menjelaskan:
* **Indikator Peta Berdasarkan Klasifikasi Tier:** Penjelasan mengenai gradasi warna dari *Tier* 1 (Daerah Tertinggal / Prioritas USO) dengan warna merah, hingga *Tier* Tertinggi (Daerah Maju & Mandiri) dengan warna hijau.
* **Penetapan 5 Fitur Ekstraksi:** Kepadatan Demografi, Kepadatan Jangkauan, Kapasitas Teletrafik, Kapasitas Ekonomi (PDRB), dan Literasi Digital (HLS).

## 3. Modul Aplikasi SPK (Langkah-Langkah Eksekusi)

**Langkah 1: Persiapan Dataset**
Sistem ini membutuhkan data dalam format CSV untuk dieksekusi. Terdapat dua cara untuk mempersiapkan data:
1. **Menggunakan Data Sampel (Rekomendasi Uji Coba):** Anda dapat menggunakan data uji coba bawaan yang telah disediakan di dalam repositori ini. Silakan unduh file bernama `dataset1.csv` (berada di dalam folder `data/`). File ini berisi data observasi riil yang digunakan dalam penelitian.
2. **Menggunakan Data Mandiri:** Jika Anda ingin mengevaluasi data baru, klik tombol **"Unduh Template CSV"** pada aplikasi untuk mendapatkan format kolom yang sesuai standar sistem, lalu isi dengan data observasi Anda.

**Langkah 2: Pengaturan Parameter Dinamis (Fuzzy C-Means)**
1. **Jumlah Cluster (c):** Tentukan berapa banyak tingkatan hierarki (*Tier*) yang ingin dibentuk (sistem mendukung dari 2 hingga batas optimal).
2. **Tingkat Toleransi / Fuzziness (m):** Atur nilai tingkat kebingungan algoritma (angka *default* adalah 2.00).

**Langkah 3: Unggah Data dan Eksekusi**
1. Seret dan lepas (*drag and drop*) atau klik tombol *Browse files* untuk mengunggah dokumen CSV.
2. Klik tombol utama **"Jalankan Algoritma Fuzzy C-Means"**.

## 4. Membaca Hasil Analisis (Output Komputasi)
* **Dasbor Atas (Validitas):** Menampilkan *Silhouette Score* (separasi) dan *Partition Coefficient / FPC* (kepadatan internal matriks).
* **Tab 1 - Peta Geospasial:** Visualisasi interaktif persebaran *Tier* (Choropleth).
* **Tab 2 - Laporan Wilayah:** Tabel diagnosis yang memuat logika cerdas untuk menentukan rekomendasi (USO, Ekspansi Komersial, Kemitraan, atau Pemeliharaan). Bisa diekspor ke Excel.
* **Tab 3 - Profil Dimensi:** Memuat *Radar Chart* untuk membedah fitur apa yang paling dominan membentuk suatu *Tier*.
* **Tab 4 - Metrik Centroid:** Menampilkan titik pusat matriks sebagai pembuktian matematis.