"""Illapa — Fragility page.

Loads the pre-computed fragility curve from the LAICSEE 2026 case study
(`app/data/fragility_curve.csv`). NO simulation runs here — this page teaches
how to read a fragility curve and what Monte-Carlo uncertainty means.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import CHART, inject_css, sidebar_brand  # noqa: E402

st.set_page_config(
    page_title="Illapa — Fragilidad",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
sidebar_brand()

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "fragility_curve.csv"

# ---------------------------------------------------------------------------
# Header.
# ---------------------------------------------------------------------------
st.markdown('<div class="ill-kicker">Caso de estudio LAICSEE 2026 · Monte-Carlo</div>', unsafe_allow_html=True)
st.markdown("# Curva de Fragilidad")
st.markdown(
    '<p class="ill-lead">Dada una intensidad sísmica <em>PGA</em>, ¿qué probabilidad '
    'hay de superar el drift admisible de la norma? La curva de fragilidad responde '
    'esa pregunta. Los datos de esta página provienen de <strong>62 registros '
    'sintéticos Kanai-Tajimi por nivel de PGA</strong>, analizados con OpenSeesPy.</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Load data.
# ---------------------------------------------------------------------------
if not DATA_PATH.exists():
    st.error(
        f"No se encontró el archivo `{DATA_PATH.name}`. "
        "Ejecutá primero el pipeline LAICSEE o copiá el CSV a `app/data/`."
    )
    st.stop()

df = pd.read_csv(DATA_PATH)

# ---------------------------------------------------------------------------
# Plot.
# ---------------------------------------------------------------------------
fig = go.Figure()

# Inelastic curve (E.030 Art. 28.2 — primary contribution).
fig.add_trace(
    go.Scatter(
        x=df["pga_g"],
        y=df["ci_upper_inelastic"],
        mode="lines",
        line=dict(color=CHART[0], width=0),
        showlegend=False,
        hoverinfo="skip",
    )
)
fig.add_trace(
    go.Scatter(
        x=df["pga_g"],
        y=df["ci_lower_inelastic"],
        mode="lines",
        line=dict(color=CHART[0], width=0),
        fill="tonexty",
        fillcolor="rgba(179,74,44,0.18)",
        name="IC 95% (inelástico)",
        hoverinfo="skip",
    )
)
fig.add_trace(
    go.Scatter(
        x=df["pga_g"],
        y=df["P_exceed_drift_inelastic"],
        mode="lines+markers",
        line=dict(color=CHART[0], width=3),
        marker=dict(size=10, color=CHART[0], line=dict(color="#14110F", width=1.5)),
        name="P(exceed drift) — inelástico E.030 Art. 28.2",
        hovertemplate="PGA = %{x} g<br>P = %{y:.3f}<extra></extra>",
    )
)

# Elastic (reference).
fig.add_trace(
    go.Scatter(
        x=df["pga_g"],
        y=df["P_exceed_drift_elastic"],
        mode="lines+markers",
        line=dict(color=CHART[1], width=2, dash="dash"),
        marker=dict(size=7, color=CHART[1], symbol="diamond"),
        name="P(exceed drift) — elástico (referencia)",
        hovertemplate="PGA = %{x} g<br>P = %{y:.3f}<extra></extra>",
    )
)

# Design level line at PGA = 0.35 g (E.030 Zona 3 Lima).
fig.add_vline(
    x=0.35,
    line_dash="dot",
    line_color="#5B4F45",
    annotation_text="PGA diseño E.030 = 0.35 g (Lima Zona 3)",
    annotation_position="top right",
    annotation_font=dict(family="Fraunces, serif", size=12, color="#5B4F45"),
)

fig.update_layout(
    template="simple_white",
    font=dict(family="Inter, sans-serif", size=14, color="#14110F"),
    title=dict(
        text="Fragilidad — caso LAICSEE 2026 (5 niveles, Lima)",
        font=dict(family="Fraunces, serif", size=22, color="#14110F"),
        x=0,
    ),
    xaxis=dict(
        title="Aceleración pico del suelo PGA (g)",
        gridcolor="#D4C6B0",
        zerolinecolor="#8A7E71",
        range=[0.05, 0.85],
    ),
    yaxis=dict(
        title="P (drift > drift admisible)",
        gridcolor="#D4C6B0",
        zerolinecolor="#8A7E71",
        range=[-0.05, 1.08],
    ),
    plot_bgcolor="#FAF6EC",
    paper_bgcolor="#F5EEDC",
    margin=dict(l=60, r=20, t=60, b=60),
    height=500,
    legend=dict(
        bgcolor="rgba(250,246,236,0.85)",
        bordercolor="#D4C6B0",
        borderwidth=1,
        x=0.02,
        y=0.98,
        font=dict(size=12),
    ),
    hoverlabel=dict(bgcolor="#FAF6EC", font=dict(family="Inter, sans-serif")),
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Summary metrics at design PGA.
# ---------------------------------------------------------------------------
row_35 = df.iloc[(df["pga_g"] - 0.35).abs().idxmin()]  # closest to design PGA
m1, m2, m3 = st.columns(3)
m1.metric(
    "P(exceed) @ PGA = 0.35 g",
    f"{float(row_35['P_exceed_drift_inelastic']):.1%}",
    help="Probabilidad de superar el drift admisible bajo la demanda de diseño de Lima.",
)
m2.metric(
    "Muestras por nivel",
    f"{int(df['n_samples'].iloc[0])}–{int(df['n_samples'].max())}",
    help="Registros Kanai-Tajimi por nivel de PGA (Monte-Carlo).",
)
m3.metric(
    "Niveles de PGA",
    f"{len(df)}",
    help="Resolución de la curva (0.1 a 0.8 g en pasos de 0.1).",
)

# ---------------------------------------------------------------------------
# Pedagogical explanation (ES + EN).
# ---------------------------------------------------------------------------
st.markdown('<hr class="ill-divider">', unsafe_allow_html=True)

exp_col_a, exp_col_b = st.columns(2)
with exp_col_a:
    st.markdown("### Cómo leer esta curva")
    st.markdown(
        """
Una curva de fragilidad es una respuesta probabilística:

- En el **eje X**, la intensidad sísmica (PGA, en unidades de g = 9.81 m/s²).
- En el **eje Y**, la probabilidad de superar un estado límite. Acá el estado es
  el drift de entrepiso admisible según la norma peruana E.030.

La banda clara alrededor de la curva es el **intervalo de confianza 95% (Wilson)**,
que representa la incertidumbre de estimar probabilidades con muestras finitas.
A PGA bajos la incertidumbre es ancha (pocos eventos de falla); a PGA altos la curva
se clava en 1.0.

La línea **inelástica** es la respuesta primaria: aplica la amplificación del Art. 28.2
(drift elástico × 0.75·R). La línea **elástica** sirve de referencia — lo que reportaría
un análisis que ignorara la no linealidad.
"""
    )

with exp_col_b:
    st.markdown("### Reading the curve")
    st.markdown(
        """
A fragility curve is a probabilistic answer:

- **X axis** — seismic intensity (PGA, in units of g).
- **Y axis** — probability of exceeding a limit state. Here the state is the
  inter-story drift allowed by Peruvian code E.030.

The light band around the line is the **95% Wilson confidence interval**, which
captures the uncertainty from estimating probabilities with finite samples. At low
PGA the band is wide (few failures observed); at high PGA the curve saturates at 1.0.

The **inelastic** line is the primary result — it applies the Art. 28.2 amplification
(elastic drift × 0.75·R). The **elastic** line is a reference: what an analysis
ignoring nonlinearity would have reported.
"""
    )

# ---------------------------------------------------------------------------
# Raw data table.
# ---------------------------------------------------------------------------
st.markdown('<hr class="ill-divider">', unsafe_allow_html=True)

with st.expander("Ver datos crudos · Raw data"):
    st.markdown(
        "Datos originales de `data/processed/fragility_curve.csv` (caso LAICSEE 2026). "
        "Cada fila es una ejecución Monte-Carlo de 62 registros sintéticos Kanai-Tajimi "
        "al nivel de PGA indicado."
    )
    st.dataframe(
        df.style.format(
            {
                "pga_g": "{:.2f}",
                "P_exceed_drift_elastic": "{:.3f}",
                "P_exceed_drift_inelastic": "{:.3f}",
                "ci_lower_elastic": "{:.3f}",
                "ci_upper_elastic": "{:.3f}",
                "ci_lower_inelastic": "{:.3f}",
                "ci_upper_inelastic": "{:.3f}",
            }
        ),
        use_container_width=True,
    )

    st.download_button(
        "Descargar CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="illapa_fragility_laicsee_2026.csv",
        mime="text/csv",
    )

st.caption(
    "Metodología: 62 registros sintéticos Kanai-Tajimi por nivel de PGA (envolvente Saragoni-Hart), "
    "analizados con un modelo 5 niveles RC MRF en OpenSeesPy. Drift admisible según NTE E.030-2018. "
    "Intervalos de confianza Wilson a 95%. Ver paper para detalles."
)
