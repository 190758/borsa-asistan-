from datetime import datetime, timedelta
import io
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Sayfa Yapılandırması
st.set_page_config(
    page_title="BIST Tüm Hisseler - 1 Yıllık Projeksiyon & Analiz",
    layout="wide",
)

st.title("⚡ BIST Tüm Hisseler - 1 Yıllık Fiyat & Grafik Projeksiyonu")
st.caption(
    "Borsa İstanbul'daki tüm hisseler için geçmiş veri analizi, 1 yıl sonraki"
    " hedef fiyat tahminleri ve X (Twitter) paylaşım görselleri."
)


# 1. BIST TÜM HİSSELERİ LİSTESİ
@st.cache_data
def get_bist_all_tickers():
  tickers = [
      "AAVST",
      "ABODV",
      "ADEL",
      "ADESE",
      "AEFES",
      "AFYON",
      "AGESA",
      "AGHOL",
      "AGROT",
      "AHGAZ",
      "AKBNK",
      "AKCNS",
      "AKFGY",
      "AKFYE",
      "AKGRT",
      "AKMGY",
      "AKSA",
      "AKSEN",
      "AKSUE",
      "AKYHO",
      "ALARK",
      "ALBRK",
      "ALCAR",
      "ALCTL",
      "ALFAS",
      "ALGYO",
      "ALKA",
      "ALMAD",
      "ALTNY",
      "ALVES",
      "ANELE",
      "ANGEN",
      "ANHYT",
      "ANSGR",
      "ARCLK",
      "ARDYZ",
      "ARENA",
      "ARSAN",
      "ARTMS",
      "ARZUM",
      "ASELS",
      "ASGYO",
      "ASTOR",
      "ATAGY",
      "ATAKP",
      "ATEKS",
      "ATLAS",
      "ATSYH",
      "AVOD",
      "AVPGY",
      "AVTUR",
      "AYCES",
      "AYDEM",
      "AYGAZ",
      "AZTEK",
      "BAGFS",
      "BAKAB",
      "BALAT",
      "BANVT",
      "BARMA",
      "BASGZ",
      "BAYRK",
      "BEVT",
      "BFREN",
      "BIENP",
      "BIGCHEFS",
      "BIMAS",
      "BINBN",
      "BIOEN",
      "BIZIM",
      "BJKAS",
      "BLCYT",
      "BMSCH",
      "BMSTL",
      "BNTAS",
      "BOBET",
      "BORLS",
      "BORSK",
      "BOSSA",
      "BRKVY",
      "BRMEN",
      "BRSAN",
      "BRSAT",
      "BRYAT",
      "BSOKE",
      "BTCIM",
      "BUCIM",
      "BURCE",
      "BURVA",
      "BVSAN",
      "BYDNR",
      "CANTE",
      "CASA",
      "CCHOL",
      "CCOLA",
      "CELHA",
      "CEMAS",
      "CEMTS",
      "CMBTN",
      "CMENT",
      "CONSE",
      "COSMO",
      "CRFSA",
      "CRDFA",
      "CUSAN",
      "CWENE",
      "DAGHL",
      "DAGI",
      "DAPGM",
      "DARDL",
      "DGATE",
      "DGGYO",
      "DITAS",
      "DMRGD",
      "DMSAS",
      "DNISI",
      "DOAS",
      "DOCO",
      "DOGUB",
      "DOHOL",
      "DOKTA",
      "DURDO",
      "DYOBY",
      "DZGYO",
      "EBEBK",
      "ECILC",
      "ECZYT",
      "EDATA",
      "EDIP",
      "EGEEN",
      "EGGUB",
      "EGPRO",
      "EGSER",
      "EKGYO",
      "EKOS",
      "EKSUN",
      "ELITE",
      "EMKEL",
      "ENJSA",
      "ENKAI",
      "ENTRA",
      "EPLAS",
      "ERCB",
      "EREGL",
      "ERHS",
      "ESCAR",
      "ESEN",
      "ETILR",
      "EUPWR",
      "EUREK",
      "EYGYO",
      "FADE",
      "FLAP",
      "FMIZP",
      "FONET",
      "FORMT",
      "FORTE",
      "FRIGO",
      "FROTO",
      "FZLGY",
      "GARAN",
      "GARFA",
      "GEDIK",
      "GEDZA",
      "GENIL",
      "GENTS",
      "GEREL",
      "GESAN",
      "GIPTA",
      "GLBMD",
      "GLYHO",
      "GMTAS",
      "GOKNR",
      "GOLTS",
      "GOODY",
      "GOZDE",
      "GRSEL",
      "GRTHO",
      "GSDHO",
      "GSDEO",
      "GUBRF",
      "GWIND",
      "GZTAN",
      "HALKB",
      "HATSN",
      "HDFGS",
      "HEDEF",
      "HEKTS",
      "HKTM",
      "HLGYO",
      "HTTBT",
      "HUBVC",
      "HUNER",
      "HURGZ",
      "ICBCT",
      "IMASM",
      "INDES",
      "INFO",
      "INGRM",
      "INTEM",
      "INVSEO",
      "INVEO",
      "INVES",
      "IPEKE",
      "ISATR",
      "ISBTR",
      "ISCTR",
      "ISDMR",
      "ISFIN",
      "ISGSY",
      "ISGYO",
      "ISKPL",
      "ISMEN",
      "ISSEN",
      "ITEKS",
      "ITTFH",
      "IZINV",
      "IZMDC",
      "JANTS",
      "KAEFD",
      "KAPLM",
      "KAREL",
      "KARSN",
      "KARTN",
      "KATMR",
      "KAYSE",
      "KCAER",
      "KCHOL",
      "KENT",
      "KRTEK",
      "KFCOR",
      "KLKIM",
      "KLMSN",
      "KLNMA",
      "KLRHO",
      "KLSER",
      "KLSYN",
      "KMCPO",
      "KNCOR",
      "KONTR",
      "KONYA",
      "KORDS",
      "KOZAL",
      "KOZAA",
      "KRPLS",
      "KRSTL",
      "KRVGD",
      "KSTUR",
      "KTLEV",
      "KTYGS",
      "KUTPO",
      "KGYO",
      "LIDER",
      "LILAK",
      "LINK",
      "LKMNH",
      "LMKDC",
      "LOGOS",
      "LRERP",
      "LUKSK",
      "MAALT",
      "MACKO",
      "MAKIM",
      "MAKTK",
      "MANAS",
      "MARKA",
      "MARTI",
      "MAVI",
      "MEDTR",
      "MEGAP",
      "MEGMT",
      "MEPET",
      "MERCN",
      "MERKO",
      "METRO",
      "METUR",
      "MHRGY",
      "MIATK",
      "MIPAZ",
      "MMCAS",
      "MNDRS",
      "MNDTR",
      "MOBTL",
      "MTRKS",
      "MGROS",
      "MPARK",
      "MRGYO",
      "MRSHL",
      "MSGYO",
      "MTRKS",
      "NATEN",
      "NETAS",
      "NIBAS",
      "NTGAZ",
      "NTHOL",
      "NUGYO",
      "OBAMS",
      "OBASE",
      "ODAS",
      "OFSYM",
      "ONCSM",
      "ORGE",
      "ORMA",
      "ORTBO",
      "OTKAR",
      "OTTO",
      "OYAKC",
      "OYAYO",
      "OYLUM",
      "OYYAT",
      "OZKGY",
      "OZSUB",
      "PAGYO",
      "PAMEL",
      "PAPIL",
      "PARSN",
      "PASEU",
      "PENGD",
      "PENTX",
      "PETKM",
      "PKART",
      "PGSUS",
      "PLTUR",
      "PNLSN",
      "PNSUT",
      "POLHO",
      "POLTK",
      "PRDGS",
      "PRKAB",
      "PRKME",
      "PRZMA",
      "PSGYO",
      "QNBFB",
      "QNBFL",
      "QUAGR",
      "RALYH",
      "RAYSG",
      "REEDR",
      "RGYAS",
      "RNPOL",
      "RODRG",
      "ROYAL",
      "RTALB",
      "RUBNS",
      "RYGYO",
      "RYSAS",
      "SAHOL",
      "SAMAT",
      "SANEL",
      "SANFM",
      "SANKO",
      "SARKY",
      "SASA",
      "SAYAS",
      "SDTTR",
      "SEKFK",
      "SEKUR",
      "SELEC",
      "SELVA",
      "SEYKM",
      "SILVR",
      "SISE",
      "SKBNK",
      "SKTAS",
      "SMART",
      "SMRTG",
      "SNAAM",
      "SNICA",
      "SNKRN",
      "SNPAM",
      "SODSN",
      "SOKM",
      "SONME",
      "SRVGY",
      "SUMAS",
      "SUNTK",
      "SURGY",
      "SUWEN",
      "TABGD",
      "TARKM",
      "TATEN",
      "TATGD",
      "TAVHL",
      "TCELL",
      "TCKRC",
      "TEKTU",
      "TERA",
      "TETMT",
      "TEZOL",
      "THYAO",
      "TKFEN",
      "TKNSA",
      "TLMAN",
      "TMPOL",
      "TMSN",
      "TNZTP",
      "TOASO",
      "TRCAS",
      "TRGYO",
      "TRILC",
      "TSKB",
      "TSPOR",
      "TTKOM",
      "TTRAK",
      "TUCLK",
      "TUPRS",
      "TUREX",
      "TURGG",
      "TURSG",
      "UFUK",
      "ULAS",
      "ULKER",
      "UNLU",
      "USAK",
      "VAKBN",
      "VAKFN",
      "VAKKO",
      "VANGD",
      "VBTYZ",
      "VERTU",
      "VERUS",
      "VESBE",
      "VESTL",
      "VKFYO",
      "VKGYO",
      "VKING",
      "YAPRK",
      "YATAS",
      "YAYLA",
      "YEOTK",
      "YGYO",
      "YKBNK",
      "YONGA",
      "YUNSA",
      "YYLGD",
      "ZOREN",
      "ZRGYO",
  ]
  return sorted(list(set(tickers)))


# 2. X FORMATI İÇİN PNG GÖRSEL ÜRETİCİ
def generate_table_image(df, title="BIST Analiz Özeti"):
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


# 3. YFINANCE VERİ ÇEKME
@st.cache_data(ttl=600)
def fetch_stock_data(symbol):
  full_symbol = f"{symbol}.IS" if not symbol.endswith(".IS") else symbol
  try:
    df = yf.download(full_symbol, period="2y", interval="1d", progress=False)
    if not df.empty and len(df) > 30:
      if isinstance(df.columns, pd.MultiIndex):
        df = df.xs(full_symbol, level=1, axis=1)
      return df
  except Exception:
    pass
  return pd.DataFrame()


# USD KURU ÇEK
df_usd = fetch_stock_data("USDTRY=X")
usd_kur = (
    float(df_usd["Close"].iloc[-1])
    if (not df_usd.empty and "Close" in df_usd.columns)
    else 34.0
)

# ARAYÜZ SEKMELERİ
tab1, tab2 = st.tabs([
    "📈 Single Hisse 1 Yıllık Projeksiyon & Grafik",
    "🚀 Toplu Hisse Karşılaştırmalı 1 Yıl Tahmini",
])

all_bist = get_bist_all_tickers()

# SEKME 1: TEK HİSSE DETAYLI PROJEKSİYON
with tab1:
  st.header("🔍 Hisse Arama & 1 Yıl Sonraki Fiyat Projeksiyonu")

  col_search, col_custom = st.columns([2, 1])
  with col_search:
    selected_ticker = st.selectbox(
        "BIST Listesinden Hisse Seçin:", all_bist, index=all_bist.index("FROTO")
    )
  with col_custom:
    custom_ticker = st.text_input(
        "Veya Manuel Hisse Kodu Girin:", value=""
    ).upper()

  target_ticker = custom_ticker if custom_ticker else selected_ticker

  if st.button(f"📊 {target_ticker} 1 Yıllık Tahminini Çalıştır"):
    with st.spinner(f"{target_ticker} geçmiş verileri işleniyor..."):
      df_stock = fetch_stock_data(target_ticker)

      if df_stock.empty:
        st.error(f"❌ {target_ticker} için veri bulunamadı.")
      else:
        close_prices = df_stock["Close"]
        last_price = float(close_prices.iloc[-1])

        daily_returns = close_prices.pct_change().dropna()
        avg_daily_ret = daily_returns.mean()
        daily_vol = daily_returns.std()

        annual_ret = avg_daily_ret * 252
        annual_vol = daily_vol * np.sqrt(252)

        last_date = df_stock.index[-1]
        future_dates = [last_date + timedelta(days=i) for i in range(1, 366)]

        t = np.linspace(1 / 252, 1, 365)
        base_projection = last_price * np.exp(
            (annual_ret - 0.5 * annual_vol**2) * t
        )
        bull_projection = last_price * np.exp(
            ((annual_ret + annual_vol) - 0.5 * annual_vol**2) * t
        )
        bear_projection = last_price * np.exp(
            ((annual_ret - annual_vol) - 0.5 * annual_vol**2) * t
        )

        target_base = base_projection[-1]
        target_bull = bull_projection[-1]
        target_bear = bear_projection[-1]
        target_date_str = future_dates[-1].strftime("%d.%m.%Y")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Güncel Fiyat", f"{last_price:.2f} TL", f"${last_price/usd_kur:.2f}")
        m2.metric(
            f"1 Yıl Sonra ({target_date_str}) Baz",
            f"{target_base:.2f} TL",
            f"%{((target_base/last_price)-1)*100:.1f}",
        )
        m3.metric(
            "İyimser Hedef (+1σ)",
            f"{target_bull:.2f} TL",
            f"%{((target_bull/last_price)-1)*100:.1f}",
        )
        m4.metric(
            "Kötümser Hedef (-1σ)",
            f"{target_bear:.2f} TL",
            f"%{((target_bear/last_price)-1)*100:.1f}",
        )

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_stock.index,
                y=close_prices,
                mode="lines",
                name="Geçmiş Fiyat",
                line=dict(color="#1DA1F2", width=2),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=future_dates,
                y=base_projection,
                mode="lines",
                name="Baz Senaryo",
                line=dict(color="#FFD700", width=2, dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=future_dates,
                y=bull_projection,
                mode="lines",
                name="İyimser (+1σ)",
                line=dict(color="#00FF7F", width=1.5, dash="dot"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=future_dates,
                y=bear_projection,
                mode="lines",
                name="Kötümser (-1σ)",
                line=dict(color="#FF4500", width=1.5, dash="dot"),
            )
        )

        fig.update_layout(
            title=f"#{target_ticker} 1 Yıllık Tarih Bazlı Projeksiyon Grafiği",
            template="plotly_dark",
            xaxis_title="Tarih",
            yaxis_title="Fiyat (TL)",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

        summary_df = pd.DataFrame([{
            "Hisse": target_ticker,
            "Mevcut Fiyat": f"{last_price:.2f} TL",
            "Hedef Tarih": target_date_str,
            "Kötümser Hedef": f"{target_bear:.2f} TL",
            "Baz Hedef": f"{target_base:.2f} TL",
            "İyimser Hedef": f"{target_bull:.2f} TL",
            "Potansiyel Getiri": f"%{((target_base/last_price)-1)*100:.1f}",
        }])

        st.dataframe(summary_df, use_container_width=True)

        buf = generate_table_image(
            summary_df, title=f"#{target_ticker} 1 Yıllık Fiyat Projeksiyon Özeti"
        )
        st.download_button(
            label=f"📥 #{target_ticker} 1 Yıllık Tahmin Tablosunu PNG Olarak İndir",
            data=buf,
            file_name=f"{target_ticker}_1_yillik_tahmin.png",
            mime="image/png",
        )

# SEKME 2: ÇOKLU HİSSE TAHMİNİ
with tab2:
  st.header("📊 Çoklu Hisse Karşılaştırmalı 1 Yıllık Tahmin")
  selected_multi = st.multiselect(
      "Analiz Edilecek Hisseleri Seçin:",
      all_bist,
      default=["FROTO", "ISMEN", "THYAO", "ASELS", "KCHOL"],
  )

  if st.button("🚀 Seçili Hisselerin 1 Yıllık Tahmin Taramasını Başlat"):
    multi_results = []
    progress_bar = st.progress(0)

    for idx, sym in enumerate(selected_multi):
      df_m = fetch_stock_data(sym)
      if not df_m.empty and len(df_m) > 30:
        c_p = df_m["Close"]
        l_p = float(c_p.iloc[-1])
        d_ret = c_p.pct_change().dropna()
        a_ret = d_ret.mean() * 252
        a_vol = d_ret.std() * np.sqrt(252)

        est_1y = l_p * np.exp(a_ret - 0.5 * a_vol**2)
        target_date_1y = (df_m.index[-1] + timedelta(days=365)).strftime(
            "%d.%m.%Y"
        )

        multi_results.append({
            "Hisse": sym,
            "Güncel Fiyat": f"{l_p:.2f} TL",
            "Hedef Tarih": target_date_1y,
            "1 Yıl Tahmini Fiyat": f"{est_1y:.2f} TL",
            "Beklenen Getiri (%)": f"%{((est_1y/l_p)-1)*100:.1f}",
            "Yıllık Volatillite": f"%{a_vol*100:.1f}",
        })

      progress_bar.progress((idx + 1) / len(selected_multi))

    res_df = pd.DataFrame(multi_results)
    st.dataframe(res_df, use_container_width=True)

    buf_multi = generate_table_image(
        res_df, title="BIST Seçili Hisseler 1 Yıllık Tahmin Özeti"
    )
    st.download_button(
        label="📥 Tüm Karşılaştırma Tablosunu PNG Olarak İndir",
        data=buf_multi,
        file_name="bist_coklu_1_yillik_tahminler.png",
        mime="image/png",
    )
