---
skill_id: project-context/generator
title: "Generator 模块详情"
description: "generator 模块的文件、符号、入口点和执行流详情"
triggers:
  - generator
  - Generator
generated_at: "2026-04-02T13:24:32.628402"
generator: "gitnexus"
---

# Generator

210 个符号 | 11 个文件 | 内聚度: 92%

## 使用场景

- 处理 `templates/`
- 理解 to_yaml_header, get_import_for, generate_all 的工作原理
- 修改 generator 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `scripts/python/generator/skill_generator.py` | SkillMetadata, to_yaml_header, ProjectPatterns, get_import_for, generate_all (+30) |
| `templates/scripts/python/generator/skill_generator.py` | SkillMetadata, to_yaml_header, ProjectPatterns, get_import_for, generate_all (+30) |
| `templates/scripts/python/generator/project_context_generator.py` | _get_project_info, _get_cluster_patterns, _get_cluster_examples, _get_unit_statistics, _group_examples_by_service (+19) |
| `scripts/python/generator/project_context_generator.py` | _get_project_info, _get_cluster_patterns, _get_cluster_examples, _get_unit_statistics, _group_examples_by_service (+16) |
| `scripts/shell/generator/skill_generator.py` | __init__, _analyze, _analyze_function_naming, _analyze_variable_naming, _analyze_logging_functions (+16) |
| `templates/scripts/shell/generator/skill_generator.py` | __init__, _analyze, _analyze_function_naming, _analyze_variable_naming, _analyze_logging_functions (+16) |
| `templates/scripts/python/generator/api_skill_generator.py` | ApiSkillGenerator, generate, _detect_service_name, _detect_base_url, _group_by_module (+10) |
| `scripts/python/generator/api_skill_generator.py` | generate, _detect_service_name, _detect_base_url, _group_by_module, _normalize_module_name (+9) |
| `scripts/python/generator/cluster_doc_generator.py` | ClusterDocGenerator, generate_cluster_doc, _generate_pattern_tables, _generate_recommendations, _generate_examples_section (+4) |
| `templates/scripts/python/generator/cluster_doc_generator.py` | ClusterDocGenerator, generate_cluster_doc, _generate_pattern_tables, _generate_recommendations, _generate_examples_section (+4) |

## 入口点

探索该模块的起点：

- **`to_yaml_header`** (函数) — `scripts/python/generator/skill_generator.py:33`
- **`get_import_for`** (函数) — `scripts/python/generator/skill_generator.py:102`
- **`generate_all`** (函数) — `scripts/python/generator/skill_generator.py:405`
- **`generate_project_overview`** (函数) — `scripts/python/generator/skill_generator.py:530`
- **`generate_web_skill`** (函数) — `scripts/python/generator/skill_generator.py:652`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `SkillMetadata` | 类 | `scripts/python/generator/skill_generator.py` | 20 |
| `ProjectPatterns` | 类 | `scripts/python/generator/skill_generator.py` | 45 |
| `SkillMetadata` | 类 | `templates/scripts/python/generator/skill_generator.py` | 20 |
| `ProjectPatterns` | 类 | `templates/scripts/python/generator/skill_generator.py` | 45 |
| `ApiSkillGenerator` | 类 | `templates/scripts/python/generator/api_skill_generator.py` | 16 |
| `ShellProjectPatterns` | 类 | `scripts/shell/generator/skill_generator.py` | 17 |
| `ClusterDocGenerator` | 类 | `scripts/python/generator/cluster_doc_generator.py` | 11 |
| `ClusterDocGenerator` | 类 | `templates/scripts/python/generator/cluster_doc_generator.py` | 11 |
| `ShellProjectPatterns` | 类 | `templates/scripts/shell/generator/skill_generator.py` | 17 |
| `ProjectContextGenerator` | 类 | `templates/scripts/python/generator/project_context_generator.py` | 16 |
| `to_yaml_header` | 函数 | `scripts/python/generator/skill_generator.py` | 33 |
| `get_import_for` | 函数 | `scripts/python/generator/skill_generator.py` | 102 |
| `generate_all` | 函数 | `scripts/python/generator/skill_generator.py` | 405 |
| `generate_project_overview` | 函数 | `scripts/python/generator/skill_generator.py` | 530 |
| `generate_web_skill` | 函数 | `scripts/python/generator/skill_generator.py` | 652 |
| `generate_models_skill` | 函数 | `scripts/python/generator/skill_generator.py` | 865 |
| `generate_error_skill` | 函数 | `scripts/python/generator/skill_generator.py` | 1070 |
| `generate_constants_skill` | 函数 | `scripts/python/generator/skill_generator.py` | 1184 |
| `generate_imports_skill` | 函数 | `scripts/python/generator/skill_generator.py` | 1291 |
| `generate_decorators_skill` | 函数 | `scripts/python/generator/skill_generator.py` | 1374 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Main → _detect_service_name` | 跨模块 | 4 |
| `Main → _detect_service_name` | 跨模块 | 4 |
| `Main → ShellProjectPatterns` | 跨模块 | 4 |
| `Main → ShellProjectPatterns` | 跨模块 | 4 |
| `Cmd_api_skill → _normalize_module_name` | 跨模块 | 4 |
| `Cmd_api_skill → _generate_endpoint_id` | 跨模块 | 4 |
| `Cmd_api_skill → _get_common_errors` | 跨模块 | 4 |
| `Cmd_api_skill → _normalize_module_name` | 跨模块 | 4 |
| `Cmd_api_skill → _generate_endpoint_id` | 跨模块 | 4 |
| `Cmd_api_skill → _get_common_errors` | 跨模块 | 4 |

## 关联模块

| 模块 | 连接数 |
|------|-------------|
| Analyzer | 1 次调用 |
