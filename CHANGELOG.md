# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] - v1.0.0-pending

### In progress

- Extraction of framework code from `belico-stack` child project `laicsee-2026`
- Generalization of hardcoded LAICSEE-specific parameters to configurable SSOT
- Test suite for CI (pytest + property-based with hypothesis)
- Documentation: architecture overview, API reference, tutorial notebooks
- First real-laptop reproduction run from `git clone` to `plot_figures` in < 10 min

### Planned for v1.0.0 (release target: 2026-05-08)

- **Core modules** (`src/physics/`):
  - `torture_chamber.py` — OpenSeesPy wrapper for MDOF shear-type models
  - `peer_adapter.py` — NGA-West2 AT2 file parser
  - `spectral_engine.py` — Response spectra computation
  - `cross_validation.py` — Verification & validation framework
  - `models/` — SSOT parameter loaders
- **Examples** (`examples/rc_5story_peru/`):
  - `run_monte_carlo.py` — 500-record Kanai-Tajimi fragility campaign
  - `run_pushover.py` — ASCE 41-17 modal pushover
  - `run_ida.py` — Incremental Dynamic Analysis (14 records × 8 IM)
- **Tooling** (`tools/`):
  - `plot_figures.py` — Publication-grade figures (quartile-aware error bars)
  - `generate_compute_manifest.py` — SHA-256 integrity sealing
  - `preflight_statistics.py` — Power analysis + assumption checks
  - `select_ground_motions.py` — PEER record selection by ASCE 7 criteria
  - `peer_downloader.py` — PEER NGA-West2 curl-based fetcher
- **Config** (`config/`):
  - `params.example.yaml` — SSOT template (generic, parameterizable)
  - `domains/structural.yaml` — Domain descriptor
- **Documentation** (`docs/`):
  - `ARCHITECTURE.md` — System overview
  - `TUTORIAL.md` — Step-by-step reproduction walkthrough
  - `API.md` — Module-level API reference

### Known limitations (design decisions, not bugs)

- **L1:** Shear-type 1-DOF-per-story idealisation; R_derived falls short of code R for ductile MRF due to model, not physics
- **L2:** NGA-West2 records are shallow-crustal; Peru subduction (NGA-Sub) excluded pending institutional access
- **L3:** Kanai-Tajimi synthetic is mildly conservative vs real records (Cohen's d ≈ 0.29)
- **L4:** Rayleigh damping tuned to 5% on first two modes (Caughey and tangent-proportional available as SSOT knobs)
- **L5:** N=1 pedagogical benchmark at v1.0.0; classroom pilot N≥20 planned for v1.1
- **L6:** Δt = 0.01 s integration step is at coarse end of T1/20 guideline; Δt = 0.005 s available as SSOT knob
- **L7:** Statistical power = 0.789 at Cohen's d = 0.5, α = 0.05 — marginally below 0.80 convention

### Scheduled for v1.1 (LACCEI 2027)

- 2-D fiber-section MRF (Concrete04 + Steel02) to close L1 and recover code-consistent R envelope
- NGA-Sub subduction records integration (L2)
- Δt = 0.005 s convergence sensitivity study (L6)
- Classroom pilot with N ≥ 20 students + SAP2000/ETABS control (L5)
- Helmholtz-PINN surrogate training as optional pedagogical extension

---

## How this project relates to belico-stack

This framework is a curated earthquake-engineering slice extracted from the [belico-stack](https://github.com/Mikisbell/belico-stack) multi-domain paper-production system. Code originates from the `laicsee-2026` child project and has been generalized for standalone use.
