# Illapa — Open-Source Reproducible Earthquake-Engineering Lab

**Open-source reproducible earthquake-engineering lab for structural dynamics education — Peru-case (NTE E.030-2018).**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Status: v1.0.0-pending](https://img.shields.io/badge/status-v1.0.0--pending-orange.svg)](CHANGELOG.md)
[![Case Study](https://img.shields.io/badge/case%20study-LAICSEE%202026-blue)](https://huggingface.co/datasets/mikisbell/laicsee-2026)

> Named after **Illapa** (*Qichwa*: the Inca deity of lightning, thunder, and earthquakes), this framework provides an open-source reproducible laboratory for earthquake engineering education — combining OpenSeesPy, Kanai-Tajimi synthetic ground motions, and full compliance with Peru's NTE E.030-2018 seismic code.

> ⚠️ **This repository is under active development.** The v1.0.0 release (scheduled for **2026-05-08**) will include a Zenodo-archived snapshot with a formal DOI. Until then, the code is provisional.

---

## What this is

A reproducible pipeline that bridges classical nonlinear structural dynamics with AI-ready educational datasets, designed for undergraduate earthquake-engineering courses in Latin America. It integrates:

1. **OpenSeesPy** numerical modelling (5-story RC MRF, lumped-plasticity IMK hinges)
2. **Kanai-Tajimi** synthetic ground-motion generator with Saragoni-Hart envelope
3. **NTE E.030-2018** Peruvian seismic code compliance, including the Art. 28.2 inelastic drift amplification (0.75·R = 6.0)
4. **Three complementary analyses:** Monte-Carlo fragility, modal pushover (ASCE 41-17), incremental dynamic analysis (Vamvatsikos & Cornell 2002)
5. **SSOT governance** via a single `config/params.yaml`, SHA-256-sealed COMPUTE manifests, and AI-ready structured outputs

## What this is NOT

- A production-grade seismic design tool (use ETABS, SAP2000, or OpenSees native for that)
- A novel algorithmic contribution (the framework integrates existing methods; it does not invent them)
- A classroom-validated pedagogy (N=1 at this release; classroom pilot planned for v1.1)

## Prerequisites — Python 3.12 required

**OpenSeesPy does not ship working wheels for Python 3.13 on Windows** (verified 2026-04-23). Installing `openseespy` under Python 3.13 on Windows *will* appear to succeed via `pip`, but importing it fails with:

```
RuntimeError: Failed to import openseespy on Windows:
DLL load failed while importing opensees: The specified module could not be found.
```

Use **Python 3.12** for the full CLI pipeline. The web demo (`app/`) runs on 3.13 because it does not depend on OpenSeesPy.

### Install Python 3.12 on Windows

```powershell
# Easiest — winget:
winget install Python.Python.3.12

# Or download installer: https://www.python.org/downloads/release/python-31210/
# Make sure the Python Launcher (`py`) is installed (default checkbox).
```

Verify with `py -3.12 --version` → should print `Python 3.12.x`.

## Quick start

```bash
git clone https://github.com/Mikisbell/illapa.git
cd illapa

# Create the venv with Python 3.12 explicitly (NOT `python -m venv`, which picks 3.13):
py -3.12 -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows
# .venv\Scripts\Activate.ps1    # PowerShell on Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt

# Run the full pipeline (approx. 75 seconds on a commodity laptop)
python examples/rc_5story_peru/run_monte_carlo.py
python examples/rc_5story_peru/run_pushover.py
python examples/rc_5story_peru/run_ida.py
python tools/plot_figures.py --domain structural
```

### Sanity check

```bash
python -c "import openseespy.opensees as ops; ops.wipe(); print('OpenSeesPy OK')"
```

If this prints `OpenSeesPy OK`, the solver is working. If it raises `DLL load failed`, the venv was created with Python 3.13 — delete `.venv` and recreate it with `py -3.12 -m venv .venv`.

All figures and statistics are regenerated locally in the working directory (not shipped with the repo) and sealed with SHA-256 integrity hashes via `tools/generate_compute_manifest.py`.

## 🌐 Web Demo Local

An interactive Streamlit app (**local-only**, no cloud deploy) is shipped under `app/`.
It lets you explore the pushover curve with live sliders and read the LAICSEE 2026
fragility curve pedagogically. The design system is Andean-inspired (terracotta +
turquoise + obsidian on cream), not default Streamlit gray.

```bash
# Works on Python 3.12 AND 3.13 — the web demo does not depend on OpenSeesPy.
pip install -r requirements-web.txt
streamlit run app/main.py
```

Then open `http://localhost:8501`. See [`app/README.md`](app/README.md) for details.

> Why a separate `requirements-web.txt`? The pushover page uses a closed-form
> bilinear ASCE 41-17 surrogate calibrated against the real OpenSeesPy paper
> outputs — so the web demo runs on any Python 3.10+, including 3.13 where
> OpenSeesPy currently has no wheels. The full framework (`requirements.txt`)
> still requires Python 3.12 + OpenSeesPy for the CLI pipeline and IDA.

![Illapa web demo screenshot placeholder](app/assets/screenshot_placeholder.png)

> The screenshot will land here after v1.0.0 is tagged; until then, the image link
> is intentionally unresolved so readers know the demo is the canonical source of
> truth for visuals.

## Case Studies

- **LAICSEE 2026** — Conference paper using this framework to demonstrate E.030-compliant seismic analysis of a 5-story RC building in Lima. [Dataset](https://huggingface.co/datasets/mikisbell/laicsee-2026) · [Paper repo](https://github.com/Mikisbell/laicsee-2026)

## Citation

If you use this framework in academic work, please cite both the paper that introduced it and this code release:

```bibtex
@software{belico_illapa_2026,
  author = {TBD},
  title = {{Illapa: Open-Source Reproducible Earthquake-Engineering Lab}},
  year = {2026},
  version = {v1.0.0},
  doi = {10.5281/zenodo.PENDING},
  url = {https://github.com/Mikisbell/illapa},
  license = {MIT}
}
```

See [`CITATION.cff`](CITATION.cff) for machine-readable citation metadata.

## Philosophy

**Honest disclosure over narrative polish.** The framework ships with seven explicit limitations (shear-type R-derived artifact, NGA-West2 crustal records vs Peru subduction, Kanai-Tajimi mild conservatism, Rayleigh damping choice, N=1 pedagogical benchmark, Δt=0.01s integration step, statistical power = 0.789 below Cohen target). Each is documented in the accompanying paper and in the CHANGELOG. No calibration, no cherry-picking.

## Licence

MIT — see [`LICENSE`](LICENSE).

## Acknowledgements

Built on the OpenSeesPy ecosystem (McKenna 2011; Arroyo et al. 2024) and the PEER NGA-West2 database. Developed as a child project of the [belico-stack](https://github.com/Mikisbell/belico-stack) paper-production framework.

---

**Maintainer:** [@Mikisbell](https://github.com/Mikisbell)
**Contact:** see GitHub profile
**Status page:** [`CHANGELOG.md`](CHANGELOG.md)
