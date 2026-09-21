import streamlit as st
import pandas as pd
import glob

# Sayfa Ayarları
st.set_page_config(page_title="Futbol Maç ve Oran Arşivi", page_icon="⚽", layout="wide")

st.title("⚽ 22 Lig - Maç ve Oran Analiz Paneli")

# Klasördeki CSV dosyalarını bul
dosyalar = glob.glob("*_HizliArsiv_*.csv")
if not dosyalar:
    dosyalar = glob.glob("*.csv")

if not dosyalar:
    st.warning("⚠️ Hiç CSV dosyası bulunamadı! Lütfen CSV dosyalarının oran-analiz deposuna yüklendiğinden emin ol.")
else:
    # Sol Menüden Lig Seçimi
    st.sidebar.header("⚙️ Lig Seçimi")
    secilen_dosya = st.sidebar.selectbox("Görüntülenecek Ligi Seçin", dosyalar)
    
    # Dosyayı Oku
    df = pd.read_csv(secilen_dosya)
    
    st.success(f"📂 Seçilen Lig: {secilen_dosya.split('_')[0]} | Toplam Maç: {len(df)}")
    
    # Takım Arama Alanı
    st.sidebar.subheader("🔍 Takım Ara")
    aranan_takim = st.sidebar.text_input("Ev Sahibi veya Deplasman Ara:")
    
    if aranan_takim:
        df = df[df['Ev Sahibi'].str.contains(aranan_takim, case=False, na=False) | 
                df['Deplasman'].str.contains(aranan_takim, case=False, na=False)]
    
    # Tabloyu Göster
    st.subheader("📊 Maç Listesi ve Sonuçları")
    st.dataframe(df, use_container_width=True)
        
    # İndirme Butonu
    csv_veri = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Bu Ligin Verilerini İndir (CSV)",
        data=csv_veri,
        file_name=f"filtrelenmis_{secilen_dosya}",
        mime="text/csv",
    )
