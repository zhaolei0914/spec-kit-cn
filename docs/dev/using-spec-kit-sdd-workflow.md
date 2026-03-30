# B. 在项目中使用 Spec Kit（SDD 工作流与产物）

本文面向“业务项目接手者”：你不是来维护 Spec Kit 的，而是要用它把需求变成可执行的规格、计划、任务并持续迭代。

## 1. 一句话理解 SDD

- 规格（spec）是源头，计划（plan）是技术翻译，任务（tasks）是可执行步骤。
- 代码是这些产物的表达，而不是唯一真相。

## 2. 典型 6 步流程（对应命令）

1) `/speckit.constitution`

- 输出到 `memory/constitution.md`
- 用来约束后续所有规划与实现

2) `/speckit.specify <需求描述>`

- 创建 feature：
  - 分支：`NNN-short-name`
  - 目录：`specs/NNN-short-name/`
  - 文件：`spec.md`

3) `/speckit.clarify`（可选但推荐）

- 收敛歧义，减少 plan 阶段返工

4) `/speckit.plan <技术栈/架构选择>`

- 生成/更新：
  - `plan.md`
  - `research.md`
  - `data-model.md`
  - `contracts/`
  - `quickstart.md`
- 并触发更新 agent 上下文文件（例如 `.windsurf/rules/...`）

5) `/speckit.tasks`

- 读 `plan.md` + 其它产物
- 输出 `tasks.md`（带依赖顺序与并行标记）

6) `/speckit.implement`

- 按 `tasks.md` 执行实现

## 3. 目录结构（用户项目里你会看到什么）

- `memory/`
  - `constitution.md`

- `specs/NNN-feature/`
  - `spec.md`：讲清 WHAT/WHY
  - `plan.md`：技术方案与 gates
  - `research.md`：关键技术决策依据
  - `data-model.md`：实体与关系
  - `contracts/`：API/事件契约
  - `quickstart.md`：验证路径
  - `tasks.md`：可执行任务列表

- `.specify/`
  - `scripts/`：实际脚本
  - `templates/`：产物模板

- agent 目录（取决于你选的 agent）：
  - `.windsurf/`、`.claude/`、`.cursor/`、`.github/agents/` 等

## 4. 特性定位：当前在做哪个 feature？

默认按 git 分支识别：

- 分支名形如 `NNN-xxx`
- 脚本会把当前分支映射到 `specs/NNN-xxx/`

无 git 仓库或需要覆盖时：

- 通过环境变量 `SPECIFY_FEATURE` 强制指定

并且脚本支持“同一 NNN 前缀多个分支复用同一 specs”这种模式。

## 5. 对新手最重要的两条实践

- `spec.md` 不要写实现细节（语言/框架/API）——把 HOW 留给 `plan.md`。
- `plan.md` 的格式不要随意改（`update-agent-context` 解析依赖固定字段写法）。

## 6. VSCode/IDE 侧的关键设置

模板里提供 `templates/vscode-settings.json`：

- 推荐启用 prompt files（让 agent 更容易发现 `/speckit.*` 命令）
- 允许对 `.specify/scripts/...` 的终端脚本自动批准（减少交互摩擦）

是否启用取决于你项目的安全策略。
