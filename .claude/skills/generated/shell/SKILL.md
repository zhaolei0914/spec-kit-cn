---
name: shell
description: "Skill for the Shell area of repo. 8 symbols across 3 files."
---

# Shell

8 symbols | 3 files | Cohesion: 74%

## When to Use

- Working with code in `scripts/`
- Understanding how analyze_project, generate_skills, run_all work
- Modifying shell-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/shell/skill_main.py` | analyze_project, generate_skills, run_all, main |
| `scripts/shell/extractor/fusion.py` | to_dict, save, ShellKnowledgeBaseFusion |
| `scripts/shell/generator/skill_generator.py` | ShellSkillGenerator |

## Entry Points

Start here when exploring this area:

- **`analyze_project`** (Function) — `scripts/shell/skill_main.py:21`
- **`generate_skills`** (Function) — `scripts/shell/skill_main.py:56`
- **`run_all`** (Function) — `scripts/shell/skill_main.py:86`
- **`main`** (Function) — `scripts/shell/skill_main.py:153`
- **`to_dict`** (Function) — `scripts/shell/extractor/fusion.py:41`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `ShellSkillGenerator` | Class | `scripts/shell/generator/skill_generator.py` | 178 |
| `ShellKnowledgeBaseFusion` | Class | `scripts/shell/extractor/fusion.py` | 124 |
| `analyze_project` | Function | `scripts/shell/skill_main.py` | 21 |
| `generate_skills` | Function | `scripts/shell/skill_main.py` | 56 |
| `run_all` | Function | `scripts/shell/skill_main.py` | 86 |
| `main` | Function | `scripts/shell/skill_main.py` | 153 |
| `to_dict` | Function | `scripts/shell/extractor/fusion.py` | 41 |
| `save` | Function | `scripts/shell/extractor/fusion.py` | 83 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → ShellKnowledgeBase` | cross_community | 4 |
| `Main → ShellFunctionExtractor` | cross_community | 4 |
| `Main → ShellVariableExtractor` | cross_community | 4 |
| `Main → ShellCommentExtractor` | cross_community | 4 |
| `Main → To_dict` | intra_community | 4 |
| `Generate_skills → Get` | cross_community | 4 |
| `Generate_skills → _format_principles` | cross_community | 4 |
| `Generate_skills → _write_file` | cross_community | 4 |
| `Run_all → ShellKnowledgeBase` | cross_community | 3 |
| `Run_all → ShellFunctionExtractor` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Generator | 4 calls |
| Extractor | 2 calls |
| Scripts | 1 calls |

## How to Explore

1. `gitnexus_context({name: "analyze_project"})` — see callers and callees
2. `gitnexus_query({query: "shell"})` — find related execution flows
3. Read key files listed above for implementation details
