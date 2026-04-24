"""Illapa theme — shared CSS injection for all Streamlit pages.

Loads design_tokens.json and emits a single <style> block that overrides the
Streamlit default chrome so the app does not look like a gray IDE panel.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

TOKENS_PATH = Path(__file__).parent / "design_tokens.json"


def load_tokens() -> dict:
    with TOKENS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


TOKENS = load_tokens()
C = TOKENS["color"]["semantic"]
P = TOKENS["color"]["primary"]
S = TOKENS["color"]["secondary"]
N = TOKENS["color"]["neutral"]
CHART = TOKENS["color"]["chart_sequence"]
FONT_DISPLAY = TOKENS["typography"]["font_display"]
FONT_BODY = TOKENS["typography"]["font_body"]
FONT_MONO = TOKENS["typography"]["font_mono"]


def inject_css() -> None:
    """Inject the Illapa design system into the current page."""
    css = f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,400&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

    <style>
    :root {{
        --ill-bg: {C['bg']};
        --ill-bg-alt: {C['bg_alt']};
        --ill-surface: {C['surface']};
        --ill-fg: {C['fg']};
        --ill-fg-muted: {C['fg_muted']};
        --ill-border: {C['border']};
        --ill-accent: {C['accent']};
        --ill-accent-alt: {C['accent_alt']};
        --ill-warning: {C['warning']};
        --ill-font-display: {FONT_DISPLAY};
        --ill-font-body: {FONT_BODY};
        --ill-font-mono: {FONT_MONO};
    }}

    /* ---------- App shell ---------- */
    html, body, [class*="css"], .stApp {{
        background: var(--ill-bg) !important;
        color: var(--ill-fg) !important;
        font-family: var(--ill-font-body) !important;
        font-size: 16px;
    }}
    .main .block-container {{
        max-width: 1180px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }}

    /* ---------- Typography ---------- */
    h1, h2, h3, .ill-display {{
        font-family: var(--ill-font-display) !important;
        letter-spacing: -0.015em;
        color: var(--ill-fg);
    }}
    h1 {{ font-weight: 600; font-size: 3rem; line-height: 1.1; margin-bottom: 0.5rem; }}
    h2 {{ font-weight: 600; font-size: 2.25rem; line-height: 1.15; margin-top: 2.5rem; }}
    h3 {{ font-weight: 600; font-size: 1.5rem; line-height: 1.25; margin-top: 1.5rem; }}
    .ill-kicker {{
        font-family: var(--ill-font-body);
        font-size: 0.75rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--ill-accent);
        font-weight: 600;
        margin-bottom: 0.75rem;
    }}
    .ill-lead {{
        font-size: 1.25rem;
        line-height: 1.55;
        color: var(--ill-fg-muted);
        max-width: 720px;
        margin-bottom: 1.5rem;
    }}
    .ill-quote {{
        font-family: var(--ill-font-display);
        font-style: italic;
        font-size: 1.35rem;
        line-height: 1.5;
        border-left: 3px solid var(--ill-accent);
        padding: 0.5rem 0 0.5rem 1.5rem;
        color: var(--ill-fg);
        max-width: 780px;
    }}
    .ill-quote-attr {{
        font-family: var(--ill-font-body);
        font-style: normal;
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--ill-fg-muted);
        margin-top: 0.75rem;
    }}
    code, .stCode {{
        font-family: var(--ill-font-mono) !important;
        background: var(--ill-bg-alt) !important;
        padding: 0.15em 0.4em;
        border-radius: 3px;
        font-size: 0.9em;
    }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background: var(--ill-fg) !important;
        border-right: 1px solid var(--ill-border);
    }}
    section[data-testid="stSidebar"] * {{
        color: {N['cream_100']} !important;
    }}
    section[data-testid="stSidebar"] .ill-side-brand {{
        font-family: var(--ill-font-display);
        font-size: 1.75rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        margin-bottom: 0.25rem;
    }}
    section[data-testid="stSidebar"] .ill-side-tag {{
        font-size: 0.75rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: {P['ocre_500']} !important;
        margin-bottom: 1.5rem;
    }}
    section[data-testid="stSidebar"] a {{
        color: {N['cream_100']} !important;
        text-decoration: none;
    }}
    section[data-testid="stSidebar"] a:hover {{
        color: {P['ocre_500']} !important;
    }}

    /* ---------- Buttons ---------- */
    .stButton > button {{
        background: var(--ill-accent) !important;
        color: {N['cream_50']} !important;
        border: none;
        border-radius: 4px;
        padding: 0.6rem 1.4rem;
        font-family: var(--ill-font-body);
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.01em;
        transition: all 220ms cubic-bezier(0.22, 0.61, 0.36, 1);
        box-shadow: 0 1px 2px rgba(20,17,15,0.08);
    }}
    .stButton > button:hover {{
        background: {P['terracotta_600']} !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 14px -2px rgba(179,74,44,0.35);
    }}
    .stButton > button:active {{
        transform: translateY(0);
    }}
    .stDownloadButton > button {{
        background: var(--ill-accent-alt) !important;
        color: {N['cream_50']} !important;
    }}
    .stDownloadButton > button:hover {{
        background: {S['turquoise_600']} !important;
    }}

    /* ---------- Sliders ---------- */
    .stSlider [data-baseweb="slider"] div[role="slider"] {{
        background: var(--ill-accent) !important;
        border: 2px solid var(--ill-fg) !important;
    }}

    /* ---------- Cards (used in Home stats) ---------- */
    .ill-card {{
        background: var(--ill-surface);
        border: 1px solid var(--ill-border);
        border-radius: 8px;
        padding: 1.5rem;
        transition: all 220ms cubic-bezier(0.22, 0.61, 0.36, 1);
    }}
    .ill-card:hover {{
        border-color: var(--ill-accent);
        transform: translateY(-2px);
        box-shadow: 0 12px 24px -8px rgba(20,17,15,0.12);
    }}
    .ill-card-number {{
        font-family: var(--ill-font-display);
        font-size: 2.5rem;
        font-weight: 600;
        line-height: 1;
        color: var(--ill-accent);
        letter-spacing: -0.02em;
    }}
    .ill-card-label {{
        font-size: 0.75rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--ill-fg-muted);
        margin-top: 0.5rem;
        font-weight: 500;
    }}
    .ill-card-desc {{
        font-size: 0.9rem;
        color: var(--ill-fg-muted);
        margin-top: 0.75rem;
        line-height: 1.45;
    }}

    /* ---------- Divider ---------- */
    .ill-divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--ill-border), transparent);
        margin: 3rem 0;
        border: none;
    }}

    /* ---------- Badges ---------- */
    .ill-badge {{
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 600;
        border: 1px solid var(--ill-border);
        background: var(--ill-surface);
        color: var(--ill-fg-muted);
        margin-right: 0.5rem;
    }}
    .ill-badge-accent {{
        background: var(--ill-accent);
        color: {N['cream_50']};
        border-color: var(--ill-accent);
    }}
    .ill-badge-alt {{
        background: var(--ill-accent-alt);
        color: {N['cream_50']};
        border-color: var(--ill-accent-alt);
    }}

    /* ---------- Hide Streamlit chrome we don't need ---------- */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    .viewerBadge_container__1QSob {{ display: none; }}

    /* ---------- Demo-only banner ---------- */
    .ill-demo-banner {{
        background: {P['ocre_500']};
        color: var(--ill-fg);
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 500;
        border-left: 3px solid {P['ocre_600']};
        margin-bottom: 1rem;
    }}

    /* ---------- Tabs / expander ---------- */
    .streamlit-expanderHeader {{
        font-family: var(--ill-font-body);
        font-weight: 500;
        background: var(--ill-bg-alt) !important;
        border-radius: 4px !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def sidebar_brand() -> None:
    """Render the Illapa brand lock-up in the sidebar."""
    st.sidebar.markdown(
        """
        <div class="ill-side-brand">Illapa</div>
        <div class="ill-side-tag">Earthquake-Engineering Lab</div>
        """,
        unsafe_allow_html=True,
    )
