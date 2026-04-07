---
name: miner
description: "Skill for the Miner area of repo. 10 symbols across 2 files."
---

# Miner

10 symbols | 2 files | Cohesion: 47%

## When to Use

- Working with code in `scripts/`
- Understanding how mine_patterns, CodePattern work
- Modifying miner-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/python/miner/pattern_miner.py` | _mine_inheritance_patterns, _mine_naming_patterns, _mine_param_patterns, _mine_return_type_patterns, mine_patterns (+4) |
| `scripts/python/parser/base.py` | CodePattern |

## Entry Points

Start here when exploring this area:

- **`mine_patterns`** (Function) — `scripts/python/miner/pattern_miner.py:29`
- **`CodePattern`** (Class) — `scripts/python/parser/base.py:50`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `CodePattern` | Class | `scripts/python/parser/base.py` | 50 |
| `mine_patterns` | Function | `scripts/python/miner/pattern_miner.py` | 29 |
| `_mine_inheritance_patterns` | Function | `scripts/python/miner/pattern_miner.py` | 76 |
| `_mine_naming_patterns` | Function | `scripts/python/miner/pattern_miner.py` | 149 |
| `_mine_param_patterns` | Function | `scripts/python/miner/pattern_miner.py` | 251 |
| `_mine_return_type_patterns` | Function | `scripts/python/miner/pattern_miner.py` | 387 |
| `_mine_decorator_patterns` | Function | `scripts/python/miner/pattern_miner.py` | 107 |
| `_mine_structure_patterns` | Function | `scripts/python/miner/pattern_miner.py` | 220 |
| `_mine_file_patterns` | Function | `scripts/python/miner/pattern_miner.py` | 282 |
| `_mine_docstring_patterns` | Function | `scripts/python/miner/pattern_miner.py` | 335 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Cmd_analyze → CodePattern` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Generator | 1 calls |

## How to Explore

1. `gitnexus_context({name: "mine_patterns"})` — see callers and callees
2. `gitnexus_query({query: "miner"})` — find related execution flows
3. Read key files listed above for implementation details
