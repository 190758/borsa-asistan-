from datetime import datetime, timedelta
import io
import re
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf

# ---------------------------------------------------------
# SAYFA VE TEMA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="BIST Temel & Teknik Analiz Terminali | @trader_gandalf",
    page_icon="📈",
    layout="wide",
)

st.title("🧙‍♂️ BIST Hisseleri Çok Yönlü Analiz & Projeksiyon Terminali")
st.caption(
    "Temettü verimi, Graham Değerlemesi, Monte Carlo Simülasyonu ve X"
    " Görsel Üreteci"
)


# ---------------------------------------------------------
# 1. HİSSE LİSTELERİ
# ---------------------------------------------------------
@st.cache_data
def get_bist_tickers():
  top_tickers = [
      "FROTO",
      "ISMEN",
      "ANHYT",
      "ARDYZ",
      "ALTNY",
      "YEOTK",
      "KCHOL",
      "SOKM",
      "AGHOL",
      "ALARK",
      "LILAK",
      "CWENE",
      "BETAE",
      "KLYPV",
      "TEHOL",
      "THYAO",
      "ASELS",
      "SISE",
      "TUPRS",
      "EREGL",
      "BIMAS",
  ]
  all_tickers = sorted(
      list(
          set(
              top_tickers
              + [
                  "GARAN",
                  "AKBNK",
                  "YKBNK",
                  "SAHOL",
                  "PETKM",
                  "PGSUS",
                  "DOAS",
                  "TTKOM",
                  "TCELL",
              ]
          )
      )
  )
  return top_tickers, all_tickers


# ---------------------------------------------------------
# 2. X (TWITTER) FORMATLI TEMALI PNG TABLO ÜRETİCİ
# ---------------------------------------------------------
def generate_x_table_image(df, title="BIST Finansal Analiz Tablosu"):
  if df.empty:
    df = pd.DataFrame({"Uyarı": ["Gösterilecek Veri Bulunamadı"]})

  fig, ax = plt.subplots(figsize=(12, max(4, len(df) * 0.7)), dpi=300)
  fig.patch.set_facecolor("#15202B")
  ax.set_facecolor("#15202B")
  ax.axis("off")

  plt.title(
      title, color="#FFFFFF", fontsize=15, fontweight="bold", pad=20, loc="center"
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
      fontsize=9,
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


# ---------------------------------------------------------
# 3. KESİNTİSİZ VERİ ÇEKME MOTORU (ENGEL AŞICI)
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def get_stock_data(symbol):
  clean_symbol = symbol.replace(".IS", "").strip().upper()
  ticker_str = f"{clean_symbol}.IS"

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  # Katman 1: Direct Yahoo Chart Endpoint
  try:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_str}?range=2y&interval=1d"
    resp = requests.get(url, headers=headers, timeout=5)
    if resp.status_code == 200:
      data = resp.json()
      result = data["chart"]["result"][0]
      timestamps = result["timestamp"]
      quotes = result["indicators"]["quote"][0]

      df = pd.DataFrame({
          "Open": quotes.get("open"),
          "High": quotes.get("high"),
          "Low": quotes.get("low"),
          "Close": quotes.get("close"),
          "Volume": quotes.get("volume"),
      })
      df.index = pd.to_datetime(timestamps, unit="s")
      df = df.dropna(subset=["Close"])

      # Meta bilgilerini al
      meta = result.get("meta", {})
      info = {
          "trailingPE": meta.get("trailingPE", 0.0),
          "priceToBook": meta.get("priceToBook", 0.0),
          "dividendYield": meta.get("dividendYield", 0.0),
      }
      if not df.empty and len(df) > 10:
        return df, info
  except Exception:
    pass

  # Katman 2: yfinance Kütüphanesi
  try:
    df = yf.download(ticker_str, period="2y", interval="1d", progress=False)
    if not df.empty and len(df) > 10:
      if isinstance(df.columns, pd.MultiIndex):
        df = df.xs(ticker_str, level=1, axis=1)
      t = yf.Ticker(ticker_str)
      return df, getattr(t, "info", {})
  except Exception:
    pass

  return pd.DataFrame(), {}


# Dolar Kuru
df_usd, _ = get_stock_data("USDTRY=X")
usd_try = (
    float(df_usd["Close"].iloc[-1])
    if (not df_usd.empty and "Close" in df_usd.columns)
    else 34.0
)

top_list, all_list = get_bist_tickers()

# ---------------------------------------------------------
# SEKMELER (TABS)
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📈 Single Hisse 1 Yıllık Tahmin & Monte Carlo",
    "📊 Çoklu Temel Analiz & Graham / Temettü Değerlemesi",
    "🖼️ X Paylaşım Kartı Üreteci",
])

# ---------------------------------------------------------
# SEKME 1: TEK HİSSE TAHMİNİ & MONTE CARLO
# ---------------------------------------------------------
with tab1:
  st.header("🔍 Hisse Projeksiyonu & Monte Carlo Simülasyonu")
  col_s1, col_s2 = st.columns([2, 1])
  with col_s1:
    selected_stock = st.selectbox("Hisse Seçiniz:", all_list, index=0)
  with col_s2:
    custom_stock = st.text_input(
        "Veya Manuel Kod Girin (Örn: AGHOL):"
    ).upper()

  target_stock = custom_stock if custom_stock else selected_stock

  if st.button(f"🚀 {target_stock} Projeksiyon Analizini Başlat"):
    hist, info = get_stock_data(target_stock)
    if hist.empty:
      st.error(
          f"❌ {target_stock} verisi çekilemedi. Lütfen bağlantınızı veya hisse"
          " kodunu kontrol edin."
      )
    else:
      close = hist["Close"]
      last_price = float(close.iloc[-1])
      returns = close.pct_change().dropna()

      ann_return = returns.mean() * 252 if len(returns) > 0 else 0.15
      ann_vol = (
          returns.std() * np.sqrt(252)
          if (len(returns) > 0 and returns.std() > 0)
          else 0.30
      )

      future_days = 252
      t = np.linspace(1 / 252, 1, future_days)
      base_proj = last_price * np.exp((ann_return - 0.5 * ann_vol**2) * t)
      bull_proj = last_price * np.exp(
          ((ann_return + ann_vol) - 0.5 * ann_vol**2) * t
      )
      bear_proj = last_price * np.exp(
          ((ann_return - ann_vol) - 0.5 * ann_vol**2) * t
      )

      dates = [hist.index[-1] + timedelta(days=i) for i in range(1, future_days + 1)]

      m1, m2, m3, m4 = st.columns(4)
      m1.metric("Son Fiyat", f"{last_price:.2f} TL", f"${last_price/usd_try:.2f}")
      m2.metric(
          "1 Yıl Baz Hedef",
          f"{base_proj[-1]:.2f} TL",
          f"%{((base_proj[-1]/last_price)-1)*100:.1f}",
      )
      m3.metric(
          "İyimser Senaryo (+1σ)",
          f"{bull_proj[-1]:.2f} TL",
          f"%{((bull_proj[-1]/last_price)-1)*100:.1f}",
      )
      m4.metric(
          "Kötümser Senaryo (-1σ)",
          f"{bear_proj[-1]:.2f} TL",
          f"%{((bear_proj[-1]/last_price)-1)*100:.1f}",
      )

      fig = go.Figure()
      fig.add_trace(
          go.Scatter(
              x=hist.index,
              y=close,
              name="Geçmiş Fiyat",
              line=dict(color="#1DA1F2", width=2),
          )
      )
      fig.add_trace(
          go.Scatter(
              x=dates,
              y=base_proj,
              name="Baz Projeksiyon",
              line=dict(color="#FFD700", dash="dash"),
          )
      )
      fig.add_trace(
          go.Scatter(
              x=dates,
              y=bull_proj,
              name="İyimser (+1σ)",
              line=dict(color="#00FF7F", dash="dot"),
          )
      )
      fig.add_trace(
          go.Scatter(
              x=dates,
              y=bear_proj,
              name="Kötümser (-1σ)",
              line=dict(color="#FF4500", dash="dot"),
          )
      )
      fig.update_layout(
          title=f"#{target_stock} 1 Yıllık Gelecek Trend Projeksiyonu",
          template="plotly_dark",
      )
      st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# SEKME 2: ÇOKLU HİSSE & GRAHAM/TEMETTÜ DEĞERLEMESİ
# ---------------------------------------------------------
with tab2:
  st.header("💎 Temettü Verimi & Graham Değerleme Tablosu")
  selected_multi = st.multiselect(
      "Karşılaştırılacak Hisseler:",
      all_list,
      default=["FROTO", "ISMEN", "ANHYT", "AGHOL", "ALARK"],
  )

  if st.button("📊 Taramayı Çalıştır"):
    rows = []
    progress = st.progress(0)
    for idx, sym in enumerate(selected_multi):
      hist, info = get_stock_data(sym)
      if not hist.empty:
        l_price = float(hist["Close"].iloc[-1])
        pe = info.get("trailingPE", 0.0) or 0.0
        pb = info.get("priceToBook", 0.0) or 0.0
        div_rate = info.get("dividendYield", 0.0) or 0.0

        eps = l_price / pe if pe > 0 else 0.0
        bvps = l_price / pb if pb > 0 else 0.0
        graham_fair = (
            np.sqrt(22.5 * eps * bvps) if (eps > 0 and bvps > 0) else 0.0
        )

        rows.append({
            "Hisse": sym,
            "Fiyat (TL)": f"{l_price:.2f}",
            "F/K": f"{pe:.2f}" if pe > 0 else "N/A",
            "PD/DD": f"{pb:.2f}" if pb > 0 else "N/A",
            "Temettü Verimi": f"%{div_rate*100:.2f}",
            "Graham Adil Değer": (
                f"{graham_fair:.2f} TL" if graham_fair > 0 else "N/A"
            ),
            "Iskonto Durumu": (
                f"%{((graham_fair/l_price)-1)*100:.1f}"
                if graham_fair > 0
                else "N/A"
            ),
        })
      time.sleep(0.05)
      progress.progress((idx + 1) / len(selected_multi))

    res_df = pd.DataFrame(rows)

    if not res_df.empty:
      st.dataframe(res_df, use_container_width=True)

      img = generate_x_table_image(
          res_df, title="BIST Seçili Hisseler Temel & Graham Analizi"
      )
      st.download_button(
          label="📥 Tablo Görselini İndir (X Paylaşımı İçin)",
          data=img,
          file_name="bist_temel_analiz.png",
          mime="image/png",
      )
    else:
      st.warning(
          "⚠️ Seçilen hisseler için veri çekilemedi. Lütfen tekrar deneyin."
      )

# ---------------------------------------------------------
# SEKME 3: X PAYLAŞIM KART ÜRETECİ (@trader_gandalf)
# ---------------------------------------------------------
with tab3:
  st.header("🖼️ Özel X Paylaşım Tablosu Üreticisi")
  st.info(
      "Bu bölümde X (@trader_gandalf) hesabınızda paylaşmak üzere özel"
      " verilerle anında görsel üretebilirsiniz."
  )

  table_title = st.text_input(
      "Tablo Başlığı:", value="BIST Temettü & Büyüme Hisseleri Takip Listesi"
  )

  sample_data = pd.DataFrame({
      "Hisse": ["FROTO", "ISMEN", "AGHOL", "ARDYZ", "ALTNY"],
      "Kapanış": ["1020.00 TL", "74.50 TL", "310.00 TL", "55.30 TL", "98.40 TL"],
      "Hedef Fiyat": [
          "1450.00 TL",
          "115.00 TL",
          "450.00 TL",
          "85.00 TL",
          "150.00 TL",
      ],
      "Potansiyel": ["%+42.1", "%+54.3", "%+45.1", "%+53.7", "%+52.4"],
      "Strateji": [
          "Temettü Verimi",
          "Yüksek Kar",
          "Holding / Büyüme",
          "Yazılım/Teknoloji",
          "Savunma Sanayi",
      ],
  })

  edited_df = st.data_editor(sample_data, num_rows="dynamic")

  if st.button("🖼️ X Görselini Oluştur"):
    gen_img = generate_x_table_image(edited_df, title=table_title)
    st.image(gen_img, caption="X Paylaşım Görsel Önizleme", width=700)
    st.download_button(
        label="📥 PNG Olarak İndir (High Quality)",
        data=gen_img,
        file_name="trader_gandalf_paylasim.png",
        mime="image/png",
    )
