---
skill_id: project-context/analyzer
title: "Analyzer 模块详情"
description: "analyzer 模块的文件、符号、入口点和执行流详情"
triggers:
  - analyzer
  - Analyzer
generated_at: "2026-04-02T13:24:32.625875"
generator: "gitnexus"
---

# Analyzer

294 个符号 | 22 个文件 | 内聚度: 88%

## 使用场景

- 处理 `scripts/`
- 理解 cmd_analyze, cmd_analyze, parse_file 的工作原理
- 修改 analyzer 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `scripts/python/analyzer/knowledge_extractor.py` | KnowledgeExtractor, extract_all, _build_knowledge_base, extract_knowledge, ModelField (+21) |
| `templates/scripts/python/analyzer/knowledge_extractor.py` | ModelField, ModelDefinition, _extract_models, _extract_model_fields, _get_field_type (+21) |
| `scripts/python/analyzer/api_extractor.py` | ApiExtractor, extract_api, ApiParameter, ApiEndpoint, _analyze_route (+19) |
| `templates/scripts/python/analyzer/api_extractor.py` | ApiParameter, _extract_parameters, _extract_function_parameters, _get_type_annotation, _get_call_string (+19) |
| `scripts/python/analyzer/entry_analyzer.py` | EntryAnalyzer, get_entries_summary, analyze_entries, EntryPoint, FunctionCall (+18) |
| `templates/scripts/python/analyzer/entry_analyzer.py` | FunctionCall, BusinessCondition, StateChange, BusinessFlow, _analyze_entry (+18) |
| `scripts/python/analyzer/antipattern_detector.py` | Violation, _detect_file, _detect_code_pattern, _detect_ast_pattern, _detect_print_calls (+17) |
| `templates/scripts/python/analyzer/antipattern_detector.py` | Violation, _detect_file, _detect_code_pattern, _detect_ast_pattern, _detect_print_calls (+17) |
| `scripts/python/analyzer/url_route_extractor.py` | UrlRoute, _parse_route_file, _parse_django_routes, _parse_django_handler, _convert_django_path (+10) |
| `templates/scripts/python/analyzer/url_route_extractor.py` | UrlRoute, _parse_route_file, _parse_django_routes, _parse_django_handler, _convert_django_path (+10) |

## 入口点

探索该模块的起点：

- **`cmd_analyze`** (函数) — `scripts/python/main.py:36`
- **`cmd_analyze`** (函数) — `templates/scripts/python/main.py:36`
- **`parse_file`** (函数) — `scripts/python/parser/base.py:104`
- **`get_file_extensions`** (函数) — `scripts/python/parser/base.py:127`
- **`parse_directory`** (函数) — `scripts/python/parser/base.py:136`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `PythonParser` | 类 | `scripts/python/parser/python_parser.py` | 12 |
| `BaseParser` | 类 | `scripts/python/parser/base.py` | 96 |
| `PatternMiner` | 类 | `scripts/python/miner/pattern_miner.py` | 15 |
| `SkeletonGenerator` | 类 | `scripts/python/analyzer/skeleton_generator.py` | 80 |
| `KnowledgeExtractor` | 类 | `scripts/python/analyzer/knowledge_extractor.py` | 129 |
| `ErrorCodeDefinition` | 类 | `scripts/python/analyzer/errorcode_extractor.py` | 14 |
| `ExceptionClassDefinition` | 类 | `scripts/python/analyzer/errorcode_extractor.py` | 39 |
| `ErrorCodeExtractor` | 类 | `scripts/python/analyzer/errorcode_extractor.py` | 57 |
| `EntryAnalyzer` | 类 | `scripts/python/analyzer/entry_analyzer.py` | 96 |
| `ApiExtractor` | 类 | `scripts/python/analyzer/api_extractor.py` | 55 |
| `ApiSkillGenerator` | 类 | `scripts/python/generator/api_skill_generator.py` | 16 |
| `ApiParameter` | 类 | `scripts/python/analyzer/api_extractor.py` | 19 |
| `ApiEndpoint` | 类 | `scripts/python/analyzer/api_extractor.py` | 33 |
| `Violation` | 类 | `scripts/python/analyzer/antipattern_detector.py` | 25 |
| `ErrorCodeDefinition` | 类 | `templates/scripts/python/analyzer/errorcode_extractor.py` | 14 |
| `ExceptionClassDefinition` | 类 | `templates/scripts/python/analyzer/errorcode_extractor.py` | 39 |
| `ErrorCodeExtractor` | 类 | `templates/scripts/python/analyzer/errorcode_extractor.py` | 57 |
| `Violation` | 类 | `templates/scripts/python/analyzer/antipattern_detector.py` | 25 |
| `SkeletonGenerator` | 类 | `templates/scripts/python/analyzer/skeleton_generator.py` | 80 |
| `ApiParameter` | 类 | `templates/scripts/python/analyzer/api_extractor.py` | 19 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Analyze_entries → _op_to_string` | 跨模块 | 7 |
| `Detect_antipatterns → Violation` | 跨模块 | 6 |
| `Detect_antipatterns → _get_decorator_name` | 跨模块 | 6 |
| `Analyze_entries → _get_call_name` | 跨模块 | 6 |
| `Analyze_entries → FunctionCall` | 跨模块 | 6 |
| `Extract_knowledge → _get_field_type` | 跨模块 | 6 |
| `Extract_knowledge → _is_field_required` | 跨模块 | 6 |
| `Extract_knowledge → _get_field_constraints` | 跨模块 | 6 |
| `Extract_knowledge → _get_field_type` | 跨模块 | 6 |
| `Extract_knowledge → _is_field_required` | 跨模块 | 6 |

## 关联模块

| 模块 | 连接数 |
|------|-------------|
| Miner | 2 次调用 |
| Generator | 2 次调用 |
