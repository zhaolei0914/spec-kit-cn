---
name: django
description: "Skill for the Django area of repo. 49 symbols across 5 files."
---

# Django

49 symbols | 5 files | Cohesion: 73%

## When to Use

- Working with code in `scripts/`
- Understanding how visit_FunctionDef, visit_Assign, visit_AugAssign work
- Modifying django-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/python/extractor/libcst/django/view_extractor.py` | visit_FunctionDef, _extract_function_view, _extract_http_method, _extract_action_method, _get_decorators (+13) |
| `scripts/python/extractor/libcst/django/model_extractor.py` | visit_ClassDef, _get_location, _extract_meta, _parse_meta_class, _extract_methods (+8) |
| `scripts/python/extractor/libcst/django/url_extractor.py` | visit_Assign, visit_AugAssign, _extract_urlpatterns, _extract_url_pattern, _parse_url_args (+4) |
| `scripts/python/extractor/libcst/django/middleware_extractor.py` | visit_ClassDef, _get_bases, _get_name, _has_middleware_methods, _extract_methods (+3) |
| `scripts/python/extractor/libcst/base_libcst.py` | _get_docstring |

## Entry Points

Start here when exploring this area:

- **`visit_FunctionDef`** (Function) — `scripts/python/extractor/libcst/django/view_extractor.py:105`
- **`visit_Assign`** (Function) — `scripts/python/extractor/libcst/django/url_extractor.py:56`
- **`visit_AugAssign`** (Function) — `scripts/python/extractor/libcst/django/url_extractor.py:66`
- **`visit_ClassDef`** (Function) — `scripts/python/extractor/libcst/django/model_extractor.py:69`
- **`visit_ClassDef`** (Function) — `scripts/python/extractor/libcst/django/middleware_extractor.py:60`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `DjangoViewVisitor` | Class | `scripts/python/extractor/libcst/django/view_extractor.py` | 62 |
| `DjangoURLVisitor` | Class | `scripts/python/extractor/libcst/django/url_extractor.py` | 44 |
| `DjangoModelVisitor` | Class | `scripts/python/extractor/libcst/django/model_extractor.py` | 59 |
| `DjangoMiddlewareVisitor` | Class | `scripts/python/extractor/libcst/django/middleware_extractor.py` | 50 |
| `visit_FunctionDef` | Function | `scripts/python/extractor/libcst/django/view_extractor.py` | 105 |
| `visit_Assign` | Function | `scripts/python/extractor/libcst/django/url_extractor.py` | 56 |
| `visit_AugAssign` | Function | `scripts/python/extractor/libcst/django/url_extractor.py` | 66 |
| `visit_ClassDef` | Function | `scripts/python/extractor/libcst/django/model_extractor.py` | 69 |
| `visit_ClassDef` | Function | `scripts/python/extractor/libcst/django/middleware_extractor.py` | 60 |
| `visit_ClassDef` | Function | `scripts/python/extractor/libcst/django/view_extractor.py` | 75 |
| `extract_from_tree` | Function | `scripts/python/extractor/libcst/django/view_extractor.py` | 48 |
| `extract_from_tree` | Function | `scripts/python/extractor/libcst/django/url_extractor.py` | 30 |
| `extract_from_tree` | Function | `scripts/python/extractor/libcst/django/model_extractor.py` | 45 |
| `extract_from_tree` | Function | `scripts/python/extractor/libcst/django/middleware_extractor.py` | 36 |
| `_get_docstring` | Function | `scripts/python/extractor/libcst/base_libcst.py` | 387 |
| `_extract_function_view` | Function | `scripts/python/extractor/libcst/django/view_extractor.py` | 188 |
| `_extract_http_method` | Function | `scripts/python/extractor/libcst/django/view_extractor.py` | 246 |
| `_extract_action_method` | Function | `scripts/python/extractor/libcst/django/view_extractor.py` | 288 |
| `_get_decorators` | Function | `scripts/python/extractor/libcst/django/view_extractor.py` | 355 |
| `_get_location` | Function | `scripts/python/extractor/libcst/django/view_extractor.py` | 390 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Visit_Assign → Get` | cross_community | 5 |
| `Visit_Assign → CodeLocation` | cross_community | 5 |
| `Visit_AugAssign → Get` | cross_community | 5 |
| `Visit_AugAssign → CodeLocation` | cross_community | 5 |
| `Visit_ClassDef → _get_name` | cross_community | 4 |
| `Visit_ClassDef → _extract_field_args` | cross_community | 4 |
| `Visit_ClassDef → Get` | cross_community | 4 |
| `Visit_FunctionDef → _get_name` | cross_community | 4 |
| `Visit_FunctionDef → CodeLocation` | cross_community | 4 |
| `Visit_FunctionDef → _extract_string_value` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Libcst | 14 calls |
| Generator | 6 calls |

## How to Explore

1. `gitnexus_context({name: "visit_FunctionDef"})` — see callers and callees
2. `gitnexus_query({query: "django"})` — find related execution flows
3. Read key files listed above for implementation details
