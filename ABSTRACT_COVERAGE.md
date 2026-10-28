# Advertised abstract → deck coverage

Each promise in `ADVERTISED_TALK.md` mapped to the slide that pays for it and
the evidence behind it. Re-run date: 2026-10-27.

| # | Promise in the abstract | Slide | Evidence | Status |
|---|---|---|---|---|
| P1 | model extraction from deployed SysML v1 / Cameo | R1: reading v1 as it actually exists | `check_xmi_vehicle.py` R1 rows; `.mdzip` importer | covered |
| P2 | clean-room transformation | Clean-room discipline; R3 mappings | spec-anchored mapping table; `UnmappedFeature` | covered |
| P3 | semantic validation | Validation: sysmlpy is the oracle | 14/14 local checks; element counts | covered, re-run |
| P4 | live Cameo integration | Live Cameo integration | `cameo_sidecar` docs + `~/.cameo_sidecar/audit.log` | covered, **not re-run** (Cameo not running) |
| P5 | connections to analysis tools | Analysis and traceability | `sysmlpy trace`, `diff` re-run | covered, re-run |
| P6 | connections to simulation tools | Simulation: a derived branch | FASSST / MSBSE paper evidence | covered as **release-gated secondhand** |
| P7 | connections to visualization tools | Regenerated views | `render_vehicle_diagrams.py` SVG/PlantUML | covered |
| P8 | connections to automation tools | Automated checking as a CI gate | `sysmlpy ci` re-run | covered, re-run |
| P9 | version control | Version control without the vendor | semantic diff; content hash | covered |
| P10 | reproducible transformations | Reproducible by construction | byte-identical writes; stable-id determinism | covered, re-run |
| P11 | automated checking | Automated checking as a CI gate | `sysmlpy ci` exit codes | covered, re-run |
| P12 | broader model utilization | The wider v2 ecosystem | SysON / Jupyter / LSP | covered |
| P13 | without abandoning existing CM practices | Identity spine and baselines | stable ids; reconcile; manifest | covered, re-run |
| P14 | preserve engineering intent during transformation | Honesty has teeth | not-mapped comments; provenance | covered |
| P15 | generate executable artifacts + analytical evidence | Simulation; Analysis | FASSST determinism; trace report | partial — see below |
| P16 | **feed results back into controlled model evolution** | The loop is not closed yet | none | **NOT implemented — stated as future work** |

## The one promise the work does not yet keep

The abstract's phrase *"feed results back into controlled model evolution with
traceability"* describes a **closed loop**. That return path is not
implemented, and the MSBSE paper plan (`msbse-paper/PLAN.md` §9) explicitly
prohibits claiming it:

> Do not claim: bidirectional transformation; result ingestion into SysML;
> stable trace identifiers; automatic stale-result detection; content-addressed
> study baselines; complete semantic fidelity.

The deck therefore keeps the forward thread as the demonstrated result and
presents the return path as designed-but-unbuilt, on an explicit slide. Do not
restore closed-loop language to the live talk without new evidence.

## Release constraints carried into the deck

- FASSST is GTRI CUI and requires public-release review
  (`msbse-paper/PLAN.md` §8). The slide names **AFSIM only as a release-gated
  context**, leads with the open Gazebo/JSBSim examples, and shows no
  controlled data or program performance.
- `cameo_sidecar` requires the commercial tool, so it is an **integration path,
  not part of the open-only thread** — the same boundary the CSER paper draws.

## Numbers in the deck I could not re-run here

These come from the umlmeta/CSER evidence base and were not reproducible in
this folder (umlmeta checks and external corpora are not vendored here).
Re-confirm against the source repos before presenting:

- "481 checks across 15 suites" (umlmeta aggregate)
- R2 CMOF generation: 175 classes, 319 associations, 623 OCL constraints
- 12/12 `.mdzip` stress corpus imports
- AP242: 28 files / 300,851 instances; XPect 123/123
