---
skill_id: project-context/miner
title: "Miner 模块详情"
description: "miner 模块的文件、符号、入口点和执行流详情"
triggers:
  - miner
  - Miner
generated_at: "2026-04-02T13:24:32.631475"
generator: "gitnexus"
---

# Miner

19 个符号 | 3 个文件 | 内聚度: 71%

## 使用场景

- 处理 `scripts/`
- 理解 mine_patterns, mine_patterns, CodePattern 的工作原理
- 修改 miner 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `templates/scripts/python/miner/pattern_miner.py` | mine_patterns, _mine_inheritance_patterns, _mine_decorator_patterns, _mine_naming_patterns, _mine_structure_patterns (+4) |
| `scripts/python/miner/pattern_miner.py` | mine_patterns, _mine_inheritance_patterns, _mine_decorator_patterns, _mine_naming_patterns, _mine_structure_patterns (+4) |
| `scripts/python/parser/base.py` | CodePattern |

## 入口点

探索该模块的起点：

- **`mine_patterns`** (函数) — `templates/scripts/python/miner/pattern_miner.py:29`
- **`mine_patterns`** (函数) — `scripts/python/miner/pattern_miner.py:29`
- **`CodePattern`** (类) — `scripts/python/parser/base.py:50`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `CodePattern` | 类 | `scripts/python/parser/base.py` | 50 |
| `mine_patterns` | 函数 | `templates/scripts/python/miner/pattern_miner.py` | 29 |
| `mine_patterns` | 函数 | `scripts/python/miner/pattern_miner.py` | 29 |
| `_mine_inheritance_patterns` | 函数 | `templates/scripts/python/miner/pattern_miner.py` | 76 |
| `_mine_decorator_patterns` | 函数 | `templates/scripts/python/miner/pattern_miner.py` | 107 |
| `_mine_naming_patterns` | 函数 | `templates/scripts/python/miner/pattern_miner.py` | 149 |
| `_mine_structure_patterns` | 函数 | `templates/scripts/python/miner/pattern_miner.py` | 220 |
| `_mine_param_patterns` | 函数 | `templates/scripts/python/miner/pattern_miner.py` | 251 |
| `_mine_file_patterns` | 函数 | `templates/scripts/python/miner/pattern_miner.py` | 282 |
| `_mine_docstring_patterns` | 函数 | `templates/scripts/python/miner/pattern_miner.py` | 335 |
| `_mine_return_type_patterns` | 函数 | `templates/scripts/python/miner/pattern_miner.py` | 387 |
| `_mine_inheritance_patterns` | 函数 | `scripts/python/miner/pattern_miner.py` | 76 |
| `_mine_decorator_patterns` | 函数 | `scripts/python/miner/pattern_miner.py` | 107 |
| `_mine_naming_patterns` | 函数 | `scripts/python/miner/pattern_miner.py` | 149 |
| `_mine_structure_patterns` | 函数 | `scripts/python/miner/pattern_miner.py` | 220 |
| `_mine_param_patterns` | 函数 | `scripts/python/miner/pattern_miner.py` | 251 |
| `_mine_file_patterns` | 函数 | `scripts/python/miner/pattern_miner.py` | 282 |
| `_mine_docstring_patterns` | 函数 | `scripts/python/miner/pattern_miner.py` | 335 |
| `_mine_return_type_patterns` | 函数 | `scripts/python/miner/pattern_miner.py` | 387 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Cmd_analyze → CodePattern` | 跨模块 | 4 |
| `Cmd_analyze → CodePattern` | 跨模块 | 4 |
| `Mine_patterns → CodePattern` | 模块内 | 3 |
