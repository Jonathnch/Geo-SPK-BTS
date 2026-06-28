import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import plotly.graph_objects as go
import io
from streamlit_folium import st_folium
from folium.plugins import MousePosition
from algoritma import pra_proses, fcm

st.set_page_config(page_title="Geo-SPK BTS Indonesia", layout="wide", page_icon="📡")

def get_color_palette(n):
    base_palette = ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#ffffbf', '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850', '#006837', '#00401a']
    if n <= 2: return ['#d73027', '#1a9850']
    if n == 3: return ['#d73027', '#fee08b', '#1a9850']
    if n == 4: return ['#d73027', '#fdae61', '#a6d96a', '#1a9850']
    return base_palette[:n] if n <= len(base_palette) else (base_palette * (n//len(base_palette) + 1))[:n]

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2859/2859292.png", width=80)
st.sidebar.title("Navigasi Utama")
menu = st.sidebar.radio("Pilih Halaman:", ["🏠 Beranda", "🖥️ Aplikasi SPK", "ℹ️ Tentang Sistem"])
st.sidebar.markdown("---")

if menu == "🏠 Beranda":
    st.title("📡 Geo-SPK: Sistem Pendukung Keputusan Pemerataan BTS")
    st.markdown("Selamat datang di aplikasi pemetaan analitik berbasis **Machine Learning (Fuzzy C-Means)** untuk mengevaluasi pemerataan infrastruktur telekomunikasi secara multidimensional.")
    
    st.markdown("---")
    st.subheader("📖 Indikator Peta Berdasarkan Klasifikasi Cluster")
    st.write("Sistem mengevaluasi dan memetakan wilayah secara dinamis ke dalam beberapa tingkatan (Tier) menggunakan gradasi spektrum **Merah hingga Hijau**:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("🔴 **Tier 1: Daerah Tertinggal (Prioritas USO)**")
        st.write("Wilayah dengan skor kesenjangan paling ekstrem. Rentan terhadap ketiadaan akses dasar (Blank Spot) dan wajib menjadi target utama Subsidi USO Negara.")
    with col2:
        st.warning("🟡 **Tier Transisi: Daerah Berkembang**")
        st.write("Wilayah berkembang yang mungkin telah memiliki sinyal, namun mengalami ketimpangan beban kapasitas jaringan (Congestion) atau anomali ekonomi.")
    with col3:
        st.success("🟢 **Tier Tertinggi: Daerah Maju & Mandiri**")
        st.write("Wilayah perkotaan/maju dengan infrastruktur, kapasitas trafik, dan daya beli masyarakat yang sangat seimbang dan mandiri.")
        
    st.markdown("---")
    st.info("👈 **Mulai Analisis:** Silakan buka menu **🖥️ Aplikasi SPK** di panel sebelah kiri untuk mulai mengunggah data.")

elif menu == "🖥️ Aplikasi SPK":
    st.title("🖥️ Eksekusi SPK")
    st.write("Silakan bereksperimen dengan jumlah klaster untuk melihat pola sebaran data telekomunikasi nasional secara mendalam.")
    
    col_param1, col_param2 = st.columns(2)
    with col_param1:
        c_input = st.number_input("Jumlah Cluster (c):", min_value=2, max_value=12, value=3, help="Masukkan jumlah pembagian tingkatan wilayah.")
    with col_param2:
        m_input = st.number_input("Tingkat Toleransi / Fuzziness (m):", min_value=1.1, max_value=3.0, value=2.0)

    st.markdown("### 📥 Unggah Dataset Observasi")
    template_csv = "PROV,KAB_KOT,JUM_PEN,LUAS_WILAYAH_KM2,PDRB_TOTAL_MILYAR,TOTAL_BTS,HLS_AVG\n"
    st.download_button("📄 Unduh Template CSV", data=template_csv, file_name='Template_BTS.csv', mime='text/csv')
    
    file_upload = st.file_uploader("Pilih file Dataset berformat CSV:", type=["csv"])

    if file_upload is not None:
        if st.button("🚀 Jalankan Analisis Klaster", use_container_width=True, type="primary"):
            with st.spinner('Mengekstraksi fitur dan menjalankan matriks komputasi...'):
                data_bersih = pra_proses(file_upload)
                data_hasil, skor_pc, skor_silhouette, tabel_centroid, penjelasan_klaster = fcm(data_bersih, c=c_input, m=m_input)
                
                st.session_state['berhasil'] = True
                st.session_state['data_hasil'] = data_hasil
                st.session_state['skor_pc'] = skor_pc
                st.session_state['skor_silhouette'] = skor_silhouette
                st.session_state['c_input'] = c_input
                st.session_state['tabel_centroid'] = tabel_centroid
                st.session_state['penjelasan_klaster'] = penjelasan_klaster

        if st.session_state.get('berhasil', False):
            data_hasil = st.session_state['data_hasil']
            skor_pc = st.session_state['skor_pc']
            skor_silhouette = st.session_state['skor_silhouette']
            c_input = st.session_state['c_input']
            tabel_centroid = st.session_state['tabel_centroid']
            penjelasan_klaster = st.session_state['penjelasan_klaster']
            
            WARNA_PALET = get_color_palette(c_input)

            try:
                peta_gdf = gpd.read_file('peta_indonesia.json')
                data_hasil['match_name'] = data_hasil['KAB_KOT'].astype(str).str.lower().str.replace(' ', '', regex=False)
                peta_gdf['match_name'] = peta_gdf['NAME_2'].astype(str).str.lower().str.replace(' ', '', regex=False)
                
                peta_gabungan = peta_gdf.merge(data_hasil, on='match_name', how='left')
                m = folium.Map(location=[0.7893, 113.9213], zoom_start=5, tiles="CartoDB positron")
                
                formatter = "function(num) {return L.Util.formatNum(num, 5);};"
                MousePosition(
                    position='topright', separator=' | ', empty_string='Arahkan kursor ke peta...',
                    lng_first=False, num_digits=5, prefix='Koordinat (Lat, Lng):',
                    lat_formatter=formatter, lng_formatter=formatter,
                ).add_to(m)

                html_legend_items = ""
                for i in range(c_input):
                    if i == 0:
                        label_tier = "Tier 1 (Prioritas)"
                    elif i == c_input - 1:
                        label_tier = f"Tier {c_input} (Mandiri)"
                    else:
                        label_tier = f"Tier {i+1} (Berkembang)"
                    
                    html_legend_items += f'<i style="background:{WARNA_PALET[i]}; width: 15px; height: 15px; float: left; margin-right: 5px; border: 1px solid black;"></i> <span style="color: black;">{label_tier}</span><br>'
                
                legend_html = f'''
                <div style="position: fixed; bottom: 50px; left: 50px; width: 170px; border:2px solid grey; z-index:9999; font-size:14px; background-color:white; color:black; opacity: 0.9; padding: 10px;">
                     <b style="color:black;">Hierarki Wilayah</b><br>{html_legend_items}
                </div>
                '''
                m.get_root().html.add_child(folium.Element(legend_html))
                
                def penentu_warna(fitur):
                    kid = fitur['properties'].get('KLASTER_ID')
                    if pd.isna(kid): return {'fillColor': '#bdc3c7', 'color': 'black', 'weight': 1, 'fillOpacity': 0.4}
                    return {'fillColor': WARNA_PALET[int(kid)], 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}
                
                folium.GeoJson(
                    peta_gabungan,
                    style_function=penentu_warna,
                    tooltip=folium.GeoJsonTooltip(fields=['NAME_2', 'STATUS', 'REKOMENDASI_INVESTASI'], aliases=['Wilayah:', 'Diagnosis:', 'Rekomendasi Strategis:'], localize=True)
                ).add_to(m)
                peta_berhasil = True
            except Exception as e:
                peta_berhasil = False
                pesan_error = e

            st.markdown("---")
            st.success(f"Komputasi Selesai! Mesin telah membagi pemerataan data menjadi **{c_input} Cluster** hierarki evaluasi.")
            
            st.subheader("📈 Ringkasan Validitas Mesin")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Wilayah Dievaluasi", f"{len(data_hasil)} Kota/Kab")
            m2.metric("Hierarki Klasifikasi", f"{c_input}")
            m3.metric("Skor Silhouette (Separasi)", f"{skor_silhouette:.4f}")
            m4.metric("Partition Coefficient (FPC)", f"{skor_pc:.4f}")
            
            st.markdown("#### 📊 Distribusi Wilayah per Tingkatan")
            kolom_dinamis = st.columns(c_input)
            
            for i in range(c_input):
                jumlah_wilayah = len(data_hasil[data_hasil['KLASTER_ID'] == i])
                persentase = (jumlah_wilayah / len(data_hasil)) * 100
                nama_tier = "Tier 1" if i == 0 else (f"Tier {c_input}" if i == c_input-1 else f"Tier {i+1}")
                kolom_dinamis[i].metric(
                    label=nama_tier, 
                    value=f"{jumlah_wilayah} Daerah", 
                    delta=f"{persentase:.1f}% Nasional", 
                    delta_color="off"
                )
            
            st.write("<br>", unsafe_allow_html=True)
            
            tab_peta, tab_list, tab_radar, tab_eval = st.tabs(["🗺️ Peta Geospasial", "📑 Laporan Wilayah", "📊 Profil Dimensi", "⚙️ Metrik Centroid"])
            
            with tab_peta:
                if peta_berhasil:
                    st_folium(m, width=1200, height=500, returned_objects=[])
                else:
                    st.error(f"Gagal merender peta. Detail error: {pesan_error}")
                    
            with tab_list:
                df_laporan = data_hasil[['PROV', 'KAB_KOT', 'STATUS', 'REKOMENDASI_INVESTASI']].copy()
                df_laporan = df_laporan.sort_values(by=['STATUS', 'PROV'], ascending=[True, True])
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_laporan.to_excel(writer, index=False, sheet_name='Laporan_BTS')
                
                st.download_button(label="📥 Ekspor Daftar Wilayah (.xlsx)", data=buffer.getvalue(), file_name="Laporan_Pemerataan_BTS.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
                st.dataframe(df_laporan, use_container_width=True)

            with tab_radar:
                st.write("### Profil Multidimensional Menggunakan Radar Chart")
                col_r1, col_r2 = st.columns([2, 1])
                
                with col_r1:
                    fig = go.Figure()
                    nama_fitur_tampil = ['Demografi', 'Jangkauan', 'Kapasitas', 'Ekonomi', 'Literasi']
                    
                    for i, (index_klaster, baris) in enumerate(tabel_centroid.iterrows()):
                        fig.add_trace(go.Scatterpolar(r=baris.values, theta=nama_fitur_tampil, fill='toself', name=index_klaster, line_color=WARNA_PALET[i]))

                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True, title=f"Distribusi Fitur Dominan (C={c_input})")
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("*Catatan: Pemetaan spasial klaster wilayah terinspirasi dari metodologi Handhayani et al. (2026). Sementara itu, Radar Chart ditambahkan secara khusus oleh peneliti untuk membedah karakteristik centroid matriks secara multidimensional.*")
                    
                with col_r2:
                    st.write("### Penentu Diagnosis Hierarki")
                    for nama_kl, penjelasan in penjelasan_klaster.items():
                        st.info(f"**{nama_kl}**\n{penjelasan}")

            with tab_eval:
                st.write("### Matriks Titik Pusat (Centroid Vector)")
                st.dataframe(tabel_centroid, use_container_width=True)

# =========================================================================
# REVISI: PENAMBAHAN FAKTA PERMASALAHAN & REVIEW 5 FITUR
# =========================================================================
elif menu == "ℹ️ Tentang Sistem":
    st.title("Informasi Penelitian & Pengembang")
    
    st.header("Latar Belakang Permasalahan")
    st.write("Pembangunan infrastruktur BTS di Indonesia selama ini sering kali dievaluasi hanya berdasarkan kuantitas menara per wilayah. Fakta di lapangan menunjukkan bahwa pendekatan sepihak ini memicu dua anomali spasial utama:")
    st.write("1. **Bias Spasial & Kesenjangan (Blank Spot):** Ekspansi komersial provider cenderung memusat di wilayah perkotaan yang memiliki jaminan *Return on Investment* (ROI) tinggi, sementara daerah pelosok ditinggalkan tanpa akses sinyal sama sekali.")
    st.write("2. **Anomali Kemacetan Jaringan (Network Congestion):** Di sisi lain, pada beberapa daerah padat penduduk, infrastruktur BTS mungkin sudah ada, namun beban rasio pengguna terhadap kapasitas menara sudah tidak proporsional, menyebabkan jaringan internet lambat.")
    
    st.header("Penetapan 5 Fitur Ekstraksi")
    st.write("Untuk menyelesaikan masalah di atas secara objektif, SPK ini menggunakan algoritma Fuzzy C-Means untuk mengevaluasi pemerataan infrastruktur berdasarkan 5 (lima) dimensi komprehensif:")
    
    st.markdown("""
    * **1. Kepadatan Demografi:** Kunci utama untuk memetakan konsentrasi beban populasi (*Demand*).
    * **2. Kepadatan Jangkauan:** Mewakili luas jangkauan sinyal di daratan fisik (Deteksi *Blank Spot*).
    * **3. Kapasitas Teletrafik:** Mengukur rasio kekuatan BTS menampung jumlah penduduk (Deteksi *Congestion*).
    * **4. Kapasitas Ekonomi (PDRB):** Mengukur tingkat daya beli masyarakat untuk menentukan rekomendasi bisnis (Target Swasta vs Subsidi Negara USO).
    * **5. Literasi Digital (HLS):** Representasi kesiapan tingkat edukasi masyarakat dalam mengadopsi akses internet.
    """)
    
    st.markdown("---")
    st.subheader("Data Pengembang")
    st.write("**Judul Skripsi:** Analisis Pemerataan Pembangunan BTS Menggunakan Algoritma Fuzzy C-Means")
    st.write("**Disusun Oleh:** Jonathan (535220026)")
    st.write("**Program Studi:** Teknik Informatika, Universitas Tarumanagara (2026)")
    st.write("**Dosen Pembimbing:** Dr. Bagus Mulyawan, S.Kom., M.M.")

if __name__ == "__main__":
    pass