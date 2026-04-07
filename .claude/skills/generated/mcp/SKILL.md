---
name: mcp
description: "Skill for the Mcp area of repo. 21 symbols across 3 files."
---

# Mcp

21 symbols | 3 files | Cohesion: 78%

## When to Use

- Working with code in `scripts/`
- Understanding how load_patterns, get_id, to_dict work
- Modifying mcp-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/python/mcp/skill_converter.py` | SkillConverter, convert_patterns, convert_patterns_to_skills, convert_pattern, _generate_skill_name (+6) |
| `scripts/python/mcp/skill_schema.py` | get_id, to_dict, to_json, save_skills, Skill (+4) |
| `scripts/python/parser/base.py` | load_patterns |

## Entry Points

Start here when exploring this area:

- **`load_patterns`** (Function) — `scripts/python/parser/base.py:220`
- **`get_id`** (Function) — `scripts/python/mcp/skill_schema.py:100`
- **`to_dict`** (Function) — `scripts/python/mcp/skill_schema.py:138`
- **`to_json`** (Function) — `scripts/python/mcp/skill_schema.py:172`
- **`save_skills`** (Function) — `scripts/python/mcp/skill_schema.py:205`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `SkillConverter` | Class | `scripts/python/mcp/skill_converter.py` | 15 |
| `Skill` | Class | `scripts/python/mcp/skill_schema.py` | 68 |
| `SkillParameter` | Class | `scripts/python/mcp/skill_schema.py` | 33 |
| `SkillExample` | Class | `scripts/python/mcp/skill_schema.py` | 44 |
| `SkillMetadata` | Class | `scripts/python/mcp/skill_schema.py` | 55 |
| `load_patterns` | Function | `scripts/python/parser/base.py` | 220 |
| `get_id` | Function | `scripts/python/mcp/skill_schema.py` | 100 |
| `to_dict` | Function | `scripts/python/mcp/skill_schema.py` | 138 |
| `to_json` | Function | `scripts/python/mcp/skill_schema.py` | 172 |
| `save_skills` | Function | `scripts/python/mcp/skill_schema.py` | 205 |
| `convert_patterns` | Function | `scripts/python/mcp/skill_converter.py` | 88 |
| `convert_patterns_to_skills` | Function | `scripts/python/mcp/skill_converter.py` | 302 |
| `convert_pattern` | Function | `scripts/python/mcp/skill_converter.py` | 37 |
| `from_dict` | Function | `scripts/python/mcp/skill_schema.py` | 154 |
| `_generate_skill_name` | Function | `scripts/python/mcp/skill_converter.py` | 116 |
| `_generate_description` | Function | `scripts/python/mcp/skill_converter.py` | 146 |
| `_determine_category` | Function | `scripts/python/mcp/skill_converter.py` | 171 |
| `_generate_context_patterns` | Function | `scripts/python/mcp/skill_converter.py` | 221 |
| `_generate_tags` | Function | `scripts/python/mcp/skill_converter.py` | 283 |
| `_convert_examples` | Function | `scripts/python/mcp/skill_converter.py` | 193 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Convert_patterns_to_skills → Get` | cross_community | 5 |
| `Convert_patterns_to_skills → _generate_skill_name` | cross_community | 4 |
| `Convert_patterns_to_skills → _generate_description` | cross_community | 4 |
| `Convert_patterns_to_skills → Get_id` | intra_community | 4 |
| `To_json → Get_id` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Generator | 3 calls |

## How to Explore

1. `gitnexus_context({name: "load_patterns"})` — see callers and callees
2. `gitnexus_query({query: "mcp"})` — find related execution flows
3. Read key files listed above for implementation details
