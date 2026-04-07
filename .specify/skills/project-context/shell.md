---
skill_id: project-context/shell
title: "Shell 模块详情"
description: "shell 模块的文件、符号、入口点和执行流详情"
triggers:
  - shell
  - Shell
generated_at: "2026-04-02T13:24:32.633223"
generator: "gitnexus"
---

# Shell

12 个符号 | 4 个文件 | 内聚度: 79%

## 使用场景

- 处理 `scripts/`
- 理解 analyze_project, generate_skills, run_all 的工作原理
- 修改 shell 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `scripts/shell/skill_main.py` | analyze_project, generate_skills, run_all, main |
| `templates/scripts/shell/skill_main.py` | analyze_project, generate_skills, run_all, main |
| `scripts/shell/extractor/fusion.py` | to_dict, save, ShellKnowledgeBaseFusion |
| `scripts/shell/generator/skill_generator.py` | ShellSkillGenerator |

## 入口点

探索该模块的起点：

- **`analyze_project`** (函数) — `scripts/shell/skill_main.py:21`
- **`generate_skills`** (函数) — `scripts/shell/skill_main.py:56`
- **`run_all`** (函数) — `scripts/shell/skill_main.py:86`
- **`main`** (函数) — `scripts/shell/skill_main.py:153`
- **`analyze_project`** (函数) — `templates/scripts/shell/skill_main.py:21`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `ShellSkillGenerator` | 类 | `scripts/shell/generator/skill_generator.py` | 178 |
| `ShellKnowledgeBaseFusion` | 类 | `scripts/shell/extractor/fusion.py` | 124 |
| `analyze_project` | 函数 | `scripts/shell/skill_main.py` | 21 |
| `generate_skills` | 函数 | `scripts/shell/skill_main.py` | 56 |
| `run_all` | 函数 | `scripts/shell/skill_main.py` | 86 |
| `main` | 函数 | `scripts/shell/skill_main.py` | 153 |
| `analyze_project` | 函数 | `templates/scripts/shell/skill_main.py` | 21 |
| `generate_skills` | 函数 | `templates/scripts/shell/skill_main.py` | 56 |
| `run_all` | 函数 | `templates/scripts/shell/skill_main.py` | 86 |
| `main` | 函数 | `templates/scripts/shell/skill_main.py` | 153 |
| `to_dict` | 函数 | `scripts/shell/extractor/fusion.py` | 41 |
| `save` | 函数 | `scripts/shell/extractor/fusion.py` | 83 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Main → ShellKnowledgeBase` | 跨模块 | 4 |
| `Main → ShellFunctionExtractor` | 跨模块 | 4 |
| `Main → ShellVariableExtractor` | 跨模块 | 4 |
| `Main → ShellCommentExtractor` | 跨模块 | 4 |
| `Main → To_dict` | 模块内 | 4 |
| `Main → ShellProjectPatterns` | 跨模块 | 4 |
| `Main → ShellKnowledgeBase` | 跨模块 | 4 |
| `Main → ShellFunctionExtractor` | 跨模块 | 4 |
| `Main → ShellVariableExtractor` | 跨模块 | 4 |
| `Main → ShellCommentExtractor` | 跨模块 | 4 |

## 关联模块

| 模块 | 连接数 |
|------|-------------|
| Extractor | 4 次调用 |
| Generator | 4 次调用 |
| Scripts | 2 次调用 |
