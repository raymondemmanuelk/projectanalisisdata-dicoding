import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="E-Commerce Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0d1b2a 0%, #1b2d45 100%);
    border-right: 1px solid #1e3a5f;
}
section[data-testid="stSidebar"] * {
    color: #e0eaff !important;
}

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0f2236 0%, #162d44 100%);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 18px 22px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
[data-testid="metric-container"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    color: #7bafd4 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: #e8f4ff !important;
}

.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #e8f4ff;
    border-left: 4px solid #2e86de;
    padding-left: 14px;
    margin: 28px 0 18px 0;
}

.insight-box {
    background: rgba(46, 134, 222, 0.08);
    border: 1px solid rgba(46, 134, 222, 0.25);
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 0.88rem;
    color: #a8c8e8;
    margin-top: 10px;
}

.logo-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0 28px 0;
}
.logo-svg-wrap {
    width: 110px;
    height: 110px;
    border-radius: 20px;
    background: linear-gradient(135deg, #1a3a5c, #0d2035);
    border: 2px solid #2e5f8a;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    margin-bottom: 12px;
}
.brand-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #e8f4ff !important;
    letter-spacing: 0.04em;
}
.brand-sub {
    font-size: 0.72rem;
    color: #6a9fc0 !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 2px;
}

hr {
    border-color: #1e3a5f !important;
    margin: 24px 0 !important;
}

.main .block-container {
    background-color: #0a1628;
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('all_data.csv')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['shipping_limit_date']      = pd.to_datetime(df['shipping_limit_date'])
    return df

all_df = load_data()

def create_monthly_orders(df, start, end):
    mask = (df['order_purchase_timestamp'].dt.date >= start) & \
           (df['order_purchase_timestamp'].dt.date <= end)
    filtered = df[mask].copy()
    filtered['order_month'] = filtered['order_purchase_timestamp'].dt.to_period('M')
    monthly = (filtered.groupby('order_month')['order_id']
               .count().reset_index()
               .rename(columns={'order_id': 'order_count'}))
    monthly['order_month'] = monthly['order_month'].astype(str)
    return monthly

def create_top_categories(df, start, end):
    mask = (df['shipping_limit_date'].dt.date >= start) & \
           (df['shipping_limit_date'].dt.date <= end)
    filtered = df[mask]
    top_category = (filtered.groupby('product_category_name_english')['order_item_id']
                    .count().reset_index()
                    .sort_values(by='order_item_id', ascending=False))
    return top_category.head(5)

def create_rfm(df, start, end):
    mask = (df['order_purchase_timestamp'].dt.date >= start) & \
           (df['order_purchase_timestamp'].dt.date <= end)
    filtered = df[mask].copy()
    filtered['total_price'] = filtered['price'] + filtered['freight_value']
    tanggal_acuan = filtered['order_purchase_timestamp'].max()
    rfm = filtered.groupby('customer_id').agg(
        recency  =('order_purchase_timestamp', lambda x: (tanggal_acuan - x.max()).days),
        frequency=('order_id', 'nunique'),
        monetary =('total_price', 'sum'),
    ).reset_index()
    return rfm

def style_fig(fig):
    fig.patch.set_facecolor('#0f2236')
    for ax in fig.get_axes():
        ax.set_facecolor('#0f2236')
        ax.tick_params(colors='#7bafd4')
        ax.xaxis.label.set_color('#7bafd4')
        ax.yaxis.label.set_color('#7bafd4')
        ax.title.set_color('#e8f4ff')
        for spine in ax.spines.values():
            spine.set_edgecolor('#1e3a5f')
    return fig

with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <div class="logo-svg-wrap">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="8" y="20" width="48" height="36" rx="5" fill="#1a4a7a" stroke="#2e86de" stroke-width="1.5"/>
                <path d="M20 20V16C20 11.58 23.58 8 28 8H36C40.42 8 44 11.58 44 16V20" stroke="#2e86de" stroke-width="2" stroke-linecap="round"/>
                <path d="M8 32H56" stroke="#2e86de" stroke-width="1.5"/>
                <rect x="26" y="28" width="12" height="10" rx="2" fill="#2e86de"/>
                <circle cx="48" cy="46" r="8" fill="#0d1b2a" stroke="#2e86de" stroke-width="1.5"/>
                <path d="M45 46L47 48L51 44" stroke="#2e86de" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="brand-name">Dashboard</div>
        <div class="brand-sub">E-Commerce Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🗓️ Filter Rentang Waktu")
    min_date = all_df['order_purchase_timestamp'].dt.date.min()
    max_date = all_df['order_purchase_timestamp'].dt.date.max()
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

    st.markdown("---")
    st.markdown("### ⚙️ Pengaturan Visualisasi")
    show_trendline = st.toggle("Tampilkan Trendline", value=True)
    chart_style = st.selectbox("Tema Grafik", ["Navy Dark", "Midnight", "Ocean"])

    palette_map = {
        "Navy Dark":  ("#2e86de", "#1a4a7a", "#0f2236"),
        "Midnight":   ("#a855f7", "#4c1d95", "#0f0a1e"),
        "Ocean":      ("#06b6d4", "#164e63", "#0a1f2e"),
    }
    accent, mid, bg = palette_map[chart_style]

    st.markdown("---")
    st.caption("© Raymond Emmanuel Krista · Dicoding 2026")

monthly_orders   = create_monthly_orders(all_df, start_date, end_date)
top_categories   = create_top_categories(all_df, start_date, end_date)
rfm              = create_rfm(all_df, start_date, end_date)

st.markdown("""
<h1 style='font-family:Syne,sans-serif; font-size:2.2rem; font-weight:800;
           color:#e8f4ff; margin-bottom:4px;'>
    📦 E-Commerce Analytics Dashboard
</h1>
<p style='color:#6a9fc0; font-size:0.9rem; margin-top:0;'>
    Brazilian E-Commerce (Olist) · Periode 2016–2018
</p>
""", unsafe_allow_html=True)

st.divider()

total_orders    = monthly_orders['order_count'].sum()
total_revenue   = (all_df[(all_df['order_purchase_timestamp'].dt.date >= start_date) &
                           (all_df['order_purchase_timestamp'].dt.date <= end_date)]
                   ['price'].sum())
total_customers = rfm['customer_id'].nunique()
avg_order_val   = total_revenue / total_orders if total_orders > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("🛒 Total Transaksi",  f"{total_orders:,}")
k2.metric("💰 Total Revenue",    f"R$ {total_revenue:,.0f}")
k3.metric("👥 Unique Customers", f"{total_customers:,}")
k4.metric("📊 Avg Order Value",  f"R$ {avg_order_val:,.1f}")

st.divider()

st.markdown("<div class='section-header'>📈 Pertanyaan 1 — Tren Jumlah Transaksi per Bulan</div>",
            unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(14, 4.5))
x = range(len(monthly_orders))
ax.fill_between(x, monthly_orders['order_count'], alpha=0.15, color=accent)
ax.plot(x, monthly_orders['order_count'],
        marker='o', linewidth=2.5, color=accent,
        markerfacecolor='white', markeredgecolor=accent, markersize=5)

if show_trendline and len(monthly_orders) > 2:
    import numpy as np
    z = np.polyfit(list(x), monthly_orders['order_count'], 1)
    p = np.poly1d(z)
    ax.plot(x, p(list(x)), '--', color='#f9ca24', linewidth=1.5, alpha=0.7, label='Trendline')
    ax.legend(facecolor=bg, edgecolor='#1e3a5f', labelcolor='#e8f4ff', fontsize=9)

ax.set_xticks(list(x))
ax.set_xticklabels(monthly_orders['order_month'], rotation=45, ha='right', fontsize=8)
ax.set_title('Tren Jumlah Transaksi Bulanan 2016–2018', fontsize=13, fontweight='bold', pad=14)
ax.set_xlabel('Periode', fontsize=10)
ax.set_ylabel('Jumlah Transaksi', fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda val, _: f'{int(val):,}'))
ax.grid(axis='y', color='#1e3a5f', linestyle='--', linewidth=0.6, alpha=0.6)
sns.despine(ax=ax)
style_fig(fig)
plt.tight_layout()
st.pyplot(fig)

st.markdown("""<div class='insight-box'>
💡 <b>Insight:</b> Transaksi <b>terus meningkat</b> sepanjang 2016–2017. Setelah itu tren
<b>stabil</b> dengan fluktuasi kecil. Penurunan drastis di akhir 2018 disebabkan data yang
belum lengkap pada periode tersebut.
</div>""", unsafe_allow_html=True)

st.divider()

st.markdown("<div class='section-header'>🏆 Pertanyaan 2 — Top 5 Kategori Produk Terlaris</div>",
            unsafe_allow_html=True)

col_chart, col_table = st.columns([3, 2])

with col_chart:
    palette = [accent] + [mid] * 4
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    bars = ax2.barh(
        top_categories['product_category_name_english'][::-1],
        top_categories['order_item_id'][::-1],
        color=palette[::-1],
        edgecolor='none',
        height=0.6,
    )
    for bar in bars:
        ax2.text(bar.get_width() + 80, bar.get_y() + bar.get_height() / 2,
                 f"{int(bar.get_width()):,}", va='center', color='#a8c8e8', fontsize=8)
    ax2.set_title('Top 5 Kategori — Jumlah Item Terjual', fontsize=12, fontweight='bold', pad=12)
    ax2.set_xlabel('Jumlah Item Terjual', fontsize=9)
    ax2.set_ylabel(None)
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda val, _: f'{int(val):,}'))
    ax2.grid(axis='x', color='#1e3a5f', linestyle='--', linewidth=0.6, alpha=0.6)
    sns.despine(ax=ax2)
    style_fig(fig2)
    plt.tight_layout()
    st.pyplot(fig2)

with col_table:
    st.markdown("#### 📋 Tabel Ringkasan")
    display_df = top_categories.reset_index(drop=True)
    display_df.index += 1
    display_df.columns = ['Kategori', 'Item Terjual']
    display_df['Item Terjual'] = display_df['Item Terjual'].apply(lambda x: f"{x:,}")
    st.dataframe(display_df, use_container_width=True, height=320)

st.markdown("""<div class='insight-box'>
💡 <b>Insight:</b> Kategori <b>bed_bath_table</b> mendominasi penjualan dengan lebih dari
10.000 item. Lima besar juga mencakup <b>health_beauty</b>, <b>sports_leisure</b>,
<b>furniture_decor</b>, dan <b>computers_accessories</b>.
</div>""", unsafe_allow_html=True)

st.divider()

st.markdown("<div class='section-header'>💎 Analisis Lanjutan — RFM (Recency · Frequency · Monetary)</div>",
            unsafe_allow_html=True)

r1, r2, r3 = st.columns(3)
r1.metric("⏱️ Avg Recency (hari)", f"{rfm['recency'].mean():.1f}")
r2.metric("🔁 Avg Frequency",      f"{rfm['frequency'].mean():.2f}")
r3.metric("💵 Avg Monetary",       f"R$ {rfm['monetary'].mean():,.0f}")

tab1, tab2, tab3 = st.tabs(["📊 Top 5 Charts", "🗂️ Tabel RFM", "🔵 Distribusi"])

rfm_palette = [accent, mid, mid, mid, mid]

with tab1:
    fig3, ax3 = plt.subplots(nrows=1, ncols=3, figsize=(22, 6))

    top_recency   = rfm.sort_values('recency',   ascending=True).head(5)
    top_frequency = rfm.sort_values('frequency', ascending=False).head(5)
    top_monetary  = rfm.sort_values('monetary',  ascending=False).head(5)

    for data, col, title, axis in [
        (top_recency,   'recency',   'By Recency (days)', ax3[0]),
        (top_frequency, 'frequency', 'By Frequency',      ax3[1]),
        (top_monetary,  'monetary',  'By Monetary (R$)',  ax3[2]),
    ]:
        sns.barplot(y=col, x='customer_id', data=data, palette=rfm_palette, ax=axis)
        axis.set_title(title, fontsize=14, fontweight='bold', pad=10)
        axis.set_xlabel('Customer ID', fontsize=10)
        axis.set_ylabel(None)
        axis.tick_params(axis='x', rotation=45, labelsize=7)
        axis.yaxis.set_major_formatter(mticker.FuncFormatter(lambda val, _: f'{val:,.0f}'))
        axis.grid(axis='y', color='#1e3a5f', linestyle='--', linewidth=0.5, alpha=0.5)
        sns.despine(ax=axis)

    plt.suptitle('Pelanggan Terbaik Berdasarkan Parameter RFM',
                 fontsize=16, fontweight='bold', color='#e8f4ff', y=1.02)
    style_fig(fig3)
    plt.tight_layout()
    st.pyplot(fig3)

with tab2:
    st.markdown("##### Top 20 Pelanggan Berdasarkan Monetary")
    top20 = (rfm.sort_values('monetary', ascending=False)
             .head(20)
             .reset_index(drop=True))
    top20.index += 1
    top20['recency']  = top20['recency'].apply(lambda x: f"{x} hari")
    top20['monetary'] = top20['monetary'].apply(lambda x: f"R$ {x:,.2f}")
    st.dataframe(top20[['customer_id', 'recency', 'frequency', 'monetary']],
                 use_container_width=True, height=420)

with tab3:
    col_a, col_b = st.columns(2)

    with col_a:
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        ax4.hist(rfm['recency'], bins=30, color=accent, edgecolor=bg, alpha=0.85)
        ax4.set_title('Distribusi Recency', fontsize=11, fontweight='bold')
        ax4.set_xlabel('Hari sejak transaksi terakhir', fontsize=9)
        ax4.set_ylabel('Jumlah Pelanggan', fontsize=9)
        ax4.grid(axis='y', color='#1e3a5f', linestyle='--', linewidth=0.5, alpha=0.5)
        sns.despine(ax=ax4)
        style_fig(fig4)
        plt.tight_layout()
        st.pyplot(fig4)

    with col_b:
        fig5, ax5 = plt.subplots(figsize=(6, 4))
        ax5.hist(rfm['monetary'].clip(upper=rfm['monetary'].quantile(0.95)),
                 bins=30, color=mid, edgecolor=bg, alpha=0.85)
        ax5.set_title('Distribusi Monetary (95th pct)', fontsize=11, fontweight='bold')
        ax5.set_xlabel('Total Pengeluaran (R$)', fontsize=9)
        ax5.set_ylabel('Jumlah Pelanggan', fontsize=9)
        ax5.xaxis.set_major_formatter(mticker.FuncFormatter(lambda val, _: f'R${val:,.0f}'))
        ax5.grid(axis='y', color='#1e3a5f', linestyle='--', linewidth=0.5, alpha=0.5)
        sns.despine(ax=ax5)
        style_fig(fig5)
        plt.tight_layout()
        st.pyplot(fig5)

st.markdown("""<div class='insight-box'>
💡 <b>Insight:</b> Dari analisis RFM terdapat <b>5 pelanggan terroyal</b>. Satu pelanggan memiliki
nilai <b>monetary jauh lebih tinggi</b> dibanding yang lain. Pelanggan dengan recency rendah &
frequency tinggi adalah kandidat utama program loyalitas.
</div>""", unsafe_allow_html=True)

st.divider()
st.caption("© Raymond Emmanuel Krista · Dashboard · Dicoding 2026")