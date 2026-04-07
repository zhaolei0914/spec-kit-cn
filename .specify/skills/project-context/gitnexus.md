---
skill_id: project-context/gitnexus
title: "Gitnexus 模块详情"
description: "gitnexus 模块的文件、符号、入口点和执行流详情"
triggers:
  - gitnexus
  - Gitnexus
generated_at: "2026-04-02T13:24:32.629102"
generator: "gitnexus"
---

# Gitnexus

18 个符号 | 1 个文件 | 内聚度: 93%

## 使用场景

- 处理 `templates/`
- 理解 load_gitnexus_meta, load_gitnexus_skills, parse_skill_md 的工作原理
- 修改 gitnexus 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | load_gitnexus_meta, load_gitnexus_skills, parse_skill_md, _store_table, generate_project_context_skill (+13) |

## 入口点

探索该模块的起点：

- **`load_gitnexus_meta`** (函数) — `templates/scripts/docker/gitnexus/gitnexus_to_skill.py:398`
- **`load_gitnexus_skills`** (函数) — `templates/scripts/docker/gitnexus/gitnexus_to_skill.py:407`
- **`parse_skill_md`** (函数) — `templates/scripts/docker/gitnexus/gitnexus_to_skill.py:428`
- **`generate_project_context_skill`** (函数) — `templates/scripts/docker/gitnexus/gitnexus_to_skill.py:498`
- **`translate_to_chinese`** (函数) — `templates/scripts/docker/gitnexus/gitnexus_to_skill.py:855`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `load_gitnexus_meta` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 398 |
| `load_gitnexus_skills` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 407 |
| `parse_skill_md` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 428 |
| `generate_project_context_skill` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 498 |
| `translate_to_chinese` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 855 |
| `generate_module_skill` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 906 |
| `generate_index_yaml` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 941 |
| `convert` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 999 |
| `main` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 1058 |
| `scan_project` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 159 |
| `_store_table` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 471 |
| `_add_unique` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 241 |
| `_parse_package_json` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 246 |
| `_parse_pyproject_toml` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 273 |
| `_parse_requirements_txt` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 317 |
| `_parse_go_mod` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 336 |
| `_parse_pom_xml` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 356 |
| `_detect_frameworks` | 函数 | `templates/scripts/docker/gitnexus/gitnexus_to_skill.py` | 381 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Main → _add_unique` | 跨模块 | 6 |
| `Main → _store_table` | 模块内 | 5 |

## 关联模块

| 模块 | 连接数 |
|------|-------------|
| Scripts | 1 次调用 |
