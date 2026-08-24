import io
import matplotlib.pyplot as plt

# 2. Streamlit butonu temiz ve parametre hatası olmadan çağrılmalı
st.download_button(
    label="📥 Tabloyu PNG Olarak İndir (X Formatı)",
    data=png_buffer,
    file_name="bist_finansal_ozet.png",
    mime="image/png",
)
import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="BIST Gelişmiş Day-Trading & AI Analiz Komuta Merkezi", layout="wide")

st.title("⚡ BIST Gelişmiş Day-Trading & AI Analiz Komuta Merkezi")
st.caption("Kısa Vadeli Günlük Al-Sat Önerileri, Detaylı İndikatör Analizleri, Yapay Zeka Yorumları ve 1 Yıllık Projeksiyonlar")

# BIST Takip ve Tarama Listesi
BIST_TAKIP_LISTESI = {
    "FROTO": "Ford Otosan - Elektrikli araç dönüşümü, Romanya Craiova yatırımları ve güçlü ihracat yapısı.",
    "ISMEN": "İş Yatırım - Borsa işlem hacimlerinden yüksek komisyon geliri ve güçlü özkaynak kârlılığı.",
    "ANHYT": "Anadolu Hayat - BES fon büyüklüğü, yüksek faiz ortamında artan net yatırım gelirleri.",
    "ARDYZ": "ARD Grup Bilişim - Siber güvenlik ve yazılım ihracatı, yüksek net kâr marjı ve düşük borçluluk.",
    "ALTNY": "Altınay Savunma - Savunma sanayii Ar-Ge projeleri ve yüksek sipariş bakiyesi.",
    "YEOTK": "Yeo Teknoloji - Yenilenebilir enerji, GES/RES projeleri ve batarya depolama yatırımları.",
    "KCHOL": "Koç Holding - Lider iştirak portföyü, net aktif değer iskontosu ve güçlü döviz pozisyonu.",
    "THYAO": "Türk Hava Yolları - Güçlü yolcu/kargo trafiği, geniş uçuş ağı ve yüksek döviz girdisi.",
    "TUPRS": "Tüpraş - Yüksek rafineri marjları, stratejik dönüşüm ve düzenli temettü verimi.",
    "ASELS": "Aselsan - Savunma sanayii liderliği, rekor bakiye siparişler ve yüksek Ar-Ge kapasitesi.",
    "SAHOL": "Sabancı Holding - Yenilenebilir enerji ve küresel yatırımlar, yüksek iskonto.",
    "EREGL": "Ereğli Demir Çelik - Yeşil çelik dönüşümü, cevher madencilik yatırımları.",
    "SOKM": "Şok Marketler - Güçlü nakit akışı ve perakende büyüme dinamikleri.",
    "AGHOL": "Anadolu Grubu Holding - İçecek, perakende ve otomotiv sektörlerinde dengeli portföy.",
    "ALARK": "Alarko Holding - Tarım/GES yatırımları ve güçlü nakit pozisyonu."
}

# Veri Çekme Fonksiyonu
@st.cache_data(ttl=300)
def veri_getir(symbol, period="1y", interval="1d"):
    for _ in range(3):
        try:
            df_raw = yf.download(symbol, period=period, interval=interval, progress=False)
            if not df_raw.empty and len(df_raw) > 10:
                return df_raw
        except Exception:
            time.sleep(0.5)
    return pd.DataFrame()

# USD Kuru Çek
df_usd = veri_getir("USDTRY=X")
if not df_usd.empty and 'Close' in df_usd.columns:
    val_usd = df_usd['Close'].iloc[-1]
    usd_kur = float(val_usd.values[0] if hasattr(val_usd, 'values') else val_usd)
else:
    usd_kur = 34.0

# Sekme Yapısı
tab_oneriler, tab_detay, tab_tarama, tab_bulten = st.tabs([
    "🔥 Günlük Al-Sat & Short-Term Öneriler",
    "📊 Detaylı Hisse & AI Analiz Komuta Merkezi",
    "🚀 BIST 15 Otomatik Sıkışma & Trend Taraması",
    "📱 X (Twitter) Bülten Üretici"
])

# ==========================================
# SEKME 1: GÜNLÜK AL-SAT ÖNERİLERİ
# ==========================================
with tab_oneriler:
    st.header("🎯 Kısa Vadeli Günlük Al-Sat Öneri Paneli")
    st.info("Aşağıdaki liste BIST hisselerinin RSI, MACD, Bollinger Sıkışması, Moving Average çaprazlamaları ve hacim trendleri yapay zeka algoritmalarınca taranarak oluşturulmuştur.")
    
    with st.spinner("Tüm takip listesi taranıyor ve gün içi al-sat fırsatları hesaplanıyor..."):
        oneriler_data = []
        
        for kod, hikaye in BIST_TAKIP_LISTESI.items():
            h_sym = f"{kod}.IS"
            df_h = veri_getir(h_sym)
            
            if not df_h.empty and len(df_h) > 30:
                if isinstance(df_h.columns, pd.MultiIndex):
                    cp = df_h['Close'][h_sym]
                    hp = df_h['High'][h_sym]
                    lp = df_h['Low'][h_sym]
                    vol = df_h['Volume'][h_sym]
                else:
                    cp, hp, lp, vol = df_h['Close'], df_h['High'], df_h['Low'], df_h['Volume']
                
                son_f = float(cp.iloc[-1].values[0] if hasattr(cp.iloc[-1], 'values') else cp.iloc[-1])
                son_h = float(hp.iloc[-1].values[0] if hasattr(hp.iloc[-1], 'values') else hp.iloc[-1])
                son_l = float(lp.iloc[-1].values[0] if hasattr(lp.iloc[-1], 'values') else lp.iloc[-1])
                
                # RSI
                delta = cp.diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi_v = float((100 - (100 / (1 + rs))).iloc[-1])
                
                # SMA
                sma20 = float(cp.rolling(20).mean().iloc[-1])
                sma50 = float(cp.rolling(50).mean().iloc[-1])
                
                # ATR
                tr1 = hp - lp
                tr2 = abs(hp - cp.shift())
                tr3 = abs(lp - cp.shift())
                tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                atr = float(tr.rolling(14).mean().iloc[-1])
                
                # Bollinger Band
                std20 = float(cp.rolling(20).std().iloc[-1])
                upper_bb = sma20 + (2 * std20)
                lower_bb = sma20 - (2 * std20)
                bb_width = (upper_bb - lower_bb) / sma20
                
                # Sinyal Skorlama
                skor = 0
                if rsi_v < 38: skor += 2
                elif rsi_v < 50: skor += 1
                elif rsi_v > 70: skor -= 2
                
                if son_f > sma20: skor += 1
                if son_f > sma50: skor += 1
                if bb_width < 0.08: skor += 1.5 # Sıkışma patlaması
                
                # Öneri Statüsü
                if skor >= 3.5:
                    durum = "🔥 GÜÇLÜ AL"
                    vade = "1-3 Gün (Day Trade / Scalp)"
                elif skor >= 2.0:
                    durum = "🟢 KADEMELİ AL"
                    vade = "3-7 Gün (Swing Trade)"
                elif skor >= 0:
                    durum = "⚪ TUT / İZLE"
                    vade = "Nötr"
                else:
                    durum = "🔴 SAT / DÜZELTME"
                    vade = "Kısa Vadeli Risk"
                
                stop_l = son_f - (atr * 1.5)
                tp1 = son_f + (atr * 1.5)
                tp2 = son_f + (atr * 3.0)
                
                oneriler_data.append({
                    "Hisse": kod,
                    "Son Fiyat": f"{son_f:.2f} TL",
                    "Sinyal / Durum": durum,
                    "İdeal Alım Aralığı": f"{son_f*0.995:.2f} - {son_f:.2f} TL",
                    "Stop-Loss (-1.5 ATR)": f"{stop_l:.2f} TL",
                    "Kâr Al 1 (+1.5 ATR)": f"{tp1:.2f} TL",
                    "Kâr Al 2 (+3.0 ATR)": f"{tp2:.2f} TL",
                    "RSI (14)": f"{rsi_v:.1f}",
                    "Önerilen Vade": vade,
                    "Potansiyel Getiri (TP1)": f"%{((tp1-son_f)/son_f)*100:.1f}"
                })
        
        df_oneriler = pd.DataFrame(oneriler_data)
        st.dataframe(df_oneriler, use_container_width=True)

# ==========================================
# SEKME 2: DETAYLI HİSSE & AI ANALİZ KOMUTA MERKEZİ
# ==========================================
with tab_detay:
    col_sec, col_yaz = st.columns([1, 1])
    with col_sec:
        secilen_hazir = st.selectbox("Analiz Edilecek Hisse Seçin:", list(BIST_TAKIP_LISTESI.keys()))
    with col_yaz:
        girilen_hisse = st.text_input("Veya Başka BIST Kodu Girin (Örn: THYAO, TUPRS):", value="").strip().upper()

    girilen_kod = girilen_hisse if girilen_hisse else secilen_hazir
    hisse_symbol = f"{girilen_kod}.IS" if not girilen_kod.endswith(".IS") else girilen_kod

    if st.button(f"🚀 {girilen_kod} İçin Detaylı AI Analizini Çalıştır"):
        with st.spinner(f"{girilen_kod} verileri işleniyor..."):
            df = veri_getir(hisse_symbol)
            ticker_obj = yf.Ticker(hisse_symbol)
            try:
                info_data = ticker_obj.info
            except:
                info_data = {}

            if not df.empty and len(df) > 20:
                if isinstance(df.columns, pd.MultiIndex):
                    cp, op, hp, lp = df['Close'][hisse_symbol], df['Open'][hisse_symbol], df['High'][hisse_symbol], df['Low'][hisse_symbol]
                else:
                    cp, op, hp, lp = df['Close'], df['Open'], df['High'], df['Low']

                son_f = float(cp.iloc[-1].values[0] if hasattr(cp.iloc[-1], 'values') else cp.iloc[-1])
                son_h = float(hp.iloc[-1].values[0] if hasattr(hp.iloc[-1], 'values') else hp.iloc[-1])
                son_l = float(lp.iloc[-1].values[0] if hasattr(lp.iloc[-1], 'values') else lp.iloc[-1])
                son_usd = son_f / usd_kur
                bugun = datetime.now()

                # İndikatörler
                delta = cp.diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = float((100 - (100 / (1 + rs))).iloc[-1])

                sma50 = float(cp.rolling(50).mean().iloc[-1]) if len(cp) >= 50 else son_f
                sma200 = float(cp.rolling(200).mean().iloc[-1]) if len(cp) >= 200 else son_f
                volatility = float(cp.pct_change().dropna().std())

                tr1 = hp - lp
                tr2 = abs(hp - cp.shift())
                tr3 = abs(lp - cp.shift())
                tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                atr = float(tr.rolling(14).mean().iloc[-1])

                # Temel Skor
                fk = info_data.get('trailingPE', None)
                pddd = info_data.get('priceToBook', None)
                kar_marji = info_data.get('profitMargins', None)
                roe = info_data.get('returnOnEquity', None)

                temel_puan = 5
                if fk and fk > 0:
                    if fk < 8: temel_puan += 2
                    elif fk < 15: temel_puan += 1
                    elif fk > 30: temel_puan -= 1
                if pddd and pddd > 0:
                    if pddd < 1.5: temel_puan += 2
                    elif pddd < 3.0: temel_puan += 1
                    elif pddd > 6.0: temel_puan -= 1
                if roe:
                    if roe > 0.30: temel_puan += 1
                    elif roe < 0: temel_puan -= 1
                temel_puan = max(1, min(10, temel_puan))

                stop_l = son_f - (atr * 1.5)
                tp1 = son_f + (atr * 1.5)
                tp2 = son_f + (atr * 3.0)

                # Metrik Kartları
                st.subheader(f"📊 {girilen_kod} Metrik Özeti")
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Son Fiyat (TL)", f"{son_f:.2f} TL")
                m2.metric("Son Fiyat (USD)", f"${son_usd:.2f}")
                m3.metric("Temel Sağlık Skoru", f"{temel_puan} / 10")
                m4.metric("RSI (14)", f"{rsi:.1f}")
                m5.metric("Günlük ATR Volatilite", f"{atr:.2f} TL")

                # AI Detaylı Yorum
                st.subheader("💡 Yapay Zeka Detaylı Bütünleşik Yorumu")
                ai_text = f"""
                ### 🤖 {girilen_kod} Yapay Zeka Sentez Raporu:
                - **Kısa Vadeli Fiyat Aksiyonu:** {girilen_kod} şu an **{son_f:.2f} TL** seviyesinde işlem görmekte. Gün içi oynaklığı temsil eden ATR değeri **{atr:.2f} TL**'dir.
                - **Teknik Momentum ve İndikatörler:** RSI **{rsi:.1f}** seviyesindedir. Fiyat 50 günlük ortalamanın ({sma50:.2f} TL) {'üzerinde seyretmektedir (Pozitif Momentum)' if son_f > sma50 else 'altında seyretmektedir (Zayıf Trend)'}.
                - **Günlük Al-Sat Trade Stratejisi:** 
                  - **Alım Bölgesi:** {son_f*0.995:.2f} TL - {son_f:.2f} TL
                  - **Stop-Loss (Zarar Kes):** {stop_l:.2f} TL (Olası kayıp: %{((son_f-stop_l)/son_f)*100:.1f})
                  - **Kâr Al 1 (Gün İçi Hedef):** {tp1:.2f} TL (Potansiyel getiri: %{((tp1-son_f)/son_f)*100:.1f})
                  - **Kâr Al 2 (Swing Hedef):** {tp2:.2f} TL (Potansiyel getiri: %{((tp2-son_f)/son_f)*100:.1f})
                - **Temel Değerlendirme:** Şirket 10 üzerinden **{temel_puan}** temel sağlık puanına sahiptir. F/K: {f'{fk:.2f}' if fk else 'N/A'}, PD/DD: {f'{pddd:.2f}' if pddd else 'N/A'}.
                """
                st.info(ai_text)

                # Gelecek 1 Yıl Tahmini
                st.subheader("📅 Gelecek 1 Yılın AI Fiyat Tahmin Grafiği (365 Gün)")
                gelecek_tarihler = [bugun + timedelta(days=i) for i in range(1, 366)]
                gunler = np.arange(1, 366)
                trend_egilimi = 0.0008 if rsi > 45 else -0.0002
                tahmin_fiyatlari = son_f * (1 + trend_egilimi) ** gunler
                ust_tahmin = son_f * np.exp(trend_egilimi * gunler + volatility * np.sqrt(gunler) * 1.5)
                alt_tahmin = son_f * np.exp(trend_egilimi * gunler - volatility * np.sqrt(gunler) * 1.5)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=cp, mode='lines', name='Geçmiş Fiyat (TL)', line=dict(color='white', width=2)))
                fig.add_trace(go.Scatter(x=gelecek_tarihler, y=ust_tahmin, mode='lines', line=dict(width=0), showlegend=False))
                fig.add_trace(go.Scatter(x=gelecek_tarihler, y=alt_tahmin, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(46, 204, 113, 0.15)', name='%80 Olasılık Bandı'))
                fig.add_trace(go.Scatter(x=gelecek_tarihler, y=tahmin_fiyatlari, mode='lines', line=dict(color='cyan', dash='dash', width=2.5), name='1 Yıllık AI Tahmin Patikası'))
                fig.update_layout(template="plotly_dark", title=f"{girilen_kod} - 1 Yıllık AI Projeksiyonu", height=450)
                st.plotly_chart(fig, use_container_width=True)

                y1, y2, y3 = st.columns(3)
                y1.metric("1 Yıl Alt Bant (Ayı)", f"{alt_tahmin[-1]:.2f} TL")
                y2.metric("1 Yıl Baz AI Hedefi", f"{tahmin_fiyatlari[-1]:.2f} TL", delta=f"%{((tahmin_fiyatlari[-1]-son_f)/son_f)*100:.1f}")
                y3.metric("1 Yıl Üst Bant (Boğa)", f"{ust_tahmin[-1]:.2f} TL")

# ==========================================
# SEKME 3: TARAMA
# ==========================================
with tab_tarama:
    st.header("🚀 BIST 15 Hisse Taraması ve Sıkışma Analizi")
    tarama_data = []
    for h_kod, hikaye in BIST_TAKIP_LISTESI.items():
        df_t = veri_getir(f"{h_kod}.IS")
        if not df_t.empty and len(df_t) > 20:
            cp_t = df_t['Close'][f"{h_kod}.IS"] if isinstance(df_t.columns, pd.MultiIndex) else df_t['Close']
            fiy_t = float(cp_t.iloc[-1].values[0] if hasattr(cp_t.iloc[-1], 'values') else cp_t.iloc[-1])
            ma20 = cp_t.rolling(20).mean()
            std20 = cp_t.rolling(20).std()
            bw = float(((ma20 + 2*std20 - (ma20 - 2*std20)) / ma20).iloc[-1])
            sikisma = "🔥 Sıkışma Var (Patlama Yakın)" if bw < 0.08 else "Normal Süzülme"
            tarama_data.append({
                "Hisse": h_kod,
                "Fiyat": f"{fiy_t:.2f} TL",
                "USD Fiyat": f"${(fiy_t/usd_kur):.2f}",
                "Bollinger Sıkışma Durumu": sikisma,
                "Şirket Hikayesi": hikaye
            })
    st.table(pd.DataFrame(tarama_data))

# ==========================================
# SEKME 4: X BÜLTEN
# ==========================================
with tab_bulten:
    st.header("📱 X (Twitter) Borsa Bülten Üretici")
    sec_b = st.selectbox("Bülten Oluşturulacak Hisse:", list(BIST_TAKIP_LISTESI.keys()))
    if st.button("Bülten Taslağı Üret"):
        df_b = veri_getir(f"{sec_b}.IS")
        if not df_b.empty:
            cp_b = df_b['Close'][f"{sec_b}.IS"] if isinstance(df_b.columns, pd.MultiIndex) else df_b['Close']
            f_b = float(cp_b.iloc[-1].values[0] if hasattr(cp_b.iloc[-1], 'values') else cp_b.iloc[-1])
            tweet = f"""📊 #{sec_b} Günlük Trade & Fiyat Analizi

💰 Son Fiyat: {f_b:.2f} TL (${f_b/usd_kur:.2f})
🎯 Gün İçi Al-Sat Seviyeleri:
• İdeal Alım: {f_b*0.995:.2f} - {f_b:.2f} TL
• Stop-Loss: {f_b*0.975:.2f} TL
• Kâr Al 1: {f_b*1.025:.2f} TL
• Kâr Al 2: {f_b*1.05:.2f} TL

#BIST100 #Borsa #Hisse #{sec_b}"""
           # 1. Tweet metnini gösteren kısım
st.code(tweet, language="text")

# 2. Görsel oluşturmak için gerekli kütüphaneler (Ayrı satırda olmalı!)
import io
import matplotlib.pyplot as plt


# 3. PNG Tablo Oluşturucu Fonksiyon
def generate_table_image(df, title="Bilanço Özeti"):
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=300)
    fig.patch.set_facecolor("#15202B")
    ax.set_facecolor("#15202B")
    ax.axis("off")

    plt.title(
        title,
        color="#FFFFFF",
        fontsize=18,
        fontweight="bold",
        pad=20,
        loc="center",
    )

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#38444D")
        if row == 0:
            cell.set_facecolor("#1DA1F2")
            cell.get_text().set_color("#FFFFFF")
            cell.get_text().set_weight("bold")
            cell.get_text().set_fontsize(12)
        else:
            bg_color = "#192734" if row % 2 == 0 else "#253341"
            cell.set_facecolor(bg_color)
            cell.get_text().set_color("#E1E8ED")

    plt.text(
        0.98,
        0.02,
        "@trader_gandalf | Borsa İstanbul Analiz",
        transform=ax.transAxes,
        color="#8899A6",
        fontsize=10,
        ha="right",
        va="bottom",
        fontstyle="italic",
    )

    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(
        img_buffer,
        format="png",
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        dpi=300,
    )
    img_buffer.seek(0)
    plt.close(fig)

    return img_buffer


# 4. İndirme Butonu
png_buffer = generate_table_image(
    df_summary, title="BIST Şirketleri Temel Değerlendirme Tablosu"
)

st.download_button(
    label="📥 Tabloyu PNG Olarak İndir (X Formatı)",
    data=png_buffer,
    file_name="bist_finansal_ozet.png",
    mime="image/png",
)
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def generate_table_image(df: pd.DataFrame, title: str = "Bilanço Özeti") -> io.BytesIO:
    """Pandas DataFrame verisini X (Twitter) paylaşımına uygun,

    koyu temalı yüksek kaliteli bir PNG görseline dönüştürür.
    """
    # X/Twitter için 16:9 oranlı canvas hazırlığı (ör. 12x6.75 inç)
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=300)
    fig.patch.set_facecolor("#15202B")  # X Dark Theme Arka Plan Rengi
    ax.set_facecolor("#15202B")
    ax.axis("off")

    # Başlık Ekleme
    plt.title(
        title,
        color="#FFFFFF",
        fontsize=18,
        fontweight="bold",
        pad=20,
        loc="center",
    )

    # Tabloyu Oluşturma
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)  # Hücre boyutları ve dikey genişlik

    # Tablo Hücrelerinin Tasarımı (Dark Mode Estetiği)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#38444D")  # Izgara Çizgisi Rengi

        if row == 0:
            # Header (Başlık) Satırı
            cell.set_facecolor("#1DA1F2")  # X Mavi Rengi
            cell.get_text().set_color("#FFFFFF")
            cell.get_text().set_weight("bold")
            cell.get_text().set_fontsize(12)
        else:
            # Veri Satırları (Alternatif satır renklendirmesi)
            bg_color = "#192734" if row % 2 == 0 else "#253341"
            cell.set_facecolor(bg_color)
            cell.get_text().set_color("#E1E8ED")

    # Alt Bilgi / Imza (Watermark - Filigran)
    plt.text(
        0.98,
        0.02,
        "@trader_gandalf | Borsa İstanbul Analiz",
        transform=ax.transAxes,
        color="#8899A6",
        fontsize=10,
        ha="right",
        va="bottom",
        fontstyle="italic",
    )

    plt.tight_layout()

    # Görseli RAM üzerinde Byte akışına dönüştürme (Diske kaydetmeden doğrudan indirmek için)
    img_buffer = io.BytesIO()
    plt.savefig(
        img_buffer,
        format="png",
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        dpi=300,
    )
    img_buffer.seek(0)
    plt.close(fig)

    return img_buffer


# -------------------------------------------------------------------
# STREAMLIT UYGULAMASI ENTEGRASYON ÖRNEĞİ
# -------------------------------------------------------------------

st.title("📊 Borsa İstanbul Finansal Tablo Oluşturucu")

# Örnek DataFrame Verisi
data = {
    "Hisse": ["FROTO", "ISMEN", "ANHYT", "ARDYZ"],
    "F/K": [8.4, 6.2, 7.1, 9.5],
    "PD/DD": [3.1, 2.4, 2.8, 3.8],
    "Temettü Verimi (%)": ["%6.8", "%8.1", "%5.4", "%1.2"],
    "Net Kar Büyümesi": ["+%24", "+%45", "+%38", "+%52"],
}
df_summary = pd.DataFrame(data)

# Tabloyu Ekran Üzerinde Göster
st.subheader("Tablo Önizleme")
st.dataframe(df_summary, use_container_width=True)

# Görsel İndirme Butonu
st.markdown("---")
st.subheader("📸 X (Twitter) Paylaşım Görseli")

# PNG Akışını Hazırla
png_buffer = generate_table_image(
    df_summary, title="BIST Şirketleri Temel Değerlendirme Tablosu"
)

st.download_button(
    label="📥 Tabloyu PNG Olarak İndir (X Formatı)",
    data=png_buffer,
    file_name="bist_finansal_ozet.png",
    mime="image/png",st.code(tweet, language="text")

# PNG Tablo Oluşturma Fonksiyonu ve Kodları

def generate_table_image(df, title="Bilanço Özeti"):
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=300)
    fig.patch.set_facecolor("#15202B")
    ax.set_facecolor("#15202B")
    ax.axis("off")

    plt.title(
        title,
        color="#FFFFFF",
        fontsize=18,
        fontweight="bold",
        pad=20,
        loc="center",
    )

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#38444D")
        if row == 0:
            cell.set_facecolor("#1DA1F2")
            cell.get_text().set_color("#FFFFFF")
            cell.get_text().set_weight("bold")
            cell.get_text().set_fontsize(12)
        else:
            bg_color = "#192734" if row % 2 == 0 else "#253341"
            cell.set_facecolor(bg_color)
            cell.get_text().set_color("#E1E8ED")

    plt.text(
        0.98,
        0.02,
        "@trader_gandalf | Borsa İstanbul Analiz",
        transform=ax.transAxes,
        color="#8899A6",
        fontsize=10,
        ha="right",
        va="bottom",
        fontstyle="italic",
    )

    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(
        img_buffer,
        format="png",
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        dpi=300,
    )
    img_buffer.seek(0)
    plt.close(fig)

    return img_buffer


# ------------------------------------------
# STREAMLIT INDIRME BUTONU
# (Buradaki df_summary yerine kendi DataFrame değişkeninizi yazın)
# ------------------------------------------
png_buffer = generate_table_image(
    df_summary, title="BIST Şirketleri Temel Değerlendirme Tablosu"
)

st.download_button(
    label="📥 Tabloyu PNG Olarak İndir (X Formatı)",
    data=png_buffer,
    file_name="bist_finansal_ozet.png",
    mime="image/png",
)


def generate_table_image(df, title="Bilanço Özeti"):
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=300)
    fig.patch.set_facecolor("#15202B")
    ax.set_facecolor("#15202B")
    ax.axis("off")

    plt.title(
        title,
        color="#FFFFFF",
        fontsize=18,
        fontweight="bold",
        pad=20,
        loc="center",
    )

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#38444D")
        if row == 0:
            cell.set_facecolor("#1DA1F2")
            cell.get_text().set_color("#FFFFFF")
            cell.get_text().set_weight("bold")
            cell.get_text().set_fontsize(12)
        else:
            bg_color = "#192734" if row % 2 == 0 else "#253341"
            cell.set_facecolor(bg_color)
            cell.get_text().set_color("#E1E8ED")

    plt.text(
        0.98,
        0.02,
        "@trader_gandalf | Borsa İstanbul Analiz",
        transform=ax.transAxes,
        color="#8899A6",
        fontsize=10,
        ha="right",
        va="bottom",
        fontstyle="italic",
    )

    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(
        img_buffer,
        format="png",
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        dpi=300,
    )
    img_buffer.seek(0)
    plt.close(fig)

    return img_buffer


# Indirme Butonu
png_buffer = generate_table_image(
    df_summary, title="BIST Şirketleri Temel Değerlendirme Tablosu"
)

st.download_button(
    label="📥 Tabloyu PNG Olarak İndir (X Formatı)",
    data=png_buffer,
    file_name="bist_finansal_ozet.png",
    mime="image/png",
)
)
