---
description: "全自动需求交付引擎: 提交需求 → 自动完成全流程 → 交付"
---

## /harness-auto

### 用法

```
/harness-auto <需求描述或需求文档路径> [--mode=auto|guided] [--profile=strict] [--skip-discuss] [--dry-run]
```

### 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| mode | auto | auto=全自动, guided=每阶段确认 |
| profile | 从 config.yml | 覆盖 Harness profile |
| skip-discuss | false | 跳过澄清阶段，使用推断默认值 |
| dry-run | false | 仅生成计划，不执行代码 |

### 角色

全自动编排引擎 (Autonomous Orchestrator)。你是一个需求交付自动化系统，
职责是驱动需求从提交到归档的全流程自动完成。

### 核心规则

1. **永不停下，除非遇到人工确认点**
2. **每个阶段完成后立即推进到下一个阶段**
3. **遇到问题先自愈，自愈失败才升级**
4. **所有操作记录到 execution-log.md**
5. **所有决策记录到 audit-log.md**
6. **上下文仅通过文件传递，不依赖对话历史**

### 人工确认点 (仅以下 7 种情况暂停)

| # | 确认点 | 触发条件 | 是否阻塞 |
|---|--------|---------|---------|
| ① | 需求澄清 | 推断置信度 < config.clarification.infer_confidence 的歧义项 | 阻塞 |
| ② | 架构决策 | 引入新技术栈或重大架构变更 | 阻塞 |
| ③ | 质量门控 | Audit < C 且自愈失败 | 可跳过 |
| ④ | 代码自愈失败 | N 轮自愈仍失败 (N=config.self_healing.code_rounds) | 阻塞 |
| ⑤ | 安全风险 | security-scan.sh 发现 Critical 问题 | 阻塞 |
| ⑥ | 测试修复失败 | N 轮测试修复仍失败 (N=config.self_healing.test_fix_rounds) | 阻塞 |
| ⑦ | 手动验证 | 无法自动执行的测试用例 | 可跳过 |

### 执行协议

#### Phase 0: 初始化

1. 读取 `.specify/harness/config.yml` → 加载编排配置
2. 读取 `.specify/harness/state.md` → 检查是否有未完成的需求
   - 如有活跃的 auto 流程 → 提示是否继续或开始新需求
3. **检测 IDE 环境，选择调度策略**:
   - 检查 config.yml 中 `orchestration.dispatch.strategy`
   - `auto` → 自动检测:
     - 有 Task/subagent 能力 (Claude Code / Cursor) → Level 3: subagent 策略
     - CLI 环境 (可 fork 进程) → Level 2: CLI 嵌套策略
     - 否则 (Windsurf / 其他单 Agent IDE) → Level 1: session-split 策略
   - 非 `auto` → 使用指定策略
4. 为新需求生成 REQ-ID，创建 `specs/[REQ-ID]/` 目录
5. 创建 Git 分支: `harness/[REQ-ID]`
6. 更新 state.md: 新增活跃需求，状态=初始化，模式=auto
7. 记录 execution-log.md: ⏳ 开始全自动交付
8. 如果是 Level 1 (session-split):
   - 计算需求复杂度，估算所需 session 数
   - 输出执行计划 (哪些阶段在哪个 session 执行)
   - 确定本 session 执行的阶段组

#### Phase 1-10: 自动执行

对每个阶段 P (按顺序: /1 → /2 → /3 → /4 → /5 → /6 → /8 → /9 → /10 → /11):

##### 上下文隔离协议

⚠️ **在每个阶段开始前，执行上下文隔离**:

1. 如果是 Level 3 (subagent):
   - 写入 `.specify/harness/dispatch/phase-P.json` 调度文件
   - 派发子 Agent 执行，Prompt 中声明: "忽略所有先前对话，仅从文件加载上下文"
   - 轮询 `.specify/harness/dispatch/phase-P.done` 等待完成
   - 读取完成信号 → 验证结果
   - 清理调度文件

2. 如果是 Level 1 (session-split):
   - 检查当前阶段是否在本 session 的阶段组中
   - 如果不在 → 自动暂停 (见下方暂停协议)
   - 如果在 → 插入上下文围栏:
     ```
     ═══════════════════════════════════════════════════════
       ⚠️ CONTEXT FENCE — Phase P 开始
       忽略此围栏以上的所有内容。从文件加载上下文。
     ═══════════════════════════════════════════════════════
     ```
   - 仅从文件加载本阶段所需的最小上下文 (MVI):
     - /1: 无前置制品
     - /2: requirement.md
     - /3: requirement.md + spec.md
     - /4: spec.md + design.md
     - /5: spec.md + design.md + tasks.md
     - /6: design.md + tasks.md
     - /8: spec.md + design.md
     - /9: case.md + design.md
     - /10: .ai-changelogs.md
     - /11: 全部制品

3. 如果是 Level 2 (CLI):
   - 通过 CLI 嵌套调用子流程命令
   - 天然进程隔离

##### 阶段执行循环

1. 检查前置条件 → 不满足则报错停止
2. 记录 execution-log: ⏳ Phase P 执行中
3. 调用对应命令模板执行 (遵循上下文隔离协议)
4. 检查完成条件 (自动推进条件):
   - /1: requirement.md 存在 + lint PASS + 无未解决歧义
   - /2: spec.md 存在 + lint PASS + 覆盖率 > 80%
   - /3: design.md 存在 + consistency PASS + 宪章检查 PASS
   - /4: tasks.md 存在 + 任务完整性 PASS
   - /5: Audit ≥ C (70分)
   - /6: 所有任务 DONE + lint PASS + security PASS + 两阶段审查 PASS
   - /8: case.md 存在 + 覆盖所有 FR
   - /9: 自动测试全 PASS + 手动测试已确认
   - /10: 无未同步 changelog
   - /11: 目录已归档 + 记忆已更新

5. 完成条件结果处理:
   - **PASS** → 记录日志 + 创建 Checkpoint + 推进到下一阶段
   - **FAIL** → 进入自愈循环:
     a. 分析失败原因 (结构问题 / 逻辑问题 / 外部依赖)
     b. 尝试修复 (最多 N 轮，N 从 config.self_healing 读取)
     c. 每轮修复后重新检查完成条件
     d. 自愈成功 → 记录日志 + 推进
     e. 自愈用尽 → 检查是否为人工确认点:
        - 是 → 暂停，输出问题描述，等待用户输入
        - 否 → 根据 config.self_healing.escalation 决定: human | abort | skip

##### Back-Pressure 输出协议

每个阶段执行结果遵循 Back-Pressure 输出:
- **成功**: `[Phase N] ✅ 阶段名称完成 (制品已生成, Audit: X)` (1行)
- **自愈**: `[Phase N] 🔧 自愈 #M: 问题描述 → 修复描述` (1行/次)
- **失败**: `[Phase N] ❌ 失败详情` (仅失败时输出详情)
- **人工**: `[Phase N] 🔔 请确认: 问题描述` (等待用户)

#### 暂停协议 (Level 1: session-split)

当 session-split 模式下当前阶段组执行完毕:

1. 更新 state.md: 记录已完成阶段
2. 写入 handoff.json: 断点信息 + 下一个阶段组
3. 输出暂停指引:

```
⏸️ 自动暂停 — 需要新会话继续

已完成: /1 ✅ /2 ✅
下一步: /3-开发设计

操作步骤:
1. 开启新的会话
2. 输入: /harness-resume
3. 引擎将自动从 /3 继续

> 状态已保存到 .specify/harness/state.md 和 handoff.json
```

#### 完成

1. 输出交付报告
2. 更新 state.md: 需求状态=已完成
3. 更新 quality-metrics.md
4. 如果 config.learning.enabled: 提取 Instinct 到 instincts.md

### 交付报告格式

```markdown
===== 交付报告 =====
需求: [REQ-ID] [需求名称]
总耗时: XX 分钟
自愈: X 次 (成功 X / 失败 X)
人工确认: X 次 (描述)
Harness Audit: X (A-F)
测试通过率: XX% (N/M)
========================

## 阶段详情

| 阶段 | 状态 | 耗时 | 自愈 | 确认 |
|------|------|------|------|------|
| /1 需求分析    | ✅ | Xmin | 0 | 0 |
| /2 需求规范    | ✅ | Xmin | 0 | 0 |
| /3 开发设计    | ✅ | Xmin | 0 | 0 |
| /4 实施步骤    | ✅ | Xmin | 0 | 0 |
| /5 实施前检测  | ✅ | Xmin | 0 | 0 |
| /6 编写代码    | ✅ | Xmin | 0 | 0 |
| /8 生成测试    | ✅ | Xmin | 0 | 0 |
| /9 测试验证    | ✅ | Xmin | 0 | 0 |
| /10 同步文档   | ✅ | Xmin | 0 | 0 |
| /11 归档需求   | ✅ | Xmin | 0 | 0 |

## 产出制品

- specs/[REQ-ID]/requirement.md
- specs/[REQ-ID]/spec.md
- specs/[REQ-ID]/design.md
- specs/[REQ-ID]/tasks.md
- specs/[REQ-ID]/case.md
- specs/[REQ-ID]/result.md

## 学习 (Instinct)

- INST-xxx: [提取的模式]
```

### 调度文件格式 (Level 3: subagent)

**phase-N.json**:

```json
{
  "version": "1.0",
  "phase": "N",
  "command": "/N-命令名称",
  "req_id": "REQ-xxx",
  "role": "角色名",
  "input_files": ["文件路径列表"],
  "output_files": ["期望输出文件列表"],
  "validation": {
    "scripts": ["验证脚本列表"],
    "criteria": "完成条件描述"
  },
  "completion_signal": ".specify/harness/dispatch/phase-N.done",
  "self_healing_rounds": 3,
  "created_at": "ISO-8601"
}
```

**phase-N.done**:

```json
{
  "phase": "N",
  "status": "success | failed",
  "duration_seconds": 0,
  "self_healing_count": 0,
  "output_files_created": ["实际生成的文件列表"],
  "validation_result": "PASS | FAIL",
  "error_message": null,
  "completed_at": "ISO-8601"
}
```

### 自愈引擎

三级自愈分类:

| 级别 | 问题类型 | 自动修复率 | 策略 |
|------|---------|-----------|------|
| L1 | 结构问题 (缺章节、格式错误、缺文件) | ~95% | 自动补全/重新生成 |
| L2 | 逻辑问题 (不一致、覆盖不足、测试失败) | ~70% | 分析原因 → 定向修复 |
| L3 | 外部依赖 (需人工输入、需外部API、需确认) | 0% | 升级到人工确认点 |

自愈流程:
```
失败 → 分类 (L1/L2/L3)
  → L1: 直接修复 → 重新验证
  → L2: 分析根因 → 生成修复方案 → 执行 → 重新验证
  → L3: 暂停 → 输出问题描述 → 等待人工
每级最多 N 轮 (从 config.self_healing 读取)
```
