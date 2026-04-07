---
name: analyzer
description: "Skill for the Analyzer area of repo. 140 symbols across 9 files."
---

# Analyzer

140 symbols | 9 files | Cohesion: 82%

## When to Use

- Working with code in `scripts/`
- Understanding how extract, extract_error_codes, cmd_api_skill work
- Modifying analyzer-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/python/analyzer/knowledge_extractor.py` | ModelField, ModelDefinition, _extract_models, _extract_model_fields, _get_field_type (+21) |
| `scripts/python/analyzer/api_extractor.py` | ApiEndpoint, _analyze_route, _find_handler, _analyze_class_handler, _analyze_function_handler (+19) |
| `scripts/python/analyzer/entry_analyzer.py` | BusinessFlow, _analyze_entry, _analyze_function, _trace_calls, _get_call_name (+18) |
| `scripts/python/analyzer/antipattern_detector.py` | Violation, _detect_file, _detect_code_pattern, _detect_ast_pattern, _detect_print_calls (+17) |
| `scripts/python/analyzer/url_route_extractor.py` | UrlRoute, _parse_route_file, _parse_django_routes, _parse_django_handler, _convert_django_path (+8) |
| `scripts/python/analyzer/skeleton_generator.py` | SkeletonGenerator, generate, _detect_project_info, _detect_framework, _detect_services (+7) |
| `scripts/python/analyzer/errorcode_extractor.py` | ErrorCodeDefinition, ExceptionClassDefinition, ErrorCodeExtractor, extract, _find_errorcode_files (+6) |
| `scripts/python/analyzer/business_rule_generator.py` | BusinessRuleGenerator, generate, _generate_entry_filename, _generate_single_entry_doc, _generate_summary (+2) |
| `scripts/python/main.py` | cmd_api_skill, cmd_business_rules |

## Entry Points

Start here when exploring this area:

- **`extract`** (Function) — `scripts/python/analyzer/errorcode_extractor.py:80`
- **`extract_error_codes`** (Function) — `scripts/python/analyzer/errorcode_extractor.py:289`
- **`cmd_api_skill`** (Function) — `scripts/python/main.py:180`
- **`generate`** (Function) — `scripts/python/analyzer/skeleton_generator.py:86`
- **`generate_skeleton`** (Function) — `scripts/python/analyzer/skeleton_generator.py:370`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `ErrorCodeDefinition` | Class | `scripts/python/analyzer/errorcode_extractor.py` | 14 |
| `ExceptionClassDefinition` | Class | `scripts/python/analyzer/errorcode_extractor.py` | 39 |
| `ErrorCodeExtractor` | Class | `scripts/python/analyzer/errorcode_extractor.py` | 57 |
| `Violation` | Class | `scripts/python/analyzer/antipattern_detector.py` | 25 |
| `ApiEndpoint` | Class | `scripts/python/analyzer/api_extractor.py` | 33 |
| `SkeletonGenerator` | Class | `scripts/python/analyzer/skeleton_generator.py` | 80 |
| `ApiParameter` | Class | `scripts/python/analyzer/api_extractor.py` | 19 |
| `UrlRoute` | Class | `scripts/python/analyzer/url_route_extractor.py` | 15 |
| `UrlRouteExtractor` | Class | `scripts/python/analyzer/url_route_extractor.py` | 30 |
| `ApiExtractor` | Class | `scripts/python/analyzer/api_extractor.py` | 55 |
| `ModelField` | Class | `scripts/python/analyzer/knowledge_extractor.py` | 50 |
| `ModelDefinition` | Class | `scripts/python/analyzer/knowledge_extractor.py` | 71 |
| `BusinessFlow` | Class | `scripts/python/analyzer/entry_analyzer.py` | 78 |
| `ConstantDefinition` | Class | `scripts/python/analyzer/knowledge_extractor.py` | 27 |
| `ImportPattern` | Class | `scripts/python/analyzer/knowledge_extractor.py` | 94 |
| `LogPattern` | Class | `scripts/python/analyzer/knowledge_extractor.py` | 111 |
| `EntryAnalyzer` | Class | `scripts/python/analyzer/entry_analyzer.py` | 96 |
| `BusinessRuleGenerator` | Class | `scripts/python/analyzer/business_rule_generator.py` | 15 |
| `AntipatternDetector` | Class | `scripts/python/analyzer/antipattern_detector.py` | 96 |
| `EntryPoint` | Class | `scripts/python/analyzer/entry_analyzer.py` | 22 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Analyze_entries → _get_call_name` | cross_community | 7 |
| `Analyze_entries → Get` | cross_community | 7 |
| `Detect_antipatterns → Violation` | cross_community | 6 |
| `Detect_antipatterns → _get_decorator_name` | cross_community | 6 |
| `Extract_knowledge → _get_field_type` | cross_community | 6 |
| `Extract_knowledge → _is_field_required` | cross_community | 6 |
| `Analyze_entries → FunctionCall` | cross_community | 6 |
| `_analyze_function_handler → _expr_to_string` | cross_community | 6 |
| `Extract_knowledge → _is_constant_name` | cross_community | 5 |
| `Extract_knowledge → _get_value_info` | cross_community | 5 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Generator | 11 calls |
| Parser | 5 calls |

## How to Explore

1. `gitnexus_context({name: "extract"})` — see callers and callees
2. `gitnexus_query({query: "analyzer"})` — find related execution flows
3. Read key files listed above for implementation details
