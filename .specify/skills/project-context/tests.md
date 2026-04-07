---
skill_id: project-context/tests
title: "Tests 模块详情"
description: "tests 模块的文件、符号、入口点和执行流详情"
triggers:
  - tests
  - Tests
generated_at: "2026-04-02T13:24:32.633918"
generator: "gitnexus"
---

# Tests

101 个符号 | 14 个文件 | 内聚度: 87%

## 使用场景

- 处理 `ecc-components/`
- 理解 analyze_project, analyze_project, test_analyze_project 的工作原理
- 修改 tests 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `ecc-components/skills/skill-comply/tests/test_grader.py` | test_returns_compliance_result, test_full_compliance, test_all_required_steps_detected, test_optional_step_detected, test_no_hook_promotion_recommended (+12) |
| `scripts/python/tests/test_generators.py` | setUp, create_test_files, create_project_structure, test_django_detection, test_generate_all_windsurf (+7) |
| `templates/scripts/python/tests/test_generators.py` | setUp, create_test_files, create_project_structure, test_django_detection, test_generate_all_windsurf (+7) |
| `ecc-components/skills/skill-comply/tests/test_parser.py` | test_parses_tdd_spec, test_step_fields, test_optional_detector_fields, test_scoring_threshold, test_required_vs_optional_steps (+6) |
| `scripts/python/tests/test_knowledge_base.py` | test_analyze_project, test_extract_classes, test_extract_functions, test_extract_constants, test_django_model_extraction (+3) |
| `templates/scripts/python/tests/test_knowledge_base.py` | test_analyze_project, test_extract_classes, test_extract_functions, test_extract_constants, test_django_model_extraction (+3) |
| `scripts/python/extractor/libcst/knowledge_base.py` | KnowledgeBaseFusion, analyze_project, _collect_python_files, _should_exclude, _analyze_patterns (+3) |
| `scripts/python/generator/windsurf_generator.py` | AgentRulesGenerator, generate_all, generate_rules_md, generate_constitution, _write_file (+2) |
| `ecc-components/skills/skill-comply/scripts/parser.py` | Detector, Step, ComplianceSpec, parse_spec, parse_trace |
| `ecc-components/skills/skill-comply/scripts/grader.py` | StepResult, ComplianceResult, _check_temporal_order, grade |

## 入口点

探索该模块的起点：

- **`analyze_project`** (函数) — `scripts/python/skill_main.py:24`
- **`analyze_project`** (函数) — `templates/scripts/python/skill_main.py:24`
- **`test_analyze_project`** (函数) — `scripts/python/tests/test_knowledge_base.py:118`
- **`test_extract_classes`** (函数) — `scripts/python/tests/test_knowledge_base.py:127`
- **`test_extract_functions`** (函数) — `scripts/python/tests/test_knowledge_base.py:139`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `KnowledgeBaseFusion` | 类 | `scripts/python/extractor/libcst/knowledge_base.py` | 151 |
| `StepResult` | 类 | `ecc-components/skills/skill-comply/scripts/grader.py` | 11 |
| `ComplianceResult` | 类 | `ecc-components/skills/skill-comply/scripts/grader.py` | 19 |
| `AgentRulesGenerator` | 类 | `scripts/python/generator/windsurf_generator.py` | 30 |
| `Detector` | 类 | `ecc-components/skills/skill-comply/scripts/parser.py` | 22 |
| `Step` | 类 | `ecc-components/skills/skill-comply/scripts/parser.py` | 29 |
| `ComplianceSpec` | 类 | `ecc-components/skills/skill-comply/scripts/parser.py` | 37 |
| `SkillGenerator` | 类 | `scripts/python/generator/skill_generator.py` | 389 |
| `analyze_project` | 函数 | `scripts/python/skill_main.py` | 24 |
| `analyze_project` | 函数 | `templates/scripts/python/skill_main.py` | 24 |
| `test_analyze_project` | 函数 | `scripts/python/tests/test_knowledge_base.py` | 118 |
| `test_extract_classes` | 函数 | `scripts/python/tests/test_knowledge_base.py` | 127 |
| `test_extract_functions` | 函数 | `scripts/python/tests/test_knowledge_base.py` | 139 |
| `test_extract_constants` | 函数 | `scripts/python/tests/test_knowledge_base.py` | 149 |
| `test_django_model_extraction` | 函数 | `scripts/python/tests/test_knowledge_base.py` | 160 |
| `test_django_view_extraction` | 函数 | `scripts/python/tests/test_knowledge_base.py` | 171 |
| `setUp` | 函数 | `scripts/python/tests/test_generators.py` | 20 |
| `create_test_files` | 函数 | `scripts/python/tests/test_generators.py` | 35 |
| `create_project_structure` | 函数 | `scripts/python/tests/test_generators.py` | 178 |
| `test_django_detection` | 函数 | `scripts/python/tests/test_generators.py` | 266 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Run_all → Get_bases` | 跨模块 | 6 |
| `Run_all → Get_decorators` | 跨模块 | 6 |
| `Run_all → Get_docstring` | 跨模块 | 6 |
| `Run_all → Get_node_source` | 跨模块 | 6 |
| `Run_all → Get_bases` | 跨模块 | 6 |
| `Run_all → Get_decorators` | 跨模块 | 6 |
| `Run_all → Get_docstring` | 跨模块 | 6 |
| `Run_all → Get_node_source` | 跨模块 | 6 |
| `Main → _should_exclude` | 跨模块 | 5 |
| `Main → _get_file_hash` | 跨模块 | 5 |

## 关联模块

| 模块 | 连接数 |
|------|-------------|
| Libcst | 3 次调用 |
| Scripts | 1 次调用 |
