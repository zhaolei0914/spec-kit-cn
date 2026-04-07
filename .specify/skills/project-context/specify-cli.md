---
skill_id: project-context/specify-cli
title: "Specify_cli 模块详情"
description: "specify-cli 模块的文件、符号、入口点和执行流详情"
triggers:
  - specify-cli
  - Specify_cli
generated_at: "2026-04-02T13:24:32.633550"
generator: "gitnexus"
---

# Specify_cli

34 个符号 | 1 个文件 | 内聚度: 90%

## 使用场景

- 处理 `src/`
- 理解 attach_refresh, add, start 的工作原理
- 修改 specify_cli 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `src/specify_cli/__init__.py` | StepTracker, attach_refresh, add, start, complete (+29) |

## 入口点

探索该模块的起点：

- **`attach_refresh`** (函数) — `src/specify_cli/__init__.py:254`
- **`add`** (函数) — `src/specify_cli/__init__.py:257`
- **`start`** (函数) — `src/specify_cli/__init__.py:262`
- **`complete`** (函数) — `src/specify_cli/__init__.py:265`
- **`error`** (函数) — `src/specify_cli/__init__.py:268`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `StepTracker` | 类 | `src/specify_cli/__init__.py` | 244 |
| `attach_refresh` | 函数 | `src/specify_cli/__init__.py` | 254 |
| `add` | 函数 | `src/specify_cli/__init__.py` | 257 |
| `start` | 函数 | `src/specify_cli/__init__.py` | 262 |
| `complete` | 函数 | `src/specify_cli/__init__.py` | 265 |
| `error` | 函数 | `src/specify_cli/__init__.py` | 268 |
| `skip` | 函数 | `src/specify_cli/__init__.py` | 271 |
| `render` | 函数 | `src/specify_cli/__init__.py` | 293 |
| `format_help` | 函数 | `src/specify_cli/__init__.py` | 429 |
| `show_banner` | 函数 | `src/specify_cli/__init__.py` | 443 |
| `callback` | 函数 | `src/specify_cli/__init__.py` | 458 |
| `check_tool` | 函数 | `src/specify_cli/__init__.py` | 483 |
| `is_git_repo` | 函数 | `src/specify_cli/__init__.py` | 514 |
| `init_git_repo` | 函数 | `src/specify_cli/__init__.py` | 534 |
| `download_and_extract_template` | 函数 | `src/specify_cli/__init__.py` | 750 |
| `ensure_executable_scripts` | 函数 | `src/specify_cli/__init__.py` | 920 |
| `init` | 函数 | `src/specify_cli/__init__.py` | 965 |
| `check` | 函数 | `src/specify_cli/__init__.py` | 1267 |
| `download_template_from_github` | 函数 | `src/specify_cli/__init__.py` | 636 |
| `version` | 函数 | `src/specify_cli/__init__.py` | 1309 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Init → _maybe_refresh` | 模块内 | 5 |
| `Check → _maybe_refresh` | 模块内 | 5 |
| `Init → Create_selection_panel` | 跨模块 | 4 |
| `Init → Get_key` | 跨模块 | 4 |
| `Main → _maybe_refresh` | 跨模块 | 4 |
| `Download_and_extract_template → _maybe_refresh` | 模块内 | 4 |
| `Download_and_extract_template → _github_token` | 跨模块 | 4 |
| `Download_and_extract_template → _parse_rate_limit_headers` | 跨模块 | 4 |
