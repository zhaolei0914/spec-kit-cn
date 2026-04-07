---
skill_id: project-context/django
title: "Django 模块详情"
description: "django 模块的文件、符号、入口点和执行流详情"
triggers:
  - django
  - Django
generated_at: "2026-04-02T13:24:32.627224"
generator: "gitnexus"
---

# Django

103 个符号 | 11 个文件 | 内聚度: 75%

## 使用场景

- 处理 `scripts/`
- 理解 visit_ClassDef, visit_FunctionDef, visit_FunctionDef 的工作原理
- 修改 django 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `scripts/python/extractor/libcst/django/view_extractor.py` | visit_FunctionDef, _extract_function_view, _extract_http_method, _extract_action_method, _get_decorators (+13) |
| `templates/scripts/python/extractor/libcst/django/view_extractor.py` | visit_FunctionDef, _extract_function_view, _extract_http_method, _extract_action_method, _get_decorators (+13) |
| `scripts/python/extractor/libcst/django/model_extractor.py` | visit_ClassDef, _get_location, _extract_meta, _parse_meta_class, _extract_methods (+8) |
| `templates/scripts/python/extractor/libcst/django/model_extractor.py` | visit_ClassDef, _get_location, _extract_meta, _parse_meta_class, _extract_methods (+8) |
| `scripts/python/extractor/libcst/django/url_extractor.py` | visit_Assign, visit_AugAssign, _extract_urlpatterns, _extract_url_pattern, _parse_url_args (+4) |
| `templates/scripts/python/extractor/libcst/django/url_extractor.py` | visit_Assign, visit_AugAssign, _extract_urlpatterns, _extract_url_pattern, _parse_url_args (+4) |
| `scripts/python/extractor/libcst/django/middleware_extractor.py` | visit_ClassDef, _get_bases, _get_name, _has_middleware_methods, _extract_methods (+3) |
| `templates/scripts/python/extractor/libcst/django/middleware_extractor.py` | visit_ClassDef, _get_bases, _get_name, _has_middleware_methods, _extract_methods (+3) |
| `scripts/python/extractor/libcst/exception_extractor.py` | visit_ClassDef, _extract_exception_attributes, _get_location_for_class |
| `scripts/python/extractor/libcst/base_libcst.py` | CodeUnit, _get_docstring, _get_annotation_string |

## 入口点

探索该模块的起点：

- **`visit_ClassDef`** (函数) — `scripts/python/extractor/libcst/exception_extractor.py:61`
- **`visit_FunctionDef`** (函数) — `scripts/python/extractor/libcst/django/view_extractor.py:105`
- **`visit_FunctionDef`** (函数) — `templates/scripts/python/extractor/libcst/django/view_extractor.py:105`
- **`visit_Assign`** (函数) — `scripts/python/extractor/libcst/django/url_extractor.py:56`
- **`visit_AugAssign`** (函数) — `scripts/python/extractor/libcst/django/url_extractor.py:66`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `CodeUnit` | 类 | `scripts/python/extractor/libcst/base_libcst.py` | 51 |
| `DjangoViewVisitor` | 类 | `scripts/python/extractor/libcst/django/view_extractor.py` | 62 |
| `DjangoURLVisitor` | 类 | `scripts/python/extractor/libcst/django/url_extractor.py` | 44 |
| `DjangoModelVisitor` | 类 | `scripts/python/extractor/libcst/django/model_extractor.py` | 59 |
| `DjangoMiddlewareVisitor` | 类 | `scripts/python/extractor/libcst/django/middleware_extractor.py` | 50 |
| `DjangoViewVisitor` | 类 | `templates/scripts/python/extractor/libcst/django/view_extractor.py` | 62 |
| `DjangoURLVisitor` | 类 | `templates/scripts/python/extractor/libcst/django/url_extractor.py` | 44 |
| `DjangoModelVisitor` | 类 | `templates/scripts/python/extractor/libcst/django/model_extractor.py` | 59 |
| `DjangoMiddlewareVisitor` | 类 | `templates/scripts/python/extractor/libcst/django/middleware_extractor.py` | 50 |
| `visit_ClassDef` | 函数 | `scripts/python/extractor/libcst/exception_extractor.py` | 61 |
| `visit_FunctionDef` | 函数 | `scripts/python/extractor/libcst/django/view_extractor.py` | 105 |
| `visit_FunctionDef` | 函数 | `templates/scripts/python/extractor/libcst/django/view_extractor.py` | 105 |
| `visit_Assign` | 函数 | `scripts/python/extractor/libcst/django/url_extractor.py` | 56 |
| `visit_AugAssign` | 函数 | `scripts/python/extractor/libcst/django/url_extractor.py` | 66 |
| `visit_Assign` | 函数 | `templates/scripts/python/extractor/libcst/django/url_extractor.py` | 56 |
| `visit_AugAssign` | 函数 | `templates/scripts/python/extractor/libcst/django/url_extractor.py` | 66 |
| `visit_ClassDef` | 函数 | `scripts/python/extractor/libcst/django/model_extractor.py` | 69 |
| `visit_ClassDef` | 函数 | `scripts/python/extractor/libcst/django/middleware_extractor.py` | 60 |
| `visit_ClassDef` | 函数 | `templates/scripts/python/extractor/libcst/django/model_extractor.py` | 69 |
| `visit_ClassDef` | 函数 | `templates/scripts/python/extractor/libcst/django/middleware_extractor.py` | 60 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Visit_FunctionDef → _get_annotation_string` | 跨模块 | 4 |
| `Visit_ClassDef → _get_name` | 跨模块 | 4 |
| `Visit_ClassDef → _extract_field_args` | 跨模块 | 4 |
| `Visit_ClassDef → _get_name` | 跨模块 | 4 |
| `Visit_ClassDef → _extract_field_args` | 跨模块 | 4 |
| `Visit_FunctionDef → _get_name` | 跨模块 | 4 |
| `Visit_FunctionDef → CodeLocation` | 跨模块 | 4 |
| `Visit_FunctionDef → _extract_string_value` | 跨模块 | 4 |
| `Visit_FunctionDef → _get_annotation_string` | 模块内 | 4 |
| `Visit_FunctionDef → _get_name` | 跨模块 | 4 |

## 关联模块

| 模块 | 连接数 |
|------|-------------|
| Libcst | 21 次调用 |
