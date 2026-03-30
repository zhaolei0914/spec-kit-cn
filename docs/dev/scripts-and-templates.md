# A. 脚本与模板体系（commands + scripts + templates）

Spec Kit 的“工作流行为”主要不是写在 Python 里，而是写在：

- `templates/commands/*.md`（命令规范 + 脚本调用入口）
- `scripts/`（bash/PowerShell 负责真正落地）
- `templates/*.md`（spec/plan/tasks/checklist 等产物模板）

## 1. 三层关系（从用户输入到产物落盘）

1) 用户在 AI agent 中输入 `/speckit.xxx ...`

2) agent 根据命令文件（`templates/commands/xxx.md`）

- 运行某个脚本（`scripts/.../*.sh|*.ps1`）
- 读取/写入 specs 产物
- 按模板约束输出结构

3) 脚本落盘到用户项目目录中的 `specs/NNN-feature/`、`memory/` 等。

## 2. commands（命令定义）

目录：`templates/commands/`

你会看到：

- `specify.md`：从自然语言生成 spec
- `plan.md`：生成 plan + 设计产物
- `tasks.md`：从 plan 派生任务清单
- `implement.md`：执行任务
- `clarify.md` / `checklist.md` / `analyze.md`：质量与一致性相关

这些文件通常包含：

- `scripts: { sh: ..., ps: ... }`
- `handoffs`：建议下一步调用哪个命令
- 详细的分步规范（强约束 LLM 行为）

## 3. templates（产物模板）

目录：`templates/`

- `spec-template.md`：spec 的结构规范（约束“讲 WHAT/WHY，不讲 HOW”）
- `plan-template.md`：计划模板（要求写技术上下文、gates、research、contracts 等）
- `tasks-template.md`：任务模板（要求可执行、可并行标记等）
- `checklist-template.md`：质量清单模板
- `agent-file-template.md`：从多个 plan 汇总后的 agent 上下文文件模板
- `vscode-settings.json`：VSCode 设置片段（推荐 prompt files + 允许自动批准脚本）

## 4. scripts（落地脚本）

目录：`scripts/bash` 与 `scripts/powershell`（双实现）

### 4.1 common.*（路径推导与 feature 识别）

- `get_repo_root`：优先 git，否则用脚本位置回退
- `get_current_branch`：
  - 优先 `SPECIFY_FEATURE` 环境变量
  - 其次 git branch
  - 否则扫描 `specs/` 找最大编号 feature

- `find_feature_dir_by_prefix`：
  - 从分支名提取 `NNN-` 前缀
  - 允许多个分支共用同一 specs（例如 `004-fix-x` 与 `004-add-y`）

### 4.2 create-new-feature.*（specify 阶段）

负责：

- 生成/清洗 short name
- 计算下一个编号（综合 branches + specs 目录最大号）
- 创建 `specs/NNN-xxx/` 并初始化 spec

### 4.3 check-prerequisites.*（前置检查）

负责：

- 校验 feature 目录、plan.md、tasks.md 是否存在
- 输出 JSON 供 commands 流程使用

### 4.4 update-agent-context.*（更新 agent 上下文）

负责：

- 从 `plan.md` 提取 `Language/Version`、`Primary Dependencies`、`Storage`、`Project Type`
- 更新各种 agent 规则/上下文文件

关键约束：

- 解析依赖 `plan.md` 的固定写法（`**Field**:`）。

## 5. 维护建议

- commands 与 scripts 是“行为契约”，修改要极度谨慎。
- 若需要扩展字段/解析：优先改 `plan-template.md` + 同步调整 `update-agent-context.*` 的解析规则。
- bash/ps 两套脚本必须同步改。
