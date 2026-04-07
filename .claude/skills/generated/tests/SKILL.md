---
name: tests
description: "Skill for the Tests area of repo. 60 symbols across 9 files."
---

# Tests

60 symbols | 9 files | Cohesion: 88%

## When to Use

- Working with code in `ecc-components/`
- Understanding how grade, classify_events, test_returns_compliance_result work
- Modifying tests-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `ecc-components/skills/skill-comply/tests/test_grader.py` | test_returns_compliance_result, test_full_compliance, test_all_required_steps_detected, test_optional_step_detected, test_no_hook_promotion_recommended (+12) |
| `ecc-components/skills/skill-comply/tests/test_parser.py` | test_parses_tdd_spec, test_step_fields, test_optional_detector_fields, test_scoring_threshold, test_required_vs_optional_steps (+6) |
| `scripts/python/tests/test_knowledge_base.py` | test_analyze_project, test_extract_classes, test_extract_functions, test_extract_constants, test_django_model_extraction (+3) |
| `scripts/python/extractor/libcst/knowledge_base.py` | KnowledgeBaseFusion, analyze_project, _collect_python_files, _should_exclude, _analyze_patterns (+3) |
| `ecc-components/skills/skill-comply/scripts/parser.py` | Detector, Step, ComplianceSpec, parse_spec, parse_trace |
| `ecc-components/skills/skill-comply/scripts/grader.py` | StepResult, ComplianceResult, _check_temporal_order, grade |
| `scripts/python/tests/test_generators.py` | setUp, create_test_files, create_project_structure, test_django_detection |
| `ecc-components/skills/skill-comply/scripts/classifier.py` | classify_events, _parse_classification |
| `scripts/python/skill_main.py` | analyze_project |

## Entry Points

Start here when exploring this area:

- **`grade`** (Function) — `ecc-components/skills/skill-comply/scripts/grader.py:61`
- **`classify_events`** (Function) — `ecc-components/skills/skill-comply/scripts/classifier.py:16`
- **`test_returns_compliance_result`** (Function) — `ecc-components/skills/skill-comply/tests/test_grader.py:54`
- **`test_full_compliance`** (Function) — `ecc-components/skills/skill-comply/tests/test_grader.py:59`
- **`test_all_required_steps_detected`** (Function) — `ecc-components/skills/skill-comply/tests/test_grader.py:64`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `StepResult` | Class | `ecc-components/skills/skill-comply/scripts/grader.py` | 11 |
| `ComplianceResult` | Class | `ecc-components/skills/skill-comply/scripts/grader.py` | 19 |
| `KnowledgeBaseFusion` | Class | `scripts/python/extractor/libcst/knowledge_base.py` | 151 |
| `Detector` | Class | `ecc-components/skills/skill-comply/scripts/parser.py` | 22 |
| `Step` | Class | `ecc-components/skills/skill-comply/scripts/parser.py` | 29 |
| `ComplianceSpec` | Class | `ecc-components/skills/skill-comply/scripts/parser.py` | 37 |
| `grade` | Function | `ecc-components/skills/skill-comply/scripts/grader.py` | 61 |
| `classify_events` | Function | `ecc-components/skills/skill-comply/scripts/classifier.py` | 16 |
| `test_returns_compliance_result` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 54 |
| `test_full_compliance` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 59 |
| `test_all_required_steps_detected` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 64 |
| `test_optional_step_detected` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 71 |
| `test_no_hook_promotion_recommended` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 77 |
| `test_step_evidence_not_empty` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 82 |
| `test_low_compliance` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 91 |
| `test_write_test_fails_ordering` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 96 |
| `test_run_test_red_not_detected` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 103 |
| `test_hook_promotion_recommended` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 109 |
| `test_failure_reasons_present` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 114 |
| `test_empty_trace` | Function | `ecc-components/skills/skill-comply/tests/test_grader.py` | 123 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_all → Get_bases` | cross_community | 6 |
| `Run_all → Get_decorators` | cross_community | 6 |
| `Run_all → Get_docstring` | cross_community | 6 |
| `Run_all → Get_node_source` | cross_community | 6 |
| `Analyze_project → Get_bases` | cross_community | 6 |
| `Analyze_project → Get_decorators` | cross_community | 6 |
| `Analyze_project → Get_docstring` | cross_community | 6 |
| `Analyze_project → Get_node_source` | cross_community | 6 |
| `Main → _should_exclude` | cross_community | 5 |
| `Main → _get_file_hash` | cross_community | 5 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Generator | 9 calls |
| Libcst | 3 calls |
| Scripts | 1 calls |

## How to Explore

1. `gitnexus_context({name: "grade"})` — see callers and callees
2. `gitnexus_query({query: "tests"})` — find related execution flows
3. Read key files listed above for implementation details
