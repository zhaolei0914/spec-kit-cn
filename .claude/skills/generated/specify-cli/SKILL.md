---
name: specify-cli
description: "Skill for the Specify_cli area of repo. 29 symbols across 2 files."
---

# Specify_cli

29 symbols | 2 files | Cohesion: 87%

## When to Use

- Working with code in `src/`
- Understanding how attach_refresh, add, start work
- Modifying specify_cli-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/specify_cli/__init__.py` | StepTracker, attach_refresh, add, start, complete (+23) |
| `ecc-components/skills/skill-comply/scripts/run.py` | main |

## Entry Points

Start here when exploring this area:

- **`attach_refresh`** (Function) — `src/specify_cli/__init__.py:254`
- **`add`** (Function) — `src/specify_cli/__init__.py:257`
- **`start`** (Function) — `src/specify_cli/__init__.py:262`
- **`complete`** (Function) — `src/specify_cli/__init__.py:265`
- **`error`** (Function) — `src/specify_cli/__init__.py:268`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `StepTracker` | Class | `src/specify_cli/__init__.py` | 244 |
| `attach_refresh` | Function | `src/specify_cli/__init__.py` | 254 |
| `add` | Function | `src/specify_cli/__init__.py` | 257 |
| `start` | Function | `src/specify_cli/__init__.py` | 262 |
| `complete` | Function | `src/specify_cli/__init__.py` | 265 |
| `error` | Function | `src/specify_cli/__init__.py` | 268 |
| `skip` | Function | `src/specify_cli/__init__.py` | 271 |
| `render` | Function | `src/specify_cli/__init__.py` | 293 |
| `format_help` | Function | `src/specify_cli/__init__.py` | 429 |
| `show_banner` | Function | `src/specify_cli/__init__.py` | 443 |
| `callback` | Function | `src/specify_cli/__init__.py` | 458 |
| `check_tool` | Function | `src/specify_cli/__init__.py` | 483 |
| `is_git_repo` | Function | `src/specify_cli/__init__.py` | 514 |
| `init_git_repo` | Function | `src/specify_cli/__init__.py` | 534 |
| `download_and_extract_template` | Function | `src/specify_cli/__init__.py` | 750 |
| `ensure_executable_scripts` | Function | `src/specify_cli/__init__.py` | 920 |
| `init` | Function | `src/specify_cli/__init__.py` | 965 |
| `check` | Function | `src/specify_cli/__init__.py` | 1267 |
| `main` | Function | `ecc-components/skills/skill-comply/scripts/run.py` | 21 |
| `get_key` | Function | `src/specify_cli/__init__.py` | 329 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Init → _maybe_refresh` | intra_community | 5 |
| `Check → _maybe_refresh` | intra_community | 5 |
| `Download_and_extract_template → Get` | cross_community | 5 |
| `Init → Create_selection_panel` | cross_community | 4 |
| `Init → Get_key` | cross_community | 4 |
| `Main → _maybe_refresh` | intra_community | 4 |
| `Main → Step` | cross_community | 4 |
| `Main → Detector` | cross_community | 4 |
| `Main → ComplianceSpec` | cross_community | 4 |
| `Download_and_extract_template → _maybe_refresh` | intra_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Scripts | 5 calls |
| Generator | 1 calls |
| Tests | 1 calls |

## How to Explore

1. `gitnexus_context({name: "attach_refresh"})` — see callers and callees
2. `gitnexus_query({query: "specify_cli"})` — find related execution flows
3. Read key files listed above for implementation details
