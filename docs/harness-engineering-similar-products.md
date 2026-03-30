# Harness Engineering 同类产品分析与复用建议

> **项目**: Spec Kit CN (spec-kit-cn)
> **编写日期**: 2026-03-30
> **前置文档**: [harness-engineering-analysis.md](./harness-engineering-analysis.md) | [harness-engineering-solution.md](./harness-engineering-solution.md)
> **目标**: 识别可复用的同类产品和开源项目，加速 Harness Engineering 能力建设

---

## 目录

- [一、同类产品全景图](#一同类产品全景图)
- [二、SDD 工作流类产品](#二sdd-工作流类产品)
- [三、Harness 基础设施类产品](#三harness-基础设施类产品)
- [四、护栏与安全类产品](#四护栏与安全类产品)
- [五、Agent 运行时与编排类产品](#五agent-运行时与编排类产品)
- [六、方法论与参考实现](#六方法论与参考实现)
- [七、复用优先级矩阵](#七复用优先级矩阵)
- [八、详细复用方案](#八详细复用方案)
- [九、不建议复用的产品](#九不建议复用的产品)
- [十、总结](#十总结)

---

## 一、同类产品全景图

```
                    Harness Engineering 产品生态

+-------------------------------------------------------------+
|                     SDD 工作流层                              |
|  Spec Kit (GitHub) | Spec Kitty | OpenSpec | FSPEC | Kiro   |
+-------------------------------------------------------------+
|                     Harness 配置层                            |
|  CLAUDE.md | AGENTS.md | .cursor/rules | Skills | Hooks    |
+-------------------------------------------------------------+
|                     护栏与安全层                              |
|  Guardrails AI | Superagent | Claude Hooks | Custom Linter  |
+-------------------------------------------------------------+
|                     Agent 运行时层                            |
|  OpenDev | Claude Code | Codex CLI | OpenCode | Gemini CLI |
+-------------------------------------------------------------+
|                     方法论与参考                              |
|  12-Factor Agents | HumanLayer | Anthropic Best Practices   |
+-------------------------------------------------------------+
```

---

## 二、SDD 工作流类产品

### 2.1 Spec Kitty

| 属性 | 详情 |
|------|------|
| **GitHub** | [Priivacy-ai/spec-kitty](https://github.com/Priivacy-ai/spec-kitty) |
| **定位** | Spec-Driven Development for AI coding agents |
| **语言** | Python CLI (`pip install spec-kitty-cli`) |
| **版本** | v2.1.x，活跃开发中 |
| **工作流** | specify - plan - tasks - implement - review - merge |

**核心能力**:
- **实时看板仪表板**: `spec-kitty dashboard` 提供 Kanban 视图，实时追踪工作包(WP)状态
- **Git Worktree 隔离**: 每个功能分支使用独立 worktree，消除分支切换冲突
- **多 Agent 编排**: 外部编排器 API (`spec-kitty orchestrator-api`)，支持并行多 Agent 开发
- **Agent Skills Pack**: 捆绑的技能包，含教义(doctrine)文件
- **自动合并**: `spec-kitty accept` + `spec-kitty merge` 自动化 review-merge 流程

**可复用组件**:

| 组件 | 复用价值 | 对应 GAP |
|------|---------|----------|
| **实时仪表板** | 极高 | GAP-C2 可观测性 |
| **编排器 API** | 高 | GAP-M1 工作流编排 |
| **Worktree 策略** | 中 | GAP-M2 快照/回滚 |
| **Skills Pack** | 中 | 上下文工程 |

**复用建议**:
- 参考仪表板设计，为 `quality-metrics.md` 和 `execution-log.md` 提供可视化
- 研究编排器 API 设计，指导工作流状态机实现
- 借鉴 Worktree 策略实现更安全的并行开发

---

### 2.2 OpenSpec

| 属性 | 详情 |
|------|------|
| **GitHub** | [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) |
| **定位** | Lightweight spec layer for AI coding assistants |
| **语言** | Node.js (`npm install -g @fission-ai/openspec`) |
| **特点** | 轻量、无刚性阶段门控、支持 20+ AI 工具 |

**核心能力**:
- **轻量级规范层**: propose - apply - archive 三步流程
- **灵活的制品更新**: 任何时间可更新任何制品，无刚性阶段门控
- **多 Profile 支持**: `openspec config profile` 切换不同工作流配置
- **验证命令**: `/opsx:verify` 检查制品一致性

**可复用组件**:

| 组件 | 复用价值 | 对应 GAP |
|------|---------|----------|
| **Profile 配置** | 高 | GAP-C3 配置层 |
| **Verify 命令** | 中 | GAP-C1 确定性验证 |
| **多工具适配** | 中 | 工具编排 |

**复用建议**:
- 借鉴 Profile 机制，让 `config.yml` 支持多环境/多模式切换
- 其验证机制偏轻量，我们的护栏体系已更完善

---

### 2.3 FSPEC

| 属性 | 详情 |
|------|------|
| **GitHub** | [sengac/fspec](https://github.com/sengac/fspec) |
| **定位** | Spec-Driven, Multi-Agent Coding Factory ("Dark Factory") |
| **语言** | Node.js (`npm install @sengac/fspec`) |
| **特点** | Gherkin BDD + TDD + Kanban + Checkpoint |

**核心能力**:
- **Gherkin 驱动**: 强制使用 Given/When/Then 场景，自动生成测试
- **Checkpoint 系统**: `fspec restore-checkpoint <id>` 内置 Git 检查点，支持安全回滚
- **代码-业务规则追溯**: 每行代码链接回实现的业务规则
- **交互式看板**: 带附件查看器（支持 Mermaid 图表）
- **Dogfooding**: 项目本身用 FSPEC 构建（257 feature files）

**可复用组件**:

| 组件 | 复用价值 | 对应 GAP |
|------|---------|----------|
| **Checkpoint 系统** | 极高 | GAP-M2 快照/回滚 |
| **BDD 测试生成** | 高 | 护栏 - 从规范自动生成验收测试 |
| **追溯机制** | 中 | 确定性验证 - 代码追溯参考 |

**复用建议**:
- 直接参考 Checkpoint 系统设计 `snapshot.sh` / `restore.sh`
- 借鉴 Gherkin 到测试自动生成思路，增强 `/8-生成测试用例` 的确定性

---

### 2.4 Kiro (AWS)

| 属性 | 详情 |
|------|------|
| **官网** | [kiro.dev](https://kiro.dev) |
| **定位** | AWS 出品的 Spec-Driven AI IDE |
| **类型** | 商业产品（闭源 IDE） |

**核心能力**:
- **内置 Spec 工作流**: IDE 原生支持 spec - design - tasks 流程
- **Kiro Hooks**: 事件驱动的自动化，文件保存时触发 Agent 后台任务
- **Steering 机制**: 持续引导 Agent 行为
- **AWS 生态集成**: 深度集成 AWS 服务

**复用建议**:
- 参考 Hooks 事件驱动理念设计我们的 Hook 集成点
- 注意: 闭源产品，仅可参考设计理念

---

### 2.5 Spec Kit (GitHub 原版)

| 属性 | 详情 |
|------|------|
| **GitHub** | [github/spec-kit](https://github.com/github/spec-kit) |
| **关系** | spec-kit-cn 的上游项目 |

**复用建议**: 持续同步上游的 Harness Engineering 改进。

---

## 三、Harness 基础设施类产品

### 3.1 HumanLayer / Advanced Context Engineering

| 属性 | 详情 |
|------|------|
| **GitHub** | [humanlayer/advanced-context-engineering-for-coding-agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents) |
| **博客** | [humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents) |
| **定位** | Harness Engineering 最佳实践集合 |

**六大 Harness 配置面**:

| 配置面 | 说明 | 我们的现状 |
|--------|------|-----------|
| **CLAUDE.md / AGENTS.md** | 持久化项目上下文 | 已有 SKILL.md |
| **MCP Servers** | 工具编排和扩展 | 已有 Confluence MCP |
| **Skills** | 渐进式上下文披露 | 已有 Skills 系统 |
| **Sub-Agents** | 上下文隔离和专业化 | 已有角色分离 |
| **Hooks** | 确定性控制流注入 | **缺失 - 关键复用点** |
| **Back-Pressure** | 验证驱动反馈回路 | **缺失 - 关键复用点** |

**关键实践 - 可直接复用**:

1. **Hook 模式**: 在 Agent 停止时自动运行 formatter + typecheck。成功静默，失败才输出。这个模式可直接用于我们的确定性验证。

2. **Back-Pressure 上下文效率**: 只在失败时输出详细信息。避免通过测试的输出淹没上下文窗口。**这个原则必须应用到 lint/consistency 脚本设计中**。

3. **渐进式 Skill 披露**: 不把所有指令放进系统提示词，按需激活。我们的三层记忆系统已实现类似模式。

**复用价值**: 极高 - 直接采用 Hook 模式和 Back-Pressure 原则

---

### 3.2 Anthropic - Effective Harnesses for Long-Running Agents

| 属性 | 详情 |
|------|------|
| **URL** | [anthropic.com/engineering/effective-harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) |
| **定位** | Anthropic 官方长时 Agent Harness 最佳实践 |

**核心实践**:

| 实践 | 说明 | 复用价值 |
|------|------|---------|
| **claude-progress.txt** | 跨上下文窗口的进度追踪 | 极高 - 直接采用 |
| **Git 历史作上下文** | 启动时读 git log 恢复状态 | 高 |
| **Clean State Management** | 会话间清洁状态管理 | 高 |

**复用建议**:
- 直接采用 `progress.txt` 模式实现 `progress.md`
- 在新对话恢复协议中加入 `git log --oneline -20` 快速上下文

---

## 四、护栏与安全类产品

### 4.1 Guardrails AI

| 属性 | 详情 |
|------|------|
| **GitHub** | [guardrails-ai/guardrails](https://github.com/guardrails-ai/guardrails) |
| **定位** | LLM 输出验证和安全护栏框架 |
| **Stars** | 5k+ |

**核心能力**:
- **Input/Output Guards**: 检测、量化和缓解特定风险
- **Guardrails Hub**: 预建验证器市场（PII 检测、注入攻击等）
- **结构化输出验证**: Pydantic 风格的 LLM 输出验证
- **独立服务模式**: REST API 服务

**复用建议**:
- 中等优先级: 如需更强的安全检测，可集成其 PII 检测模块
- 对于纯 SDD 工作流，自定义 Linter 更直接有效

---

### 4.2 Superagent

| 属性 | 详情 |
|------|------|
| **GitHub** | [superagent-ai/superagent](https://github.com/superagent-ai/superagent) |
| **定位** | AI Agent 安全 SDK |

**核心能力**:
- **Prompt 注入防护**: 开源 HuggingFace 模型，本地 50-100ms
- **PII/Secret 脱敏**: 自动检测和脱敏
- **仓库安全扫描**: 代码仓库安全问题检测

**复用建议**:
- 中等优先级: 可集成替代简单的 grep 脚本做安全扫描
- 引入额外 Python 依赖，需评估成本

---

## 五、Agent 运行时与编排类产品

### 5.1 OpenDev

| 属性 | 详情 |
|------|------|
| **GitHub** | [opendev-to/opendev](https://github.com/opendev-to/opendev) |
| **论文** | [arxiv 2603.05344](https://arxiv.org/abs/2603.05344) |
| **定位** | 开源终端 AI 编码 Agent（复合 AI 系统） |
| **语言** | Rust（18MB 二进制，4.3ms 启动） |

**核心 Harness 三层架构**:

| 层次 | 说明 | 参考价值 |
|------|------|---------|
| **Scaffolding** | Agent 构建前的结构设置 | 对应 `/0-制定项目上下文` |
| **Harness** | 运行时编排: 工具、上下文、安全、持久化 | 核心参考 |
| **Safety** | 5 层防御架构 | GAP-M4 安全 |

**五层安全架构**:
1. Prompt 层护栏 - 系统提示词中的行为约束
2. Schema 层工具门控 - 双 Agent 分离（规划 vs 执行）
3. 权限边界 - 文件和命令的白名单/黑名单
4. 运行时监控 - 异常检测和循环打断
5. 会话隔离 - 并行 Agent 的状态隔离

**Agent Fleet**:
- 多个 Sub-Agent 并行，各自独立 LLM 绑定和上下文窗口
- 5 种工作流槽位: Normal, Thinking, Compact, Critique, VLM

**复用建议**:
- 高: 采用五层安全模型重新设计安全 Harness
- 中: 参考 Scaffolding/Harness 分离理念
- 注意: OpenDev 是运行时 Agent，我们是命令模板系统，参考设计理念为主

---

## 六、方法论与参考实现

### 6.1 12-Factor Agents (HumanLayer)

| 属性 | 详情 |
|------|------|
| **URL** | [humanlayer.dev/blog/12-factor-agents](https://www.humanlayer.dev/blog/12-factor-agents) |
| **定位** | 生产级 AI Agent 的 12 条工程原则 |

**可复用原则**:
- **LLMs 是无状态函数** - 需要外部状态管理 (对应 GAP-M1)
- **将工具视为代码** - 工具需要测试和版本管理 (对应 GAP-M3)
- **让人类参与高风险决策** - 设计 Human-in-the-Loop
- **频繁有意压缩** - research/plan/implement 流程
- **构建高杠杆人工审核** - 审核结果反馈到管线

---

### 6.2 OpenAI Codex 团队实践

| 属性 | 详情 |
|------|------|
| **URL** | [openai.com/index/harness-engineering](https://openai.com/index/harness-engineering/) |
| **规模** | 100 万行代码，全部由 Agent 编写 |
| **效率** | 3-7 人团队，平均 3.5 PR/人/天 |

**核心实践**:
- **AGENTS.md**: 机器可读的仓库级指令 (我们已有 SKILL.md)
- **可复现环境**: 一键启动 + worktree 隔离
- **CI 机械不变量**: 格式化、架构边界、数据验证 (**GAP-C1 关键复用点**)
- **"垃圾回收" Agent**: 定期巡检文档和架构违规 (我们的 `/10` `/11` 已部分实现)
- **失败即信号**: Agent 失败时改进 Harness 而非重试 (**方法论核心**)

---

### 6.3 LangChain Harness 驱动性能跃升

| 属性 | 详情 |
|------|------|
| **URL** | [blog.langchain.com/improving-deep-agents-with-harness-engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/) |
| **关键数据** | 仅改 Harness（不换模型），Terminal Bench 2.0 从 52.8% 升至 66.5% |

**复用启示**: 自验证循环 + 循环检测 = 最高杠杆的 Harness 改进

---

## 七、复用优先级矩阵

按 **影响力 x 复用成本** 排序:

| 优先级 | 来源 | 复用组件 | 解决 GAP | 成本 | 影响 |
|--------|------|---------|---------|------|------|
| **P0** | HumanLayer | Hook 模式 + Back-Pressure | GAP-C1 确定性验证 | 低 | 极高 |
| **P0** | Anthropic | progress.txt 模式 | GAP-M1 工作流编排 | 低 | 极高 |
| **P0** | OpenAI Codex | CI 机械不变量理念 | GAP-C1 确定性验证 | 中 | 极高 |
| **P1** | FSPEC | Checkpoint 系统 | GAP-M2 快照/回滚 | 低 | 高 |
| **P1** | Spec Kitty | 仪表板 + 编排器 API | GAP-C2 可观测性 | 高 | 高 |
| **P1** | OpenDev | 五层安全架构 | GAP-M4 安全 | 中 | 高 |
| **P1** | OpenSpec | Profile 配置机制 | GAP-C3 配置层 | 低 | 中 |
| **P2** | 12-Factor | 设计原则检查清单 | 全局设计 | 低 | 中 |
| **P2** | Guardrails AI | PII/Secret 检测 | GAP-M4 安全 | 中 | 中 |
| **P2** | Superagent | 仓库安全扫描 | GAP-M4 安全 | 中 | 中 |

---

## 八、详细复用方案

### 方案 A: 确定性验证 Hook (来源: HumanLayer + OpenAI)

**原理**: HumanLayer 在 Claude Stop Hook 中运行 formatter + typecheck，成功静默、失败输出。OpenAI 在 CI 中执行机械不变量。

**实现路径**:
```
.specify/scripts/harness/
  lint-specs.sh          # 制品结构 Linter
  consistency-check.sh   # 跨制品一致性
  pre-commit-hook.sh     # Git Hook

集成方式 1: Git pre-commit hook (对应 OpenAI CI 不变量)
集成方式 2: 命令模板内嵌调用 (对应 HumanLayer Stop Hook)
集成方式 3: Claude Code Hooks (如使用 Claude Code)
```

**关键设计原则** (来自 HumanLayer Back-Pressure):
- 验证通过时静默（不消耗上下文窗口）
- 验证失败时只输出失败项详细信息

---

### 方案 B: 跨会话进度恢复 (来源: Anthropic)

**原理**: 使用 progress 文件 + git history 实现跨上下文窗口状态恢复。

**实现路径**:
```
.specify/harness/progress.md   (对标 claude-progress.txt)

恢复协议（新对话第一步）:
1. 读取 progress.md     -> 当前工作状态
2. 读取 git log -20      -> 最近变更
3. 建议下一步操作
```

---

### 方案 C: Checkpoint 快照 (来源: FSPEC)

**原理**: 使用 Git tag/stash 实现检查点，支持一键恢复。

**实现路径**: 用 git tag 而非文件复制，更可靠高效:
```
snapshot: git tag "harness/checkpoint/{REQ_ID}/{DESC}"
restore: git checkout {TAG} -- "specs/{REQ_ID}/"
```

---

### 方案 D: 可视化仪表板 (来源: Spec Kitty)

**实现路径** (分阶段):
- **阶段 1** (低成本): 文本仪表板，由 `/9` 和 `/11` 更新 `quality-metrics.md`
- **阶段 2** (中成本): CLI 仪表板，用 Python rich 库渲染终端 UI
- **阶段 3** (高成本): Web 仪表板，参考 spec-kitty 的 Web 看板

---

### 方案 E: 五层安全模型 (来源: OpenDev)

**适配实现**:

| OpenDev 层 | 我们的对应 |
|-----------|-----------|
| 1. Prompt 层护栏 | 命令模板权限声明 + 禁止列表 |
| 2. Schema 层门控 | `/5-实施前检测` 只读模式 |
| 3. 权限边界 | `config.yml` 的 `file_access_whitelist` |
| 4. 运行时监控 | `security-scan.sh` + pre-commit hook |
| 5. 会话隔离 | 交接协议 + 角色分离 |

---

## 九、不建议复用的产品

| 产品 | 原因 |
|------|------|
| **LangChain/LangGraph** | 过于重量级的 Agent 框架，我们是命令模板系统而非运行时 Agent |
| **AutoGPT/CrewAI** | 通用 Agent 编排，与 SDD 工作流定位不同 |
| **Cursor Rules (直接复用)** | IDE 特定，无法跨 Agent 使用 |
| **Kiro (直接复用)** | 闭源 IDE，只能参考设计理念 |

---

## 十、总结

### 核心发现

1. **没有一个产品完整覆盖所有 Harness Engineering 能力**。每个产品在某些方面优秀，需要组合复用。

2. **最高杠杆的复用来自方法论和设计模式**，而非直接代码复制:
   - HumanLayer 的 Hook + Back-Pressure 模式
   - Anthropic 的 progress.txt 跨会话恢复
   - OpenAI 的 "失败即信号" 方法论
   - FSPEC 的 Checkpoint 机制

3. **我们的项目在 SDD 工作流层已经是最完善的之一**。11 个命令覆盖全生命周期 + 三层记忆系统 + 多层护栏，超过大多数竞品。主要短板在 Harness 基础设施层（可观测性、确定性验证、安全）。

4. **Spec Kitty 是最接近的竞品**，在仪表板和编排方面领先。但其 SDD 深度不如我们（无 10 类覆盖扫描、无自愈循环、无三层记忆）。

### 推荐的复用路线

| 阶段 | 复用来源 | 复用内容 | 产出 |
|------|---------|---------|------|
| Week 1-2 | HumanLayer + OpenAI | Hook 模式 + Back-Pressure + CI 不变量 | 确定性验证脚本 |
| Week 1-2 | Anthropic | progress.txt 模式 | 跨会话进度恢复 |
| Week 3-4 | FSPEC | Checkpoint 系统 | 快照/回滚脚本 |
| Week 3-4 | OpenSpec | Profile 机制 | Harness 配置层 |
| Week 5-6 | OpenDev | 五层安全模型 | 安全 Harness |
| Week 7-8 | Spec Kitty | 仪表板设计 | 质量指标可视化 |

### 一句话总结

> **借鉴 HumanLayer 的 Hook 模式做确定性验证，借鉴 Anthropic 的 progress.txt 做跨会话恢复，借鉴 FSPEC 的 Checkpoint 做快照回滚，借鉴 OpenDev 的五层模型做安全，借鉴 Spec Kitty 的仪表板做可观测性。方法论上以 OpenAI 的"失败即信号"和 12-Factor Agents 为指导原则。**

---

## 参考文献

1. [Spec Kitty - GitHub](https://github.com/Priivacy-ai/spec-kitty)
2. [OpenSpec - GitHub](https://github.com/Fission-AI/OpenSpec)
3. [FSPEC - GitHub](https://github.com/sengac/fspec)
4. [Kiro - AWS](https://kiro.dev)
5. [Spec Kit - GitHub](https://github.com/github/spec-kit)
6. [HumanLayer - Skill Issue: Harness Engineering](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents)
7. [Anthropic - Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
8. [Guardrails AI - GitHub](https://github.com/guardrails-ai/guardrails)
9. [Superagent - GitHub](https://github.com/superagent-ai/superagent)
10. [OpenDev - GitHub](https://github.com/opendev-to/opendev)
11. [OpenAI - Harness Engineering](https://openai.com/index/harness-engineering/)
12. [12-Factor Agents - HumanLayer](https://www.humanlayer.dev/blog/12-factor-agents)
13. [Martin Fowler - Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)
14. [LangChain - Improving Deep Agents](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)
