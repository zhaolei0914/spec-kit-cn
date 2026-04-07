---
name: parser
description: "Skill for the Parser area of repo. 21 symbols across 6 files."
---

# Parser

21 symbols | 6 files | Cohesion: 73%

## When to Use

- Working with code in `scripts/`
- Understanding how parse_file, hash_code, get_docstring work
- Modifying parser-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/python/parser/python_parser.py` | parse_file, _parse_class, _parse_function, _get_decorator_name, _get_attribute_name (+6) |
| `scripts/python/parser/base.py` | CodeUnit, hash_code, BaseParser, parse_file, get_file_extensions (+1) |
| `scripts/python/extractor/libcst/knowledge_base.py` | get_docstring |
| `scripts/python/main.py` | cmd_analyze |
| `scripts/python/miner/pattern_miner.py` | PatternMiner |
| `scripts/python/analyzer/skeleton_generator.py` | save |

## Entry Points

Start here when exploring this area:

- **`parse_file`** (Function) — `scripts/python/parser/python_parser.py:21`
- **`hash_code`** (Function) — `scripts/python/parser/base.py:186`
- **`get_docstring`** (Function) — `scripts/python/extractor/libcst/knowledge_base.py:397`
- **`cmd_analyze`** (Function) — `scripts/python/main.py:36`
- **`parse_file`** (Function) — `scripts/python/parser/base.py:104`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `CodeUnit` | Class | `scripts/python/parser/base.py` | 14 |
| `PythonParser` | Class | `scripts/python/parser/python_parser.py` | 12 |
| `BaseParser` | Class | `scripts/python/parser/base.py` | 96 |
| `PatternMiner` | Class | `scripts/python/miner/pattern_miner.py` | 15 |
| `parse_file` | Function | `scripts/python/parser/python_parser.py` | 21 |
| `hash_code` | Function | `scripts/python/parser/base.py` | 186 |
| `get_docstring` | Function | `scripts/python/extractor/libcst/knowledge_base.py` | 397 |
| `cmd_analyze` | Function | `scripts/python/main.py` | 36 |
| `parse_file` | Function | `scripts/python/parser/base.py` | 104 |
| `get_file_extensions` | Function | `scripts/python/parser/base.py` | 127 |
| `parse_directory` | Function | `scripts/python/parser/base.py` | 136 |
| `save` | Function | `scripts/python/analyzer/skeleton_generator.py` | 363 |
| `_parse_class` | Function | `scripts/python/parser/python_parser.py` | 51 |
| `_parse_function` | Function | `scripts/python/parser/python_parser.py` | 71 |
| `_get_decorator_name` | Function | `scripts/python/parser/python_parser.py` | 95 |
| `_get_attribute_name` | Function | `scripts/python/parser/python_parser.py` | 108 |
| `_get_base_name` | Function | `scripts/python/parser/python_parser.py` | 119 |
| `_get_function_params` | Function | `scripts/python/parser/python_parser.py` | 133 |
| `_get_return_annotation` | Function | `scripts/python/parser/python_parser.py` | 140 |
| `_is_abstract_class` | Function | `scripts/python/parser/python_parser.py` | 149 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_all → Get_docstring` | cross_community | 6 |
| `Analyze_project → Get_docstring` | cross_community | 6 |
| `Extract_knowledge → Get_docstring` | cross_community | 5 |
| `Extract_api → Get_docstring` | cross_community | 5 |
| `Analyze_entries → Get_docstring` | cross_community | 5 |
| `Cmd_analyze → CodePattern` | cross_community | 4 |
| `Main → Get_file_extensions` | cross_community | 4 |
| `Main → Parse_file` | cross_community | 4 |
| `Extract_error_codes → Get_docstring` | cross_community | 4 |
| `Parse_file → _get_attribute_name` | intra_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Analyzer | 10 calls |
| Miner | 1 calls |
| Generator | 1 calls |

## How to Explore

1. `gitnexus_context({name: "parse_file"})` — see callers and callees
2. `gitnexus_query({query: "parser"})` — find related execution flows
3. Read key files listed above for implementation details
