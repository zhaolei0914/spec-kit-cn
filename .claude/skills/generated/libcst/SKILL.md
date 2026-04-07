---
name: libcst
description: "Skill for the Libcst area of repo. 115 symbols across 15 files."
---

# Libcst

115 symbols | 15 files | Cohesion: 81%

## When to Use

- Working with code in `scripts/`
- Understanding how visit_ClassDef, visit_Raise, visit_Try work
- Modifying libcst-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/python/extractor/libcst/knowledge_base.py` | __init__, _process_single_file, _fast_extract_all, _get_file_hash, KnowledgeBase (+11) |
| `scripts/python/extractor/libcst/function_extractor.py` | FunctionExtractor, visit_FunctionDef, _get_location, _get_decorators, _get_parameters (+10) |
| `scripts/python/extractor/libcst/exception_extractor.py` | visit_ClassDef, visit_Raise, visit_Try, _get_bases, _get_name (+9) |
| `scripts/python/extractor/libcst/base_libcst.py` | CodeLocation, CodeUnit, LibCSTExtractor, _get_annotation_string, ExtractorResult (+8) |
| `scripts/python/extractor/libcst/constant_extractor.py` | ConstantExtractor, visit_ClassDef, _extract_value, _get_location, _get_base_name (+8) |
| `scripts/python/extractor/libcst/decorator_extractor.py` | DecoratorExtractor, visit_ClassDef, visit_FunctionDef, _extract_decorator_usage, _parse_decorator (+6) |
| `scripts/python/extractor/libcst/class_extractor.py` | ClassExtractor, visit_ClassDef, _get_location, _get_decorators, _get_bases (+6) |
| `scripts/python/extractor/libcst/import_extractor.py` | ImportExtractor, visit_Import, visit_ImportFrom, _get_module_name, _get_location (+5) |
| `scripts/python/extractor/libcst/comment_extractor.py` | extract_from_tree, _is_block_comment, _find_comment_position, CommentExtractor |
| `scripts/python/extractor/libcst/django/middleware_extractor.py` | _get_location, DjangoMiddlewareExtractor |

## Entry Points

Start here when exploring this area:

- **`visit_ClassDef`** (Function) — `scripts/python/extractor/libcst/exception_extractor.py:61`
- **`visit_Raise`** (Function) — `scripts/python/extractor/libcst/exception_extractor.py:119`
- **`visit_Try`** (Function) — `scripts/python/extractor/libcst/exception_extractor.py:164`
- **`extract_from_tree`** (Function) — `scripts/python/extractor/libcst/comment_extractor.py:31`
- **`setUp`** (Function) — `scripts/python/tests/test_extractors.py:29`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `CodeLocation` | Class | `scripts/python/extractor/libcst/base_libcst.py` | 32 |
| `CodeUnit` | Class | `scripts/python/extractor/libcst/base_libcst.py` | 51 |
| `ImportExtractor` | Class | `scripts/python/extractor/libcst/import_extractor.py` | 16 |
| `FunctionExtractor` | Class | `scripts/python/extractor/libcst/function_extractor.py` | 16 |
| `ExceptionExtractor` | Class | `scripts/python/extractor/libcst/exception_extractor.py` | 16 |
| `DecoratorExtractor` | Class | `scripts/python/extractor/libcst/decorator_extractor.py` | 17 |
| `ConstantExtractor` | Class | `scripts/python/extractor/libcst/constant_extractor.py` | 17 |
| `CommentExtractor` | Class | `scripts/python/extractor/libcst/comment_extractor.py` | 17 |
| `ClassExtractor` | Class | `scripts/python/extractor/libcst/class_extractor.py` | 19 |
| `LibCSTExtractor` | Class | `scripts/python/extractor/libcst/base_libcst.py` | 188 |
| `DjangoViewExtractor` | Class | `scripts/python/extractor/libcst/django/view_extractor.py` | 16 |
| `DjangoURLExtractor` | Class | `scripts/python/extractor/libcst/django/url_extractor.py` | 16 |
| `DjangoModelExtractor` | Class | `scripts/python/extractor/libcst/django/model_extractor.py` | 16 |
| `DjangoMiddlewareExtractor` | Class | `scripts/python/extractor/libcst/django/middleware_extractor.py` | 16 |
| `ExtractorResult` | Class | `scripts/python/extractor/libcst/base_libcst.py` | 163 |
| `KnowledgeBase` | Class | `scripts/python/extractor/libcst/knowledge_base.py` | 32 |
| `ImportVisitor` | Class | `scripts/python/extractor/libcst/import_extractor.py` | 41 |
| `FunctionVisitor` | Class | `scripts/python/extractor/libcst/function_extractor.py` | 41 |
| `ExceptionVisitor` | Class | `scripts/python/extractor/libcst/exception_extractor.py` | 41 |
| `DecoratorVisitor` | Class | `scripts/python/extractor/libcst/decorator_extractor.py` | 42 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_all → Get_bases` | cross_community | 6 |
| `Run_all → Get_decorators` | cross_community | 6 |
| `Run_all → Get_docstring` | cross_community | 6 |
| `Run_all → Get_node_source` | cross_community | 6 |
| `Analyze_project → Get_bases` | cross_community | 6 |
| `Analyze_project → Get_decorators` | cross_community | 6 |
| `Analyze_project → Get_docstring` | cross_community | 6 |
| `Analyze_project → Get_node_source` | cross_community | 6 |
| `Main → _get_file_hash` | cross_community | 5 |
| `Visit_Assign → CodeLocation` | cross_community | 5 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Generator | 4 calls |
| Django | 3 calls |
| Parser | 1 calls |

## How to Explore

1. `gitnexus_context({name: "visit_ClassDef"})` — see callers and callees
2. `gitnexus_query({query: "libcst"})` — find related execution flows
3. Read key files listed above for implementation details
