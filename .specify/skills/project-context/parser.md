---
skill_id: project-context/parser
title: "Parser 模块详情"
description: "parser 模块的文件、符号、入口点和执行流详情"
triggers:
  - parser
  - Parser
generated_at: "2026-04-02T13:24:32.631930"
generator: "gitnexus"
---

# Parser

29 个符号 | 4 个文件 | 内聚度: 100%

## 使用场景

- 处理 `templates/`
- 理解 parse_file, hash_code, parse_file 的工作原理
- 修改 parser 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `templates/scripts/python/parser/python_parser.py` | parse_file, _parse_class, _parse_function, _get_decorator_name, _get_attribute_name (+6) |
| `scripts/python/parser/python_parser.py` | parse_file, _parse_class, _parse_function, _get_decorator_name, _get_attribute_name (+5) |
| `templates/scripts/python/parser/base.py` | CodeUnit, hash_code, parse_file, get_file_extensions, parse_directory (+1) |
| `scripts/python/parser/base.py` | CodeUnit, hash_code |

## 入口点

探索该模块的起点：

- **`parse_file`** (函数) — `scripts/python/parser/python_parser.py:21`
- **`hash_code`** (函数) — `scripts/python/parser/base.py:186`
- **`parse_file`** (函数) — `templates/scripts/python/parser/python_parser.py:21`
- **`hash_code`** (函数) — `templates/scripts/python/parser/base.py:186`
- **`parse_file`** (函数) — `templates/scripts/python/parser/base.py:104`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `CodeUnit` | 类 | `scripts/python/parser/base.py` | 14 |
| `CodeUnit` | 类 | `templates/scripts/python/parser/base.py` | 14 |
| `PythonParser` | 类 | `templates/scripts/python/parser/python_parser.py` | 12 |
| `BaseParser` | 类 | `templates/scripts/python/parser/base.py` | 96 |
| `parse_file` | 函数 | `scripts/python/parser/python_parser.py` | 21 |
| `hash_code` | 函数 | `scripts/python/parser/base.py` | 186 |
| `parse_file` | 函数 | `templates/scripts/python/parser/python_parser.py` | 21 |
| `hash_code` | 函数 | `templates/scripts/python/parser/base.py` | 186 |
| `parse_file` | 函数 | `templates/scripts/python/parser/base.py` | 104 |
| `get_file_extensions` | 函数 | `templates/scripts/python/parser/base.py` | 127 |
| `parse_directory` | 函数 | `templates/scripts/python/parser/base.py` | 136 |
| `_parse_class` | 函数 | `scripts/python/parser/python_parser.py` | 51 |
| `_parse_function` | 函数 | `scripts/python/parser/python_parser.py` | 71 |
| `_get_decorator_name` | 函数 | `scripts/python/parser/python_parser.py` | 95 |
| `_get_attribute_name` | 函数 | `scripts/python/parser/python_parser.py` | 108 |
| `_get_base_name` | 函数 | `scripts/python/parser/python_parser.py` | 119 |
| `_get_function_params` | 函数 | `scripts/python/parser/python_parser.py` | 133 |
| `_get_return_annotation` | 函数 | `scripts/python/parser/python_parser.py` | 140 |
| `_is_abstract_class` | 函数 | `scripts/python/parser/python_parser.py` | 149 |
| `_hash_node` | 函数 | `scripts/python/parser/python_parser.py` | 166 |
