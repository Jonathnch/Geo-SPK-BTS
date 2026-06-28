import pandas as pd
import numpy as np
import skfuzzy as fuzz
from sklearn.metrics import silhouette_score

def pra_proses(data):
    df = pd.read_csv(data)
    
    df = df.dropna(subset=['PROV', 'KAB_KOT'])
    df = df[~df['PROV'].str.contains('Total', case=False, na=False)]
    
    df['LUAS_WILAYAH_KM2'] = df['LUAS_WILAYAH_KM2'].replace(0,1)
    df['TOTAL_BTS'] = df['TOTAL_BTS'].replace(0,1)
    df['JUM_PEN'] = df['JUM_PEN'].replace(0,1)
    
    df['PENGGUNA_HP'] = df['JUM_PEN'] * 0.6865
    
    df['D1_DEMOGRAFI'] = df['PENGGUNA_HP'] / df['LUAS_WILAYAH_KM2']
    df['D2_JANGKAUAN'] = df['TOTAL_BTS'] / df['LUAS_WILAYAH_KM2']
    df['D3_KAPASITAS'] = df['PENGGUNA_HP'] / df['TOTAL_BTS']
    df['D4_EKONOMI'] = (df['PDRB_TOTAL_MILYAR'] * 1000000000) / df['JUM_PEN']
    df['D5_LITERASI'] = df['HLS_AVG']
    
    fitur_awal = ['D1_DEMOGRAFI', 'D2_JANGKAUAN', 'D3_KAPASITAS', 'D4_EKONOMI', 'D5_LITERASI']
    for col in fitur_awal:
        df[col] = np.log1p(df[col])
        
    return df 

def fcm(df_awal, c=3, m=2.0):
    fitur = ['D1_DEMOGRAFI', 'D2_JANGKAUAN', 'D3_KAPASITAS', 'D4_EKONOMI', 'D5_LITERASI']
    nama_fitur_tampil = ['Kepadatan Demografi', 'Kepadatan Jangkauan', 'Kapasitas Teletrafik', 'PDRB per Kapita', 'Literasi Digital (HLS)']
    
    X = df_awal[fitur].values
    X_min = X.min(axis=0)
    X_max = X.max(axis=0)
    
    denominator = np.where((X_max - X_min) == 0, 1e-10, (X_max - X_min))
    X_norm = (X - X_min) / denominator
    
    df_normalisasi = df_awal.copy()
    df_normalisasi[fitur] = X_norm
    alldata = df_normalisasi[fitur].values.T
    
    cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
        alldata, c=c, m=m, error=0.001, maxiter=1000, init=None, seed=42)
        
    cluster_membership = np.argmax(u, axis=0)
    
    try:
        skor_silhouette = silhouette_score(X_norm, cluster_membership)
    except:
        skor_silhouette = 0.0

    jangkauan_centroids = cntr[:, 1]
    sorted_indices = np.argsort(jangkauan_centroids)
    
    mapping_baru = {lama: baru for baru, lama in enumerate(sorted_indices)}
    df_normalisasi['KLASTER_ID'] = [mapping_baru[label] for label in cluster_membership]
    
    for i in range(c):
        df_normalisasi[f'C{i+1}'] = u[sorted_indices[i]]
        
    # =========================================================================
    # REVISI: PENAMAAN KLASTER YANG LEBIH DESKRIPTIF DAN ILMIAH
    # =========================================================================
    nama_klaster = []
    for i in range(c):
        if i == 0:
            nama_klaster.append("Tier 1: Tertinggal (Prioritas USO)")
        elif i == c - 1:
            nama_klaster.append(f"Tier {c}: Maju & Mandiri")
        else:
            nama_klaster.append(f"Tier {i+1}: Berkembang (Transisi)")
    
    df_centroid = pd.DataFrame(cntr[sorted_indices], columns=fitur, index=nama_klaster)
    
    penjelasan_klaster = {}
    for i in range(c):
        baris_centroid = df_centroid.iloc[i].values
        index_dominan = np.argmax(baris_centroid)
        fitur_dominan = nama_fitur_tampil[index_dominan]
        penjelasan_klaster[nama_klaster[i]] = f"Ciri khas evaluasi wilayah: ditarik secara dominan oleh dimensi **{fitur_dominan}**."
    
    batas_ekonomi = df_normalisasi['D4_EKONOMI'].mean()
    status_list = []
    rekomendasi_list = []
    
    for index, row in df_normalisasi.iterrows():
        kid = row['KLASTER_ID']
        status_list.append(nama_klaster[kid]) # Memasukkan nama Tier ke dalam laporan
        
        if kid == 0:
            rekomendasi_list.append("Subsidi Negara USO (Target Penuntasan Blank Spot)")
        elif kid == c - 1:
            rekomendasi_list.append("Pemeliharaan Berkala (Optimal)")
        else:
            if row['D4_EKONOMI'] >= batas_ekonomi:
                rekomendasi_list.append("Ekspansi Swasta (Resolusi Congestion)")
            else:
                rekomendasi_list.append("Kemitraan Swasta & Pemerintah")
            
    df_normalisasi['STATUS'] = status_list
    df_normalisasi['REKOMENDASI_INVESTASI'] = rekomendasi_list
    
    return df_normalisasi, fpc, skor_silhouette, df_centroid, penjelasan_klaster