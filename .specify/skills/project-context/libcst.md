---
skill_id: project-context/libcst
title: "Libcst 模块详情"
description: "libcst 模块的文件、符号、入口点和执行流详情"
triggers:
  - libcst
  - Libcst
generated_at: "2026-04-02T13:24:32.629540"
generator: "gitnexus"
---

# Libcst

234 个符号 | 30 个文件 | 内聚度: 84%

## 使用场景

- 处理 `templates/`
- 理解 visit_ClassDef, visit_Raise, visit_Try 的工作原理
- 修改 libcst 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `templates/scripts/python/extractor/libcst/knowledge_base.py` | __init__, _process_single_file, _fast_extract_all, _get_file_hash, KnowledgeBase (+19) |
| `scripts/python/extractor/libcst/knowledge_base.py` | __init__, _process_single_file, _fast_extract_all, _get_file_hash, KnowledgeBase (+12) |
| `scripts/python/extractor/libcst/function_extractor.py` | FunctionExtractor, visit_FunctionDef, _get_location, _get_decorators, _get_parameters (+10) |
| `templates/scripts/python/extractor/libcst/function_extractor.py` | FunctionExtractor, visit_FunctionDef, _get_location, _get_decorators, _get_parameters (+10) |
| `templates/scripts/python/extractor/libcst/exception_extractor.py` | visit_ClassDef, visit_Raise, visit_Try, _get_bases, _get_name (+9) |
| `templates/scripts/python/extractor/libcst/base_libcst.py` | CodeLocation, CodeUnit, LibCSTExtractor, _get_annotation_string, ExtractorResult (+8) |
| `scripts/python/extractor/libcst/constant_extractor.py` | ConstantExtractor, visit_ClassDef, _extract_value, _get_location, _get_base_name (+8) |
| `templates/scripts/python/extractor/libcst/constant_extractor.py` | ConstantExtractor, visit_ClassDef, _extract_value, _get_location, _get_base_name (+8) |
| `scripts/python/extractor/libcst/exception_extractor.py` | ExceptionExtractor, visit_Raise, visit_Try, _get_bases, _get_name (+6) |
| `scripts/python/extractor/libcst/decorator_extractor.py` | DecoratorExtractor, visit_ClassDef, visit_FunctionDef, _extract_decorator_usage, _parse_decorator (+6) |

## 入口点

探索该模块的起点：

- **`visit_ClassDef`** (函数) — `templates/scripts/python/extractor/libcst/exception_extractor.py:61`
- **`visit_Raise`** (函数) — `templates/scripts/python/extractor/libcst/exception_extractor.py:119`
- **`visit_Try`** (函数) — `templates/scripts/python/extractor/libcst/exception_extractor.py:164`
- **`extract_from_tree`** (函数) — `templates/scripts/python/extractor/libcst/comment_extractor.py:31`
- **`setUp`** (函数) — `scripts/python/tests/test_extractors.py:29`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `CodeLocation` | 类 | `templates/scripts/python/extractor/libcst/base_libcst.py` | 32 |
| `CodeUnit` | 类 | `templates/scripts/python/extractor/libcst/base_libcst.py` | 51 |
| `ImportExtractor` | 类 | `scripts/python/extractor/libcst/import_extractor.py` | 16 |
| `FunctionExtractor` | 类 | `scripts/python/extractor/libcst/function_extractor.py` | 16 |
| `ExceptionExtractor` | 类 | `scripts/python/extractor/libcst/exception_extractor.py` | 16 |
| `DecoratorExtractor` | 类 | `scripts/python/extractor/libcst/decorator_extractor.py` | 17 |
| `ConstantExtractor` | 类 | `scripts/python/extractor/libcst/constant_extractor.py` | 17 |
| `CommentExtractor` | 类 | `scripts/python/extractor/libcst/comment_extractor.py` | 17 |
| `ClassExtractor` | 类 | `scripts/python/extractor/libcst/class_extractor.py` | 19 |
| `LibCSTExtractor` | 类 | `scripts/python/extractor/libcst/base_libcst.py` | 188 |
| `DjangoViewExtractor` | 类 | `scripts/python/extractor/libcst/django/view_extractor.py` | 16 |
| `DjangoURLExtractor` | 类 | `scripts/python/extractor/libcst/django/url_extractor.py` | 16 |
| `DjangoModelExtractor` | 类 | `scripts/python/extractor/libcst/django/model_extractor.py` | 16 |
| `DjangoMiddlewareExtractor` | 类 | `scripts/python/extractor/libcst/django/middleware_extractor.py` | 16 |
| `CodeLocation` | 类 | `scripts/python/extractor/libcst/base_libcst.py` | 32 |
| `ImportExtractor` | 类 | `templates/scripts/python/extractor/libcst/import_extractor.py` | 16 |
| `FunctionExtractor` | 类 | `templates/scripts/python/extractor/libcst/function_extractor.py` | 16 |
| `ExceptionExtractor` | 类 | `templates/scripts/python/extractor/libcst/exception_extractor.py` | 16 |
| `DecoratorExtractor` | 类 | `templates/scripts/python/extractor/libcst/decorator_extractor.py` | 17 |
| `ConstantExtractor` | 类 | `templates/scripts/python/extractor/libcst/constant_extractor.py` | 17 |

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
| `Analyze_project → Get_bases` | 跨模块 | 5 |
| `Analyze_project → Get_decorators` | 跨模块 | 5 |

## 关联模块

| 模块 | 连接数 |
|------|-------------|
| Django | 21 次调用 |
