import streamlit as st
import pandas as pd
import glob

# Sayfa Ayarları
st.set_page_config(page_title="Futbol Maç ve Oran Arşivi", page_icon="⚽", layout="wide")

st.title("⚽ 22 Lig - Kapsamlı Maç ve Oran Analiz Paneli")
st.markdown("Bu panel, seçtiğin ligin **ilk yarı ve maç sonu tüm oranlarını** ve maç detaylarını listeler.")

# Klasördeki CSV dosyalarını bul
dosyalar = glob.glob("*_HizliArsiv_*.csv")

if not dosyalar:
    st.warning("⚠️ Klasörde hiç CSV dosyası bulunamadı! Lig dosyalarının bu klasörde olduğundan emin ol.")
else:
    # Sol Menüden Lig Seçimi
    st.sidebar.header("⚙️ Lig ve Filtreleme")
    secilen_dosya = st.sidebar.selectbox("Görüntülenecek Ligi Seçin", dosyalar)
    
    # Dosyayı Oku
    df = pd.read_csv(secilen_dosya)
    
    st.success(f"📂 Seçilen Lig Dosyası: {secilen_dosya} | Toplam Maç Sayısı: {len(df)}")
    
    # Oran kolonlarını akıllıca bulup öne çıkarma veya direkt tüm tabloyu gösterme
    with st.expander("📊 Tüm Verileri ve Oranları Tabloda Gör (Genişlet)", expanded=True):
        st.dataframe(df, use_container_width=True)
        
    # İndirme Butonu
    csv_veri = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Bu Ligin Oranlı Verilerini İndir (CSV)",
        data=csv_veri,
        file_name=f"oranli_{secilen_dosya}",
        mime="text/csv",
    )