---
name: python
description: "Skill for the Python area of repo. 7 symbols across 3 files."
---

# Python

7 symbols | 3 files | Cohesion: 58%

## When to Use

- Working with code in `scripts/`
- Understanding how generate_skills, run_all, main work
- Modifying python-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/python/skill_main.py` | generate_skills, run_all, main |
| `scripts/python/tests/test_generators.py` | test_generate_all, test_skill_content, test_models_skill |
| `scripts/python/generator/skill_generator.py` | SkillGenerator |

## Entry Points

Start here when exploring this area:

- **`generate_skills`** (Function) — `scripts/python/skill_main.py:58`
- **`run_all`** (Function) — `scripts/python/skill_main.py:104`
- **`main`** (Function) — `scripts/python/skill_main.py:241`
- **`test_generate_all`** (Function) — `scripts/python/tests/test_generators.py:63`
- **`test_skill_content`** (Function) — `scripts/python/tests/test_generators.py:75`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `SkillGenerator` | Class | `scripts/python/generator/skill_generator.py` | 389 |
| `generate_skills` | Function | `scripts/python/skill_main.py` | 58 |
| `run_all` | Function | `scripts/python/skill_main.py` | 104 |
| `main` | Function | `scripts/python/skill_main.py` | 241 |
| `test_generate_all` | Function | `scripts/python/tests/test_generators.py` | 63 |
| `test_skill_content` | Function | `scripts/python/tests/test_generators.py` | 75 |
| `test_models_skill` | Function | `scripts/python/tests/test_generators.py` | 91 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_all → Get_bases` | cross_community | 6 |
| `Run_all → Get_decorators` | cross_community | 6 |
| `Run_all → Get_docstring` | cross_community | 6 |
| `Run_all → Get_node_source` | cross_community | 6 |
| `Main → _should_exclude` | cross_community | 5 |
| `Main → _get_file_hash` | cross_community | 5 |
| `Main → KnowledgeBase` | cross_community | 4 |
| `Run_all → _should_exclude` | cross_community | 4 |
| `Run_all → _get_file_hash` | cross_community | 4 |
| `Run_all → ExtractorResult` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Generator | 4 calls |
| Tests | 3 calls |
| Scripts | 1 calls |
| Validator | 1 calls |

## How to Explore

1. `gitnexus_context({name: "generate_skills"})` — see callers and callees
2. `gitnexus_query({query: "python"})` — find related execution flows
3. Read key files listed above for implementation details
