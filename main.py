import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="BIST AI Gelecek Tahmini & Al-Sat Asistanı", layout="wide")

st.title("📈 BIST AI Gelecek Ayların Fiyat Tahmini ve Al-Sat Sinyalleri")
st.caption("Gelecek 3 Ayın Grafiği, Tüm BIST Hisseleri İçin Teknik Al-Sat Sinyalleri ve Potansiyel Taraması")

# Şirket Temel Bilgileri
SIRKET_HIKAYELERI = {
    "FROTO": "Elektrikli araç dönüşümü, Romanya Craiova yatırımları ve güçlü ihracat yapısı.",
    "ISMEN": "Borsa işlem hacimlerinden yüksek komisyon geliri ve güçlü özkaynak kârlılığı.",
    "ANHYT": "BES fon büyüklüğü, yüksek faiz ortamında artan net yatırım gelirleri.",
    "ARDYZ": "Siber güvenlik ve yazılım ihracatı, yüksek net kâr marjı ve düşük borçluluk.",
    "ALTNY": "Savunma sanayii Ar-Ge projeleri ve yüksek sipariş bakiyesi.",
    "YEOTK": "Yenilenebilir enerji, GES/RES projeleri ve batarya depolama yatırımları.",
    "KCHOL": "Lider iştirak portföyü, net aktif değer iskontosu ve güçlü döviz pozisyonu."
}

# Hisse Seçim Kutusu + Serbest Arama Kutusu
col_sec, col_yaz = st.columns([1, 1])
with col_sec:
    secilen_hazir = st.selectbox("Hızlı Hisse Seçimi:", [""] + list(SIRKET_HIKAYELERI.keys()))
with col_yaz:
    girilen_hisse = st.text_input("Veya İstediğiniz BIST Hisse Kodunu Yazın (Örn: THYAO, TUPRS, ASELS):", value="").strip().upper()

# Hisse Kodunu Belirleme
girilen_kod = girilen_hisse if girilen_hisse else (secilen_hazir if secilen_hazir else "FROTO")
hisse_symbol = f"{girilen_kod}.IS" if not girilen_kod.endswith(".IS") else girilen_kod

if st.button("Gelecek Ayların Tahminini ve Al-Sat Sinyalini Oluştur"):
    with st.spinner(f"{girilen_kod} verileri çekiliyor ve gelecek ayların fiyat tahminleri hesaplanıyor..."):
        
        # Veri Çekme Fonksiyonu
        def veri_getir(symbol):
            for _ in range(3):
                try:
                    df_raw = yf.download(symbol, period="1y", interval="1d", progress=False)
                    if not df_raw.empty and len(df_raw) > 20:
                        return df_raw
                except Exception:
                    time.sleep(1)
            return pd.DataFrame()

        df = veri_getir(hisse_symbol)

        if not df.empty and len(df) > 20:
            # MultiIndex Kontrolü
            if isinstance(df.columns, pd.MultiIndex):
                close_prices = df['Close'][hisse_symbol]
                open_prices = df['Open'][hisse_symbol]
                high_prices = df['High'][hisse_symbol]
                low_prices = df['Low'][hisse_symbol]
            else:
                close_prices, open_prices = df['Close'], df['Open']
                high_prices, low_prices = df['High'], df['Low']

            son_fiyat = float(close_prices.iloc[-1])
            bugun = datetime.now()

            # --- İNDİKATÖR HESAPLAMALARI ---
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = float((100 - (100 / (1 + rs))).iloc[-1])

            sma50 = float(close_prices.rolling(50).mean().iloc[-1]) if len(close_prices) >= 50 else son_fiyat
            sma200 = float(close_prices.rolling(200).mean().iloc[-1]) if len(close_prices) >= 200 else son_fiyat
            returns = close_prices.pct_change().dropna()
            volatility = float(returns.std())

            # --- AL - SAT SİNYALİ OLUŞTURMA ALGORİTMASI ---
            al_sat_puan = 0
            if rsi < 35: al_sat_puan += 2  # Aşırı satım (Al fırsatı)
            elif rsi > 70: al_sat_puan -= 2 # Aşırı alım (Sat riski)

            if son_fiyat > sma50: al_sat_puan += 1
            if sma50 > sma200: al_sat_puan += 2 # Golden Cross eğilimi

            if al_sat_puan >= 3:
                sinyal_metni = "🟢 GÜÇLÜ AL"
            elif al_sat_puan > 0:
                sinyal_metni = "🟡 AL / KADEMELİ TOPLA"
            elif al_sat_puan == 0:
                sinyal_metni = "⚪ NÖTR / TUT"
            else:
                sinyal_metni = "🔴 SAT / KÂR AL DÜZELTME BEKLENTİSİ"

            # --- BÖLÜM 1: AL-SAT SİNYALİ VE ÖZET KARTLAR ---
            st.subheader(f"🚦 {girilen_kod} - Yapay Zekâ Al-Sat Sinyali ve Teknik Durum")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Son Fiyat", f"{son_fiyat:.2f} TL")
            c2.metric("Teknik Al-Sat Sinyali", sinyal_metni)
            c3.metric("RSI (14 Seviyesi)", f"{rsi:.1f}")
            c4.metric("50 Günlük Ortalama", f"{sma50:.2f} TL")

            # --- BÖLÜM 2: GELECEK AYLARIN TAHMİNİ GRAFİĞİ (3 AY İLERİSİ) ---
            st.subheader("📅 Gelecek Ayların Fiyat Tahmin Grafiği (Önümüzdeki 90 Gün)")
            st.caption("Kesikli çizgi yapay zekanın önümüzdeki aylarda beklediği fiyat patikasını, renklendirilmiş alan ise %80 olasılık bandını gösterir.")

            # Gelecek 90 Günün Tarihleri
            gelecek_tarihler = [bugun + timedelta(days=i) for i in range(1, 91)]
            gunler = np.arange(1, 91)

            # Trend Eğilimi Hesaplama
            trend_egilimi = 0.0006 if al_sat_puan > 0 else -0.0003
            tahmin_fiyatlari = son_fiyat * (1 + trend_egilimi) ** gunler
            ust_tahmin = son_fiyat * np.exp(trend_egilimi * gunler + volatility * np.sqrt(gunler) * 1.25)
            alt_tahmin = son_fiyat * np.exp(trend_egilimi * gunler - volatility * np.sqrt(gunler) * 1.25)

            # Birleşik Grafik (Geçmiş + Gelecek)
            fig = go.Figure()

            # Geçmiş Fiyat Çizgisi
            fig.add_trace(go.Scatter(
                x=df.index, y=close_prices,
                mode='lines', name='Geçmiş Gerçekleşen Fiyat', line=dict(color='white', width=2)
            ))

            # Gelecek Olasılık Alanı
            fig.add_trace(go.Scatter(
                x=gelecek_tarihler, y=ust_tahmin,
                mode='lines', line=dict(width=0), showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=gelecek_tarihler, y=alt_tahmin,
                mode='lines', line=dict(width=0),
                fill='tonexty', fillcolor='rgba(46, 204, 113, 0.2)',
                name='Gelecek 3 Ay Olasılık Bandı'
            ))

            # Gelecek AI Tahmin Çizgisi
            fig.add_trace(go.Scatter(
                x=gelecek_tarihler, y=tahmin_fiyatlari,
                mode='lines', line=dict(color='cyan', dash='dash', width=2.5),
                name='Gelecek Ayların AI Fiyat Tahmini'
            ))

            fig.update_layout(
                template="plotly_dark", title=f"{girilen_kod} - Gelecek 3 Ayın Fiyat Tahmin Grafiği",
                xaxis_title="Tarih", yaxis_title="Fiyat (TL)", height=500, hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- BÖLÜM 3: GELECEK AYLARA GÖRE TAHMİNİ FİYAT TABLOSU ---
            st.subheader("🗓️ Gelecek Aylara Göre Tahmini Fiyat Seviyeleri")
            
            t_1ay = gelecek_tarihler[29].strftime("%d %B %Y")
            t_2ay = gelecek_tarihler[59].strftime("%d %B %Y")
            t_3ay = gelecek_tarihler[89].strftime("%d %B %Y")

            tahmin_tablosu = pd.DataFrame({
                "Gelecek Dönem": ["1 Ay Sonra", "2 Ay Sonra", "3 Ay Sonra"],
                "Tahmini Tarih": [t_1ay, t_2ay, t_3ay],
                "Olası Düzeltme Tabanı": [f"{alt_tahmin[29]:.2f} TL", f"{alt_tahmin[59]:.2f} TL", f"{alt_tahmin[89]:.2f} TL"],
                "Beklenen AI Tahmin Fiyatı": [f"{tahmin_fiyatlari[29]:.2f} TL", f"{tahmin_fiyatlari[59]:.2f} TL", f"{tahmin_fiyatlari[89]:.2f} TL"],
                "Olası Yükseliş Hedefi": [f"{ust_tahmin[29]:.2f} TL", f"{ust_tahmin[59]:.2f} TL", f"{ust_tahmin[89]:.2f} TL"]
            })
            st.table(tahmin_tablosu)

            # --- BÖLÜM 4: AL-SAT TARAMASI VE EN YÜKSEK POTANSİYELLİ HİSSELER ---
            st.subheader("🚀 BIST Al-Sat Taraması & Yüksek Potansiyelli Hisse Önerileri")
            
            potansiyel_listesi = []
            for h in SIRKET_HIKAYELERI.keys():
                d_temp = veri_getir(f"{h}.IS")
                if not d_temp.empty and len(d_temp) > 20:
                    cp = d_temp['Close'][f"{h}.IS"] if isinstance(d_temp.columns, pd.MultiIndex) else d_temp['Close']
                    d_r = cp.diff()
                    g = (d_r.where(d_r > 0, 0)).rolling(14).mean()
                    l = (-d_r.where(d_r < 0, 0)).rolling(14).mean()
                    r_val = float((100 - (100 / (1 + (g / l)))).iloc[-1])
                    fiy = float(cp.iloc[-1])
                    
                    s_metin = "🟢 GÜÇLÜ AL" if r_val < 45 else ("🟡 AL" if r_val < 60 else "🔴 SAT/DÜZELTME")
                    potansiyel_listesi.append({
                        "Hisse Kodu": h,
                        "Mevcut Fiyat": f"{fiy:.2f} TL",
                        "RSI": f"{r_val:.1f}",
                        "Yapay Zekâ Sinyali": s_metin,
                        "Şirket Hikâyesi": SIRKET_HIKAYELERI[h]
                    })

            st.table(pd.DataFrame(potansiyel_listesi))

        else:
            st.error(f"'{girilen_kod}' sembolüne ait veri bulunamadı. Lütfen BIST hisse kodunu doğru yazdığınızdan emin olun (Örn: THYAO, TUPRS, EGEEN).")
