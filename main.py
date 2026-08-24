import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="BIST Day-Trading & AI Komuta Merkezi", layout="wide")

st.title("⚡ BIST Günlük Trade Komuta Merkezi & AI Tahmin Asistanı")
st.caption("Anlık Al-Sat Sinyalleri, ATR Stop/Kâr Al Seviyeleri, Pivotlar, USD Grafik ve X (Twitter) Bülten Üretici")

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

# Hisse Seçimi
col_sec, col_yaz = st.columns([1, 1])
with col_sec:
    secilen_hazir = st.selectbox("Hızlı Hisse Seçimi:", [""] + list(SIRKET_HIKAYELERI.keys()))
with col_yaz:
    girilen_hisse = st.text_input("Veya BIST Hisse Kodu Yazın (Örn: THYAO, TUPRS, ASELS):", value="").strip().upper()

girilen_kod = girilen_hisse if girilen_hisse else (secilen_hazir if secilen_hazir else "FROTO")
hisse_symbol = f"{girilen_kod}.IS" if not girilen_kod.endswith(".IS") else girilen_kod

if st.button("🚀 Günlük Trade Analizini ve Sinyalleri Çalıştır"):
    with st.spinner(f"{girilen_kod} ve USD/TRY verileri çekiliyor, günlük trade parametreleri hesaplanıyor..."):
        
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
        df_usd = veri_getir("USDTRY=X")

        if not df.empty and len(df) > 20:
            # MultiIndex Kontrolü ve Güvenli Veri Çekimi
            if isinstance(df.columns, pd.MultiIndex):
                close_prices = df['Close'][hisse_symbol]
                open_prices = df['Open'][hisse_symbol]
                high_prices = df['High'][hisse_symbol]
                low_prices = df['Low'][hisse_symbol]
                volume = df['Volume'][hisse_symbol]
            else:
                close_prices, open_prices = df['Close'], df['Open']
                high_prices, low_prices = df['High'], df['Low']
                volume = df['Volume']

            # USD Kuru Hesabı
            if not df_usd.empty and 'Close' in df_usd.columns:
                val_usd = df_usd['Close'].iloc[-1]
                usd_kur = float(val_usd.values[0] if hasattr(val_usd, 'values') else val_usd)
            else:
                usd_kur = 34.0

            # Fiyatları Güvenli Dönüştürme
            val_close = close_prices.iloc[-1]
            val_high = high_prices.iloc[-1]
            val_low = low_prices.iloc[-1]

            son_fiyat = float(val_close.values[0] if hasattr(val_close, 'values') else val_close)
            son_yuksek = float(val_high.values[0] if hasattr(val_high, 'values') else val_high)
            son_dusuk = float(val_low.values[0] if hasattr(val_low, 'values') else val_low)
            son_fiyat_usd = son_fiyat / usd_kur
            bugun = datetime.now()

            # İndikatörler
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi_val = (100 - (100 / (1 + rs))).iloc[-1]
            rsi = float(rsi_val.values[0] if hasattr(rsi_val, 'values') else rsi_val)

            sma50_val = close_prices.rolling(50).mean().iloc[-1] if len(close_prices) >= 50 else son_fiyat
            sma50 = float(sma50_val.values[0] if hasattr(sma50_val, 'values') else sma50_val)

            sma200_val = close_prices.rolling(200).mean().iloc[-1] if len(close_prices) >= 200 else son_fiyat
            sma200 = float(sma200_val.values[0] if hasattr(sma200_val, 'values') else sma200_val)

            volatility = float(close_prices.pct_change().dropna().std())

            # ATR (Average True Range) Hesabı
            tr1 = high_prices - low_prices
            tr2 = abs(high_prices - close_prices.shift())
            tr3 = abs(low_prices - close_prices.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr_val = tr.rolling(14).mean().iloc[-1]
            atr = float(atr_val.values[0] if hasattr(atr_val, 'values') else atr_val)

            # Al-Sat Sinyal Puanı
            al_sat_puan = 0
            if rsi < 35: al_sat_puan += 2
            elif rsi > 70: al_sat_puan -= 2
            if son_fiyat > sma50: al_sat_puan += 1
            if sma50 > sma200: al_sat_puan += 2

            if al_sat_puan >= 3:
                sinyal_metni = "🟢 GÜÇLÜ AL"
            elif al_sat_puan > 0:
                sinyal_metni = "🟡 AL / KADEMELİ"
            elif al_sat_puan == 0:
                sinyal_metni = "⚪ NÖTR / TUT"
            else:
                sinyal_metni = "🔴 SAT / DÜZELTME"

            # --- MODÜL 1: ÖZET METRİKLER & USD FİYAT ---
            st.subheader(f"🚦 {girilen_kod} - Anlık Durum & USD Değeri")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Son Fiyat (TL)", f"{son_fiyat:.2f} TL")
            m2.metric("Son Fiyat (USD)", f"${son_fiyat_usd:.2f}")
            m3.metric("Sinyal", sinyal_metni)
            m4.metric("RSI (14)", f"{rsi:.1f}")
            m5.metric("Günlük Oynaklık (ATR)", f"±{atr:.2f} TL")

            # --- MODÜL 2: GÜN İÇİ ATR BAZLI RISK & KÂR YÖNETİMİ ---
            st.subheader("🎯 Gün İçi Risk Yönetimi: Stop-Loss & Kâr Al Seviyeleri")
            
            stop_loss = son_fiyat - (atr * 1.5)
            kar_al_1 = son_fiyat + (atr * 1.5)
            kar_al_2 = son_fiyat + (atr * 3.0)

            c_stop, c_tp1, c_tp2 = st.columns(3)
            c_stop.error(f"🔴 **Stop-Loss (Zarar Kes):** {stop_loss:.2f} TL\n\n*(Risk: %{((stop_loss-son_fiyat)/son_fiyat)*100:.1f})*")
            c_tp1.warning(f"🟡 **Kâr Al 1 (İlk Hedef):** {kar_al_1:.2f} TL\n\n*(Getiri: %{((kar_al_1-son_fiyat)/son_fiyat)*100:.1f})*")
            c_tp2.success(f"🟢 **Kâr Al 2 (Ana Hedef):** {kar_al_2:.2f} TL\n\n*(Getiri: %{((kar_al_2-son_fiyat)/son_fiyat)*100:.1f})*")

            # --- MODÜL 3: PİVOT NOKTALARI (DESTEK / DİRENÇ) ---
            st.subheader("📌 Günlük Pivot, Destek ve Direnç Seviyeleri")
            pivot = (son_yuksek + son_dusuk + son_fiyat) / 3
            r1 = (2 * pivot) - son_dusuk
            r2 = pivot + (son_yuksek - son_dusuk)
            s1 = (2 * pivot) - son_yuksek
            s2 = pivot - (son_yuksek - son_dusuk)

            pivot_df = pd.DataFrame({
                "Seviye Tipi": ["Direnç 2 (R2)", "Direnç 1 (R1)", "Pivot Noktası (Denge)", "Destek 1 (S1)", "Destek 2 (S2)"],
                "Fiyat (TL)": [f"{r2:.2f} TL", f"{r1:.2f} TL", f"{pivot:.2f} TL", f"{s1:.2f} TL", f"{s2:.2f} TL"],
                "Açıklama": ["Gün İçi Zirve Satış Bölgesi", "İlk Direnç / Kâr Alma", "Fiyat Üstündeyse Boğa, Altındaysa Ayı", "İlk Tepki Alım Bölgesi", "Ana Gün İçi Taban"]
            })
            st.table(pivot_df)

            # --- MODÜL 4: GELECEK 3 AYIN TAHMİNİ GRAFİĞİ ---
            st.subheader("📅 Gelecek Ayların Fiyat Tahmin Grafiği (Önümüzdeki 90 Gün)")
            
            gelecek_tarihler = [bugun + timedelta(days=i) for i in range(1, 91)]
            gunler = np.arange(1, 91)
            trend_egilimi = 0.0006 if al_sat_puan > 0 else -0.0003
            tahmin_fiyatlari = son_fiyat * (1 + trend_egilimi) ** gunler
            ust_tahmin = son_fiyat * np.exp(trend_egilimi * gunler + volatility * np.sqrt(gunler) * 1.25)
            alt_tahmin = son_fiyat * np.exp(trend_egilimi * gunler - volatility * np.sqrt(gunler) * 1.25)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=close_prices, mode='lines', name='Geçmiş Fiyat (TL)', line=dict(color='white', width=2)))
            fig.add_trace(go.Scatter(x=gelecek_tarihler, y=ust_tahmin, mode='lines', line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=gelecek_tarihler, y=alt_tahmin, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(46, 204, 113, 0.2)', name='%80 Olasılık Bandı'))
            fig.add_trace(go.Scatter(x=gelecek_tarihler, y=tahmin_fiyatlari, mode='lines', line=dict(color='cyan', dash='dash', width=2.5), name='AI Tahmin Patikası'))
            fig.update_layout(template="plotly_dark", title=f"{girilen_kod} - 90 Günlük AI Fiyat Tahmini", height=450)
            st.plotly_chart(fig, use_container_width=True)

            # --- MODÜL 5: X (TWITTER) İÇİN BÜLTEN ÜRETİCİ ---
            st.subheader("📱 X (Twitter) İçin Günlük Analiz Bülteni Üretici")
            st.caption("Aşağıdaki bülteni kopyalayarak doğrudan sosyal medya hesabınızda paylaşabilirsiniz:")

            tweet_metni = f"""📊 #{girilen_kod} Günlük BIST Trade Notları

💰 Son Fiyat: {son_fiyat:.2f} TL (${son_fiyat_usd:.2f})
🚦 Yapay Zekâ Sinyali: {sinyal_metni}
📈 RSI (14): {rsi:.1f}

🎯 Gün İçi Seviyeler:
• Stop-Loss: {stop_loss:.2f} TL
• Denge (Pivot): {pivot:.2f} TL
• Kâr Al 1: {kar_al_1:.2f} TL
• Kâr Al 2: {kar_al_2:.2f} TL

#BIST100 #Borsa #Hisse #{girilen_kod}"""

            st.code(tweet_metni, language="text")

            # --- MODÜL 6: GENEL TARAMA & SIKIŞAN HİSSELER ---
            st.subheader("🚀 BIST Hisse Taraması & Sıkışma / Hacim Durumları")
            
            potansiyel_listesi = []
            for h in SIRKET_HIKAYELERI.keys():
                d_temp = veri_getir(f"{h}.IS")
                if not d_temp.empty and len(d_temp) > 20:
                    cp = d_temp['Close'][f"{h}.IS"] if isinstance(d_temp.columns, pd.MultiIndex) else d_temp['Close']
                    fiy_val = cp.iloc[-1]
                    fiy = float(fiy_val.values[0] if hasattr(fiy_val, 'values') else fiy_val)
                    
                    # Sıkışma Kontrolü (Bollinger Genişliği)
                    ma20 = cp.rolling(20).mean()
                    std20 = cp.rolling(20).std()
                    bw_val = ((ma20 + 2*std20 - (ma20 - 2*std20)) / ma20).iloc[-1]
                    b_width = float(bw_val.values[0] if hasattr(bw_val, 'values') else bw_val)
                    sikisma_durumu = "🔥 Sıkışma Var (Patlayabilir)" if b_width < 0.08 else "Normal"

                    potansiyel_listesi.append({
                        "Hisse Kodu": h,
                        "Fiyat": f"{fiy:.2f} TL",
                        "USD Fiyat": f"${(fiy/usd_kur):.2f}",
                        "Volatilite Durumu": sikisma_durumu,
                        "Şirket Hikâyesi": SIRKET_HIKAYELERI[h]
                    })

            st.table(pd.DataFrame(potansiyel_listesi))

        else:
            st.error(f"'{girilen_kod}' sembolüne ait veri bulunamadı. Lütfen BIST kodunu kontrol edin (Örn: THYAO, TUPRS).")
