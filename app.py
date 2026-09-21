import streamlit as st
import requests
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Avrupa Kupaları Hızlı Arşiv", page_icon="⚽", layout="wide")

# API-Football Anahtarınız
API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"

# Maçkolik Tarzı Karanlık Tema Tasarımı (CSS)
st.markdown("""
<style>
    .stApp {
        background-color: #0e0f11;
        color: #ffffff;
    }
    .stSelectbox div {
        background-color: #1a1b1e !important;
        color: #ffffff !important;
        border: 1px solid #2d2f34 !important;
        border-radius: 8px !important;
    }
    .summary-card {
        background-color: #121315;
        border: 1px solid #2e7d32;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        font-family: sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ UEFA Avrupa & Konferans Ligi 5 Yıllık Hızlı Maç Arşivi (2021 - 2026)")
st.caption("Bekleme yapmadan, UEFA turnuva maçlarını ve istatistiklerini anında Excel'e (CSV) aktar.")

SEZON_SECENEKLERI = {
    "🗓️ TÜM SEZONLAR (2021 - 2026)": "ALL",
    "2026": 2026,
    "2025": 2025,
    "2024": 2024,
    "2023": 2023,
    "2022": 2022,
    "2021": 2021
}

# Hızlı Veri Çekme Fonksiyonu (Avrupa Ligi ID: 3, Konferans Ligi ID: 848)
@st.cache_data(ttl=86400)
def api_avrupa_kupalari_getir(api_key, sezon):
    headers = {
        'x-apisports-key': api_key,
        'x-rapidapi-key': api_key
    }
    ligler = [3, 848]  # 3: Avrupa Ligi, 848: Konferans Ligi
    maclar = []

    for lig_id in ligler:
        url_fixtures = f"https://v3.football.api-sports.io/fixtures?league={lig_id}&season={sezon}"
        try:
            res_fix = requests.get(url_fixtures, headers=headers)
            data_fix = res_fix.json()
            fixtures_raw = data_fix.get("response", [])
            
            for item in fixtures_raw:
                f = item["fixture"]
                l = item["league"]
                t = item["teams"]
                g = item["goals"]
                score = item["score"]

                if f["status"]["short"] in ["FT", "AET", "PEN"]:
                    ev_gol = g["home"] if g["home"] is not None else 0
                    dep_gol = g["away"] if g["away"] is not None else 0
                    toplam_gol = ev_gol + dep_gol

                    ms_sonuc = "1" if ev_gol > dep_gol else ("2" if dep_gol > ev_gol else "X")
                    kg_var = (ev_gol > 0) and (dep_gol > 0)

                    maclar.append({
                        "Tarih": f["date"][:10],
                        "Sezon": sezon,
                        "Kupa / Lig": l["name"],
                        "Ev Sahibi": t["home"]["name"],
                        "Deplasman": t["away"]["name"],
                        "MS Skor": f"{ev_gol} - {dep_gol}",
                        "IY Skor": f"{score['halftime']['home'] or 0} - {score['halftime']['away'] or 0}",
                        "MS Sonucu": ms_sonuc,
                        "Toplam Gol": toplam_gol,
                        "KG Var": "Evet" if kg_var else "Yok"
                    })
        except Exception:
            continue
            
    return maclar

# Sol Menü
st.sidebar.header("⚙️ Hızlı Arşiv Ayarları")
secilen_sezon_key = st.sidebar.selectbox("Sezon / Yıl Aralığı Seçin", list(SEZON_SECENEKLERI.keys()))
secim_degeri = SEZON_SECENEKLERI[secilen_sezon_key]

st.sidebar.markdown("---")
if st.sidebar.button("⚡ Avrupa Kupaları Hızlı Arşivi Derle", type="primary"):
    hedef_sezonlar = [2026, 2025, 2024, 2023, 2022, 2021] if secim_degeri == "ALL" else [secim_degeri]
    
    tum_toplanan_maclar = []
    with st.spinner("UEFA Avrupa ve Konferans Ligi maçları hızla yükleniyor..."):
        for s in hedef_sezonlar:
            m_list = api_avrupa_kupalari_getir(API_KEY, s)
            tum_toplanan_maclar.extend(m_list)
            
    st.session_state['avrupa_hizli_arsiv'] = tum_toplanan_maclar
    st.session_state['aktif_secim_adi'] = secilen_sezon_key

# Hafızada maç varsa göster ve Excel İndir butonu sun
if 'avrupa_hizli_arsiv' in st.session_state and st.session_state['avrupa_hizli_arsiv']:
    arsiv = st.session_state['avrupa_hizli_arsiv']
    toplam_mac = len(arsiv)
    
    if toplam_mac > 0:
        df = pd.DataFrame(arsiv)
        
        # CSV Verisi Hazırlığı
        csv_verisi = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        dosya_adi = f"UEFA_AvrupaKonferans_HizliArsiv_{st.session_state['aktif_secim_adi'].replace(' ', '_')}.csv"

        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"🎉 UEFA Avrupa Kupaları için toplam **{toplam_mac} adet maç** başarıyla ve anında derlendi!")
        with col2:
            st.download_button(
                label="📥 Excel (CSV) İndir",
                data=csv_verisi,
                file_name=dosya_adi,
                mime="text/csv",
                type="primary"
            )

        # Özet İstatistikler
        ms1_sayisi = len(df[df['MS Sonucu'] == '1'])
        ms0_sayisi = len(df[df['MS Sonucu'] == 'X'])
        ms2_sayisi = len(df[df['MS Sonucu'] == '2'])
        ust_sayisi = len(df[df['Toplam Gol'] > 2.5])
        kg_sayisi = len(df[df['KG Var'] == 'Evet'])

        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size: 16px; font-weight: bold; color: #81c784; margin-bottom: 6px;">
                📊 UEFA Avrupa Kupaları — {st.session_state['aktif_secim_adi']} Genel İstatistikler
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; font-size: 13px; margin-top: 10px;">
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">Toplam Maç: {toplam_mac}</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 1: %{round(ms1_sayisi/toplam_mac*100)} ({ms1_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS X: %{round(ms0_sayisi/toplam_mac*100)} ({ms0_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 2: %{round(ms2_sayisi/toplam_mac*100)} ({ms2_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">2.5 Üst: %{round(ust_sayisi/toplam_mac*100)}</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">KG Var: %{round(kg_sayisi/toplam_mac*100)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("📋 Arşiv Tablosu Önizlemesi")
        st.dataframe(df, use_container_width=True, height=450)
    else:
        st.warning("⚠️ Seçilen kriterde maç bulunamadı.")
else:
    st.info("👈 Sol menüden **'TÜM SEZONLAR (2021 - 2026)'** veya istediğin yılı seçip **'Avrupa Kupaları Hızlı Arşivi Derle'** butonuna basarak anında indirebilirsin.")
