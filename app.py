"""
Dashboard Streamlit — Insight 2 Olist
Tech Challenge POSTECH DTAT Fase 1
Sellers com melhor SLA geram mais receita?
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Insight 2 · Olist — SLA & Receita",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── PALETA ────────────────────────────────────────────────────────────────────
NAVY   = "#1A3C5E"
BLUE   = "#2E86AB"
PURP   = "#A23B72"
ORANGE = "#F18F01"
RED    = "#C73E1D"
GREEN  = "#27AE60"
TEAL   = "#44BBA4"
GRAY   = "#95A5A6"
LTBLUE = "#D6EAF8"

# ─── CSS GLOBAL ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Fonte e background */
  html, body, [data-testid="stApp"] { font-family: 'Segoe UI', sans-serif; }

  /* Cards KPI */
  .kpi-card {
    background: linear-gradient(135deg, #1A3C5E 0%, #2E86AB 100%);
    border-radius: 12px; padding: 18px 22px; color: white;
    text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,.15);
  }
  .kpi-value { font-size: 2rem; font-weight: 700; margin: 0; }
  .kpi-label { font-size: 0.8rem; opacity: .85; margin-top: 4px; text-transform: uppercase; letter-spacing: .05em; }

  /* Cards de impacto */
  .impact-card {
    border-left: 5px solid #2E86AB;
    background: #f0f6fc; border-radius: 8px;
    padding: 16px 20px; margin-bottom: 12px;
  }
  .impact-card.orange { border-left-color: #F18F01; background: #fff8ee; }
  .impact-card.purple { border-left-color: #A23B72; background: #fdf0f6; }
  .impact-card.green  { border-left-color: #27AE60; background: #eafaf1; }
  .impact-card.red    { border-left-color: #C73E1D; background: #fdf1ef; }
  .impact-text { font-size: 1.05rem; color: #1A3C5E; font-weight: 600; margin: 0; }

  /* Seções */
  .section-header {
    font-size: 1.15rem; font-weight: 700; color: #1A3C5E;
    border-bottom: 2px solid #D6EAF8; padding-bottom: 6px; margin: 20px 0 12px 0;
  }
  /* Insight box */
  .insight-box {
    background: #eaf4fb; border-radius: 10px;
    padding: 14px 18px; margin-bottom: 10px; border: 1px solid #aed6f1;
  }
  .rec-box {
    background: linear-gradient(135deg,#1A3C5E,#2E86AB);
    color: white; border-radius: 12px; padding: 22px 28px; margin: 20px 0;
  }
  .warn-box {
    background: #fffbea; border-left: 4px solid #F18F01;
    border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;
  }
</style>
""", unsafe_allow_html=True)


# ─── CARREGAMENTO DE DADOS ─────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    path = "analise_insight2_olist.xlsx"
    xl = pd.ExcelFile(path)

    sellers = xl.parse("Dataset Seller", header=1)
    sellers.columns = ["seller_id","estado","receita","qtd_pedidos","sla_mediana",
                       "sla_media","sla_std","pct_no_prazo","handling_mediano","review_medio"]
    sellers = sellers.dropna(subset=["seller_id","receita","sla_mediana"])
    sellers["receita"] = pd.to_numeric(sellers["receita"], errors="coerce")
    sellers["sla_mediana"] = pd.to_numeric(sellers["sla_mediana"], errors="coerce")
    sellers["pct_no_prazo"] = pd.to_numeric(sellers["pct_no_prazo"], errors="coerce")
    sellers["handling_mediano"] = pd.to_numeric(sellers["handling_mediano"], errors="coerce")
    sellers["review_medio"] = pd.to_numeric(sellers["review_medio"], errors="coerce")
    sellers["qtd_pedidos"] = pd.to_numeric(sellers["qtd_pedidos"], errors="coerce").fillna(0).astype(int)
    sellers["receita_por_pedido"] = sellers["receita"] / sellers["qtd_pedidos"].replace(0, np.nan)

    faixas = xl.parse("Faixas SLA", header=1)
    faixas.columns = ["faixa","n_sellers","receita_total","receita_media","receita_mediana","sla_medio","pct_receita"]
    faixas = faixas.dropna(subset=["faixa"])
    faixas["pct_receita"] = pd.to_numeric(faixas["pct_receita"], errors="coerce") * 100

    estados = xl.parse("Analise por Estado", header=1)
    estados.columns = ["estado","n_sellers","sla_mediano","receita_media"]
    estados = estados.dropna(subset=["estado"])
    estados["sla_mediano"] = pd.to_numeric(estados["sla_mediano"], errors="coerce")
    estados["receita_media"] = pd.to_numeric(estados["receita_media"], errors="coerce")

    top20 = xl.parse("Top 20 Sellers", header=1)
    top20.columns = ["rank","seller_id","estado","receita","pedidos","sla_mediana","pct_no_prazo","review_medio"]
    top20 = top20.dropna(subset=["seller_id"])
    top20["receita"] = pd.to_numeric(top20["receita"], errors="coerce")
    top20["pct_no_prazo"] = pd.to_numeric(top20["pct_no_prazo"], errors="coerce")

    pareto = xl.parse("Pareto", header=1)
    pareto.columns = ["seller_id","sla_mediana","receita","pct_sellers_cum","pct_receita_cum"]
    pareto = pareto.dropna(subset=["seller_id"])
    pareto["pct_sellers_cum"] = pd.to_numeric(pareto["pct_sellers_cum"], errors="coerce")
    pareto["pct_receita_cum"] = pd.to_numeric(pareto["pct_receita_cum"], errors="coerce")

    return sellers, faixas, estados, top20, pareto

with st.spinner("Carregando dados do Olist..."):
    df_sellers, df_faixas, df_estados, df_top20, df_pareto = load_data()


# ─── MÉTRICAS GLOBAIS ──────────────────────────────────────────────────────────
receita_total   = df_sellers["receita"].sum()
n_sellers       = len(df_sellers)
n_pedidos       = df_sellers["qtd_pedidos"].sum()
sla_global      = df_sellers["sla_mediana"].median()
sla10           = df_sellers[df_sellers["sla_mediana"] < 10]
pct_sell_sla10  = len(sla10) / n_sellers * 100
pct_rec_sla10   = sla10["receita"].sum() / receita_total * 100
sla_fast_mean   = df_sellers[df_sellers["sla_mediana"] < 10]["receita"].mean()
sla_slow_mean   = df_sellers[df_sellers["sla_mediana"] > 21]["receita"].mean()
mult            = sla_fast_mean / sla_slow_mean if sla_slow_mean else 0

# Spearman sem scipy
def spearman_r(x, y):
    s = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(s) < 3:
        return 0.0
    rx = s["x"].rank(); ry = s["y"].rank()
    return float(np.corrcoef(rx, ry)[0, 1])

spearman_sla_rec = spearman_r(df_sellers["sla_mediana"], df_sellers["receita"])

ontime_high = df_sellers[df_sellers["pct_no_prazo"] > 0.9]["receita"].mean()
ontime_low  = df_sellers[df_sellers["pct_no_prazo"] < 0.7]["receita"].mean()
pct_diff_prazo = (ontime_high - ontime_low) / ontime_low * 100 if ontime_low else 0

pct_sp_top20 = (df_top20["estado"] == "SP").sum() / len(df_top20) * 100


# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/package--v1.png", width=60)
    st.title("📦 Filtros")
    st.caption("Insight 2 · Olist · POSTECH DTAT")
    st.divider()

    all_states = sorted(df_sellers["estado"].dropna().unique().tolist())
    sel_states = st.multiselect(
        "🗺️ Estado do Seller",
        options=all_states,
        default=all_states,
        help="Filtra sellers pelo estado de origem"
    )

    sla_range = st.slider(
        "⏱️ Faixa de SLA (dias)",
        min_value=0.0, max_value=60.0,
        value=(0.0, 60.0), step=0.5,
        help="SLA mediano do seller em dias"
    )

    min_pedidos = st.slider(
        "📦 Volume mínimo de pedidos",
        min_value=1, max_value=200,
        value=10,
        help="Sellers com menos pedidos que este valor são excluídos"
    )

    pct_max_receita = st.slider(
        "💰 Percentil máximo de receita",
        min_value=50, max_value=100,
        value=100,
        help="Remove outliers de receita acima deste percentil"
    )

    st.divider()
    st.caption(f"Dataset: 96.164 pedidos · 2016–2018")
    st.caption("POSTECH DTAT Fase 1 — Tech Challenge")


# ─── FILTRO APLICADO ───────────────────────────────────────────────────────────
cap_receita = df_sellers["receita"].quantile(pct_max_receita / 100)

df_f = df_sellers[
    (df_sellers["estado"].isin(sel_states)) &
    (df_sellers["sla_mediana"] >= sla_range[0]) &
    (df_sellers["sla_mediana"] <= sla_range[1]) &
    (df_sellers["qtd_pedidos"] >= min_pedidos) &
    (df_sellers["receita"] <= cap_receita)
].copy()

n_filtrado = len(df_f)
rec_filtrada = df_f["receita"].sum()


# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,{NAVY},{BLUE});
     border-radius:14px;padding:28px 32px;margin-bottom:20px;">
  <h1 style="color:white;margin:0;font-size:1.8rem;">
    📦 Insight 2 · Olist &nbsp;|&nbsp; SLA &amp; Receita
  </h1>
  <p style="color:#AED6F1;margin:6px 0 0 0;font-size:1rem;">
    Sellers que entregam mais rápido faturam mais? &nbsp;·&nbsp;
    <b style="color:white;">{n_filtrado:,}</b> sellers filtrados de {n_sellers:,}
  </p>
</div>
""", unsafe_allow_html=True)


# ─── ABAS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Resumo Executivo",
    "🏆 Rankings",
    "⏱️ Análise de SLA",
    "🗺️ Geografia & Confiabilidade",
    "💡 Insights & Recomendações",
])


# ══════════════════════════════════════════════════════════════════════════════
# ABA 1 — RESUMO EXECUTIVO
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        (c1, f"{n_filtrado:,}",            "Sellers Analisados"),
        (c2, f"{n_pedidos:,}",             "Pedidos Entregues"),
        (c3, f"R$ {rec_filtrada/1e6:.2f}M","Receita Total"),
        (c4, f"{sla_global:.1f}d",         "SLA Mediano Geral"),
        (c5, f"{spearman_sla_rec:.3f}",    "Spearman r (SLA×Rec.)"),
    ]
    for col, val, lbl in kpis:
        col.markdown(f"""
        <div class="kpi-card">
          <p class="kpi-value">{val}</p>
          <p class="kpi-label">{lbl}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-header">🎯 Frases de Impacto</p>', unsafe_allow_html=True)

    impactos = [
        ("blue",
         f"Os sellers com SLA mediano &lt; 10 dias representam apenas "
         f"<b>{pct_sell_sla10:.1f}%</b> dos sellers ativos, "
         f"mas concentram <b>{pct_rec_sla10:.1f}%</b> da receita total."),
        ("orange",
         f"Sellers com SLA &lt; 10 dias faturam em média <b>{mult:.1f}× mais</b> "
         f"do que sellers com SLA &gt; 21 dias."),
        ("purple",
         f"Sellers que cumprem o prazo prometido em &gt;90% dos pedidos têm receita "
         f"média <b>{pct_diff_prazo:.0f}% superior</b> aos que cumprem em &lt;70%."),
        ("green",
         f"A correlação de Spearman entre SLA e receita é <b>{spearman_sla_rec:.4f}</b> "
         f"— relação {'moderada' if abs(spearman_sla_rec) > 0.15 else 'fraca'} e "
         f"{'negativa' if spearman_sla_rec < 0 else 'positiva'}: "
         f"sellers mais rápidos tendem a faturar mais."),
        ("red",
         f"<b>{pct_sp_top20:.0f}%</b> dos Top 20 sellers por receita estão em SP — "
         f"a geografia explica parte do SLA e deve ser controlada em programas de incentivo."),
    ]
    for color, txt in impactos:
        st.markdown(
            f'<div class="impact-card {color}"><p class="impact-text">{txt}</p></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-header">📈 Distribuição Geral de Receita por SLA</p>',
                unsafe_allow_html=True)

    fig_overview = px.scatter(
        df_f, x="sla_mediana", y="receita",
        color="estado", size="qtd_pedidos",
        size_max=28, opacity=0.65,
        log_y=True,
        hover_data={"seller_id": False, "receita": ":,.0f",
                    "sla_mediana": ":.1f", "qtd_pedidos": True, "estado": True},
        labels={"sla_mediana": "SLA Mediano (dias)",
                "receita": "Receita Total (R$)", "estado": "Estado"},
        title=f"Dispersão: SLA × Receita  |  Spearman r = {spearman_sla_rec:.3f}",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_overview.add_vline(x=10, line_dash="dash", line_color=RED,
                           annotation_text="SLA = 10d", annotation_position="top right")
    fig_overview.update_layout(height=480, plot_bgcolor="white", paper_bgcolor="white",
                               legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_overview, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ABA 2 — RANKINGS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    # Sub A — Top 20 por receita
    st.markdown('<p class="section-header">🥇 Top 20 Sellers por Receita</p>',
                unsafe_allow_html=True)

    top20_r = df_f.nlargest(20, "receita").copy()
    top20_r["seller_short"] = top20_r["seller_id"].str[:12] + "…"
    top20_r["sla_color"] = top20_r["sla_mediana"].apply(
        lambda x: GREEN if x <= 10 else (ORANGE if x <= 14 else RED))

    fig_r = px.bar(
        top20_r.sort_values("receita"),
        x="receita", y="seller_short",
        orientation="h",
        color="sla_mediana",
        color_continuous_scale=[[0, GREEN], [0.35, ORANGE], [1, RED]],
        text=top20_r.sort_values("receita")["sla_mediana"].apply(lambda x: f"SLA {x:.1f}d"),
        labels={"receita": "Receita (R$)", "seller_short": "",
                "sla_mediana": "SLA Mediano (d)"},
        title="Top 20 por Receita — cor indica SLA (verde=rápido, vermelho=lento)",
        hover_data={"estado": True, "qtd_pedidos": True, "pct_no_prazo": ":.0%"},
    )
    fig_r.update_traces(textposition="outside", textfont_size=9)
    fig_r.update_layout(height=560, plot_bgcolor="white", paper_bgcolor="white",
                        coloraxis_colorbar=dict(title="SLA (d)"))
    st.plotly_chart(fig_r, use_container_width=True)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.caption("📋 Tabela completa — Top 20 por Receita")
        disp_r = top20_r[["seller_id","estado","receita","qtd_pedidos",
                           "sla_mediana","pct_no_prazo","review_medio"]].copy()
        disp_r.columns = ["Seller ID","Estado","Receita (R$)","Pedidos",
                          "SLA Med. (d)","% No Prazo","Review"]
        st.dataframe(
            disp_r.style
              .format({"Receita (R$)": "R$ {:,.0f}", "SLA Med. (d)": "{:.1f}",
                       "% No Prazo": "{:.0%}", "Review": "{:.2f}"})
              .background_gradient(subset=["Receita (R$)"], cmap="Blues")
              .background_gradient(subset=["SLA Med. (d)"], cmap="RdYlGn_r"),
            height=420, use_container_width=True
        )

    # Sub B — Top 20 por volume
    st.markdown('<p class="section-header">📦 Top 20 Sellers por Volume de Pedidos</p>',
                unsafe_allow_html=True)

    top20_v = df_f.nlargest(20, "qtd_pedidos").copy()
    top20_v["seller_short"] = top20_v["seller_id"].str[:12] + "…"

    fig_v = px.bar(
        top20_v.sort_values("qtd_pedidos"),
        x="qtd_pedidos", y="seller_short",
        orientation="h",
        color="receita_por_pedido",
        color_continuous_scale=[[0, LTBLUE], [0.5, BLUE], [1, NAVY]],
        text=top20_v.sort_values("qtd_pedidos")["receita_por_pedido"].apply(
            lambda x: f"R$ {x:,.0f}/ped"),
        labels={"qtd_pedidos": "Nº de Pedidos", "seller_short": "",
                "receita_por_pedido": "R$/Pedido"},
        title="Top 20 por Volume — cor indica receita por pedido",
        hover_data={"estado": True, "receita": ":,.0f", "sla_mediana": ":.1f"},
    )
    fig_v.update_traces(textposition="outside", textfont_size=9)
    fig_v.update_layout(height=560, plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_v, use_container_width=True)

    # Sub C — Comparação
    st.markdown('<p class="section-header">🔀 Comparação: Quem aparece nos dois tops?</p>',
                unsafe_allow_html=True)

    ids_r = set(top20_r["seller_id"].values)
    ids_v = set(top20_v["seller_id"].values)
    ambos = ids_r & ids_v

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Só no Top Receita",   len(ids_r - ids_v))
    col_b.metric("Em AMBOS os tops",     len(ambos), delta="mais eficientes")
    col_c.metric("Só no Top Volume",    len(ids_v - ids_r))

    if ambos:
        df_ambos = df_f[df_f["seller_id"].isin(ambos)][
            ["seller_id","estado","receita","qtd_pedidos","sla_mediana","receita_por_pedido"]
        ].sort_values("receita", ascending=False)
        df_ambos.columns = ["Seller ID","Estado","Receita","Pedidos","SLA Med.(d)","R$/Pedido"]
        st.caption(f"✅ {len(ambos)} sellers que aparecem no top 20 de receita E volume:")
        st.dataframe(
            df_ambos.style.format({"Receita": "R$ {:,.0f}", "SLA Med.(d)": "{:.1f}",
                                   "R$/Pedido": "R$ {:,.0f}"}),
            height=280, use_container_width=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# ABA 3 — ANÁLISE DE SLA
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    # Scatter SLA × Receita
    st.markdown('<p class="section-header">🔵 Scatter: SLA Mediano × Receita</p>',
                unsafe_allow_html=True)

    df_sc = df_f.copy()

    fig_sc = px.scatter(
        df_sc,
        x="sla_mediana", y="receita",
        color="estado",
        size="qtd_pedidos",
        size_max=35, opacity=0.6,
        log_y=True,
        hover_data={"seller_id": False, "receita": ":,.0f",
                    "sla_mediana": ":.1f", "qtd_pedidos": True,
                    "pct_no_prazo": ":.0%", "review_medio": ":.2f"},
        labels={"sla_mediana": "SLA Mediano (dias)",
                "receita": "Receita Total — escala log (R$)", "estado": "Estado"},
        title=f"SLA Mediano × Receita por Seller  |  Spearman r = {spearman_sla_rec:.4f}",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    # Linha de tendência polinomial via numpy (sem statsmodels)
    _sc_valid = df_sc.dropna(subset=["sla_mediana", "receita"])
    if len(_sc_valid) > 5:
        _x = _sc_valid["sla_mediana"].values
        _y = np.log10(_sc_valid["receita"].values)
        _coef = np.polyfit(_x, _y, deg=2)
        _x_line = np.linspace(_x.min(), _x.max(), 200)
        _y_line = 10 ** np.polyval(_coef, _x_line)
        fig_sc.add_trace(go.Scatter(
            x=_x_line, y=_y_line, mode="lines",
            line=dict(color=RED, width=2.5, dash="dash"),
            name="Tendência (polinomial)", showlegend=True,
        ))
    fig_sc.add_vline(x=10, line_dash="dot", line_color=ORANGE, line_width=1.5,
                     annotation_text="SLA = 10d", annotation_position="top right")
    fig_sc.add_vline(x=21, line_dash="dot", line_color=RED, line_width=1.5,
                     annotation_text="SLA = 21d", annotation_position="top right")
    fig_sc.update_layout(height=580, plot_bgcolor="white", paper_bgcolor="white",
                         legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_sc, use_container_width=True)

    # Barras por faixa SLA
    st.markdown('<p class="section-header">📊 Receita por Faixa de SLA</p>',
                unsafe_allow_html=True)

    # Recalcular faixas com dados filtrados
    df_faixas_live = df_f.copy()
    bins   = [0, 7, 14, 21, 61]
    labels = ["0–7d", "8–14d", "15–21d", "21+d"]
    df_faixas_live["faixa"] = pd.cut(df_faixas_live["sla_mediana"],
                                      bins=bins, labels=labels, right=True)
    faixa_agg = df_faixas_live.groupby("faixa", observed=True).agg(
        n_sellers=("seller_id", "count"),
        receita_total=("receita", "sum"),
        receita_media=("receita", "mean"),
        receita_mediana=("receita", "median"),
    ).reset_index()
    faixa_agg["pct_receita"] = faixa_agg["receita_total"] / faixa_agg["receita_total"].sum() * 100

    col_f1, col_f2 = st.columns([3, 2])

    with col_f1:
        fig_faixas = go.Figure()
        fig_faixas.add_trace(go.Bar(
            name="Receita Média", x=faixa_agg["faixa"].astype(str),
            y=faixa_agg["receita_media"],
            marker_color=BLUE, text=faixa_agg["receita_media"].apply(lambda x: f"R$ {x:,.0f}"),
            textposition="outside",
        ))
        fig_faixas.add_trace(go.Bar(
            name="Receita Mediana", x=faixa_agg["faixa"].astype(str),
            y=faixa_agg["receita_mediana"],
            marker_color=TEAL, text=faixa_agg["receita_mediana"].apply(lambda x: f"R$ {x:,.0f}"),
            textposition="outside",
        ))
        fig_faixas.update_layout(
            barmode="group", height=420,
            title="Receita Média vs Mediana por Faixa de SLA",
            yaxis_title="Receita (R$)", xaxis_title="Faixa SLA",
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_faixas, use_container_width=True)

    with col_f2:
        st.caption("📋 Detalhamento por faixa")
        st.dataframe(
            faixa_agg.rename(columns={
                "faixa": "Faixa SLA", "n_sellers": "Sellers",
                "receita_total": "Rec. Total", "receita_media": "Rec. Média",
                "receita_mediana": "Rec. Mediana", "pct_receita": "% Receita",
            }).style.format({
                "Rec. Total": "R$ {:,.0f}", "Rec. Média": "R$ {:,.0f}",
                "Rec. Mediana": "R$ {:,.0f}", "% Receita": "{:.1f}%",
            }).background_gradient(subset=["Rec. Média"], cmap="Blues"),
            height=280, use_container_width=True,
        )
        # Pie chart
        fig_pie = px.pie(
            faixa_agg, names="faixa", values="receita_total",
            title="% da Receita Total por Faixa",
            color_discrete_sequence=[GREEN, BLUE, ORANGE, RED],
            hole=0.4,
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(height=280, showlegend=False,
                              paper_bgcolor="white", margin=dict(t=40,b=0,l=0,r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Curva de Pareto
    st.markdown('<p class="section-header">📉 Curva de Pareto: Concentração de Receita</p>',
                unsafe_allow_html=True)

    # Recalcular pareto com dados filtrados
    df_par = df_f.sort_values("sla_mediana").reset_index(drop=True)
    df_par["pct_sellers_cum"] = (df_par.index + 1) / len(df_par) * 100
    df_par["pct_receita_cum"] = df_par["receita"].cumsum() / df_par["receita"].sum() * 100
    sla10_par = df_par[df_par["sla_mediana"] < 10]
    pct_s10 = len(sla10_par) / len(df_par) * 100
    pct_r10 = sla10_par["receita"].sum() / df_par["receita"].sum() * 100

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Scatter(
        x=df_par["pct_sellers_cum"], y=df_par["pct_receita_cum"],
        mode="lines", name="Receita acumulada",
        line=dict(color=BLUE, width=2.5),
        fill="tozeroy", fillcolor="rgba(46,134,171,0.12)",
    ))
    fig_pareto.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100], mode="lines",
        name="Igualdade perfeita",
        line=dict(color=GRAY, width=1, dash="dash"),
    ))
    fig_pareto.add_vline(x=pct_s10, line_dash="dot", line_color=ORANGE, line_width=2,
                         annotation_text=f"{pct_s10:.1f}% sellers (SLA<10d)",
                         annotation_position="top right")
    fig_pareto.add_hline(y=pct_r10, line_dash="dot", line_color=RED, line_width=2,
                         annotation_text=f"{pct_r10:.1f}% da receita",
                         annotation_position="bottom right")
    fig_pareto.add_vrect(x0=0, x1=pct_s10, fillcolor="rgba(39,174,96,0.07)", line_width=0,
                         annotation_text="Sellers SLA<10d", annotation_position="top left")
    fig_pareto.update_layout(
        title=f"Curva de Pareto · {pct_s10:.1f}% dos sellers (SLA<10d) "
              f"concentram {pct_r10:.1f}% da receita",
        xaxis_title="% Acumulado de Sellers (ordenados por SLA crescente)",
        yaxis_title="% Acumulado de Receita",
        height=500, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(range=[0, 100]), yaxis=dict(range=[0, 100]),
        legend=dict(x=0.02, y=0.95),
    )
    st.plotly_chart(fig_pareto, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ABA 4 — GEOGRAFIA & CONFIABILIDADE
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    # A. SLA por estado
    st.markdown('<p class="section-header">🗺️ SLA Mediano por Estado</p>',
                unsafe_allow_html=True)

    # Recalcular por estado com filtro
    est_live = df_f.groupby("estado").agg(
        n_sellers=("seller_id", "count"),
        sla_mediano=("sla_mediana", "median"),
        receita_media=("receita", "mean"),
        receita_total=("receita", "sum"),
    ).reset_index().sort_values("sla_mediano")

    destaques = {"SP": GREEN, "RJ": BLUE, "MG": TEAL}
    est_live["cor"] = est_live["estado"].apply(
        lambda x: destaques.get(x, ORANGE))

    col_e1, col_e2 = st.columns([3, 2])

    with col_e1:
        fig_est = go.Figure()
        fig_est.add_trace(go.Bar(
            x=est_live["sla_mediano"],
            y=est_live["estado"],
            orientation="h",
            marker_color=est_live["cor"],
            text=est_live["sla_mediano"].apply(lambda x: f"{x:.1f}d"),
            textposition="outside",
            customdata=np.stack([est_live["n_sellers"], est_live["receita_media"]], axis=-1),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "SLA Mediano: %{x:.1f} dias<br>"
                "N Sellers: %{customdata[0]}<br>"
                "Receita Média: R$ %{customdata[1]:,.0f}<extra></extra>"
            ),
        ))
        fig_est.update_layout(
            title="SLA Mediano por Estado — verde=SP, azul=RJ, teal=MG",
            xaxis_title="SLA Mediano (dias)", yaxis_title="",
            height=520, plot_bgcolor="white", paper_bgcolor="white",
        )
        st.plotly_chart(fig_est, use_container_width=True)

    with col_e2:
        fig_rec_est = px.bar(
            est_live.sort_values("receita_media", ascending=False).head(15),
            x="receita_media", y="estado",
            orientation="h",
            color="sla_mediano",
            color_continuous_scale=[[0, GREEN], [0.5, ORANGE], [1, RED]],
            title="Receita Média por Estado",
            labels={"receita_media": "Receita Média (R$)", "estado": "",
                    "sla_mediano": "SLA (d)"},
            text=est_live.sort_values("receita_media", ascending=False).head(15)[
                "receita_media"].apply(lambda x: f"R${x/1000:.0f}k"),
        )
        fig_rec_est.update_traces(textposition="outside", textfont_size=9)
        fig_rec_est.update_layout(height=400, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_rec_est, use_container_width=True)

        st.dataframe(
            est_live[["estado","n_sellers","sla_mediano","receita_media"]].rename(
                columns={"estado":"Estado","n_sellers":"Sellers",
                         "sla_mediano":"SLA Med.(d)","receita_media":"Rec. Média"}
            ).style.format({"SLA Med.(d)":"{:.1f}","Rec. Média":"R$ {:,.0f}"}),
            height=250, use_container_width=True
        )

    # B. Confiabilidade (% no prazo)
    st.markdown('<p class="section-header">✅ SLA Prometido vs Realizado (Confiabilidade)</p>',
                unsafe_allow_html=True)

    df_prazo = df_f.dropna(subset=["pct_no_prazo"]).copy()
    df_prazo["grupo_prazo"] = pd.cut(
        df_prazo["pct_no_prazo"],
        bins=[0, 0.70, 0.90, 1.0],
        labels=["< 70% (inconsistente)", "70–90% (regular)", "> 90% (confiável)"],
        right=True,
    )

    col_p1, col_p2 = st.columns([2, 3])

    with col_p1:
        grupo_rec = df_prazo.groupby("grupo_prazo", observed=True).agg(
            n_sellers=("seller_id","count"),
            receita_media=("receita","mean"),
            receita_total=("receita","sum"),
        ).reset_index()

        fig_grupos = px.bar(
            grupo_rec, x="grupo_prazo", y="receita_media",
            color="grupo_prazo",
            color_discrete_map={
                "< 70% (inconsistente)": RED,
                "70–90% (regular)": ORANGE,
                "> 90% (confiável)": GREEN,
            },
            text=grupo_rec["receita_media"].apply(lambda x: f"R$ {x:,.0f}"),
            labels={"grupo_prazo": "Grupo de Pontualidade", "receita_media": "Receita Média (R$)"},
            title="Receita Média por Grupo de Pontualidade",
        )
        fig_grupos.update_traces(textposition="outside")
        fig_grupos.update_layout(height=380, showlegend=False,
                                 plot_bgcolor="white", paper_bgcolor="white",
                                 xaxis_tickangle=-15)
        st.plotly_chart(fig_grupos, use_container_width=True)

        for _, row in grupo_rec.iterrows():
            st.metric(str(row["grupo_prazo"]),
                      f"R$ {row['receita_media']:,.0f}",
                      f"n={int(row['n_sellers'])} sellers")

    with col_p2:
        # Scatter pontualidade × receita
        fig_punt = px.scatter(
            df_prazo, x="pct_no_prazo", y="receita",
            color="grupo_prazo",
            size="qtd_pedidos", size_max=25, opacity=0.65,
            log_y=True,
            color_discrete_map={
                "< 70% (inconsistente)": RED,
                "70–90% (regular)": ORANGE,
                "> 90% (confiável)": GREEN,
            },
            hover_data={"seller_id": False, "estado": True,
                        "sla_mediana": ":.1f", "receita": ":,.0f"},
            labels={"pct_no_prazo": "% de Pedidos no Prazo",
                    "receita": "Receita — escala log (R$)",
                    "grupo_prazo": "Grupo"},
            title="Pontualidade × Receita por Seller",
        )
        fig_punt.update_xaxes(tickformat=".0%")
        fig_punt.add_vline(x=0.9, line_dash="dash", line_color=GREEN,
                           annotation_text=">90% no prazo")
        fig_punt.add_vline(x=0.7, line_dash="dash", line_color=RED,
                           annotation_text="<70%")
        fig_punt.update_layout(height=480, plot_bgcolor="white", paper_bgcolor="white",
                               legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_punt, use_container_width=True)

    # Top 10 mais confiáveis
    st.markdown('<p class="section-header">🏅 Top 10 Sellers Mais Confiáveis (&gt;90% no prazo)</p>',
                unsafe_allow_html=True)

    top_conf = df_prazo[df_prazo["pct_no_prazo"] > 0.9].nlargest(10, "receita")[
        ["seller_id","estado","receita","qtd_pedidos","sla_mediana","pct_no_prazo","review_medio"]
    ]
    top_conf.columns = ["Seller ID","Estado","Receita","Pedidos","SLA Med.(d)","% No Prazo","Review"]
    st.dataframe(
        top_conf.style.format({
            "Receita": "R$ {:,.0f}", "SLA Med.(d)": "{:.1f}",
            "% No Prazo": "{:.0%}", "Review": "{:.2f}",
        }).background_gradient(subset=["Receita"], cmap="Greens"),
        height=300, use_container_width=True,
    )

    # C. Handling Time
    st.markdown('<p class="section-header">🔧 Handling Time vs Receita</p>',
                unsafe_allow_html=True)

    df_ht = df_f.dropna(subset=["handling_mediano"]).copy()
    df_ht = df_ht[(df_ht["handling_mediano"] >= 0) & (df_ht["handling_mediano"] <= 20)]
    spearman_h = spearman_r(df_ht["handling_mediano"], df_ht["receita"])

    col_h1, col_h2 = st.columns([3, 2])

    with col_h1:
        fig_ht = px.scatter(
            df_ht, x="handling_mediano", y="receita",
            color="sla_mediana",
            color_continuous_scale=[[0, GREEN], [0.5, ORANGE], [1, RED]],
            size="qtd_pedidos", size_max=25, opacity=0.6,
            log_y=True,
            hover_data={"seller_id": False, "estado": True,
                        "sla_mediana": ":.1f", "receita": ":,.0f"},
            labels={"handling_mediano": "Handling Mediano (dias)",
                    "receita": "Receita — escala log (R$)",
                    "sla_mediano": "SLA (d)"},
            title=f"Handling Time × Receita  |  Spearman r = {spearman_h:.4f}",
        )
        # Tendência polinomial via numpy
        if len(df_ht) > 5:
            _hx = df_ht["handling_mediano"].values
            _hy = np.log10(df_ht["receita"].values)
            _hcoef = np.polyfit(_hx, _hy, deg=2)
            _hx_line = np.linspace(_hx.min(), _hx.max(), 200)
            _hy_line = 10 ** np.polyval(_hcoef, _hx_line)
            fig_ht.add_trace(go.Scatter(
                x=_hx_line, y=_hy_line, mode="lines",
                line=dict(color=RED, width=2.5, dash="dash"),
                name="Tendência", showlegend=False,
            ))
        fig_ht.update_layout(height=440, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_ht, use_container_width=True)

    with col_h2:
        st.markdown(f"""
        <div class="insight-box">
          <b>🔧 O que é Handling Time?</b><br><br>
          É o tempo entre a <b>aprovação do pedido</b> e a
          <b>entrega ao transportador</b> — componente diretamente
          controlado pelo seller.<br><br>
          <b>Handling</b> = <code>carrier_date − approved_at</code><br>
          <b>Transporte</b> = <code>delivered_date − carrier_date</code><br><br>
          Spearman r = <b>{spearman_h:.4f}</b><br>
          Um handling menor indica que o seller é mais eficiente na
          preparação e expedição do pedido.
        </div>
        """, unsafe_allow_html=True)

        # Distribuição handling
        fig_dist_h = px.histogram(
            df_ht, x="handling_mediano", nbins=30,
            color_discrete_sequence=[BLUE],
            title="Distribuição do Handling Mediano",
            labels={"handling_mediano": "Handling Mediano (dias)"},
        )
        fig_dist_h.update_layout(height=260, plot_bgcolor="white", paper_bgcolor="white",
                                 showlegend=False)
        st.plotly_chart(fig_dist_h, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ABA 5 — INSIGHTS & RECOMENDAÇÕES
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-header">🔍 Descobertas Principais</p>',
                unsafe_allow_html=True)

    descobertas = [
        ("A · Faixas de SLA", BLUE,
         f"A maioria dos sellers qualificados se concentra na faixa 8–14 dias. "
         f"A faixa 0–7d tem apenas {int(df_faixas['n_sellers'].iloc[0])} sellers "
         f"mas com receita mediana de R$ {df_faixas['receita_mediana'].iloc[0]:,.0f} — "
         f"mostrando que velocidade extrema é rara e tem retorno."),
        ("B · Concentração de Receita", GREEN,
         f"{pct_sell_sla10:.1f}% dos sellers ativos (SLA<10d) concentram "
         f"{pct_rec_sla10:.1f}% da receita total. "
         f"Efeito Pareto: poucos sellers rápidos dominam a receita."),
        ("C · Geografia", ORANGE,
         f"{pct_sp_top20:.0f}% do Top 20 em receita é de SP. "
         f"Sellers de SP, RJ e MG têm SLA naturalmente menor pela proximidade "
         f"dos centros de consumo — a localização é um confundidor importante."),
        ("D · Confiabilidade", TEAL,
         f"Sellers com >90% de pedidos no prazo têm receita média {pct_diff_prazo:.0f}% superior "
         f"aos com <70%. Consistência supera velocidade absoluta."),
        ("E · Handling Time", PURP,
         f"Spearman r = {spearman_r(df_f.dropna(subset=['handling_mediano'])['handling_mediano'], df_f.dropna(subset=['handling_mediano'])['receita']):.4f} "
         f"entre handling e receita. O componente que o seller controla (handling) "
         f"também se correlaciona com maior faturamento."),
        ("F · Review Score", RED,
         f"Pearson r ≈ −0.40 entre SLA e review — sellers com menor SLA têm "
         f"melhores avaliações. Ciclo virtuoso: SLA bom → reviews melhores → mais vendas."),
    ]

    colors_map = {BLUE: "blue", GREEN: "green", ORANGE: "orange",
                  TEAL: "blue", PURP: "purple", RED: "red"}

    for titulo, cor, texto in descobertas:
        cls = colors_map.get(cor, "blue")
        st.markdown(f"""
        <div class="impact-card {cls}">
          <p class="impact-text">📌 {titulo}</p>
          <p style="margin:6px 0 0 0;font-size:.95rem;color:#333;font-weight:400;">{texto}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recomendação
    st.markdown(f"""
    <div class="rec-box">
      <h3 style="margin:0 0 10px 0;">🎯 Recomendação Final</h3>
      <p style="font-size:1.05rem;line-height:1.6;margin:0;">
        Criar um <b>programa de incentivo a sellers com bom SLA</b>, priorizando aqueles que
        demonstram <b>consistência no cumprimento de prazo</b> (não apenas velocidade absoluta)
        e <b>bom handling time</b> (componente que o seller controla diretamente). O programa
        deve ser ajustado por estado para não beneficiar sellers de SP simplesmente pela
        vantagem geográfica.
      </p>
      <br>
      <p style="font-size:.95rem;opacity:.85;margin:0;">
        <b>Critérios sugeridos de elegibilidade:</b><br>
        ✔ ≥ 10 pedidos entregues &nbsp;·&nbsp;
        ✔ SLA mediano ≤ 14 dias &nbsp;·&nbsp;
        ✔ ≥ 80% dos pedidos no prazo &nbsp;·&nbsp;
        ✔ Handling mediano ≤ 3 dias &nbsp;·&nbsp;
        ✔ Review médio ≥ 4.0
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Gráfico — elegíveis vs não elegíveis
    df_elig = df_f.copy()
    df_elig["elegivel"] = (
        (df_elig["qtd_pedidos"] >= 10) &
        (df_elig["sla_mediana"] <= 14) &
        (df_elig["pct_no_prazo"].fillna(0) >= 0.8) &
        (df_elig["handling_mediano"].fillna(99) <= 3) &
        (df_elig["review_medio"].fillna(0) >= 4.0)
    )

    n_elig = df_elig["elegivel"].sum()
    rec_elig = df_elig[df_elig["elegivel"]]["receita"].sum()
    pct_elig_sellers = n_elig / len(df_elig) * 100
    pct_elig_receita = rec_elig / df_elig["receita"].sum() * 100

    col_el1, col_el2, col_el3 = st.columns(3)
    col_el1.metric("Sellers Elegíveis", f"{n_elig:,}",
                   f"{pct_elig_sellers:.1f}% do total")
    col_el2.metric("Receita dos Elegíveis", f"R$ {rec_elig:,.0f}",
                   f"{pct_elig_receita:.1f}% da receita total")
    col_el3.metric("Receita Média (elegíveis)",
                   f"R$ {df_elig[df_elig['elegivel']]['receita'].mean():,.0f}")

    fig_elig = px.scatter(
        df_elig, x="sla_mediana", y="receita",
        color="elegivel",
        color_discrete_map={True: GREEN, False: GRAY},
        size="qtd_pedidos", size_max=25, opacity=0.65,
        log_y=True,
        hover_data={"seller_id": False, "estado": True,
                    "pct_no_prazo": ":.0%", "review_medio": ":.2f"},
        labels={"sla_mediana": "SLA Mediano (dias)",
                "receita": "Receita — escala log (R$)",
                "elegivel": "Elegível?"},
        title="Sellers Elegíveis para o Programa de Incentivo (verde = elegível)",
        category_orders={"elegivel": [True, False]},
    )
    fig_elig.update_layout(height=450, plot_bgcolor="white", paper_bgcolor="white",
                           legend=dict(title="Elegível", orientation="h", y=1.05))
    st.plotly_chart(fig_elig, use_container_width=True)

    # Limitações
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("⚠️ Limitações da Análise (expandir para ver)", expanded=False):
        limitacoes = [
            ("Correlação ≠ Causalidade",
             "SLA bom pode ser consequência de escala (seller grande → mais profissional), "
             "não a causa direta de mais receita. Para estabelecer causalidade, seriam "
             "necessários experimentos controlados (A/B test)."),
            ("Viés de Seleção",
             "Sellers com ≥10 pedidos já são mais profissionais. Os 1.730 sellers removidos "
             "(<10 pedidos) podem ter padrões completamente diferentes."),
            ("Îodo dos Dados",
             "Dataset de 2016–2018. O comportamento logístico mudou significativamente "
             "pós-pandemia e os padrões podem não se aplicar ao cenário atual."),
            ("Geografia como Confundidor",
             "Sellers de SP têm SLA naturalmente menor pela proximidade dos centros de consumo. "
             "A análise não controla formalmente por essa variável."),
            ("Receita ≠ Margem",
             "Usamos price como proxy de receita, sem acesso ao custo dos produtos. "
             "Alta receita não garante alta margem."),
        ]
        for titulo, desc in limitacoes:
            st.markdown(f"""
            <div class="warn-box">
              <b>⚠ {titulo}:</b> {desc}
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.caption(
        "Dashboard · Insight 2 — SLA & Receita Olist · "
        "POSTECH DTAT Fase 1 — Tech Challenge · Dataset: 2016–2018"
    )
