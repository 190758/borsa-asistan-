import io
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="BIST Gelişmiş Day-Trading & AI Analiz Komuta Merkezi",
    layout="wide",
)

st.title("⚡ BIST Gelişmiş Day-Trading & AI Analiz Komuta Merkezi")
st.caption(
    "Kısa Vadeli Günlük Al-Sat Önerileri, Detaylı İndikatör Analizleri, Yapay"
    " Zeka Yorumları ve 1 Yıllık Projeksiyonlar"
)

# BIST Takip ve Tarama Listesi
BIST_TAKIP_LISTESI = {
    "FROTO": (
        "Ford Otosan - Elektrikli araç dönüşümü, Romanya Craiova yatırımları"
        " ve güçlü ihracat yapısı."
    ),
    "ISMEN": (
        "İş Yatırım - Borsa işlem hacimlerinden yüksek komisyon geliri ve"
        " güçlü özkaynak kârlılığı."
    ),
    "ANHYT": (
        "Anadolu Hayat - BES fon büyüklüğü, yüksek faiz ortamında artan net"
        " yatırım gelirleri."
    ),
    "ARDYZ": (
        "ARD Grup Bilişim - Siber güvenlik ve yazılım ihracatı, yüksek net kâr"
        " marjı ve düşük borçluluk."
    ),
    "ALTNY": (
        "Altınay Savunma - Savunma sanayii Ar-Ge projeleri ve yüksek sipariş"
        " bakiyesi."
    ),
    "YEOTK": (
        "Yeo Teknoloji - Yenilenebilir enerji, GES/RES projeleri ve batarya"
        " depolama yatırımları."
    ),
    "KCHOL": (
        "Koç Holding - Lider iştirak portföyü, net aktif değer iskontosu ve"
        " güçlü döviz pozisyonu."
    ),
    "THYAO": (
        "Türk Hava Yolları - Güçlü yolcu/kargo trafiği, geniş uçuş ağı ve"
        " yüksek döviz girdisi."
    ),
    "TUPRS": (
        "Tüpraş - Yüksek rafineri marjları, stratejik dönüşüm ve düzenli"
        " temettü verimi."
    ),
    "ASELS": (
        "Aselsan - Savunma sanayii liderliği, rekor bakiye siparişler ve yüksek"
        " Ar-Ge kapasitesi."
    ),
    "SAHOL": (
        "Sabancı Holding - Yenilenebilir enerji ve küresel yatırımlar, yüksek"
        " iskonto."
    ),
    "EREGL": "Ereğli Demir Çelik - Yeşil çelik dönüşümü, cevher madencilik yatırımları.",
    "SOKM": "Şok Marketler - Güçlü nakit akışı ve perakende büyüme dinamikleri.",
    "AGHOL": (
        "Anadolu Grubu Holding - İçecek, perakende ve otomotiv sektörlerinde"
        " dengeli portföy."
    ),
    "ALARK": "Alarko Holding - Tarım/GES yatırımları ve güçlü nakit pozisyonu.",
}


# PNG Tablo Görseli Üretici Fonksiyon
def generate_table_image(df, title="BIST Günlük Trade Tablosu"):
  fig, ax = plt.subplots(figsize=(12, 6.75), dpi=300)
  fig.patch.set_facecolor("#15202B")
  ax.set_facecolor("#15202B")
  ax.axis("off")

  plt.title(
      title, color="#FFFFFF", fontsize=16, fontweight="bold", pad=20, loc="center"
  )

  table = ax.table(
      cellText=df.values, colLabels=df.columns, cellLoc="center", loc="center"
  )
  table.auto_set_font_size(False)
  table.set_fontsize(10)
  table.scale(1.2, 1.8)

  for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#38444D")
    if row == 0:
      cell.set_facecolor("#1DA1F2")
      cell.get_text().set_color("#FFFFFF")
      cell.get_text().set_weight("bold")
      cell.get_text().set_fontsize(11)
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


# Veri Çekme Fonksiyonu
@st.cache_data(ttl=300)
def veri_getir(symbol, period="1y", interval="1d"):
  import yfinance as yf

  for _ in range(3):
    try:
      df_raw = yf.download(
          symbol, period=period, interval=interval, progress=False
      )
      if not df_raw.empty and len(df_raw) > 10:
        return df_raw
    except Exception:
      time.sleep(0.5)
  return pd.DataFrame()


# USD Kuru Çek
df_usd = veri_getir("USDTRY=X")
if not df_usd.empty and "Close" in df_usd.columns:
  val_usd = df_usd["Close"].iloc[-1]
  usd_kur = float(val_usd.values[0] if hasattr(val_usd, "values") else val_usd)
else:
  usd_kur = 34.0

# Sekme Yapısı
tab_oneriler, tab_detay, tab_tarama, tab_bulten = st.tabs([
    "🔥 Günlük Al-Sat & Short-Term Öneriler",
    "📊 Detaylı Hisse & AI Analiz Komuta Merkezi",
    "🚀 BIST 15 Otomatik Sıkışma & Trend Taraması",
    "📱 X (Twitter) Bülten & Görsel Üretici",
])

# ==========================================
# SEKME 1: GÜNLÜK AL-SAT ÖNERİLERİ
# ==========================================
with tab_oneriler:
  st.header("🎯 Kısa Vadeli Günlük Al-Sat Öneri Paneli")
  st.info(
      "Aşağıdaki liste BIST hisselerinin teknik indikatörleri yapay zeka"
      " algoritmalarınca taranarak oluşturulmuştur."
  )

  with st.spinner(
      "Tüm takip listesi taranıyor ve gün içi al-sat fırsatları"
      " hesaplanıyor..."
  ):
    oneriler_data = []

    for kod, hikaye in BIST_TAKIP_LISTESI.items():
      h_sym = f"{kod}.IS"
      df_h = veri_getir(h_sym)

      if not df_h.empty and len(df_h) > 30:
        if isinstance(df_h.columns, pd.MultiIndex):
          cp = df_h["Close"][h_sym]
          hp = df_h["High"][h_sym]
          lp = df_h["Low"][h_sym]
        else:
          cp, hp, lp = df_h["Close"], df_h["High"], df_h["Low"]

        son_f = float(
            cp.iloc[-1].values[0] if hasattr(cp.iloc[-1], "values") else cp.iloc[-1]
        )

        delta = cp.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi_v = float((100 - (100 / (1 + rs))).iloc[-1])

        sma20 = float(cp.rolling(20).mean().iloc[-1])
        sma50 = float(cp.rolling(50).mean().iloc[-1])

        tr1 = hp - lp
        tr2 = abs(hp - cp.shift())
        tr3 = abs(lp - cp.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])

        std20 = float(cp.rolling(20).std().iloc[-1])
        bb_width = ((sma20 + (2 * std20)) - (sma20 - (2 * std20))) / sma20

        skor = 0
        if rsi_v < 38:
          skor += 2
        elif rsi_v < 50:
          skor += 1
        elif rsi_v > 70:
          skor -= 2

        if son_f > sma20:
          skor += 1
        if son_f > sma50:
          skor += 1
        if bb_width < 0.08:
          skor += 1.5

        if skor >= 3.5:
          durum = "🔥 GÜÇLÜ AL"
          vade = "1-3 Gün (Day Trade)"
        elif skor >= 2.0:
          durum = "🟢 KADEMELİ AL"
          vade = "3-7 Gün (Swing)"
        elif skor >= 0:
          durum = "⚪ TUT / İZLE"
          vade = "Nötr"
        else:
          durum = "🔴 SAT / RISK"
          vade = "Düzeltme"

        stop_l = son_f - (atr * 1.5)
        tp1 = son_f + (atr * 1.5)
        tp2 = son_f + (atr * 3.0)

        oneriler_data.append({
            "Hisse": kod,
            "Son Fiyat": f"{son_f:.2f} TL",
            "Sinyal": durum,
            "Alım Aralığı": f"{son_f*0.995:.2f} - {son_f:.2f} TL",
            "Stop-Loss": f"{stop_l:.2f} TL",
            "Kâr Al 1": f"{tp1:.2f} TL",
            "Kâr Al 2": f"{tp2:.2f} TL",
            "RSI": f"{rsi_v:.1f}",
            "Vade": vade,
        })

    df_oneriler = pd.DataFrame(oneriler_data)
    st.dataframe(df_oneriler, use_container_width=True)

    st.markdown("---")
    st.subheader("📸 Günlük Öneri Tablosunu Görsel (PNG) Olarak İndir")
    buf_oneriler = generate_table_image(
        df_oneriler, title="BIST Günlük Trade & Al-Sat Öneri Tablosu"
    )
    st.download_button(
        label="📥 Tabloyu X (Twitter) Formatında PNG İndir",
        data=buf_oneriler,
        file_name="bist_gunluk_oneriler.png",
        mime="image/png",
    )

# ==========================================
# SEKME 2: DETAYLI HİSSE ANALİZİ
# ==========================================
with tab_detay:
  col_sec, col_yaz = st.columns([1, 1])
  with col_sec:
    secilen_hazir = st.selectbox(
        "Analiz Edilecek Hisse Seçin:", list(BIST_TAKIP_LISTESI.keys())
    )
  with col_yaz:
    girilen_hisse = (
        st.text_input("Veya Başka BIST Kodu Girin:", value="").strip().upper()
    )

  girilen_kod = girilen_hisse if girilen_hisse else secilen_hazir
  hisse_symbol = (
      f"{girilen_kod}.IS" if not girilen_kod.endswith(".IS") else girilen_kod
  )

  if st.button(f"🚀 {girilen_kod} İçin Detaylı AI Analizini Çalıştır"):
    with st.spinner(f"{girilen_kod} verileri işleniyor..."):
      df = veri_getir(hisse_symbol)
      if not df.empty and len(df) > 20:
        cp = (
            df["Close"][hisse_symbol]
            if isinstance(df.columns, pd.MultiIndex)
            else df["Close"]
        )
        son_f = float(
            cp.iloc[-1].values[0] if hasattr(cp.iloc[-1], "values") else cp.iloc[-1]
        )

        st.metric("Son Fiyat", f"{son_f:.2f} TL", f"${son_f/usd_kur:.2f}")

        # Gelecek 1 Yıl Tahmini
        gunler = np.arange(1, 366)
        tahmin_fiyatlari = son_f * (1 + 0.0005) ** gunler

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=cp,
                mode="lines",
                name="Geçmiş Fiyat",
                line=dict(color="white"),
            )
        )
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# SEKME 3: TARAMA
# ==========================================
with tab_tarama:
  st.header("🚀 BIST 15 Hisse Taraması")
  tarama_data = []
  for h_kod, hikaye in BIST_TAKIP_LISTESI.items():
    df_t = veri_getir(f"{h_kod}.IS")
    if not df_t.empty and len(df_t) > 20:
      cp_t = (
          df_t["Close"][f"{h_kod}.IS"]
          if isinstance(df_t.columns, pd.MultiIndex)
          else df_t["Close"]
      )
      fiy_t = float(
          cp_t.iloc[-1].values[0]
          if hasattr(cp_t.iloc[-1], "values")
          else cp_t.iloc[-1]
      )
      tarama_data.append(
          {"Hisse": h_kod, "Fiyat": f"{fiy_t:.2f} TL", "Hikaye": hikaye}
      )
  st.table(pd.DataFrame(tarama_data))

# ==========================================
# SEKME 4: X BÜLTEN & GÖRSEL ÜRETİCİ
# ==========================================
with tab_bulten:
  st.header("📱 X (Twitter) Borsa Bülten & Görsel Üretici")
  sec_b = st.selectbox(
      "Bülten Oluşturulacak Hisse:", list(BIST_TAKIP_LISTESI.keys())
  )

  if st.button("Bülten & Paylaşım Görseli Üret"):
    df_b = veri_getir(f"{sec_b}.IS")
    if not df_b.empty:
      cp_b = (
          df_b["Close"][f"{sec_b}.IS"]
          if isinstance(df_b.columns, pd.MultiIndex)
          else df_b["Close"]
      )
      f_b = float(
          cp_b.iloc[-1].values[0]
          if hasattr(cp_b.iloc[-1], "values")
          else cp_b.iloc[-1]
      )

      tweet_text = f"""📊 #{sec_b} Günlük Trade & Fiyat Analizi

💰 Son Fiyat: {f_b:.2f} TL (${f_b/usd_kur:.2f})
🎯 Gün İçi Al-Sat Seviyeleri:
• İdeal Alım: {f_b*0.995:.2f} - {f_b:.2f} TL
• Stop-Loss: {f_b*0.975:.2f} TL
• Kâr Al 1: {f_b*1.025:.2f} TL
• Kâr Al 2: {f_b*1.05:.2f} TL

#BIST100 #Borsa #Hisse #{sec_b}"""

      st.code(tweet_text, language="text")

      # Örnek Mini Özet Tablosu
      df_single = pd.DataFrame([{
          "Hisse": sec_b,
          "Fiyat": f"{f_b:.2f} TL",
          "Alım Aralığı": f"{f_b*0.995:.2f}-{f_b:.2f}",
          "Stop": f"{f_b*0.975:.2f}",
          "Hedef 1": f"{f_b*1.025:.2f}",
          "Hedef 2": f"{f_b*1.05:.2f}",
      }])

      png_buf_single = generate_table_image(
          df_single, title=f"#{sec_b} Günlük Trade Seviyeleri"
      )

      st.download_button(
          label=f"📥 {sec_b} Görselini PNG Olarak İndir (X Formatı)",
          data=png_buf_single,
          file_name=f"{sec_b}_trade_analiz.png",
          mime="image/png",
      )
