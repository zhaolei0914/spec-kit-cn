# A. 新增/维护 AI Agent 支持

本文面向 Spec Kit 维护者：当你要新增一个 AI Agent（或维护已有 agent 的目录/命令形态）时，应该改哪些地方、遵循什么约束。

## 1. 总原则

- `AGENT_CONFIG` 是单一事实源（SSOT）。
- `AGENT_CONFIG` 的 key 必须使用“用户机器上真实可执行文件名”（如果需要检测 CLI）。
  - 例如 Cursor 用 `cursor-agent` 而不是 `cursor`。

## 2. 必改清单

### 2.1 `src/specify_cli/__init__.py`

在 `AGENT_CONFIG` 新增条目：

- `name`
- `folder`
- `install_url`（若 requires_cli=true）
- `requires_cli`

并同步更新：

- `init()` 命令的 `--ai` help 文本

### 2.2 `README.md`

更新 Supported AI Agents 表。

### 2.3 scripts（双实现）

- `scripts/bash/update-agent-context.sh`
- `scripts/powershell/update-agent-context.ps1`

新增该 agent 的目标上下文文件路径，并在 agent 分发逻辑里支持更新。

### 2.4 release/打包（若需要）

如果 release 会产出 agent 对应 zip：

- 更新 release packages 脚本
- 更新 GitHub release 产物列表

## 3. 快速自测路径

- 本地跑 CLI：
  - `python -m src.specify_cli init demo --ai <agent> --ignore-agent-tools --script sh|ps`

- 验证生成结构：
  - agent 目录（例如 `.windsurf/`、`.claude/`）是否存在
  - `templates/commands` 是否按 agent 约定生成

- 验证 agent 上下文更新：
  - 跑一次 `/speckit.plan`（对应脚本会触发 `update-agent-context`）

## 4. 常见坑

- 忘记同步 PowerShell 版本脚本。
- `requires_cli` 填错导致用户 init 被阻断或漏检。
- folder 命名不一致造成模板落盘路径错。
- 命令参数占位符不一致：Markdown 通常 `$ARGUMENTS`，TOML 通常 `{{args}}`。
