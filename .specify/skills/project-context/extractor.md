---
skill_id: project-context/extractor
title: "Extractor 模块详情"
description: "extractor 模块的文件、符号、入口点和执行流详情"
triggers:
  - extractor
  - Extractor
generated_at: "2026-04-02T13:24:32.627856"
generator: "gitnexus"
---

# Extractor

114 个符号 | 18 个文件 | 内聚度: 88%

## 使用场景

- 处理 `templates/`
- 理解 extract, extract_all, extract 的工作原理
- 修改 extractor 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `scripts/shell/extractor/function_extractor.py` | extract_all, ShellFunctionExtractor, extract, _match_function_start, _get_function_docstring (+4) |
| `templates/scripts/shell/extractor/function_extractor.py` | extract_all, ShellFunctionExtractor, extract, _match_function_start, _get_function_docstring (+4) |
| `scripts/python/extractor/fusion.py` | get_by_type, KnowledgeFusion, __init__, extract_all, add_items (+4) |
| `templates/scripts/python/extractor/fusion.py` | get_by_type, KnowledgeFusion, __init__, extract_all, add_items (+4) |
| `scripts/shell/extractor/base.py` | ShellVariable, ShellSource, ShellPattern, _find_shell_files, _read_file (+3) |
| `templates/scripts/shell/extractor/base.py` | ShellVariable, ShellSource, ShellPattern, _find_shell_files, _read_file (+3) |
| `scripts/shell/extractor/comment_extractor.py` | extract_all, ShellCommentExtractor, extract, _extract_header_comments, _extract_todo_comments (+2) |
| `templates/scripts/shell/extractor/comment_extractor.py` | extract_all, ShellCommentExtractor, extract, _extract_header_comments, _extract_todo_comments (+2) |
| `scripts/python/extractor/base.py` | from_dict, get, calculate_confidence, determine_priority, extract (+2) |
| `templates/scripts/python/extractor/base.py` | from_dict, get, calculate_confidence, determine_priority, extract (+2) |

## 入口点

探索该模块的起点：

- **`extract`** (函数) — `scripts/shell/extractor/variable_extractor.py:35`
- **`extract_all`** (函数) — `scripts/shell/extractor/variable_extractor.py:118`
- **`extract`** (函数) — `scripts/shell/extractor/source_extractor.py:23`
- **`extract_all`** (函数) — `scripts/shell/extractor/source_extractor.py:56`
- **`extract`** (函数) — `scripts/shell/extractor/pattern_miner.py:66`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `ShellVariable` | 类 | `scripts/shell/extractor/base.py` | 85 |
| `ShellSource` | 类 | `scripts/shell/extractor/base.py` | 152 |
| `ShellPattern` | 类 | `scripts/shell/extractor/base.py` | 178 |
| `ShellVariable` | 类 | `templates/scripts/shell/extractor/base.py` | 85 |
| `ShellSource` | 类 | `templates/scripts/shell/extractor/base.py` | 152 |
| `ShellPattern` | 类 | `templates/scripts/shell/extractor/base.py` | 178 |
| `ShellVariableExtractor` | 类 | `scripts/shell/extractor/variable_extractor.py` | 15 |
| `ShellSourceExtractor` | 类 | `scripts/shell/extractor/source_extractor.py` | 12 |
| `ShellPatternMiner` | 类 | `scripts/shell/extractor/pattern_miner.py` | 16 |
| `ShellKnowledgeBase` | 类 | `scripts/shell/extractor/fusion.py` | 21 |
| `ShellFunctionExtractor` | 类 | `scripts/shell/extractor/function_extractor.py` | 17 |
| `ShellCommentExtractor` | 类 | `scripts/shell/extractor/comment_extractor.py` | 15 |
| `BaseShellExtractor` | 类 | `scripts/shell/extractor/base.py` | 203 |
| `ShellFunction` | 类 | `scripts/shell/extractor/base.py` | 44 |
| `ShellVariableExtractor` | 类 | `templates/scripts/shell/extractor/variable_extractor.py` | 15 |
| `ShellSourceExtractor` | 类 | `templates/scripts/shell/extractor/source_extractor.py` | 12 |
| `ShellPatternMiner` | 类 | `templates/scripts/shell/extractor/pattern_miner.py` | 16 |
| `ShellKnowledgeBase` | 类 | `templates/scripts/shell/extractor/fusion.py` | 21 |
| `ShellFunctionExtractor` | 类 | `templates/scripts/shell/extractor/function_extractor.py` | 17 |
| `ShellCommentExtractor` | 类 | `templates/scripts/shell/extractor/comment_extractor.py` | 15 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Extract_all → KnowledgeItem` | 跨模块 | 5 |
| `Extract_all → KnowledgeItem` | 跨模块 | 5 |
| `Main → ShellKnowledgeBase` | 跨模块 | 4 |
| `Main → ShellFunctionExtractor` | 跨模块 | 4 |
| `Main → ShellVariableExtractor` | 跨模块 | 4 |
| `Main → ShellCommentExtractor` | 跨模块 | 4 |
| `Main → ShellKnowledgeBase` | 跨模块 | 4 |
| `Main → ShellFunctionExtractor` | 跨模块 | 4 |
| `Main → ShellVariableExtractor` | 跨模块 | 4 |
| `Main → ShellCommentExtractor` | 跨模块 | 4 |
