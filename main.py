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
        import io
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Page Configuration
st.set_page_config(
    page_title="BIST Tüm Hisseler - 1 Yıllık Projeksiyon & Analiz",
    layout="wide",
)

st.title("⚡ BIST Tüm Hisseler - 1 Yıllık Fiyat & Grafik Projeksiyonu")
st.caption(
    "Borsa İstanbul'daki tüm hisseler için geçmiş veri analizi, 1 yıl sonraki"
    " hedef fiyat tahminleri ve X (Twitter) paylaşım görselleri."
)


# 1. BIST TÜM HİSSELERİ LİSTESİ (Sık İşlem Gören Popüler + Genel Liste)
@st.cache_data
def get_bist_all_tickers():
  # BIST üzerindeki yaygın hisse kodları
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

# ==========================================
# SEKME 1: TEK HİSSE DETAYLI 1 YILLIK PROJEKSİYON
# ==========================================
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
    with st.spinner(f"{target_ticker} geçmiş verileri ve trendi işleniyor..."):
      df_stock = fetch_stock_data(target_ticker)

      if df_stock.empty:
        st.error(
            f"❌ {target_ticker} için veri bulunamadı. Lütfen borsa kodunu"
            " kontrol edin."
        )
      else:
        close_prices = df_stock["Close"]
        last_price = float(close_prices.iloc[-1])

        # Yıllıklandırılmış Getiri & Volatillik Hesaplama
        daily_returns = close_prices.pct_change().dropna()
        avg_daily_ret = daily_returns.mean()
        daily_vol = daily_returns.std()

        annual_ret = avg_daily_ret * 252
        annual_vol = daily_vol * np.sqrt(252)

        # 1 Yıl (365 Gün) Gelecek Tarih Silsilesi Oluşturma
        last_date = df_stock.index[-1]
        future_dates = [last_date + timedelta(days=i) for i in range(1, 366)]

        # 3 Farklı Senaryo İle 1 Yıl Sonraki Fiyat Yolu
        t = np.linspace(1 / 252, 1, 365)

        # 1. Baz Senaryo (Mevcut Trend)
        base_projection = last_price * np.exp(
            (annual_ret - 0.5 * annual_vol**2) * t
        )
        # 2. İyimser Senaryo (+1 Standart Sapma)
        bull_projection = last_price * np.exp(
            ((annual_ret + annual_vol) - 0.5 * annual_vol**2) * t
        )
        # 3. Kötümser Senaryo (-1 Standart Sapma)
        bear_projection = last_price * np.exp(
            ((annual_ret - annual_vol) - 0.5 * annual_vol**2) * t
        )

        target_base = base_projection[-1]
        target_bull = bull_projection[-1]
        target_bear = bear_projection[-1]
        target_date_str = future_dates[-1].strftime("%d.%m.%Y")

        # Metrikler
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

        # PLOTLY GRAFİĞİ (Geçmiş + 1 Yıl Gelecek Projeksiyonu)
        fig = go.Figure()

        # Geçmiş Fiyat
        fig.add_trace(
            go.Scatter(
                x=df_stock.index,
                y=close_prices,
                mode="lines",
                name="Geçmiş Fiyat",
                line=dict(color="#1DA1F2", width=2),
            )
        )

        # Baz Projeksiyon
        fig.add_trace(
            go.Scatter(
                x=future_dates,
                y=base_projection,
                mode="lines",
                name="Baz Senaryo (Mevcut Trend)",
                line=dict(color="#FFD700", width=2, dash="dash"),
            )
        )

        # İyimser Senaryo
        fig.add_trace(
            go.Scatter(
                x=future_dates,
                y=bull_projection,
                mode="lines",
                name="İyimser (+1σ)",
                line=dict(color="#00FF7F", width=1.5, dash="dot"),
            )
        )

        # Kötümser Senaryo
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
            title=f"#{target_ticker} 1 Yıllık Tarih Bazlı Fiyat Projeksiyon Grafiği",
            template="plotly_dark",
            xaxis_title="Tarih",
            yaxis_title="Fiyat (TL)",
            height=500,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Özet İndirme Tablosu
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

# ==========================================
# SEKME 2: ÇOKLU HİSSE TAHMİNİ LİSTESİ
# ==========================================
with tab2:
  st.header("📊 Çoklu Hisse Karşılaştırmalı 1 Yıllık Tahmin")
  selected_multi = st.multiselect(
      "Analiz Edilecek Hisseleri Seçin:",
      all_bist,
      default=["FROTO", "ISMEN", "THYAO", "ASELS", "KCHOL"],
  )

  if st.button("🚀 Seçili Hisselerin 1 Yıllık Tahminlerini Taramasını Başlat"):
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
        label="📥 Tüm Karşılaştırma Tablosunu PNG Olarak İndir (X Formatı)",
        data=buf_multi,
        file_name="bist_coklu_1_yillik_tahminler.png",
        mime="image/png",
    )
