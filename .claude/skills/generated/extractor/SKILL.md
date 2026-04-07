---
name: extractor
description: "Skill for the Extractor area of repo. 51 symbols across 9 files."
---

# Extractor

51 symbols | 9 files | Cohesion: 86%

## When to Use

- Working with code in `scripts/`
- Understanding how extract, extract_all, extract work
- Modifying extractor-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/shell/extractor/function_extractor.py` | extract_all, ShellFunctionExtractor, extract, _match_function_start, _get_function_docstring (+4) |
| `scripts/shell/extractor/base.py` | ShellVariable, ShellSource, ShellPattern, _find_shell_files, _read_file (+3) |
| `scripts/python/extractor/fusion.py` | KnowledgeFusion, __init__, extract_all, add_items, _add_item (+3) |
| `scripts/shell/extractor/comment_extractor.py` | extract_all, ShellCommentExtractor, extract, _extract_header_comments, _extract_todo_comments (+2) |
| `scripts/shell/extractor/variable_extractor.py` | extract, extract_all, _create_variable, _categorize_variable, _get_preceding_comment (+1) |
| `scripts/shell/extractor/source_extractor.py` | extract, extract_all, _resolve_path, ShellSourceExtractor |
| `scripts/shell/extractor/pattern_miner.py` | extract, extract_all, ShellPatternMiner |
| `scripts/shell/extractor/fusion.py` | _compute_statistics, ShellKnowledgeBase, analyze_project |
| `scripts/python/extractor/base.py` | extract, KnowledgeItem, get_supported_types |

## Entry Points

Start here when exploring this area:

- **`extract`** (Function) — `scripts/shell/extractor/variable_extractor.py:35`
- **`extract_all`** (Function) — `scripts/shell/extractor/variable_extractor.py:118`
- **`extract`** (Function) — `scripts/shell/extractor/source_extractor.py:23`
- **`extract_all`** (Function) — `scripts/shell/extractor/source_extractor.py:56`
- **`extract`** (Function) — `scripts/shell/extractor/pattern_miner.py:66`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `ShellVariable` | Class | `scripts/shell/extractor/base.py` | 85 |
| `ShellSource` | Class | `scripts/shell/extractor/base.py` | 152 |
| `ShellPattern` | Class | `scripts/shell/extractor/base.py` | 178 |
| `ShellVariableExtractor` | Class | `scripts/shell/extractor/variable_extractor.py` | 15 |
| `ShellSourceExtractor` | Class | `scripts/shell/extractor/source_extractor.py` | 12 |
| `ShellPatternMiner` | Class | `scripts/shell/extractor/pattern_miner.py` | 16 |
| `ShellKnowledgeBase` | Class | `scripts/shell/extractor/fusion.py` | 21 |
| `ShellFunctionExtractor` | Class | `scripts/shell/extractor/function_extractor.py` | 17 |
| `ShellCommentExtractor` | Class | `scripts/shell/extractor/comment_extractor.py` | 15 |
| `BaseShellExtractor` | Class | `scripts/shell/extractor/base.py` | 203 |
| `ShellFunction` | Class | `scripts/shell/extractor/base.py` | 44 |
| `ShellComment` | Class | `scripts/shell/extractor/base.py` | 123 |
| `KnowledgeFusion` | Class | `scripts/python/extractor/fusion.py` | 11 |
| `KnowledgeItem` | Class | `scripts/python/extractor/base.py` | 59 |
| `extract` | Function | `scripts/shell/extractor/variable_extractor.py` | 35 |
| `extract_all` | Function | `scripts/shell/extractor/variable_extractor.py` | 118 |
| `extract` | Function | `scripts/shell/extractor/source_extractor.py` | 23 |
| `extract_all` | Function | `scripts/shell/extractor/source_extractor.py` | 56 |
| `extract` | Function | `scripts/shell/extractor/pattern_miner.py` | 66 |
| `extract_all` | Function | `scripts/shell/extractor/pattern_miner.py` | 131 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Extract_all → KnowledgeItem` | cross_community | 5 |
| `Main → ShellKnowledgeBase` | cross_community | 4 |
| `Main → ShellFunctionExtractor` | cross_community | 4 |
| `Main → ShellVariableExtractor` | cross_community | 4 |
| `Main → ShellCommentExtractor` | cross_community | 4 |
| `Extract_all → _categorize_variable` | intra_community | 4 |
| `Extract_all → ShellVariable` | intra_community | 4 |
| `Extract_all → ShellComment` | cross_community | 4 |
| `Run_all → ShellKnowledgeBase` | cross_community | 3 |
| `Run_all → ShellFunctionExtractor` | cross_community | 3 |

## How to Explore

1. `gitnexus_context({name: "extract"})` — see callers and callees
2. `gitnexus_query({query: "extractor"})` — find related execution flows
3. Read key files listed above for implementation details
