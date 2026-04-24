"""Illapa — Home landing page.

Local-only Streamlit demo (no cloud deploy). Run with:

    streamlit run app/main.py
"""
from __future__ import annotations

import streamlit as st

from theme import inject_css, sidebar_brand

# ---------------------------------------------------------------------------
# Page config — MUST be first Streamlit call.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Illapa — Earthquake-Engineering Lab",
    page_icon="⚡",  # used only by browsers; design avoids emoji in UI copy.
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "Illapa — open-source reproducible earthquake-engineering lab "
            "for LATAM structural-dynamics education. MIT licensed."
        ),
    },
)

inject_css()
sidebar_brand()

st.sidebar.markdown(
    """
**Navegación**

- Inicio
- Pushover (análisis estático no lineal)
- Fragilidad (caso LAICSEE 2026)

---

[GitHub](https://github.com/Mikisbell/illapa) · [Dataset](https://huggingface.co/datasets/mikisbell/laicsee-2026)
""",
)

# ---------------------------------------------------------------------------
# Hero section — Illapa myth + framework description.
# ---------------------------------------------------------------------------
st.markdown('<div class="ill-kicker">Laboratorio Reproducible · Ingeniería Sísmica · LATAM</div>', unsafe_allow_html=True)
st.markdown("# Illapa")
st.markdown(
    '<p class="ill-lead">Un laboratorio de ingeniería sísmica reproducible, de código abierto, '
    'para la educación estructural en Latinoamérica. OpenSeesPy, movimientos sintéticos '
    'Kanai-Tajimi y la norma peruana NTE E.030-2018, en un solo pipeline gobernado por '
    'una única fuente de verdad.</p>',
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="ill-quote">
«Illapa camina por las nubes con una honda en la mano. Cuando la lanza, nace el rayo,
retumba el trueno, y la tierra, a veces, tiembla.»
<div class="ill-quote-attr">— Cronistas andinos, s. XVI · Qichwa</div>
</div>
""",
    unsafe_allow_html=True,
)

with st.expander("English translation"):
    st.markdown(
        """
        > *"Illapa walks among the clouds with a sling in his hand. When he casts it,
        > lightning is born, thunder echoes, and the earth, sometimes, trembles."*
        >
        > — Andean chroniclers, 16th century · Qichwa

        In the Inca cosmovision, **Illapa** is the deity of lightning, thunder, and
        earthquakes — the force that both destroys and fertilises. The framework
        borrows the name as a cultural anchor: a reminder that seismic engineering
        in the Andes long predates modern codes, and that honesty about uncertainty
        is a form of respect.
        """
    )

st.markdown('<hr class="ill-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# What Illapa is — definition.
# ---------------------------------------------------------------------------
col_def_a, col_def_b = st.columns([1.3, 1])
with col_def_a:
    st.markdown("## ¿Qué es Illapa?")
    st.markdown(
        """
Illapa integra análisis dinámico no lineal clásico con datasets estructurados listos
para la enseñanza. Reúne cuatro piezas que, por separado, son estándar; juntas, son
poco comunes en un curso de pregrado:

- **OpenSeesPy** — modelado no lineal de un pórtico de concreto armado de 5 niveles
  con rótulas de plasticidad concentrada (IMK).
- **Kanai-Tajimi** — generador de movimientos sintéticos con envolvente Saragoni-Hart,
  calibrable por sitio.
- **NTE E.030-2018** — cumplimiento explícito de la norma peruana, incluyendo la
  amplificación inelástica del Art. 28.2 (0.75·R = 6.0).
- **Gobernanza SSOT** — todos los parámetros viven en un único `config/params.yaml`;
  cada ejecución emite un manifiesto sellado con SHA-256.

Las tres pestañas laterales muestran el pipeline completo: modelo, demanda, fragilidad.
"""
    )

with col_def_b:
    st.markdown("## ¿Qué no es?")
    st.markdown(
        """
- **No** es una herramienta de diseño comercial (para eso, ETABS o SAP2000).
- **No** es una contribución algorítmica nueva — integra métodos existentes.
- **No** es una pedagogía validada en aula (N=1 en esta versión; piloto planificado
  para v1.1).
"""
    )

st.markdown('<hr class="ill-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Stats cards.
# ---------------------------------------------------------------------------
st.markdown("## Caso de estudio — LAICSEE 2026")
st.markdown(
    '<p class="ill-lead">El primer artículo construido con Illapa: un edificio '
    'de concreto armado de 5 niveles en Lima, Zona 3 (PGA = 0.35 g). '
    'Todos los resultados en esta web provienen de esa campaña.</p>',
    unsafe_allow_html=True,
)

stat_cols = st.columns(4)
stats = [
    ("112", "Simulaciones NLTH", "Análisis tiempo-historia no lineales, convergidos."),
    ("14", "Registros PEER NGA-West2", "Validación cruzada con registros reales (7 RSN × 2 componentes)."),
    ("E.030-2018", "Norma peruana", "Cumplimiento Art. 28.2 — amplificación inelástica aplicada."),
    ("MIT", "Licencia", "Código abierto, reutilizable en cualquier curso universitario."),
]
for col, (number, label, desc) in zip(stat_cols, stats):
    col.markdown(
        f"""
<div class="ill-card">
  <div class="ill-card-number">{number}</div>
  <div class="ill-card-label">{label}</div>
  <div class="ill-card-desc">{desc}</div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown('<hr class="ill-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# How to navigate.
# ---------------------------------------------------------------------------
st.markdown("## Cómo navegar")

nav_col_a, nav_col_b = st.columns(2)
with nav_col_a:
    st.markdown(
        """
### Pushover — ¿Cuánto resiste la estructura?
Un análisis estático no lineal: aplicá una carga lateral creciente hasta la rotura.
La curva **V vs Δ** revela la rigidez inicial, el punto de fluencia, la ductilidad
y la sobrerresistencia.

**Slider → Correr → Curva.** Tres pasos, una clase completa.
"""
    )
    st.markdown('<span class="ill-badge ill-badge-accent">Interactivo</span>', unsafe_allow_html=True)

with nav_col_b:
    st.markdown(
        """
### Fragilidad — ¿Qué probabilidad de daño hay en cada sismo?
Curva de fragilidad Monte-Carlo del caso LAICSEE 2026: 62 registros sintéticos por
cada nivel de PGA (0.1 a 0.8 g). Muestra, con intervalos de confianza, la
probabilidad de superar el drift admisible de la norma.

Datos precomputados — sin simulación en esta página.
"""
    )
    st.markdown('<span class="ill-badge ill-badge-alt">Caso de estudio</span>', unsafe_allow_html=True)

st.markdown('<hr class="ill-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Honest footer.
# ---------------------------------------------------------------------------
st.markdown(
    """
<div style="color: var(--ill-fg-muted); font-size: 0.85rem; line-height: 1.6; max-width: 780px;">
<strong>Transparencia.</strong> Illapa documenta siete limitaciones explícitas en su
paper de referencia (modelo shear-type, registros crustales vs subducción, conservadurismo
de Kanai-Tajimi, amortiguamiento Rayleigh, N=1 pedagógico, Δt=0.01 s, poder estadístico
0.789). Ninguna fue calibrada ni silenciada. Ver <code>CHANGELOG.md</code> para detalles.
<br><br>
<strong>Local-only.</strong> Esta web no recopila telemetría ni envía datos a ningún
servidor. Corre íntegramente en tu máquina.
</div>
""",
    unsafe_allow_html=True,
)
