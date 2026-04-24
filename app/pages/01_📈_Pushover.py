"""Illapa — Pushover analysis page.

Static nonlinear pushover: lateral load grows monotonically until roof drift
reaches target. The plot shows base-shear V vs roof displacement Δ.

DUAL MODE
---------
- **Default (instant)**: ASCE 41-17 idealised bilinear, closed-form, recomputed
  on every slider change. Calibrated against the LAICSEE 2026 paper outputs.
- **Real OpenSeesPy (~1 s)**: on demand, via the `🔬 Correr OpenSeesPy real`
  button. Spawns a subprocess against the `laicsee-2026/.venv` (Python 3.12 with
  openseespywin) and runs a 1-DOF zeroLength spring with `uniaxialMaterial
  Steel01`, driven by the current slider values. This is NOT the full 5-story
  Bilin IMK model of the paper (that takes 30 s and lives in
  `examples/rc_5story_peru/run_pushover.py`). It is a genuine OpenSeesPy solve
  using the same (K₀, V_y, α, H) the user typed into the sliders.

The two curves overlay on the same canvas so the student sees both:
- Bilinear (terracota, solid): the textbook idealisation.
- OpenSeesPy (turquesa, dashed): what the actual nonlinear solver produces.

Both curves should match closely when Steel01 is a good proxy for the ASCE
41-17 idealisation — i.e. when α is not too negative. Divergence between the
two is itself a pedagogical signal: the idealisation is a model, the solver
is the physics.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Add parent to path so `theme` imports resolve.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import CHART, inject_css, sidebar_brand  # noqa: E402

st.set_page_config(
    page_title="Illapa — Pushover",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
sidebar_brand()

# Secondary-button style for the OpenSeesPy action (turquesa/accent_alt).
# Streamlit renders primary/secondary buttons via data-testid; we scope the
# override to buttons wrapped in our .ill-real-btn container.
st.markdown(
    """
    <style>
    .ill-real-btn + div .stButton > button {
        background: var(--ill-accent-alt) !important;
        color: #FAF6EC !important;
    }
    .ill-real-btn + div .stButton > button:hover {
        background: #226E6E !important;
        box-shadow: 0 6px 14px -2px rgba(46,139,139,0.35) !important;
    }
    .ill-real-btn + div .stButton > button:disabled {
        background: #8A7E71 !important;
        color: #EDE4D3 !important;
        cursor: not-allowed;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# OpenSeesPy subprocess runner.
# ---------------------------------------------------------------------------
# The venv that ships openseespywin on Windows (Python 3.12). If missing,
# the button stays disabled with a user-facing explanation.
_OPENSEES_VENV_PY = Path(
    r"E:/FREECLOUD/FREECLOUD-IA/PROYECTOS/laicsee-2026/.venv/Scripts/python.exe"
)

# OpenSeesPy driver script written once on first use (into the OS temp dir so
# it survives across Streamlit reruns without polluting the repo). Uses
# Steel01 — a canonical OpenSeesPy bilinear with kinematic hardening — on a
# zeroLength spring. Fed by (K0, Vy, alpha, H) from the sliders.
_OPENSEES_SCRIPT = r'''"""1-DOF pushover via OpenSeesPy Steel01. Driven by CLI args."""
import json
import sys

import openseespy.opensees as ops


def run(K0_Nm, Vy_N, alpha, H_m, out_path):
    ops.wipe()
    ops.model("basic", "-ndm", 1, "-ndf", 1)

    ops.node(1, 0.0)
    ops.node(2, 0.0)
    ops.fix(1, 1)

    # Steel01: fy = Vy_N, E0 = K0_Nm, b = alpha (post-yield / elastic ratio).
    # Used on a zeroLength spring, so "stress"=force and "strain"=displacement.
    ops.uniaxialMaterial("Steel01", 1, float(Vy_N), float(K0_Nm), float(alpha))
    ops.element("zeroLength", 1, 1, 2, "-mat", 1, "-dir", 1)

    # Pushover target: FEMA 356 Table C1-3 near-collapse roof drift = 4 % H.
    target = 0.04 * H_m
    n_steps = 400
    du = target / n_steps

    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(2, 1.0)

    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-8, 50, 0)
    ops.algorithm("Newton")
    ops.integrator("DisplacementControl", 2, 1, du)
    ops.analysis("Static")

    delta = [0.0]
    V = [0.0]
    converged = True
    diverged_step = None

    for step in range(n_steps):
        ok = ops.analyze(1)
        if ok != 0:
            recovered = False
            for algo in ("ModifiedNewton", "KrylovNewton"):
                ops.algorithm(algo)
                if ops.analyze(1) == 0:
                    recovered = True
                    break
            ops.algorithm("Newton")
            if not recovered:
                converged = False
                diverged_step = step
                break
        ops.reactions()
        d = float(ops.nodeDisp(2, 1))
        r = -float(ops.nodeReaction(1, 1))  # reaction sign flips
        delta.append(d)
        V.append(r)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "delta_m": delta,
                "V_N": V,
                "converged": converged,
                "diverged_step": diverged_step,
                "steps_run": len(delta) - 1,
                "n_steps_target": n_steps,
                "target_disp_m": target,
            },
            f,
        )


if __name__ == "__main__":
    K0 = float(sys.argv[1]) * 1.0e6   # MN/m -> N/m
    Vy = float(sys.argv[2]) * 1.0e3   # kN   -> N
    alpha = float(sys.argv[3])
    H = float(sys.argv[4])            # m
    out = sys.argv[5]
    run(K0, Vy, alpha, H, out)
    print(f"DONE {out}")
'''


def _ensure_driver_script() -> Path:
    """Write the OpenSeesPy driver into the OS temp dir once per session."""
    script_path = Path(tempfile.gettempdir()) / "illapa_1dof_pushover.py"
    if not script_path.exists() or script_path.read_text(encoding="utf-8") != _OPENSEES_SCRIPT:
        script_path.write_text(_OPENSEES_SCRIPT, encoding="utf-8")
    return script_path


def run_real_opensees(
    K0_MNm: float, Vy_kN: float, alpha: float, H_m: float
) -> dict:
    """Execute the 1-DOF OpenSeesPy pushover via subprocess, return parsed JSON.

    Raises RuntimeError on subprocess failure. Does NOT silently fall back.
    """
    if not _OPENSEES_VENV_PY.exists():
        raise FileNotFoundError(
            f"OpenSeesPy venv not found at {_OPENSEES_VENV_PY}. "
            "This button requires the laicsee-2026 Python 3.12 venv."
        )

    script = _ensure_driver_script()
    out_path = Path(tempfile.gettempdir()) / f"illapa_pushover_{int(time.time()*1000)}.json"

    t0 = time.time()
    result = subprocess.run(
        [
            str(_OPENSEES_VENV_PY),
            str(script),
            f"{K0_MNm:.6f}",
            f"{Vy_kN:.6f}",
            f"{alpha:.6f}",
            f"{H_m:.6f}",
            str(out_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    elapsed = time.time() - t0

    if result.returncode != 0:
        raise RuntimeError(
            f"OpenSeesPy subprocess failed (code {result.returncode}).\n"
            f"stderr: {result.stderr[:500]}"
        )

    if not out_path.exists():
        raise RuntimeError(
            "OpenSeesPy finished with code 0 but wrote no output file. "
            f"stdout={result.stdout[:200]}"
        )

    with out_path.open(encoding="utf-8") as f:
        data = json.load(f)
    data["elapsed_s"] = elapsed
    try:
        out_path.unlink()
    except OSError:
        pass
    return data


# ---------------------------------------------------------------------------
# Header.
# ---------------------------------------------------------------------------
st.markdown('<div class="ill-kicker">Análisis Estático No Lineal · ASCE 41-17</div>', unsafe_allow_html=True)
st.markdown("# Pushover")
st.markdown(
    '<p class="ill-lead">Aplicá una distribución lateral modal creciente y observá '
    'cómo se degrada la rigidez, aparece la fluencia, y la estructura transita hacia '
    'el colapso. El corte basal <em>V</em> contra el desplazamiento de azotea <em>Δ</em> '
    'es la firma no lineal del edificio.</p>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="ill-demo-banner">'
    '<strong>Doble modo</strong> · La vista por defecto es la <em>idealización bilineal '
    'ASCE 41-17</em> (forma cerrada, instantánea). El botón <em>"Correr OpenSeesPy real"</em> '
    'ejecuta en subproceso un modelo 1-DOF con <code>Steel01</code> alimentado por los mismos '
    'sliders y superpone la curva real. No es el modelo 5-niveles Bilin IMK del paper '
    '(ése vive en <code>examples/rc_5story_peru/run_pushover.py</code>), pero sí es '
    'OpenSeesPy de verdad.'
    '</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Controls.
# ---------------------------------------------------------------------------
col_inputs, col_plot = st.columns([1, 2.2], gap="large")

with col_inputs:
    st.markdown("### Parámetros")
    st.caption("Defaults = caso LAICSEE 2026 (5 niveles, Lima Zona 3).")

    height_m = st.slider(
        "Altura total H (m)",
        min_value=8.0,
        max_value=24.0,
        value=15.0,
        step=0.5,
        help="Altura total del edificio. Defaults a un 5-niveles de 3 m entre pisos.",
    )
    mass_tons = st.slider(
        "Masa total M (toneladas)",
        min_value=100.0,
        max_value=1200.0,
        value=500.0,
        step=10.0,
        help="Masa sísmica agrupada. 500 t ≈ losa típica de concreto armado × 5 niveles.",
    )
    k_MNm = st.slider(
        "Rigidez inicial K₀ (MN/m)",
        min_value=20.0,
        max_value=200.0,
        value=89.4,
        step=0.5,
        help="Rigidez lateral elástica inicial. Default del LAICSEE: 89.4 MN/m.",
    )
    fy_kN = st.slider(
        "Cortante de fluencia V_y (kN)",
        min_value=1000,
        max_value=8000,
        value=3643,
        step=25,
        help="Corte basal al cual aparece la primera rótula plástica significativa.",
    )
    xi = st.slider(
        "Amortiguamiento ξ (%)",
        min_value=1.0,
        max_value=10.0,
        value=5.0,
        step=0.5,
        help="Amortiguamiento viscoso equivalente. 5% es el valor E.030 por defecto.",
    )
    alpha_post = st.slider(
        "Pendiente post-fluencia α",
        min_value=-0.20,
        max_value=0.10,
        value=-0.116,
        step=0.005,
        help="Rigidez post-fluencia normalizada. α < 0 indica ablandamiento (suavizado).",
        format="%.3f",
    )

    st.markdown("---")

    # Primary action: re-render bilinear (kept for clarity, though it updates
    # on any slider change — the button is effectively a "confirm" signal).
    run_bilinear = st.button(
        "Actualizar vista bilineal",
        use_container_width=True,
        help="La curva bilineal ya se recomputa en cada cambio de slider; este botón sólo confirma.",
    )

    # Secondary action: spawn OpenSeesPy subprocess. Rendered inside a
    # marker div so the CSS above repaints it turquesa (design system).
    st.markdown('<div class="ill-real-btn"></div>', unsafe_allow_html=True)
    run_real = st.button(
        "🔬 Correr OpenSeesPy real (~1 s)",
        use_container_width=True,
        help=(
            "Lanza un subproceso Python (venv laicsee-2026) que arma un modelo "
            "1-DOF Steel01 en OpenSeesPy y corre el pushover con los valores "
            "actuales de los sliders. Superpone el resultado sobre la bilineal."
        ),
        key="btn_run_real",
    )

    # Availability probe: if the venv is missing, disable the button visually.
    if not _OPENSEES_VENV_PY.exists():
        st.caption(
            "⚠️ `venv laicsee-2026` no encontrado en "
            f"`{_OPENSEES_VENV_PY}`. El botón no puede ejecutar OpenSeesPy real."
        )

# ---------------------------------------------------------------------------
# Plot.
# ---------------------------------------------------------------------------
with col_plot:
    # -----------------------------------------------------------------------
    # Bilinear (default, instant).
    # -----------------------------------------------------------------------
    K0 = k_MNm * 1e6  # N/m
    Vy_N = fy_kN * 1e3
    delta_y = Vy_N / K0  # m

    # FEMA 356 / ASCE 41-17 Sec. 3.3.1.2.1 definition of Delta_u:
    # "first post-peak drop to 0.80 V_peak" (paper §2.4).
    # In the bilinear idealisation with softening (alpha < 0), V_peak = V_y
    # and V(delta) = Vy + alpha*K0*(delta - delta_y) for delta > delta_y.
    # Setting V(delta_u) = 0.80 * V_y gives:
    #     delta_u = delta_y + (-0.20 * V_y) / (alpha * K0)        (alpha < 0)
    # For alpha >= 0 (hardening / perfectly plastic) the curve never drops to
    # 0.80 V_peak, so we fall back to FEMA 356 Table C1-3 near-collapse roof
    # drift of 0.04 * H. In practice the FEMA criterion also gets capped by
    # 0.04 * H if alpha is very small (near-elastic-perfectly-plastic).
    roof_drift_cap = 0.04 * height_m  # FEMA 356 near-collapse roof drift
    if alpha_post < 0:
        delta_u_fema = delta_y + (-0.20 * Vy_N) / (alpha_post * K0)
    else:
        delta_u_fema = float("inf")
    delta_u = min(delta_u_fema, roof_drift_cap)
    cap_active = delta_u_fema > roof_drift_cap  # True when 4% H governs

    n_pts = 200
    delta = np.linspace(0.0, delta_u, n_pts)
    V = np.where(
        delta <= delta_y,
        K0 * delta,
        Vy_N + alpha_post * K0 * (delta - delta_y),
    )
    V_peak = float(np.max(V))
    V_final = float(V[-1])
    mu = delta_u / delta_y

    # -----------------------------------------------------------------------
    # Real OpenSeesPy (on-demand, cached by slider state).
    # -----------------------------------------------------------------------
    # Cache key: every slider that affects the subprocess result.
    state_key = (
        round(k_MNm, 4),
        round(fy_kN, 4),
        round(alpha_post, 4),
        round(height_m, 4),
    )
    cache = st.session_state.setdefault("opensees_cache", {})

    if run_real:
        # If sliders moved since last click, re-run; else re-use cached.
        if state_key not in cache:
            with st.spinner(
                "Procesando OpenSeesPy real (1-DOF Steel01)… "
                "subproceso Python 3.12 + venv laicsee-2026."
            ):
                try:
                    result = run_real_opensees(k_MNm, fy_kN, alpha_post, height_m)
                    cache[state_key] = result
                    if result["converged"]:
                        st.toast(
                            f"OpenSeesPy OK · {result['steps_run']} steps · "
                            f"{result['elapsed_s']:.2f} s",
                            icon="✅",
                        )
                    else:
                        st.warning(
                            f"OpenSeesPy divergió en step {result['diverged_step']} "
                            f"de {result['n_steps_target']}. La curva muestra lo que "
                            "alcanzó a resolver antes del fallo. Probá α menos negativo "
                            "o una malla de desplazamiento más fina."
                        )
                except FileNotFoundError as exc:
                    st.error(f"**venv no disponible** — {exc}")
                except subprocess.TimeoutExpired:
                    st.error(
                        "OpenSeesPy excedió el timeout de 30 s. El modelo 1-DOF "
                        "no debería tardar tanto — probablemente un bug del driver; "
                        "revisá los sliders (¿valores fuera de rango?)."
                    )
                except RuntimeError as exc:
                    st.error(f"**OpenSeesPy falló** — {exc}")

    real_result = cache.get(state_key)

    # -----------------------------------------------------------------------
    # Figure — overlay both curves.
    # -----------------------------------------------------------------------
    fig = go.Figure()

    # 1. Bilinear curve (baseline, terracota solid, width 3).
    fig.add_trace(
        go.Scatter(
            x=delta * 1000,  # mm
            y=V / 1e3,  # kN
            mode="lines",
            line=dict(color=CHART[0], width=3),
            name="Bilineal ASCE 41-17 (forma cerrada)",
            hovertemplate="Δ = %{x:.1f} mm<br>V = %{y:.0f} kN<extra>bilineal</extra>",
        )
    )

    # 2. Real OpenSeesPy overlay (turquesa dashed, thinner, slightly lower opacity).
    if real_result is not None:
        delta_os = np.array(real_result["delta_m"]) * 1000  # mm
        V_os = np.array(real_result["V_N"]) / 1e3  # kN
        legend_label = "OpenSeesPy real (1-DOF Steel01)"
        if not real_result["converged"]:
            legend_label += f" — divergió @ step {real_result['diverged_step']}"
        fig.add_trace(
            go.Scatter(
                x=delta_os,
                y=V_os,
                mode="lines",
                line=dict(color=CHART[1], width=2, dash="dash"),
                opacity=0.88,
                name=legend_label,
                hovertemplate="Δ = %{x:.1f} mm<br>V = %{y:.0f} kN<extra>OpenSeesPy</extra>",
            )
        )

    # 3. Yield marker (bilinear).
    fig.add_trace(
        go.Scatter(
            x=[delta_y * 1000],
            y=[Vy_N / 1e3],
            mode="markers+text",
            marker=dict(color=CHART[2], size=12, symbol="circle", line=dict(color="#14110F", width=1.5)),
            text=["  Fluencia"],
            textposition="middle right",
            textfont=dict(family="Fraunces, serif", size=14, color="#14110F"),
            name="Punto de fluencia (bilineal)",
            hovertemplate="Δ_y = %{x:.1f} mm<br>V_y = %{y:.0f} kN<extra></extra>",
        )
    )

    # 4. Elastic slope dashed reference.
    fig.add_trace(
        go.Scatter(
            x=[0, delta_u * 1000],
            y=[0, K0 * delta_u / 1e3],
            mode="lines",
            line=dict(color=CHART[3], width=1, dash="dot"),
            name="Extensión elástica (referencia)",
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        template="simple_white",
        font=dict(family="Inter, sans-serif", size=14, color="#14110F"),
        title=dict(
            text="Curva de capacidad (pushover)",
            font=dict(family="Fraunces, serif", size=22, color="#14110F"),
            x=0,
        ),
        xaxis=dict(
            title="Desplazamiento de azotea Δ (mm)",
            gridcolor="#D4C6B0",
            zerolinecolor="#8A7E71",
        ),
        yaxis=dict(
            title="Corte basal V (kN)",
            gridcolor="#D4C6B0",
            zerolinecolor="#8A7E71",
        ),
        plot_bgcolor="#FAF6EC",
        paper_bgcolor="#F5EEDC",
        margin=dict(l=60, r=20, t=60, b=60),
        height=460,
        legend=dict(
            bgcolor="rgba(250,246,236,0.8)",
            bordercolor="#D4C6B0",
            borderwidth=1,
            x=0.02,
            y=0.98,
            font=dict(size=12),
        ),
        hoverlabel=dict(bgcolor="#FAF6EC", font=dict(family="Inter, sans-serif")),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Status caption — reflects what was last computed.
    if real_result is not None:
        mode_msg = (
            f"Bilineal + OpenSeesPy real · solver corrió {real_result['steps_run']} "
            f"steps en {real_result['elapsed_s']:.2f} s "
            f"({'convergió' if real_result['converged'] else 'divergió'})."
        )
    elif run_bilinear:
        mode_msg = (
            f"Modelo bilineal (ASCE 41-17) recomputado · {n_pts} puntos en la curva · "
            "respuesta instantánea (forma cerrada, sin solver)."
        )
    else:
        mode_msg = (
            f"Bilineal por defecto · {n_pts} puntos · forma cerrada. "
            "Usá el botón 🔬 para superponer OpenSeesPy real."
        )
    st.caption(mode_msg)

    # Key metrics.
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Δ_y (mm)", f"{delta_y*1000:.1f}")
    m2.metric("V_y (kN)", f"{Vy_N/1e3:,.0f}")
    mu_help = (
        "Δ_u = 0.04·H (tope FEMA 356 near-collapse). α ≥ 0 no ablanda."
        if cap_active
        else "Δ_u donde V cae al 80 % de V_peak (FEMA 356 / ASCE 41-17)."
    )
    m3.metric("Ductilidad μ", f"{mu:.2f}", help=mu_help)
    m4.metric("V_peak (kN)", f"{V_peak/1e3:,.0f}")

# ---------------------------------------------------------------------------
# Pedagogical explanation.
# ---------------------------------------------------------------------------
st.markdown('<hr class="ill-divider">', unsafe_allow_html=True)

exp_a, exp_b = st.columns(2)
with exp_a:
    st.markdown("### ¿Qué estás viendo?")
    st.markdown(
        """
La curva **V vs Δ** resume el comportamiento no lineal del edificio:

1. **Tramo elástico** — pendiente = K₀. La estructura es reversible.
2. **Punto de fluencia** — primera rótula plástica; la rigidez cae.
3. **Post-fluencia** — si α > 0, endurecimiento (poco común). Si α < 0, ablandamiento
   (típico en estructuras reales de concreto, porque la carga axial induce daño geométrico P-Δ).
4. **Ductilidad μ = Δ_u / Δ_y** — cuántas veces la deformación de fluencia aguanta
   la estructura antes de que el corte basal caiga al **80 % del pico** (criterio FEMA 356
   / ASCE 41-17 §3.3.1.2.1). Con rama de ablandamiento, Δ_u sale del slope α directamente;
   si α ≥ 0 se aplica el tope FEMA 356 de 0.04·H (near-collapse roof drift).

El caso LAICSEE reporta μ ≈ 2.73 y α ≈ -0.116, valores consistentes con un pórtico
peruano de 5 niveles sin muros de corte. Observá que μ depende fuertemente de α: a mayor
ablandamiento (α más negativo), menor ductilidad.

**Doble curva:** la línea terracota (bilineal) es la idealización ASCE 41-17. La línea
turquesa a rayas (cuando la activás con el botón 🔬) es lo que un solver real de
OpenSeesPy produce con los mismos parámetros — 1-DOF con `Steel01`. Cuando ambas
coinciden, la idealización es buena. Cuando se separan, la separación es la lección.
"""
    )

with exp_b:
    st.markdown("### Lectura en inglés")
    st.markdown(
        """
**Capacity curve V vs Δ — the nonlinear signature of the building.**

1. **Elastic branch** — slope = K₀. Structure is reversible.
2. **Yield point** — first significant plastic hinge; stiffness drops.
3. **Post-yield** — α > 0 means hardening (rare). α < 0 means softening, typical of
   real RC frames because axial load triggers P-Δ geometric damage.
4. **Ductility μ = Δ_u / Δ_y** — how many yield-deformations the building sustains
   before base shear drops to **80 % of the peak** (FEMA 356 / ASCE 41-17 §3.3.1.2.1).
   With softening branch, Δ_u follows directly from α; if α ≥ 0 we fall back to the
   FEMA 356 near-collapse cap of 0.04·H.

The LAICSEE case reports μ ≈ 2.73 and α ≈ −0.116, consistent with a 5-story Peruvian
frame without shear walls. Note μ is mostly controlled by α: the more negative the
softening, the lower the available ductility.

**Dual overlay:** the terracota solid line is the ASCE 41-17 bilinear idealisation.
The turquoise dashed line (enabled by the 🔬 button) is what a real OpenSeesPy solver
— 1-DOF `Steel01` spring — produces with the same slider inputs. When the two match,
the idealisation is trustworthy. When they diverge, the divergence itself is the lesson.
"""
    )

st.caption(
    "Fuente de los defaults: `config/params.yaml` (SSOT) y "
    "`data/processed/pushover_results.json` del paper LAICSEE 2026. "
    "Referencia normativa: ASCE 41-17 Sec. 3.3.1.2.1. "
    "Modelo OpenSeesPy real: 1-DOF zeroLength + Steel01 "
    "(simplificación del 5-niveles Bilin IMK del paper; "
    "ver `examples/rc_5story_peru/run_pushover.py` para el modelo completo)."
)
