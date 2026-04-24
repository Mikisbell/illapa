# Illapa — Web Demo Local (Streamlit)

Demo interactivo del framework Illapa. **Corre íntegramente en tu máquina** — sin
nube, sin telemetría, sin backend remoto.

## Contenido

```
app/
├── main.py                     # Home · mito Illapa + descripción del framework
├── pages/
│   ├── 01_📈_Pushover.py       # Sliders → análisis no lineal estático
│   └── 02_🌊_Fragility.py      # Curva de fragilidad del caso LAICSEE 2026
├── .streamlit/config.toml      # Tema aplicando design_tokens.json
├── assets/                     # Estáticos (logo, imágenes)
├── data/
│   ├── fragility_curve.csv     # Precomputado desde el paper LAICSEE 2026
│   └── pushover_reference.json # Salida del OpenSeesPy real (referencia)
├── design_tokens.json          # Sistema de diseño andino (Phase 1)
├── brand_voice.md              # Guías de voz (Phase 1)
└── theme.py                    # Inyector de CSS Illapa para todas las páginas
```

## Requisitos

- Python ≥ 3.12 (mismo que el framework principal)
- Dependencias en `requirements.txt` de la raíz del repo — incluye `streamlit` y `plotly`.

## Correr

Desde la **raíz del repo `illapa/`** (no desde `app/`):

```bash
# 1. Activá el venv del proyecto
source .venv/Scripts/activate          # Git Bash Windows
# .venv\Scripts\Activate.ps1           # PowerShell Windows
# source .venv/bin/activate            # Linux/macOS

# 2. Instalá dependencias si es la primera vez
pip install -r requirements.txt

# 3. Corré la web
streamlit run app/main.py
```

Streamlit abrirá `http://localhost:8501` en tu navegador. Las páginas Pushover y
Fragilidad aparecen automáticamente en la barra lateral.

## Qué hace cada página

| Página | Propósito | Datos | Simulación en vivo |
|--------|-----------|-------|--------------------|
| **Inicio** | Mito Illapa + definición del framework + stats del caso LAICSEE. | Estáticos. | No. |
| **Pushover** | Sliders (altura, masa, K₀, V_y, ξ, α) → curva V vs Δ. | Modelo bilineal cerrado ASCE 41-17, calibrado contra el OpenSeesPy real. | Sí (demo pedagógica). |
| **Fragilidad** | Curva Monte-Carlo del caso LAICSEE 2026 con IC 95% Wilson. | `data/fragility_curve.csv` — 62 registros KT por PGA. | No (datos precomputados). |

## Decisión de diseño: por qué la página Pushover es un modelo cerrado

El modelo OpenSeesPy real del paper (5 niveles, plasticidad concentrada IMK) demora
~30 s por ejecución — demasiado para un slider interactivo. La página usa la
idealización bilineal ASCE 41-17 Sec. 3.3.1.2.1 calibrada contra los parámetros
reales del paper (K₀ = 89.4 MN/m, V_y = 3643 kN, α = −0.116). El banner naranja
de "Simulación pedagógica" lo declara explícitamente.

Para la corrida real, usá el CLI:

```bash
python examples/rc_5story_peru/run_pushover.py
```

## Sistema de diseño

Ver [`design_tokens.json`](design_tokens.json) y [`brand_voice.md`](brand_voice.md).
Paleta inspirada en textiles andinos (terracota + turquesa + obsidiana + crema).
Tipografía Fraunces (serif de piedra) + Inter (sans humanista). Zero emojis en las
copias de UI — los pictogramas de Streamlit en los nombres de archivo son la única
concesión (para que aparezcan en la sidebar del framework).

## Local-only, siempre

Esta app **no** tiene deploy a producción. Es una herramienta pedagógica de escritorio.
No recopila analytics (`gatherUsageStats = false` en `.streamlit/config.toml`).
