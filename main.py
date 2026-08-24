import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="BIST AI Olasılık Asistanı", layout="wide")

st.title("📈 BIST Yapay Zekâ Fiyat & Tarih Olasılık Asistanı")
st.caption("Gelecek Zaman Çizgisine Göre Fiyat Hedefleri, Düzeltme Seviyeleri ve İstatistiksel Olasılıklar")

# Hisse Seçimi
hisse_listesi = ["FROTO.IS", "ISMEN.IS", "ANHYT.IS", "ARDYZ.IS", "ALTNY.IS", "YEOTK.IS", "KCHOL.IS"]
secilen_hisse = st.selectbox("Analiz Edilecek Hisseyi Seçin:", hisse_listesi)

if st.button("Olasılık ve Tarih Analizini Oluştur"):
    with st.spinner("Borsa İstanbul verileri çekiliyor ve zaman çizgisi hesaplanıyor..."):
        
        # Güvenli Veri Çekme Fonksiyonu
        df = None
        for i in range(3):
            try:
                ticker = yf.Ticker(secilen_hisse)
                df = ticker.history(period="1y")
                if not df.empty:
                    break
            except Exception:
                time.sleep(1)

        if df is not None and not df.empty and len(df) > 10:
            son_fiyat = float(df['Close'].iloc[-1])
            bugun = datetime.now()
            
            # Günlük Getiri ve Volatilite Hesabı
            returns = df['Close'].pct_change().dropna()
            volatility = float(returns.std())
            
            # 90 Günlük Zaman Çizgisi Oluşturma
            tarihler = [bugun + timedelta(days=int(i)) for i in range(1, 91)]
            tarih_etiketleri = [t.strftime("%d %b %Y") for t in tarihler]
            gunler = np.arange(1, 91)
            
            # Olasılık Konisi Hesaplamaları
            beklenen_fiyat = son_fiyat * (1 + 0.0005) ** gunler
            ust_bant = son_fiyat * np.exp(0.0005 * gunler + volatility * np.sqrt(gunler) * 1.28)
            alt_bant = son_fiyat * np.exp(0.0005 * gunler - volatility * np.sqrt(gunler) * 1.28)
            
            # 1. Plotly Grafik
            fig = go.Figure()
            
            # Olasılık Alanı
            fig.add_trace(go.Scatter(
                x=tarih_etiketleri, y=ust_bant,
                mode='lines', line=dict(width=0),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=tarih_etiketleri, y=alt_bant,
                mode='lines', line=dict(width=0),
                fill='tonexty', fillcolor='rgba(31, 119, 180, 0.25)',
                name='%80 Olasılık Bandı'
            ))
            
            # Beklenen Trend
            fig.add_trace(go.Scatter(
                x=tarih_etiketleri, y=beklenen_fiyat,
                mode='lines', line=dict(color='deepskyblue', dash='dash', width=2),
                name='Beklenen AI Trendi'
            ))
            
            fig.update_layout(
                title=f"{secilen_hisse.replace('.IS', '')} - Zaman Çizgisine Göre Fiyat Olasılık Konisi (Son Fiyat: {son_fiyat:.2f} TL)",
                xaxis_title="Tarih",
                yaxis_title="Fiyat (TL)",
                template="plotly_dark",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 2. Tarih Bazlı Olasılık Tablosu
            st.subheader("📅 Tarih Bazlı Fiyat ve Düzeltme Seviyeleri")
            
            tarih_30 = tarihler[29].strftime("%d %B %Y")
            tarih_60 = tarihler[59].strftime("%d %B %Y")
            tarih_90 = tarihler[89].strftime("%d %B %Y")
            
            tablo_data = {
                "Hedef Tarih": [tarih_30, tarih_60, tarih_90],
                "Vade": ["30 Gün Sonra", "60 Gün Sonra", "90 Gün Sonra"],
                "Düzeltme Desteği (%80 Alt)": [f"{alt_bant[29]:.2f} TL", f"{alt_bant[59]:.2f} TL", f"{alt_bant[89]:.2f} TL"],
                "En Olası Fiyat": [f"{beklenen_fiyat[29]:.2f} TL", f"{beklenen_fiyat[59]:.2f} TL", f"{beklenen_fiyat[89]:.2f} TL"],
                "Üst Hedef Direnci (%80 Üst)": [f"{ust_bant[29]:.2f} TL", f"{ust_bant[59]:.2f} TL", f"{ust_bant[89]:.2f} TL"]
            }
            
            df_tablo = pd.DataFrame(tablo_data)
            st.table(df_tablo)
            
            # 3. AI Yorum Kartı
            st.subheader("💡 Yapay Zekâ Zaman Çizgisi Analizi")
            hisse_adi = secilen_hisse.replace('.IS', '')
            
            st.info(
                f"**{hisse_adi}** için yapılan istatistiksel simülasyona göre:\n\n"
                f"• **Kısa Vadeli Düzeltme Riski ({tarih_30}):** Fiyatın bu tarihe kadar olasılık dahilindeki ilk güçlü desteği **{alt_bant[29]:.2f} TL** seviyesindedir.\n"
                f"• **Orta Vadeli Hedef Bölgesi ({tarih_90}):** Mevcut tarihsel volatilite (%{volatility*100:.1f}) korunduğu takdirde, 90 günlük vadede üst bant hedefi **{ust_bant[89]:.2f} TL** olarak hesaplanmaktadır.\n\n"
                f"*Not: Bu seviyeler kesin fiyat taahhüdü içermez; tarihsel fiyat oynaklığına dayalı istatistiksel olasılık aralıklarını ifade eder.*"
            )
            
        else:
            st.error("Veri çekme sırasında bağlantı gecikmesi yaşandı. Lütfen 'Olasılık ve Tarih Analizini Oluştur' butonuna tekrar basın.")
