import streamlit as st
import yfinance as yf
import numpy as np
import plotly.graph_objects as go

# Sayfa Yapılandırması
st.set_page_config(page_title="BIST AI Olasılık Asistanı", layout="wide")

st.title("📈 BIST Yapay Zekâ Fiyat Olasılık Asistanı")
st.caption("Kısa ve Orta Vadeli Olasılık Konisi ve Teknik Düzeltme/Hedef Seviyeleri")

# Hisse Seçimi
hisse_listesi = ["FROTO.IS", "ISMEN.IS", "ANHYT.IS"]
secilen_hisse = st.selectbox("Analiz Edilecek Hisseyi Seçin:", hisse_listesi)

if st.button("Olasılık Grafiğini Oluştur"):
    with st.spinner("Veriler indiriliyor ve olasılık hesaplanıyor..."):
        # 1. Veri Çekme
        df = yf.download(secilen_hisse, period="1y")
        
        if not df.empty:
            son_fiyat = float(df['Close'].iloc[-1])
            
            # Günlük Getiri ve Volatilite Hesabı
            returns = df['Close'].pct_change().dropna()
            volatility = float(returns.std())
            
            # 2. Olasılık Konisi Hesabı (90 Günlük)
            gunler = np.arange(1, 91)
            beklenen_fiyat = son_fiyat * (1 + 0.0005) ** gunler
            
            # %80 Güven Aralığı (Üst ve Alt Bant)
            ust_bant = son_fiyat * np.exp(0.0005 * gunler + volatility * np.sqrt(gunler) * 1.28)
            alt_bant = son_fiyat * np.exp(0.0005 * gunler - volatility * np.sqrt(gunler) * 1.28)
            
            # 3. Plotly İnteraktif Grafik
            fig = go.Figure()
            
            # Olasılık Alanı (Bant)
            fig.add_trace(go.Scatter(
                x=np.concatenate([gunler, gunler[::-1]]),
                y=np.concatenate([ust_bant, alt_bant[::-1]]),
                fill='toself',
                fillcolor='rgba(31, 119, 180, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='%80 Olasılık Aralığı'
            ))
            
            # Beklenen Trend Çizgisi
            fig.add_trace(go.Scatter(
                x=gunler, y=beklenen_fiyat,
                mode='lines',
                line=dict(color='deepskyblue', dash='dash'),
                name='Beklenen AI Patikası'
            ))
            
            fig.update_layout(
                title=f"{secilen_hisse.replace('.IS', '')} - 90 Günlük Fiyat Olasılık Konisi (Son Fiyat: {son_fiyat:.2f} TL)",
                xaxis_title="Gelecek Gün Sayısı",
                yaxis_title="Fiyat (TL)",
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 4. Özet Analiz Kartları
            st.subheader("📊 Tahmini Olasılık Seviyeleri")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("30 Gün Destek (Düzeltme)", f"{alt_bant[29]:.2f} TL", delta="-Düzeltme Riski", delta_color="inverse")
                st.metric("30 Gün Hedef (Direnç)", f"{ust_bant[29]:.2f} TL", delta="+Üst Potansiyel")
                
            with col2:
                st.metric("60 Gün Destek (Düzeltme)", f"{alt_bant[59]:.2f} TL", delta="-Düzeltme Riski", delta_color="inverse")
                st.metric("60 Gün Hedef (Direnç)", f"{ust_bant[59]:.2f} TL", delta="+Üst Potansiyel")
                
            with col3:
                st.metric("90 Gün Destek (Düzeltme)", f"{alt_bant[89]:.2f} TL", delta="-Düzeltme Riski", delta_color="inverse")
                st.metric("90 Gün Hedef (Direnç)", f"{ust_bant[89]:.2f} TL", delta="+Üst Potansiyel")
                
            st.info(f"💡 **AI Notu:** {secilen_hisse.replace('.IS', '')} için geçmiş 1 yıllık oynaklık (volatilite) %{volatility*100:.1f} seviyesindedir. Fiyatın önümüzdeki 30 gün içinde {alt_bant[29]:.2f} TL ile {ust_bant[29]:.2f} TL aralığında kalma olasılığı %80'dir.")
        else:
            st.error("Veri çekilemedi, lütfen tekrar deneyin.")
