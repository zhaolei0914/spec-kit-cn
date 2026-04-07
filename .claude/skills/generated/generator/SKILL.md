---
name: generator
description: "Skill for the Generator area of repo. 156 symbols across 23 files."
---

# Generator

156 symbols | 23 files | Cohesion: 59%

## When to Use

- Working with code in `scripts/`
- Understanding how download_template_from_github, version, from_dict work
- Modifying generator-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/python/generator/skill_generator.py` | _select_model_examples, _find_decorator_import, _get_decorator_description, __init__, _analyze (+33) |
| `scripts/python/generator/project_context_generator.py` | _get_project_info, _get_unit_statistics, _group_examples_by_service, _generate_skill_md, _generate_models_md (+21) |
| `scripts/shell/generator/skill_generator.py` | __init__, _analyze, _analyze_function_naming, _analyze_variable_naming, _analyze_logging_functions (+16) |
| `scripts/python/generator/api_skill_generator.py` | _generate_single_endpoint_doc, _get_example_value, _generate_response_example, _generate_endpoint_doc, ApiSkillGenerator (+11) |
| `scripts/python/generator/cluster_doc_generator.py` | _generate_examples_section, _group_examples_by_service, _extract_service_name, _extract_code, _read_code_block (+4) |
| `scripts/python/generator/windsurf_generator.py` | __init__, AgentRulesGenerator, generate_all, generate_rules, generate_rules_md (+3) |
| `src/specify_cli/__init__.py` | _github_token, _github_auth_headers, _parse_rate_limit_headers, _format_rate_limit_error, download_template_from_github (+1) |
| `scripts/python/tests/test_extractors.py` | test_inherited_class, test_decorated_class, test_async_function, test_simple_model, test_class_based_view |
| `scripts/python/tests/test_generators.py` | test_generate_rules, test_generate_all_windsurf, test_generate_all_claude, test_generate_all_cursor, test_full_pipeline |
| `scripts/python/extractor/base.py` | from_dict, get, calculate_confidence, determine_priority |

## Entry Points

Start here when exploring this area:

- **`download_template_from_github`** (Function) — `src/specify_cli/__init__.py:636`
- **`version`** (Function) — `src/specify_cli/__init__.py:1309`
- **`from_dict`** (Function) — `scripts/shell/extractor/fusion.py:63`
- **`from_dict`** (Function) — `scripts/shell/extractor/base.py:70`
- **`test_inherited_class`** (Function) — `scripts/python/tests/test_extractors.py:50`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `AgentRulesGenerator` | Class | `scripts/python/generator/windsurf_generator.py` | 30 |
| `ApiSkillGenerator` | Class | `scripts/python/generator/api_skill_generator.py` | 16 |
| `ClusterDocGenerator` | Class | `scripts/python/generator/cluster_doc_generator.py` | 11 |
| `SkillMetadata` | Class | `scripts/python/generator/skill_generator.py` | 20 |
| `ProjectPatterns` | Class | `scripts/python/generator/skill_generator.py` | 45 |
| `ProjectContextGenerator` | Class | `scripts/python/generator/project_context_generator.py` | 16 |
| `ShellProjectPatterns` | Class | `scripts/shell/generator/skill_generator.py` | 17 |
| `download_template_from_github` | Function | `src/specify_cli/__init__.py` | 636 |
| `version` | Function | `src/specify_cli/__init__.py` | 1309 |
| `from_dict` | Function | `scripts/shell/extractor/fusion.py` | 63 |
| `from_dict` | Function | `scripts/shell/extractor/base.py` | 70 |
| `test_inherited_class` | Function | `scripts/python/tests/test_extractors.py` | 50 |
| `test_decorated_class` | Function | `scripts/python/tests/test_extractors.py` | 61 |
| `test_async_function` | Function | `scripts/python/tests/test_extractors.py` | 109 |
| `test_simple_model` | Function | `scripts/python/tests/test_extractors.py` | 255 |
| `test_class_based_view` | Function | `scripts/python/tests/test_extractors.py` | 287 |
| `from_dict` | Function | `scripts/python/parser/base.py` | 38 |
| `get_by_type` | Function | `scripts/python/extractor/fusion.py` | 77 |
| `from_dict` | Function | `scripts/python/extractor/base.py` | 98 |
| `get` | Function | `scripts/python/extractor/base.py` | 211 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Analyze_entries → Get` | cross_community | 7 |
| `Download_and_extract_template → Get` | cross_community | 5 |
| `Cmd_evolve → Parse_instinct_file` | cross_community | 5 |
| `Generate_agent_rules → Get` | cross_community | 5 |
| `Main → Get` | cross_community | 5 |
| `Convert_patterns_to_skills → Get` | cross_community | 5 |
| `Visit_Assign → Get` | cross_community | 5 |
| `Visit_AugAssign → Get` | cross_community | 5 |
| `_generate_test_md → Get` | cross_community | 5 |
| `_generate_test_md → _extract_service_name` | cross_community | 5 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Scripts | 5 calls |
| Analyzer | 2 calls |
| Tests | 2 calls |
| Specify_cli | 1 calls |
| Parser | 1 calls |
| Python | 1 calls |

## How to Explore

1. `gitnexus_context({name: "download_template_from_github"})` — see callers and callees
2. `gitnexus_query({query: "generator"})` — find related execution flows
3. Read key files listed above for implementation details
