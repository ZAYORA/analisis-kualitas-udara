from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import streamlit as st

# ---------- Konfigurasi halaman ----------
st.set_page_config(page_title="Dashboard Kualitas Udara Beijing", page_icon="🌫️", layout="wide")

GREY, RED, BLUE = "#BFC5CC", "#D1495B", "#2E86AB"
BATAS = 75  # batas harian PM2.5 (µg/m³)
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
URUT_KATEGORI = ["Baik", "Sedang", "Tidak sehat bagi sensitif", "Tidak sehat", "Sangat tidak sehat", "Berbahaya"]
WARNA_KATEGORI = ["#4C9F70", "#E9C46A", "#F4A261", "#E76F51", "#B5446E", "#6D2E46"]

plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False


@st.cache_data
def load_data():
    path = Path(__file__).parent / "main_data.csv"
    df = pd.read_csv(path, parse_dates=["tanggal", "bulan_tahun"])
    return df


df = load_data()

# ---------- Sidebar (filter) ----------
st.sidebar.header("Filter Data")
tgl_min, tgl_max = df["tanggal"].min().date(), df["tanggal"].max().date()
rentang = st.sidebar.date_input("Rentang tanggal", value=(tgl_min, tgl_max), min_value=tgl_min, max_value=tgl_max)
semua_stasiun = sorted(df["station"].unique())
pilih_stasiun = st.sidebar.multiselect("Stasiun", semua_stasiun, default=semua_stasiun)

if isinstance(rentang, tuple) and len(rentang) == 2:
    awal, akhir = rentang
else:
    awal, akhir = tgl_min, tgl_max

data = df[
    (df["tanggal"].dt.date >= awal)
    & (df["tanggal"].dt.date <= akhir)
    & (df["station"].isin(pilih_stasiun))
]

st.title("🌫️ Dashboard Kualitas Udara Beijing")
st.caption("Data PM2.5 harian dari 12 stasiun pemantau (Maret 2013 - Februari 2017). Batas harian acuan: 75 µg/m³.")

if data.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Ubah rentang tanggal atau pilih minimal satu stasiun.")
    st.stop()

# ---------- Ringkasan ----------
per_stasiun = (
    data.assign(lewat=data["PM25"] > BATAS)
    .groupby("station")
    .agg(rata_PM25=("PM25", "mean"), persen_hari_lewat=("lewat", "mean"))
)
per_stasiun["persen_hari_lewat"] *= 100
per_bulan = data.groupby("bulan")["PM25"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Rata-rata PM2.5", f"{data['PM25'].mean():.1f} µg/m³")
c2.metric("Hari melebihi 75 µg/m³", f"{(data['PM25'] > BATAS).mean() * 100:.1f}%")
c3.metric("Stasiun tertinggi", per_stasiun["rata_PM25"].idxmax())
c4.metric("Bulan tertinggi", BULAN[per_bulan.idxmax() - 1])

tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Tren & Musiman (Pertanyaan 1)", "🏙️ Perbandingan Stasiun (Pertanyaan 2)", "🎨 Kategori Kualitas Udara", "🗺️ Peta Stasiun"]
)

# ---------- Tab 1 ----------
with tab1:
    col_a, col_b = st.columns([1.4, 1])
    with col_a:
        tren = data.groupby("bulan_tahun")["PM25"].mean()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(tren.index, tren.values, color=GREY, lw=2)
        ax.axhline(BATAS, color=RED, ls="--", lw=1)
        ax.text(tren.index[0], BATAS + 3, "Batas harian 75 µg/m³", color=RED, fontsize=8)
        puncak = tren.nlargest(3)
        ax.scatter(puncak.index, puncak.values, color=RED, zorder=3)
        for t, v in puncak.items():
            ax.annotate(f"{v:.0f}", (t, v), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8, color=RED)
        ax.set_title("Tren bulanan PM2.5", loc="left", fontweight="bold")
        ax.set_ylabel("PM2.5 rata-rata (µg/m³)")
        st.pyplot(fig)
    with col_b:
        tinggi, rendah = per_bulan.idxmax(), per_bulan.idxmin()
        warna = [RED if m == tinggi else BLUE if m == rendah else GREY for m in per_bulan.index]
        fig, ax = plt.subplots(figsize=(5, 4))
        bars = ax.bar([BULAN[m - 1] for m in per_bulan.index], per_bulan.values, color=warna)
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5, f"{b.get_height():.0f}", ha="center", fontsize=7)
        ax.set_title(f"Per bulan: tertinggi {BULAN[tinggi - 1]}, terendah {BULAN[rendah - 1]}", loc="left", fontweight="bold", fontsize=10)
        st.pyplot(fig)

    per = data.groupby("periode")["PM25"].mean()
    fig, ax = plt.subplots(figsize=(7, 3.6))
    warna = [GREY] + [BLUE if v < per.iloc[0] else RED for v in per.iloc[1:]]
    bars = ax.bar(per.index, per.values, color=warna, width=0.55)
    for b, v in zip(bars, per.values):
        pct = (v / per.iloc[0] - 1) * 100
        label = f"{v:.1f}" + ("" if b is bars[0] else f"\n({pct:+.1f}%)")
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1, label, ha="center", fontsize=8)
    ax.set_ylim(0, per.max() * 1.25)
    ax.set_title("Rata-rata PM2.5 per periode (Maret-Februari), perubahan vs periode pertama", loc="left", fontweight="bold", fontsize=10)
    st.pyplot(fig)

# ---------- Tab 2 ----------
with tab2:
    a = per_stasiun.sort_values("rata_PM25")
    b = per_stasiun.sort_values("persen_hari_lewat")
    wa = [RED if s == a.index[-1] else BLUE if s == a.index[0] else GREY for s in a.index]
    wb = [RED if s == b.index[-1] else BLUE if s == b.index[0] else GREY for s in b.index]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].barh(a.index, a["rata_PM25"], color=wa)
    for i, v in enumerate(a["rata_PM25"]):
        axes[0].text(v + 0.8, i, f"{v:.1f}", va="center", fontsize=8)
    axes[0].set_title("Rata-rata PM2.5 (µg/m³)", loc="left", fontweight="bold")
    axes[0].set_xlim(0, a["rata_PM25"].max() * 1.15)
    axes[1].barh(b.index, b["persen_hari_lewat"], color=wb)
    for i, v in enumerate(b["persen_hari_lewat"]):
        axes[1].text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=8)
    axes[1].set_title("% hari melebihi 75 µg/m³", loc="left", fontweight="bold")
    axes[1].xaxis.set_major_formatter(mtick.PercentFormatter())
    axes[1].set_xlim(0, b["persen_hari_lewat"].max() * 1.15)
    plt.tight_layout()
    st.pyplot(fig)
    st.dataframe(per_stasiun.sort_values("rata_PM25", ascending=False).round(1).rename(
        columns={"rata_PM25": "Rata-rata PM2.5", "persen_hari_lewat": "% hari > 75"}))

# ---------- Tab 3 ----------
with tab3:
    kat = data.groupby(["station", "kategori"]).size().unstack(fill_value=0)
    kat = kat.reindex(columns=[k for k in URUT_KATEGORI if k in kat.columns], fill_value=0)
    kat_persen = kat.div(kat.sum(axis=1), axis=0) * 100
    kat_persen = kat_persen.loc[per_stasiun.sort_values("rata_PM25").index]
    warna_k = [WARNA_KATEGORI[URUT_KATEGORI.index(k)] for k in kat_persen.columns]
    fig, ax = plt.subplots(figsize=(10, 5))
    kat_persen.plot(kind="barh", stacked=True, color=warna_k, ax=ax, width=0.75)
    ax.set_title("Komposisi kategori kualitas udara harian per stasiun", loc="left", fontweight="bold")
    ax.set_xlabel("% hari")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.legend(title="Kategori PM2.5", bbox_to_anchor=(1.01, 1), loc="upper left", frameon=False)
    plt.tight_layout()
    st.pyplot(fig)

# ---------- Tab 4 ----------
with tab4:
    st.write("Ukuran dan warna titik menunjukkan rata-rata PM2.5 stasiun (merah = lebih tinggi). Koordinat stasiun adalah perkiraan.")
    peta = per_stasiun.join(data.groupby("station")[["lat", "lon"]].first()).reset_index()
    norm = (peta["rata_PM25"] - peta["rata_PM25"].min()) / max(peta["rata_PM25"].max() - peta["rata_PM25"].min(), 1e-9)
    peta["color"] = [f"#{int(230 - 30 * (1 - n)):02x}{int(190 - 130 * n):02x}{int(70 - 10 * n):02x}" for n in norm]
    peta["size"] = peta["rata_PM25"] * 12
    st.map(peta, latitude="lat", longitude="lon", size="size", color="color")
    st.dataframe(peta[["station", "rata_PM25", "persen_hari_lewat"]].round(1).set_index("station"))

st.caption("Sumber data: PRSA Beijing Multi-Site Air Quality Data (Dicoding Analisis Data).")
