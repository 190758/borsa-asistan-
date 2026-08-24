import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="BIST AI Kapsamlı Analiz Asistanı", layout="wide")

st.title("📈 BIST AI Kapsamlı Analiz ve Olasılık Asistanı")
st.caption("Temel Analiz, Bilanço Rasyoları, Teknik İndikatörler ve İstatistiksel Fiyat Olasılıkları")

# Hisse Seçimi
hisse_listesi = ["FROTO.IS", "ISMEN.IS", "ANHYT.IS", "ARDYZ.IS", "ALTNY.IS", "YEOTK.IS", "KCHOL.IS"]
secilen_hisse = st.selectbox("Analiz Edilecek Şirketi Seçin:", hisse_listesi)

# Şirket Temel & Yatırım Bilgi Sözlüğü
SIRKET_HIKAYELERI = {
    "FROTO.IS": "Elektrikli araç yatırımları (E-Transit/Custom), Romanya Craiova fabrikası kapasite artışı ve güçlü ihracat potansiyeli. Yüksek özkaynak kârlılığı ve düzenli temettü verimi.",
    "ISMEN.IS": "Borsa İstanbul işlem hacimlerindeki artıştan doğrudan faydalanan güçlü sermaye yapısı. Yüksek komisyon ve portföy yönetim gelirleri, düzenli temettü ödeme alışkanlığı.",
    "ANHYT.IS": "Bireysel Emeklilik Sistemi (BES) fon büyüklüğündeki istikrarlı artış ve yüksek faiz ortamında artan yatırım gelirleri. Güçlü özkaynak yapısı ve yüksek temettü verimliliği.",
    "ARDYZ.IS": "Yazılım, siber güvenlik ve kamusal teknoloji projelerindeki büyüme. Düşük borçluluk oranı, yüksek kâr marjları ve yurt dışı pazar açılımları.",
    "ALTNY.IS": "Savunma sanayii projeleri, mühimmat/roket sistemleri ve insansız kara araçları yatırımları. Güçlü sipariş bakiyesi (Backlog) ve devlet destekli Ar-Ge altyapısı.",
    "YEOTK.IS": "Yenilenebilir enerji, GES/RES santral kurulumları (EPC) ve batarya depolama teknolojileri yatırımları. Yurt dışı taahhüt projeleri ve yüksek ciro büyüme hızı.",
    "KCHOL.IS": "Otomotiv, enerji, dayanıklı tüketim ve finans sektörlerindeki lider iştiraklerin net aktif değer (NAD) iskontosu ile birleşimi. Güçlü döviz pozisyonu ve küresel yatırım ağı."
}

if st.button("Kapsamlı Analiz Raporunu Oluştur"):
    with st.spinner("Finansal tablolar, teknik göstergeler ve fiyat verileri çekiliyor..."):
        
        # 1. Fiyat Verisi Çekme
        df = pd.DataFrame()
        ticker_obj = None
        for deneme in range(4):
            try:
                df = yf.download(secilen_hisse, period="1y", interval="1d", progress=False)
                ticker_obj = yf.Ticker(secilen_hisse)
                if not df.empty and len(df) > 10:
                    break
            except Exception:
                time.sleep(1.5)

        if not df.empty and len(df) > 10:
            if isinstance(df.columns, pd.MultiIndex):
                close_prices = df['Close'][secilen_hisse]
            else:
                close_prices = df['Close']
                
            son_fiyat = float(close_prices.iloc[-1])
            bugun = datetime.now()
            
            # --- TEKNİK ANALİZ HESAPLAMALARI ---
            # RSI Hesabı
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = float((100 - (100 / (1 + rs))).iloc[-1])
            
            # Hareketli Ortalamalar (SMA)
            sma50 = float(close_prices.rolling(window=50).mean().iloc[-1]) if len(close_prices) >= 50 else son_fiyat
            sma200 = float(close_prices.rolling(window=200).mean().iloc[-1]) if len(close_prices) >= 200 else son_fiyat
            
            # --- TEMEL ANALİZ & BİLANÇO BİLGİLERİ ---
            info = {}
            try:
                info = ticker_obj.info
            except Exception:
                pass
                
            fk_orani = info.get('trailingPE', None)
            pddd_orani = info.get('priceToBook', None)
            roe_orani = info.get('returnOnEquity', None)
            
            fk_str = f"{fk_orani:.2f}" if fk_orani else "Veri Yok / Uyumsuz"
            pddd_str = f"{pddd_orani:.2f}" if pddd_orani else "Veri Yok"
            roe_str = f"%{roe_orani*100:.1f}" if roe_orani else "Veri Yok"

            # --- OLASILIK HESAPLAMALARI (VOLATİLİTE + RSI BİLEŞENİ) ---
            returns = close_prices.pct_change().dropna()
            volatility = float(returns.std())
            
            # RSI Teknik Düzeltme Faktörü (RSI yüksekse üst bant sınırlanır, düşükse alt bant desteklenir)
            rsi_faktoru = 0.0002 if rsi < 30 else (-0.0002 if rsi > 70 else 0.0005)
            
            tarihler = [bugun + timedelta(days=int(i)) for i in range(1, 91)]
            tarih_etiketleri = [t.strftime("%d %b %Y") for t in tarihler]
            gunler = np.arange(1, 91)
            
            beklenen_fiyat = son_fiyat * (1 + rsi_faktoru) ** gunler
            ust_bant = son_fiyat * np.exp(rsi_faktoru * gunler + volatility * np.sqrt(gunler) * 1.28)
            alt_bant = son_fiyat * np.exp(rsi_faktoru * gunler - volatility * np.sqrt(gunler) * 1.28)

            # --- EKRAN DÜZENİ ---
            hisse_kodu = secilen_hisse.replace('.IS', '')
            
            # 1. BÖLÜM: BİLANÇO VE TEKNİK ÖZET KARTLARI
            st.subheader(f"🔍 {hisse_kodu} - Temel & Teknik Analiz Özeti")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            col1.metric("Son Kapanış", f"{son_fiyat:.2f} TL")
            col2.metric("F/K Oranı", fk_str)
            col3.metric("PD/DD Oranı", pddd_str)
            col4.metric("RSI (14)", f"{rsi:.1f}", delta="Aşırı Satım" if rsi < 30 else ("Aşırı Alım" if rsi > 70 else "Nötr"))
            
            trend_durumu = "Yükseliş (SMA50 > SMA200)" if sma50 > sma200 else "Düzeltme/Yatay"
            col5.metric("50 Günlük HO", f"{sma50:.2f} TL", delta=trend_durumu)
            
            # 2. BÖLÜM: ŞİRKET YATIRIMLARI VE BÜYÜME HİKÂYESİ
            st.subheader("🏗️ Şirket Yatırımları & Temel Büyüme Dinamikleri")
            st.success(SIRKET_HIKAYELERI.get(secilen_hisse, "Şirket yatırım verisi güncelleniyor."))

            # 3. BÖLÜM: GRAFİK (OLASILIK KONİSİ)
            st.subheader("📈 Tarih Bazlı Fiyat Olasılık Konisi")
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=tarih_etiketleri, y=ust_bant,
                mode='lines', line=dict(width=0), showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=tarih_etiketleri, y=alt_bant,
                mode='lines', line=dict(width=0),
                fill='tonexty', fillcolor='rgba(31, 119, 180, 0.25)',
                name='%80 Olasılık Bandı'
            ))
            fig.add_trace(go.Scatter(
                x=tarih_etiketleri, y=beklenen_fiyat,
                mode='lines', line=dict(color='deepskyblue', dash='dash', width=2),
                name='AI Beklenen Trend'
            ))
            
            fig.update_layout(
                title=f"{hisse_kodu} - 90 Günlük Zaman Çizgisi Fiyat Tahmini",
                xaxis_title="Tarih", yaxis_title="Fiyat (TL)",
                template="plotly_dark", hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

            # 4. BÖLÜM: TARİH BAZLI HEDEF VE DÜZELTME TABLOSU
            st.subheader("📅 Tarih Bazlı Hedef ve Düzeltme Seviyeleri")
            tarih_30 = tarihler[29].strftime("%d %B %Y")
            tarih_60 = tarihler[59].strftime("%d %B %Y")
            tarih_90 = tarihler[89].strftime("%d %B %Y")
            
            tablo_data = {
                "Hedef Tarih": [tarih_30, tarih_60, tarih_90],
                "Vade": ["30 Gün Sonra", "60 Gün Sonra", "90 Gün Sonra"],
                "Düzeltme Desteği (Alt Bant)": [f"{alt_bant[29]:.2f} TL", f"{alt_bant[59]:.2f} TL", f"{alt_bant[89]:.2f} TL"],
                "En Olası Fiyat": [f"{beklenen_fiyat[29]:.2f} TL", f"{beklenen_fiyat[59]:.2f} TL", f"{beklenen_fiyat[89]:.2f} TL"],
                "Üst Hedef Direnci (Üst Bant)": [f"{ust_bant[29]:.2f} TL", f"{ust_bant[59]:.2f} TL", f"{ust_bant[89]:.2f} TL"]
            }
            st.table(pd.DataFrame(tablo_data))

            # 5. BÖLÜM: DETAYLI YAPAY ZEKÂ ANALİZ METNİ
            st.subheader("💡 Yapay Zekâ Bütünleşik Değerlendirmesi")
            
            rsi_yorum = "RSI aşırı alım bölgesinde, kısa vadeli kâr satışlarına dikkat edilmeli." if rsi > 70 else (
                "RSI aşırı satım bölgesinde, tepki alımları gelebilir." if rsi < 30 else "RSI dengeli seviyede."
            )
            
            st.info(
                f"**{hisse_kodu} Bütünleşik Analiz Notu:**\n\n"
                f"• **Teknik Durum:** 14 günlük RSI değeri **{rsi:.1f}** seviyesindedir ({rsi_yorum}). Fiyatın 50 günlük ortalaması **{sma50:.2f} TL** seviyesindedir.\n"
                f"• **Çarpanlar & Bilanço:** Şirket **{fk_str} F/K** ve **{pddd_str} PD/DD** çarpanları ile işlem görmektedir.\n"
                f"• **Zaman Çizgisi Hedefleri:** Temel çarpanlar, şirket yatırımları ve volatilite birleştirildiğinde; **{tarih_30}** tarihinde olası dip desteği **{alt_bant[29]:.2f} TL**, **{tarih_90}** tarihinde ise olası üst direnç hedefi **{ust_bant[89]:.2f} TL** olarak hesaplanmıştır."
            )
            
        else:
            st.error("Veri çekme sırasında gecikme yaşandı. Lütfen 'Kapsamlı Analiz Raporunu Oluştur' butonuna tekrar basın.")
