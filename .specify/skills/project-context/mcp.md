---
skill_id: project-context/mcp
title: "Mcp 模块详情"
description: "mcp 模块的文件、符号、入口点和执行流详情"
triggers:
  - mcp
  - Mcp
generated_at: "2026-04-02T13:24:32.630847"
generator: "gitnexus"
---

# Mcp

41 个符号 | 5 个文件 | 内聚度: 78%

## 使用场景

- 处理 `scripts/`
- 理解 convert_pattern, get_id, to_dict 的工作原理
- 修改 mcp 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `scripts/python/mcp/skill_converter.py` | convert_pattern, _generate_skill_name, _generate_description, _determine_category, _generate_context_patterns (+6) |
| `templates/scripts/python/mcp/skill_converter.py` | convert_pattern, _generate_skill_name, _generate_description, _determine_category, _generate_context_patterns (+6) |
| `scripts/python/mcp/skill_schema.py` | Skill, get_id, to_dict, to_json, save_skills (+4) |
| `templates/scripts/python/mcp/skill_schema.py` | Skill, SkillParameter, SkillExample, SkillMetadata, from_dict (+4) |
| `scripts/python/parser/base.py` | load_patterns |

## 入口点

探索该模块的起点：

- **`convert_pattern`** (函数) — `scripts/python/mcp/skill_converter.py:37`
- **`get_id`** (函数) — `scripts/python/mcp/skill_schema.py:100`
- **`to_dict`** (函数) — `scripts/python/mcp/skill_schema.py:138`
- **`to_json`** (函数) — `scripts/python/mcp/skill_schema.py:172`
- **`save_skills`** (函数) — `scripts/python/mcp/skill_schema.py:205`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `Skill` | 类 | `scripts/python/mcp/skill_schema.py` | 68 |
| `SkillConverter` | 类 | `scripts/python/mcp/skill_converter.py` | 15 |
| `Skill` | 类 | `templates/scripts/python/mcp/skill_schema.py` | 68 |
| `SkillParameter` | 类 | `scripts/python/mcp/skill_schema.py` | 33 |
| `SkillExample` | 类 | `scripts/python/mcp/skill_schema.py` | 44 |
| `SkillMetadata` | 类 | `scripts/python/mcp/skill_schema.py` | 55 |
| `SkillParameter` | 类 | `templates/scripts/python/mcp/skill_schema.py` | 33 |
| `SkillExample` | 类 | `templates/scripts/python/mcp/skill_schema.py` | 44 |
| `SkillMetadata` | 类 | `templates/scripts/python/mcp/skill_schema.py` | 55 |
| `SkillConverter` | 类 | `templates/scripts/python/mcp/skill_converter.py` | 15 |
| `convert_pattern` | 函数 | `scripts/python/mcp/skill_converter.py` | 37 |
| `get_id` | 函数 | `scripts/python/mcp/skill_schema.py` | 100 |
| `to_dict` | 函数 | `scripts/python/mcp/skill_schema.py` | 138 |
| `to_json` | 函数 | `scripts/python/mcp/skill_schema.py` | 172 |
| `save_skills` | 函数 | `scripts/python/mcp/skill_schema.py` | 205 |
| `convert_patterns` | 函数 | `scripts/python/mcp/skill_converter.py` | 88 |
| `convert_patterns_to_skills` | 函数 | `scripts/python/mcp/skill_converter.py` | 302 |
| `convert_pattern` | 函数 | `templates/scripts/python/mcp/skill_converter.py` | 37 |
| `from_dict` | 函数 | `scripts/python/mcp/skill_schema.py` | 154 |
| `from_dict` | 函数 | `templates/scripts/python/mcp/skill_schema.py` | 154 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Convert_patterns_to_skills → SkillExample` | 跨模块 | 5 |
| `Convert_patterns_to_skills → SkillExample` | 跨模块 | 5 |
| `Convert_patterns_to_skills → _generate_skill_name` | 跨模块 | 4 |
| `Convert_patterns_to_skills → _generate_description` | 跨模块 | 4 |
| `Convert_patterns_to_skills → _determine_category` | 跨模块 | 4 |
| `Convert_patterns_to_skills → Get_id` | 模块内 | 4 |
| `Convert_patterns_to_skills → _generate_skill_name` | 跨模块 | 4 |
| `Convert_patterns_to_skills → _generate_description` | 跨模块 | 4 |
| `Convert_patterns_to_skills → _determine_category` | 跨模块 | 4 |
| `Convert_patterns_to_skills → Get_id` | 跨模块 | 4 |
