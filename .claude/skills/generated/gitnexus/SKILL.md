---
name: gitnexus
description: "Skill for the Gitnexus area of repo. 41 symbols across 2 files."
---

# Gitnexus

41 symbols | 2 files | Cohesion: 82%

## When to Use

- Working with code in `scripts/`
- Understanding how detect_all, collect_project_facts, save_context_facts work
- Modifying gitnexus-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/docker/gitnexus/gitnexus_to_skill.py` | detect_all, _collect_code_files, _read_samples, _detect_naming, _classify_naming (+28) |
| `scripts/docker/gitnexus/context_drift_detector.py` | load_facts, get_git_changes, detect_language_drift, detect_dependency_drift, detect_structure_drift (+3) |

## Entry Points

Start here when exploring this area:

- **`detect_all`** (Function) — `scripts/docker/gitnexus/gitnexus_to_skill.py:190`
- **`collect_project_facts`** (Function) — `scripts/docker/gitnexus/gitnexus_to_skill.py:795`
- **`save_context_facts`** (Function) — `scripts/docker/gitnexus/gitnexus_to_skill.py:902`
- **`load_gitnexus_meta`** (Function) — `scripts/docker/gitnexus/gitnexus_to_skill.py:915`
- **`load_gitnexus_skills`** (Function) — `scripts/docker/gitnexus/gitnexus_to_skill.py:924`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `CodePatternDetector` | Class | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 159 |
| `detect_all` | Function | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 190 |
| `collect_project_facts` | Function | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 795 |
| `save_context_facts` | Function | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 902 |
| `load_gitnexus_meta` | Function | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 915 |
| `load_gitnexus_skills` | Function | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 924 |
| `parse_skill_md` | Function | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 945 |
| `translate_to_chinese` | Function | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 1414 |
| `generate_module_skill` | Function | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 1465 |
| `generate_index_yaml` | Function | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 1500 |
| `convert` | Function | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 1558 |
| `scan_project` | Function | `scripts/docker/gitnexus/gitnexus_to_skill.py` | 556 |
| `load_facts` | Function | `scripts/docker/gitnexus/context_drift_detector.py` | 33 |
| `get_git_changes` | Function | `scripts/docker/gitnexus/context_drift_detector.py` | 41 |
| `detect_language_drift` | Function | `scripts/docker/gitnexus/context_drift_detector.py` | 133 |
| `detect_dependency_drift` | Function | `scripts/docker/gitnexus/context_drift_detector.py` | 182 |
| `detect_structure_drift` | Function | `scripts/docker/gitnexus/context_drift_detector.py` | 211 |
| `detect_config_drift` | Function | `scripts/docker/gitnexus/context_drift_detector.py` | 248 |
| `compute_drift_score` | Function | `scripts/docker/gitnexus/context_drift_detector.py` | 277 |
| `detect_drift` | Function | `scripts/docker/gitnexus/context_drift_detector.py` | 307 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Collect_project_facts → _add_unique` | cross_community | 5 |
| `Convert → _add_unique` | cross_community | 5 |
| `Main → Get` | cross_community | 5 |
| `Main → _add_unique` | cross_community | 5 |
| `Main → _classify_naming` | cross_community | 5 |
| `Collect_project_facts → Get` | cross_community | 4 |
| `Collect_project_facts → _classify_naming` | cross_community | 4 |
| `Main → Get` | cross_community | 4 |
| `Main → _collect_code_files` | cross_community | 4 |
| `Main → _read_samples` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Generator | 12 calls |

## How to Explore

1. `gitnexus_context({name: "detect_all"})` — see callers and callees
2. `gitnexus_query({query: "gitnexus"})` — find related execution flows
3. Read key files listed above for implementation details
