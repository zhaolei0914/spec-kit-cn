# A. 维护 Spec Kit（仓库维护者视角）

本文面向需要维护 `github/spec-kit` 仓库的人：你需要理解哪些目录是“产品表面”，哪些是“实现内核”，改动的风险点在哪里。

## 1. Spec Kit 的组成

- `Specify CLI`（Python 包：`specify-cli`）
  - 目标：把 Spec Kit 的模板/脚本/命令体系 bootstrap 到用户项目里。
  - 入口：`pyproject.toml` 的 `[project.scripts] specify = "specify_cli:main"`。

- `templates/`（模板与命令定义）
  - 目标：定义 SDD 产物结构（spec/plan/tasks/checklist）与 agent slash commands 的规范流程。

- `scripts/`（bash + PowerShell 脚本）
  - 目标：让命令真正“落地执行”，包括创建 feature、检查前置、生成计划、更新 agent 上下文等。

- `docs/`（DocFX 文档站源码）
  - 目标：Spec Kit 自己的对外文档（安装、快速开始、升级、本地开发）。

## 2. 关键权威位置（SSOT）

- `src/specify_cli/__init__.py`
  - CLI 的绝大多数逻辑集中在此文件。
  - `AGENT_CONFIG` 是 agent 元数据的单一事实源。

- `templates/commands/*.md`
  - 这是“用户与 AI agent 的实际交互流程规范”，属于行为契约。
  - 任何改动都可能改变用户工作流，属于高影响变更。

- `scripts/bash/common.sh`、`scripts/powershell/common.ps1`
  - 这是 feature 识别与路径推导的权威逻辑。

## 3. 修改的高风险区域（优先谨慎）

- 模板下载与解压合并逻辑（`specify init`）
  - 风险：覆盖用户已有文件、Windows/POSIX 差异、zip 结构差异、TLS/代理环境。

- `.vscode/settings.json` 合并逻辑
  - 风险：JSON 深度合并规则变化会影响用户 IDE 行为。

- feature 目录/分支号推导逻辑（`create-new-feature.*`、`common.*`）
  - 风险：编号冲突、非 git 仓库兼容、多个分支对应同一 specs 前缀。

- agent 上下文更新（`update-agent-context.*`）
  - 风险：依赖 `plan.md` 格式（例如 `**Language/Version**:`）的解析非常脆弱。

## 4. 本地开发与验证（维护者建议）

仓库已经在 `docs/local-development.md` 提供了建议路径，常用做法：

- 直接运行（最快）：
  - `python -m src.specify_cli --help`
  - `python -m src.specify_cli init demo --ai copilot --ignore-agent-tools --script sh`

- 可编辑安装（更接近用户安装形态）：
  - `uv venv`
  - `uv pip install -e .`
  - `specify --help`

## 5. 发布/版本约束

- 若修改 `src/specify_cli/__init__.py` 的对外行为或 agent 列表：
  - 需要同步更新 `pyproject.toml` 的版本号
  - 需要更新 `CHANGELOG.md`

## 6. 本仓库与“被 bootstrap 的用户项目”的边界

Spec Kit 仓库里：

- `templates/`、`scripts/`、`src/specify_cli/` 是“生成器”

被 bootstrap 的用户项目里：

- 生成出来的 `.specify/`、`specs/`、`memory/`、以及 agent 目录（如 `.windsurf/`、`.claude/`）才是“运行时工作区”。
