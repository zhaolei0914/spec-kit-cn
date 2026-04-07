---
skill_id: project-context/validator
title: "Validator 模块详情"
description: "validator 模块的文件、符号、入口点和执行流详情"
triggers:
  - validator
  - Validator
generated_at: "2026-04-02T13:24:32.634515"
generator: "gitnexus"
---

# Validator

60 个符号 | 6 个文件 | 内聚度: 90%

## 使用场景

- 处理 `scripts/`
- 理解 add_error, add_warning, add_info 的工作原理
- 修改 validator 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `scripts/python/validator/skill_validator.py` | ValidationIssue, ValidationResult, add_error, add_warning, add_info (+12) |
| `templates/scripts/python/validator/skill_validator.py` | ValidationIssue, ValidationResult, add_error, add_warning, add_info (+12) |
| `scripts/python/validator/conflict_detector.py` | ConflictItem, ConflictReport, detect_conflicts, _load_skills, _parse_skill (+5) |
| `templates/scripts/python/validator/conflict_detector.py` | ConflictItem, ConflictReport, detect_conflicts, _load_skills, _parse_skill (+5) |
| `scripts/python/skill_main.py` | generate_skills, validate_skills, main |
| `templates/scripts/python/skill_main.py` | generate_skills, validate_skills, main |

## 入口点

探索该模块的起点：

- **`add_error`** (函数) — `scripts/python/validator/skill_validator.py:40`
- **`add_warning`** (函数) — `scripts/python/validator/skill_validator.py:50`
- **`add_info`** (函数) — `scripts/python/validator/skill_validator.py:59`
- **`merge`** (函数) — `scripts/python/validator/skill_validator.py:75`
- **`validate_skill_file`** (函数) — `scripts/python/validator/skill_validator.py:134`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `ValidationIssue` | 类 | `scripts/python/validator/skill_validator.py` | 23 |
| `ValidationResult` | 类 | `scripts/python/validator/skill_validator.py` | 33 |
| `ValidationIssue` | 类 | `templates/scripts/python/validator/skill_validator.py` | 23 |
| `ValidationResult` | 类 | `templates/scripts/python/validator/skill_validator.py` | 33 |
| `ConflictItem` | 类 | `scripts/python/validator/conflict_detector.py` | 15 |
| `ConflictReport` | 类 | `scripts/python/validator/conflict_detector.py` | 27 |
| `ConflictItem` | 类 | `templates/scripts/python/validator/conflict_detector.py` | 15 |
| `ConflictReport` | 类 | `templates/scripts/python/validator/conflict_detector.py` | 27 |
| `SkillValidator` | 类 | `scripts/python/validator/skill_validator.py` | 84 |
| `ConflictDetector` | 类 | `scripts/python/validator/conflict_detector.py` | 45 |
| `SkillValidator` | 类 | `templates/scripts/python/validator/skill_validator.py` | 84 |
| `ConflictDetector` | 类 | `templates/scripts/python/validator/conflict_detector.py` | 45 |
| `add_error` | 函数 | `scripts/python/validator/skill_validator.py` | 40 |
| `add_warning` | 函数 | `scripts/python/validator/skill_validator.py` | 50 |
| `add_info` | 函数 | `scripts/python/validator/skill_validator.py` | 59 |
| `merge` | 函数 | `scripts/python/validator/skill_validator.py` | 75 |
| `validate_skill_file` | 函数 | `scripts/python/validator/skill_validator.py` | 134 |
| `validate_skill_directory` | 函数 | `scripts/python/validator/skill_validator.py` | 162 |
| `add_error` | 函数 | `templates/scripts/python/validator/skill_validator.py` | 40 |
| `add_warning` | 函数 | `templates/scripts/python/validator/skill_validator.py` | 50 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Main → _should_exclude` | 跨模块 | 5 |
| `Main → _get_file_hash` | 跨模块 | 5 |
| `Main → ExtractorResult` | 跨模块 | 5 |
| `Main → _should_exclude` | 跨模块 | 5 |
| `Main → _get_file_hash` | 跨模块 | 5 |
| `Main → ExtractorResult` | 跨模块 | 5 |
| `Main → KnowledgeBase` | 跨模块 | 4 |
| `Main → KnowledgeBase` | 跨模块 | 4 |
| `Main → Ensure_private_dir` | 跨模块 | 3 |
| `Main → Default_output_dir` | 跨模块 | 3 |

## 关联模块

| 模块 | 连接数 |
|------|-------------|
| Tests | 6 次调用 |
| Scripts | 2 次调用 |
