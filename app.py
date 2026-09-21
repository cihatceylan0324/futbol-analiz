import streamlit as st
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Avrupa Futbol Arşivi (2021-2026)", page_icon="⚽", layout="wide")

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
    .match-card {
        background-color: #1a1b1e;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
        border: 1px solid #2d2f34;
        font-family: sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Avrupa Futbol Arşivi & Genişletilmiş Maç Listesi (2021 - 2026)")
st.caption("Seçilen ligin 2021'den 2026'ya kadar olan tüm sezonlarını toplu halde listeler.")

# Avrupa'nın önde gelen 20 ligi
LIGLER = {
    "🇹🇷 Türkiye - Süper Lig": 203,
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 İngiltere - Premier League": 39,
    "🇪🇸 İspanya - La Liga": 140,
    "🇮🇹 İtalya - Serie A": 135,
    "🇩🇪 Almanya - Bundesliga": 78,
    "🇫🇷 Fransa - Ligue 1": 61,
    "🇳🇱 Hollanda - Eredivisie": 88,
    "🇵🇹 Portekiz - Liga Portugal": 94,
    "🇧🇪 Belçika - Pro League": 144,
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 İskoçya - Premiership": 179,
    "🇦🇹 Avusturya - Bundesliga": 218,
    "🇨🇭 İsviçre - Super League": 207,
    "🇬🇷 Yunanistan - Super League": 197,
    "🇩🇰 Danimarka - Superliga": 119,
    "🇸🇪 İsveç - Allsvenskan": 113,
    "🇳🇴 Norveç - Eliteserien": 103,
    "🇵🇱 Polonya - Ekstraklasa": 106,
    "🇨🇿 Çekya - 1. Liga": 345,
    "🇭🇷 Hırvatistan - HNL": 210,
    "🇪🇺 UEFA Şampiyonlar Ligi": 2
}

SEZON_SECENEKLERI = {
    "🗓️ TÜM SEZONLAR (2021 - 2026)": "ALL",
    "2026": 2026,
    "2025": 2025,
    "2024": 2024,
    "2023": 2023,
    "2022": 2022,
    "2021": 2021
}

# Tekil Sezon Veri Çekme Fonksiyonu
@st.cache_data(ttl=86400)
def api_maclari_getir_tekil(api_key, lig_id, sezon):
    headers = {
        'x-apisports-key': api_key,
        'x-rapidapi-key': api_key
    }
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?league={lig_id}&season={sezon}"
    try:
        res_fix = requests.get(url_fixtures, headers=headers)
        data_fix = res_fix.json()
        fixtures_raw = data_fix.get("response", [])
        if not fixtures_raw:
            return []

        maclar = []
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
                    "tarih": f["date"][:10],
                    "sezon": sezon,
                    "lig_adi": l["name"],
                    "ev_sahibi": t["home"]["name"],
                    "deplasman": t["away"]["name"],
                    "ms_skor": f"{ev_gol} - {dep_gol}",
                    "iy_skor": f"{score['halftime']['home'] or 0} - {score['halftime']['away'] or 0}",
                    "ms_sonuc": ms_sonuc,
                    "toplam_gol": toplam_gol,
                    "kg_var": kg_var
                })
        return maclar
    except Exception:
        return []

# Sol Menü / Seçimler
st.sidebar.header("🌍 Lig & Sezon Filtresi")
secilen_lig_key = st.sidebar.selectbox("Avrupa Ligi Seçin", list(LIGLER.keys()))
secilen_sezon_key = st.sidebar.selectbox("Sezon / Yıl Seçin", list(SEZON_SECENEKLERI.keys()))

lig_id = LIGLER[secilen_lig_key]
secim_degeri = SEZON_SECENEKLERI[secilen_sezon_key]

st.sidebar.markdown("---")
st.sidebar.info("💡 'TÜM SEZONLAR' seçildiğinde 2021'den 2026'ya kadar oynanan tüm maçlar tek seferde toplanır.")

# Verileri Yükle Butonu
if st.sidebar.button("🔍 Arşivi Getir", type="primary"):
    hedef_sezonlar = [2026, 2025, 2024, 2023, 2022, 2021] if secim_degeri == "ALL" else [secim_degeri]
    
    tum_toplanan_maclar = []
    with st.spinner(f"{secilen_lig_key} için arşiv taranıyor..."):
        for s in hedef_sezonlar:
            m_list = api_maclari_getir_tekil(API_KEY, lig_id, s)
            tum_toplanan_maclar.extend(m_list)
            
    st.session_state['yuklenen_arsiv'] = tum_toplanan_maclar
    st.session_state['aktif_lig'] = secilen_lig_key
    st.session_state['aktif_sezon_bilgi'] = secilen_sezon_key

# Hafızada maç varsa göster
if 'yuklenen_arsiv' in st.session_state and st.session_state['yuklenen_arsiv']:
    arsiv = st.session_state['yuklenen_arsiv']
    toplam_mac = len(arsiv)
    
    if toplam_mac > 0:
        ms1_sayisi = sum(1 for m in arsiv if m['ms_sonuc'] == '1')
        ms0_sayisi = sum(1 for m in arsiv if m['ms_sonuc'] == 'X')
        ms2_sayisi = sum(1 for m in arsiv if m['ms_sonuc'] == '2')
        ust_sayisi = sum(1 for m in arsiv if m['toplam_gol'] > 2.5)
        kg_sayisi = sum(1 for m in arsiv if m['kg_var'])

        # Özet Kartı
        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size: 16px; font-weight: bold; color: #81c784; margin-bottom: 6px;">
                📊 {st.session_state['aktif_lig']} — {st.session_state['aktif_sezon_bilgi']} Arşiv Özeti
            </div>
            <div style="font-size: 15px; color: #fff; margin-bottom: 10px;">
                Toplam Maç Sayısı: <b>{toplam_mac}</b>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; font-size: 13px;">
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 1: %{round(ms1_sayisi/toplam_mac*100)} ({ms1_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS X: %{round(ms0_sayisi/toplam_mac*100)} ({ms0_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 2: %{round(ms2_sayisi/toplam_mac*100)} ({ms2_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">2.5 Üst: %{round(ust_sayisi/toplam_mac*100)}</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">KG Var: %{round(kg_sayisi/toplam_mac*100)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("📋 Toplu Maç Arşivi")
        
        # Performans için son 300 maçı göster (Tümünü aynı anda basmak tarayıcıyı dondurabilir)
        for m in arsiv[:300]:
            st.markdown(f"""
            <div class="match-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 11px; color: #888;">{m['tarih']} ({m['sezon']} Sezonu)</span>
                        <div style="font-size: 15px; font-weight: bold; color: #fff; margin-top: 2px;">
                            {m['ev_sahibi']} <span style="color: #81c784; margin: 0 6px;">vs</span> {m['deplasman']}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background-color: #1e2720; color: #4caf50; font-size: 15px; font-weight: bold; padding: 4px 10px; border-radius: 6px; border: 1px solid #2e7d32;">
                            MS: {m['ms_skor']}
                        </span>
                        <span style="font-size: 11px; color: #aaa; display: block; margin-top: 4px;">(İY: {m['iy_skor']})</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        if len(arsiv) > 300:
            st.info(f"ℹ️ Performans amacıyla listenin ilk 300 maçı gösteriliyor (Toplam eşleşen: {len(arsiv)} maç).")
    else:
        st.warning("⚠️ Bu kriterlere uygun maç bulunamadı.")
else:
    st.info("👈 Sol menüden ligi ve sezonu seçip **'Arşivi Getir'** butonuna basarak binlerce maçı listeyebilirsin.")
