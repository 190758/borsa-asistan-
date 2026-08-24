import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="BIST Day-Trading & AI Komuta Merkezi", layout="wide")

st.title("⚡ BIST Günlük Trade Komuta Merkezi & AI Analiz Sistemi")
st.caption("1 Yıllık AI Tahmini, Günlük Al-Sat Sinyalleri, Temel Sağlık Skoru (F/K, PD/DD), ATR Stop/Kâr Al Seviyeleri ve X Bülten Üretici")

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

if st.button("🚀 Tüm Analizleri ve 1 Yıllık AI Tahminini Çalıştır"):
    with st.spinner(f"{girilen_kod} verileri çekiliyor, temel ve teknik parametreler hesaplanıyor..."):
        
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
        
        # Şirket Temel Analiz Verilerini Çekme
        ticker_obj = yf.Ticker(hisse_symbol)
        info_data = {}
        try:
            info_data = ticker_obj.info
        except Exception:
            info_data = {}

        if not df.empty and len(df) > 20:
            # MultiIndex Kontrolü ve Güvenli Veri Çekimi
            if isinstance(df.columns, pd.MultiIndex):
                close_prices = df['Close'][hisse_symbol]
                open_prices = df['Open'][hisse_symbol]
                high_prices = df['High'][hisse_symbol]
                low_prices = df['Low'][hisse_symbol]
            else:
                close_prices, open_prices = df['Close'], df['Open']
                high_prices, low_prices = df['High'], df['Low']

            # USD Kuru Hesabı
            if not df_usd.empty and 'Close' in df_usd.columns:
                val_usd = df_usd['Close'].iloc[-1]
                usd_kur = float(val_usd.values[0] if hasattr(val_usd, 'values') else val_usd)
            else:
                usd_kur = 34.0

            # Fiyatları Dönüştürme
            val_close = close_prices.iloc[-1]
            val_high = high_prices.iloc[-1]
            val_low = low_prices.iloc[-1]

            son_fiyat = float(val_close.values[0] if hasattr(val_close, 'values') else val_close)
            son_yuksek = float(val_high.values[0] if hasattr(val_high, 'values') else val_high)
            son_dusuk = float(val_low.values[0] if hasattr(val_low, 'values') else val_low)
            son_fiyat_usd = son_fiyat / usd_kur
            bugun = datetime.now()

            # Teknik İndikatörler
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

            # ATR (Average True Range)
            tr1 = high_prices - low_prices
            tr2 = abs(high_prices - close_prices.shift())
            tr3 = abs(low_prices - close_prices.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr_val = tr.rolling(14).mean().iloc[-1]
            atr = float(atr_val.values[0] if hasattr(atr_val, 'values') else atr_val)

            # --- TEMEL ANALİZ SAĞLIK SKORU HESAPLAMA ---
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
            if temel_puan >= 8: temel_durum = "🟢 ÇOK GÜÇLÜ FİNANSAL YAPI"
            elif temel_puan >= 5: temel_durum = "🟡 MAKUL / DENGELİ"
            else: temel_durum = "🔴 ZAYIF / RİSKLİ TEMEL VERİ"

            # Teknik Sinyal
            al_sat_puan = 0
            if rsi < 35: al_sat_puan += 2
            elif rsi > 70: al_sat_puan -= 2
            if son_fiyat > sma50: al_sat_puan += 1
            if sma50 > sma200: al_sat_puan += 2

            if al_sat_puan >= 3: sinyal_metni = "🟢 GÜÇLÜ AL"
            elif al_sat_puan > 0: sinyal_metni = "🟡 AL / KADEMELİ"
            elif al_sat_puan == 0: sinyal_metni = "⚪ NÖTR / TUT"
            else: sinyal_metni = "🔴 SAT / DÜZELTME"

            # --- MODÜL 1: TEMEL SAĞLIK KARTI VE ANLIK DURUM ---
            st.subheader(f"📊 {girilen_kod} - Temel Sağlık Skoru & Anlık Metrikler")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Son Fiyat (TL)", f"{son_fiyat:.2f} TL")
            m2.metric("Son Fiyat (USD)", f"${son_fiyat_usd:.2f}")
            m3.metric("Temel Sağlık Skoru", f"{temel_puan} / 10", delta=temel_durum)
            m4.metric("Teknik Sinyal", sinyal_metni)
            m5.metric("RSI (14)", f"{rsi:.1f}")

            # --- MODÜL 2: GÜNLÜK AL-SAT TRADE PANENİ (GÜN İÇİ / SWING) ---
            st.subheader("🤖 Yapay Zeka Günlük Al-Sat & Swing Trade Paneli")
            stop_loss = son_fiyat - (atr * 1.5)
            kar_al_1 = son_fiyat + (atr * 1.5)
            kar_al_2 = son_fiyat + (atr * 3.0)

            t1, t2, t3, t4 = st.columns(4)
            t1.info(f"📍 **Önerilen Giriş Bölgesi:**\n\n{son_fiyat*0.995:.2f} - {son_fiyat:.2f} TL")
            t2.error(f"🔴 **Stop-Loss (Zarar Kes):**\n\n{stop_loss:.2f} TL (-%{((son_fiyat-stop_loss)/son_fiyat)*100:.1f})")
            t3.warning(f"🟡 **Kâr Al 1 (Gün İçi Hedef):**\n\n{kar_al_1:.2f} TL (+%{((kar_al_1-son_fiyat)/son_fiyat)*100:.1f})")
            t4.success(f"🟢 **Kâr Al 2 (Swing Hedef):**\n\n{kar_al_2:.2f} TL (+%{((kar_al_2-son_fiyat)/son_fiyat)*100:.1f})")

            # --- MODÜL 3: YAPAY ZEKA OTOMATİK ROPORU VE YORUMU ---
            st.subheader("💡 Yapay Zeka Bütünleşik Analiz Yorumu")
            
            ai_yorum_metni = f"""
            **{girilen_kod} İÇİN YAPAY ZEKA SENTEZ YORUMU:**
            
            1. **Teknik Görünüm:** Hissenin RSI değeri **{rsi:.1f}** seviyesindedir. Fiyatın 50 günlük hareketli ortalamanın ({sma50:.2f} TL) {'üzerinde' if son_fiyat > sma50 else 'altında'} seyretmesi, kısa vadeli momentumun {'pozitif' if son_fiyat > sma50 else 'zayıf'} olduğunu göstermektedir.
            2. **Temel Büyüme & Çarpanlar:** Şirket **10 üzerinden {temel_puan}** temel sağlık skoruna sahiptir. {'Çarpanlar ve kârlılık rasyoları hisse fiyatını destekleyecek düzeydedir.' if temel_puan >= 6 else 'Temel rasyolar yüksek çarpanlara işaret etmekte, bu nedenle teknik kırılımlar dikkatle izlenmelidir.'}
            3. **Trade Stratejisi Tavsiyesi:** Gün içi işlemlerde **{stop_loss:.2f} TL** altında günlük kapanış yapılmadıkça pozisyonlar korunabilir. İlk direnç olan **{kar_al_1:.2f} TL** seviyesinde Kâr Al 1 stratejisiyle %50 pozisyon kapatılması riski azaltacaktır.
            """
            st.info(ai_yorum_metni)

            # --- MODÜL 4: TEMEL ANALİZ DETAY TABLOSU ---
            st.subheader("📋 Şirket Temel Analiz Göstergeleri")
            fk_str = f"{fk:.2f}" if fk else "N/A"
            pddd_str = f"{pddd:.2f}" if pddd else "N/A"
            kar_marji_str = f"%{kar_marji*100:.1f}" if kar_marji else "N/A"
            roe_str = f"%{roe*100:.1f}" if roe else "N/A"

            temel_df = pd.DataFrame({
                "Finansal Rasyo": ["F/K (Fiyat / Kazanç)", "PD/DD (Piyasa Değeri / Defter Değeri)", "Net Kâr Marjı", "Özkaynak Kârlılığı (ROE)"],
                "Mevcut Değer": [fk_str, pddd_str, kar_marji_str, roe_str],
                "İdeal Değer Aralığı": ["< 10-12 (Düşük F/K İyidir)", "< 2.0 - 3.0", "> %15 - %20", "> %25 - %30"],
                "Yorum": [
                    "Hissenin kârlılığına göre ucuzluğunu gösterir." if fk else "Veri bulunamadı",
                    "Şirketin özvarlıklarına göre fiyatlama çarpanıdır." if pddd else "Veri bulunamadı",
                    "Satışlardan kalan net kâr oranını ifade eder." if kar_marji else "Veri bulunamadı",
                    "Şirketin özkaynaklarını ne verimlilikte kullandığını gösterir." if roe else "Veri bulunamadı"
                ]
            })
            st.table(temel_df)

            # --- MODÜL 5: PİVOT NOKTALARI ---
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

            # --- MODÜL 6: GELECEK 1 YILIN (365 GÜN) TAHMİNİ GRAFİĞİ VE HEDEFLERİ ---
            st.subheader("📅 Gelecek 1 Yılın Fiyat Tahmin Grafiği & Senaryoları (Önümüzdeki 365 Gün)")
            gelecek_tarihler = [bugun + timedelta(days=i) for i in range(1, 366)]
            gunler = np.arange(1, 366)
            trend_egilimi = 0.0008 if al_sat_puan > 0 else -0.0002
            tahmin_fiyatlari = son_fiyat * (1 + trend_egilimi) ** gunler
            ust_tahmin = son_fiyat * np.exp(trend_egilimi * gunler + volatility * np.sqrt(gunler) * 1.5)
            alt_tahmin = son_fiyat * np.exp(trend_egilimi * gunler - volatility * np.sqrt(gunler) * 1.5)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=close_prices, mode='lines', name='Geçmiş Fiyat (TL)', line=dict(color='white', width=2)))
            fig.add_trace(go.Scatter(x=gelecek_tarihler, y=ust_tahmin, mode='lines', line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=gelecek_tarihler, y=alt_tahmin, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(46, 204, 113, 0.15)', name='%80 Olasılık Bandı'))
            fig.add_trace(go.Scatter(x=gelecek_tarihler, y=tahmin_fiyatlari, mode='lines', line=dict(color='cyan', dash='dash', width=2.5), name='1 Yıllık AI Tahmin Patikası'))
            fig.update_layout(template="plotly_dark", title=f"{girilen_kod} - 1 Yıllık (365 Günlük) AI Fiyat Projeksiyonu", height=450)
            st.plotly_chart(fig, use_container_width=True)

            # 1 Yıllık Hedef Özet Kartları
            y1, y2, y3 = st.columns(3)
            y1.metric("1 Yıl Ayı Senaryosu (Alt Bant)", f"{alt_tahmin[-1]:.2f} TL", delta=f"%{((alt_tahmin[-1]-son_fiyat)/son_fiyat)*100:.1f}")
            y2.metric("1 Yıl Ana AI Hedefi (Baz)", f"{tahmin_fiyatlari[-1]:.2f} TL", delta=f"%{((tahmin_fiyatlari[-1]-son_fiyat)/son_fiyat)*100:.1f}")
            y3.metric("1 Yıl Boğa Senaryosu (Üst Bant)", f"{ust_tahmin[-1]:.2f} TL", delta=f"%{((ust_tahmin[-1]-son_fiyat)/son_fiyat)*100:.1f}")

            # --- MODÜL 7: X (TWITTER) İÇİN BÜLTEN ÜRETİCİ ---
            st.subheader("📱 X (Twitter) İçin Analiz Bülteni Üretici")
            tweet_metni = f"""📊 #{girilen_kod} 1 Yıllık & Günlük Analiz Bülteni

💰 Fiyat: {son_fiyat:.2f} TL (${son_fiyat_usd:.2f})
🏥 Temel Sağlık Skoru: {temel_puan}/10 ({temel_durum})
🚦 Teknik Sinyal: {sinyal_metni} | RSI: {rsi:.1f}

🎯 Gün İçi Al-Sat Seviyeleri:
• Stop-Loss: {stop_loss:.2f} TL
• Kâr Al 1: {kar_al_1:.2f} TL | Kâr Al 2: {kar_al_2:.2f} TL

📅 1 Yıllık AI Fiyat Hedefi: {tahmin_fiyatlari[-1]:.2f} TL (+%{((tahmin_fiyatlari[-1]-son_fiyat)/son_fiyat)*100:.1f})

#BIST100 #Borsa #Hisse #{girilen_kod}"""

            st.code(tweet_metni, language="text")

            # --- MODÜL 8: GENEL TARAMA & HİSSE ÖNERİLERİ ---
            st.subheader("🚀 BIST Hisse Taraması & Günlük Fırsat Listesi")
            potansiyel_listesi = []
            for h in SIRKET_HIKAYELERI.keys():
                d_temp = veri_getir(f"{h}.IS")
                if not d_temp.empty and len(d_temp) > 20:
                    cp = d_temp['Close'][f"{h}.IS"] if isinstance(d_temp.columns, pd.MultiIndex) else d_temp['Close']
                    fiy_val = cp.iloc[-1]
                    fiy = float(fiy_val.values[0] if hasattr(fiy_val, 'values') else fiy_val)
                    
                    ma20 = cp.rolling(20).mean()
                    std20 = cp.rolling(20).std()
                    bw_val = ((ma20 + 2*std20 - (ma20 - 2*std20)) / ma20).iloc[-1]
                    b_width = float(bw_val.values[0] if hasattr(bw_val, 'values') else bw_val)
                    sikisma_durumu = "🔥 Sıkışma Var (Patlama Yakın)" if b_width < 0.08 else "Normal"

                    potansiyel_listesi.append({
                        "Hisse Kodu": h,
                        "Fiyat": f"{fiy:.2f} TL",
                        "USD Fiyat": f"${(fiy/usd_kur):.2f}",
                        "Volatilite / Sıkışma": sikisma_durumu,
                        "Şirket Hikâyesi": SIRKET_HIKAYELERI[h]
                    })

            st.table(pd.DataFrame(potansiyel_listesi))

        else:
            st.error(f"'{girilen_kod}' sembolüne ait veri bulunamadı. Lütfen BIST kodunu kontrol edin (Örn: THYAO, TUPRS).")
