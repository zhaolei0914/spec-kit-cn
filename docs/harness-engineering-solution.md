# Harness Engineering 解决方案文档

> **项目**: Spec Kit CN (spec-kit-cn)
> **编写日期**: 2026-03-30
> **前置文档**: [harness-engineering-analysis.md](./harness-engineering-analysis.md)
> **目标**: 从当前 ⭐⭐⭐ (3.1/5) 提升至 ⭐⭐⭐⭐½ (4.5/5)

---

## 目录

- [一、解决方案总览](#一解决方案总览)
- [二、P0 — 确定性验证工具](#二p0--确定性验证工具)
- [三、P0 — 可观测性体系](#三p0--可观测性体系)
- [四、P1 — Harness 配置层](#四p1--harness-配置层)
- [五、P1 — 工作流编排引擎](#五p1--工作流编排引擎)
- [六、P2 — 安全 Harness](#六p2--安全-harness)
- [七、P2 — Agent 快照/回滚](#七p2--agent-快照回滚)
- [八、P3 — Prompt 版本管理](#八p3--prompt-版本管理)
- [九、P3 — 跨项目学习与 Dry-run](#九p3--跨项目学习与-dry-run)
- [十、实施路线图](#十实施路线图)
- [十一、目录结构变更](#十一目录结构变更)
- [十二、预期成效](#十二预期成效)

---

## 一、解决方案总览

### 1.1 设计原则

| 原则 | 说明 |
|------|------|
| **渐进增强** | 在现有命令体系上叠加能力，不破坏已有流程 |
| **确定性优先** | 能用脚本验证的，不依赖 LLM 判断 |
| **配置驱动** | 阈值、规则、权限集中配置，可按项目定制 |
| **最小侵入** | 新增的 Harness 组件作为独立模块，通过 Hook 点接入现有流程 |
| **可观测性原生** | 每个组件内建日志和指标输出 |

### 1.2 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    Harness 配置层                         │
│              .specify/harness/config.yml                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ 确定性    │  │ 可观测性  │  │ 安全     │  │ 编排    │ │
│  │ 验证工具  │  │ 体系     │  │ Harness  │  │ 引擎    │ │
│  │          │  │          │  │          │  │         │ │
│  │ • Linter │  │ • 日志   │  │ • 敏感   │  │ • 状态  │ │
│  │ • 结构测试│  │ • 指标   │  │   信息   │  │   机    │ │
│  │ • CI Hook│  │ • 审计   │  │ • 权限   │  │ • 进度  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       │             │             │              │       │
├───────┴─────────────┴─────────────┴──────────────┴──────┤
│                  现有 SDD 工作流命令                       │
│          /0 → /1 → /2 → /3 → /4 → /5 → /6 → /8 → /9   │
│                    → /10 → /11                           │
└─────────────────────────────────────────────────────────┘
```

### 1.3 对标差距-解决方案映射

| GAP ID | 差距描述 | 解决方案 | 优先级 |
|--------|---------|---------|--------|
| GAP-C1 | 确定性验证工具缺失 | P0 — 自定义 Linter + 结构化测试 + CI Hook | P0 |
| GAP-C2 | 可观测性体系缺失 | P0 — 执行日志 + 质量指标 + 审计追踪 | P0 |
| GAP-C3 | Harness 配置层缺失 | P1 — 集中配置文件 + 环境适配 | P1 |
| GAP-M1 | 工作流编排引擎缺失 | P1 — 状态机 + 进度持久化 | P1 |
| GAP-M2 | Agent 快照/回滚缺失 | P2 — 制品快照 + 回滚命令 | P2 |
| GAP-M3 | Prompt 版本管理缺失 | P3 — 变更日志 + 效果评估 | P3 |
| GAP-M4 | 安全 Harness 缺失 | P2 — 敏感信息检测 + 权限白名单 | P2 |

---

## 二、P0 — 确定性验证工具

> **解决 GAP-C1**: 从"LLM 说了算"进化到"LLM + 确定性双重验证"

### 2.1 制品结构 Linter

**目标**: 用确定性脚本验证 specs/ 目录下的文档结构完整性。

**实现**: 创建 `.specify/scripts/harness/lint-specs.sh`

```bash
#!/bin/bash
# specs/ 目录结构 Linter
# 用法: lint-specs.sh <REQ_ID>
# 返回: 0=通过, 1=有错误, 2=有警告

REQ_ID="$1"
SPEC_DIR="specs/${REQ_ID}"
ERRORS=0; WARNINGS=0

# --- 规则 1: 必需文件检查 ---
check_required_file() {
    local file="$1" desc="$2"
    if [[ ! -f "${SPEC_DIR}/${file}" ]]; then
        echo "❌ [ERROR] 缺少必需文件: ${file} (${desc})"
        ((ERRORS++))
    fi
}

check_required_file "requirement.md" "需求文档"
check_required_file "spec.md" "功能规范"

# --- 规则 2: FR 追溯完整性 ---
# 检查 spec.md 中的每个 FR-xxx 是否在 tasks.md 中有对应任务
if [[ -f "${SPEC_DIR}/spec.md" && -f "${SPEC_DIR}/tasks.md" ]]; then
    while IFS= read -r fr_id; do
        if ! grep -q "$fr_id" "${SPEC_DIR}/tasks.md"; then
            echo "⚠️ [WARN] ${fr_id} 在 spec.md 中定义但 tasks.md 中无对应任务"
            ((WARNINGS++))
        fi
    done < <(grep -oE 'FR-[0-9]+' "${SPEC_DIR}/spec.md" | sort -u)
fi

# --- 规则 3: 设计追溯标记检查 ---
# 检查代码文件中是否包含 FR-xxx 或 design.md 追溯注释
check_code_traceability() {
    local code_dir="$1"
    if [[ -d "$code_dir" ]]; then
        local files_without_trace=0
        while IFS= read -r file; do
            if ! grep -qE '(FR-[0-9]+|design\.md|设计追溯)' "$file"; then
                echo "⚠️ [WARN] ${file} 缺少设计追溯注释"
                ((WARNINGS++))
                ((files_without_trace++))
            fi
        done < <(find "$code_dir" -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.sh" -o -name "*.go" -o -name "*.java" \) 2>/dev/null)
    fi
}

# --- 规则 4: 模板合规性检查 ---
# 检查 spec.md 是否包含必需章节
if [[ -f "${SPEC_DIR}/spec.md" ]]; then
    for section in "用户故事" "功能需求" "成功标准"; do
        if ! grep -q "$section" "${SPEC_DIR}/spec.md"; then
            echo "❌ [ERROR] spec.md 缺少必需章节: ${section}"
            ((ERRORS++))
        fi
    done
fi

# --- 规则 5: 禁止模糊词检查 ---
if [[ -f "${SPEC_DIR}/tasks.md" ]]; then
    for word in "快速" "高效" "可扩展" "安全" "健壮" "合理" "适当" "TODO" "TKTK" "???"; do
        count=$(grep -c "$word" "${SPEC_DIR}/tasks.md" 2>/dev/null || echo 0)
        if [[ "$count" -gt 0 ]]; then
            echo "⚠️ [WARN] tasks.md 包含模糊词「${word}」(${count}处)"
            ((WARNINGS++))
        fi
    done
fi

# --- 规则 6: [NEEDS CLARIFICATION] 残留检查 ---
for file in requirement.md spec.md design.md; do
    if [[ -f "${SPEC_DIR}/${file}" ]]; then
        count=$(grep -c "NEEDS CLARIFICATION" "${SPEC_DIR}/${file}" 2>/dev/null || echo 0)
        if [[ "$count" -gt 0 ]]; then
            echo "❌ [ERROR] ${file} 包含 ${count} 个未解决的 [NEEDS CLARIFICATION]"
            ((ERRORS++))
        fi
    fi
done

# --- 汇总 ---
echo ""
echo "========================================"
echo "  Lint 结果: 错误 ${ERRORS} | 警告 ${WARNINGS}"
echo "========================================"

if [[ $ERRORS -gt 0 ]]; then exit 1
elif [[ $WARNINGS -gt 0 ]]; then exit 2
else exit 0; fi
```

### 2.2 跨制品一致性测试

**目标**: 确定性验证 spec↔design↔tasks↔code 的引用完整性。

**实现**: 创建 `.specify/scripts/harness/consistency-check.sh`

```bash
#!/bin/bash
# 跨制品一致性检查
# 确定性验证 spec ↔ design ↔ tasks 之间的引用

REQ_ID="$1"
SPEC_DIR="specs/${REQ_ID}"
ERRORS=0

# 1. 提取 spec.md 中所有 FR-xxx
spec_frs=$(grep -oE 'FR-[0-9]+' "${SPEC_DIR}/spec.md" 2>/dev/null | sort -u)

# 2. 提取 design.md 中引用的 FR-xxx
design_frs=$(grep -oE 'FR-[0-9]+' "${SPEC_DIR}/design.md" 2>/dev/null | sort -u)

# 3. 提取 tasks.md 中引用的 FR-xxx
tasks_frs=$(grep -oE 'FR-[0-9]+' "${SPEC_DIR}/tasks.md" 2>/dev/null | sort -u)

# 4. 检查 spec→design 覆盖
echo "=== spec.md → design.md 覆盖检查 ==="
for fr in $spec_frs; do
    if ! echo "$design_frs" | grep -q "$fr"; then
        echo "⚠️ ${fr} 在 spec.md 中定义，但 design.md 中未引用"
        ((ERRORS++))
    fi
done

# 5. 检查 spec→tasks 覆盖
echo "=== spec.md → tasks.md 覆盖检查 ==="
for fr in $spec_frs; do
    if ! echo "$tasks_frs" | grep -q "$fr"; then
        echo "❌ ${fr} 在 spec.md 中定义，但 tasks.md 中无对应任务"
        ((ERRORS++))
    fi
done

# 6. 检查 tasks 中引用的 FR 是否都在 spec 中定义
echo "=== tasks.md → spec.md 反向检查 ==="
for fr in $tasks_frs; do
    if ! echo "$spec_frs" | grep -q "$fr"; then
        echo "⚠️ ${fr} 在 tasks.md 中引用，但 spec.md 中未定义（幽灵引用）"
        ((ERRORS++))
    fi
done

# 7. 用户故事一致性: spec 中的用户故事标签是否在 tasks 中都有体现
echo "=== 用户故事覆盖检查 ==="
spec_stories=$(grep -oE '用户故事[0-9]+' "${SPEC_DIR}/spec.md" 2>/dev/null | sort -u)
for story in $spec_stories; do
    # tasks.md 中使用 [故事N] 格式
    story_num=$(echo "$story" | grep -oE '[0-9]+')
    if ! grep -qE "\[故事${story_num}\]" "${SPEC_DIR}/tasks.md" 2>/dev/null; then
        echo "⚠️ ${story} 在 spec.md 中定义，但 tasks.md 中无对应 [故事${story_num}] 标签"
        ((ERRORS++))
    fi
done

echo ""
echo "========================================"
echo "  一致性检查: 发现 ${ERRORS} 个问题"
echo "========================================"

[[ $ERRORS -eq 0 ]] && exit 0 || exit 1
```

### 2.3 CI/CD 集成 Hook

**目标**: 在代码提交和 PR 时自动运行确定性验证。

**实现**: 创建 `.specify/scripts/harness/pre-commit-hook.sh`

```bash
#!/bin/bash
# Git pre-commit hook for Harness Engineering
# 安装: cp .specify/scripts/harness/pre-commit-hook.sh .git/hooks/pre-commit

HARNESS_DIR=".specify/scripts/harness"
ERRORS=0

echo "🔍 Harness Engineering Pre-commit Check..."

# 1. 检查所有活跃需求的制品完整性
for req_dir in specs/[0-9]*/; do
    if [[ -d "$req_dir" ]]; then
        req_id=$(basename "$req_dir")
        echo "  检查 ${req_id}..."
        
        # 运行 Lint
        if ! bash "${HARNESS_DIR}/lint-specs.sh" "$req_id" > /dev/null 2>&1; then
            echo "  ❌ ${req_id} Lint 检查失败"
            ((ERRORS++))
        fi
    fi
done

# 2. 敏感信息检测
echo "  检查敏感信息..."
if grep -rn -E '(password|secret|api_key|token)\s*=\s*["\x27][^"\x27]+["\x27]' \
    --include="*.py" --include="*.js" --include="*.ts" --include="*.sh" \
    --exclude-dir=".git" --exclude-dir="node_modules" . 2>/dev/null; then
    echo "  ❌ 发现硬编码的敏感信息"
    ((ERRORS++))
fi

# 3. 检查是否有未同步的 changelog
if [[ -f ".ai-changelogs.md" ]]; then
    unsync_count=$(sed -n '/^## 未同步/,/^## /p' .ai-changelogs.md | grep -c '^\- \*\*\[')
    if [[ "$unsync_count" -gt 0 ]]; then
        echo "  ⚠️ 有 ${unsync_count} 条未同步的 changelog 条目"
    fi
fi

if [[ $ERRORS -gt 0 ]]; then
    echo ""
    echo "❌ Pre-commit 检查失败 (${ERRORS} 个错误)"
    echo "   运行 'bash ${HARNESS_DIR}/lint-specs.sh <REQ_ID>' 查看详情"
    exit 1
fi

echo "✅ Pre-commit 检查通过"
exit 0
```

### 2.4 与现有命令的集成方式

在现有命令的关键节点调用确定性验证：

| 命令 | 集成点 | 调用的验证 |
|------|--------|-----------|
| `/2-需求规范` 步骤3 后 | 生成 spec.md 后 | `lint-specs.sh` 检查必需章节 |
| `/4-实施步骤` 步骤5 后 | 生成 tasks.md 后 | `consistency-check.sh` 跨制品一致性 |
| `/5-实施前检测` 步骤4 后 | 一致性分析后 | `consistency-check.sh` + `lint-specs.sh` |
| `/6-编写代码` 自愈循环后 | 代码完成后 | `lint-specs.sh` FR 追溯检查 |

**集成示例**（在命令模板中添加）:

```markdown
### 步骤 X.X: 确定性验证（自动执行）

// turbo
```bash
bash .specify/scripts/harness/lint-specs.sh [REQ_ID]
bash .specify/scripts/harness/consistency-check.sh [REQ_ID]
```

如果验证失败，在继续下一步之前必须修复所有 ❌ ERROR 级别的问题。
⚠️ WARN 级别的问题记录到报告中，不阻塞流程。
```

---

## 三、P0 — 可观测性体系

> **解决 GAP-C2**: 使 Harness 效果可量化、可改进

### 3.1 工作流执行日志

**目标**: 记录每次命令执行的元数据，便于回溯和分析。

**实现**: 创建 `.specify/harness/execution-log.md`

每次命令执行时，在命令开头和结尾记录日志：

```markdown
# 工作流执行日志

<!-- 
  本文件由 Harness 系统自动维护。
  记录每次 SDD 命令的执行信息。
  保留最近 100 条，超出自动归档。
-->

## 活跃记录

### [2026-03-30T10:15:00] /2-需求规范

| 属性 | 值 |
|------|------|
| **命令** | /2-需求规范 |
| **需求 ID** | 001-user-auth |
| **执行角色** | BA/PM |
| **状态** | ✅ 完成 |
| **耗时** | ~15 分钟 |
| **关键输出** | specs/001-user-auth/spec.md |
| **质量指标** | 覆盖扫描: 10/10 ✅, FR 数量: 12 |
| **确定性验证** | lint: ✅ 0错误/2警告 |
| **备注** | 无 |

---
```

**命令模板集成**: 在每个命令的开头和结尾添加日志记录步骤。

```markdown
### 步骤 0: 记录执行开始（自动）

在 `.specify/harness/execution-log.md` 的「活跃记录」章节顶部追加一条新记录，
填写命令名、需求 ID、执行角色、开始时间。状态标记为「⏳ 执行中」。

---
[... 命令主体 ...]
---

### 步骤 N: 记录执行结束（自动）

更新 `.specify/harness/execution-log.md` 中当前执行的记录：
- 状态更新为 ✅ 完成 / ❌ 失败 / ⏸️ 暂停
- 填写耗时、关键输出、质量指标
- 如果日志超过 100 条，将最早的条目移到「归档记录」章节
```

### 3.2 质量指标聚合

**目标**: 提供跨需求的质量趋势视图。

**实现**: 创建 `.specify/harness/quality-metrics.md`

```markdown
# 质量指标仪表板

## 总体指标

| 指标 | 值 | 趋势 |
|------|------|------|
| 活跃需求数 | X | - |
| 平均 FR 覆盖率 | XX% | ↑/↓/→ |
| 平均 Lint 通过率 | XX% | ↑/↓/→ |
| 自愈循环平均轮次 | X.X | ↑/↓/→ |
| 平均缺陷密度 | X.X/需求 | ↑/↓/→ |
| 人工干预率 | XX% | ↑/↓/→ |

## 最近 10 个需求的质量趋势

| 需求 ID | FR 覆盖率 | Lint 通过 | 一致性检查 | 自愈轮次 | 测试通过率 | 综合 |
|---------|-----------|----------|-----------|---------|-----------|------|
| 001-xxx | 95% | ✅ | ✅ | 1 | 88% | ⭐⭐⭐⭐ |
| 002-xxx | 87% | ⚠️ | ✅ | 2 | 92% | ⭐⭐⭐⭐ |

## 常见问题 Top 5

| 排名 | 问题类型 | 出现次数 | 典型原因 |
|------|---------|---------|---------|
| 1 | FR 追溯缺失 | X | 编码时遗漏追溯注释 |
| 2 | 模糊词残留 | X | tasks.md 生成时用词不精确 |
```

**更新时机**: 由 `/9-测试验证` 完成时和 `/11-归档需求` 时自动更新。

### 3.3 决策审计日志

**目标**: 记录关键的人工决策和 Agent 决策点。

**实现**: 创建 `.specify/harness/audit-log.md`

```markdown
# 决策审计日志

<!-- 
  记录 Harness 中的关键决策点。
  包括人工审批、Agent 判断、质量门控结果。
-->

## 审计记录

### [2026-03-30T11:30:00] 发布决策

| 属性 | 值 |
|------|------|
| **需求 ID** | 001-user-auth |
| **决策类型** | 发布审批 |
| **决策者** | 用户（人工） |
| **决策结果** | ✅ 批准发布 |
| **依据** | 测试通过率 95%, 无致命缺陷 |
| **相关报告** | specs/001-user-auth/test/result.md |
```

**记录时机**:

| 命令 | 决策点 | 记录内容 |
|------|--------|---------|
| `/1` | 需求澄清回答 | 用户选择了哪个选项 |
| `/3` | 设计检测结果确认 | 是否通过、修改了什么 |
| `/5` | 严重问题处理决策 | 是否修复、如何修复 |
| `/6` | design.md 一致性预检查确认 | 用户确认或拒绝 |
| `/6` | 自愈循环升级到人工 | 剩余问题和用户决策 |
| `/9` | 发布建议决策 | 可发布/修复后发布/不建议发布 |

---

## 四、P1 — Harness 配置层

> **解决 GAP-C3**: 使 Harness 可配置、可复用

### 4.1 集中配置文件

**实现**: 创建 `.specify/harness/config.yml`

```yaml
# Harness Engineering 配置文件
# 所有工作流命令、验证工具和观测组件从此文件读取配置

harness:
  version: "1.0"
  project_name: ""  # 由 /0-制定项目上下文 填充

# --- 质量门控阈值 ---
quality_gates:
  # /2-需求规范: 覆盖扫描阈值
  spec_coverage:
    min_categories_pass: 8  # 10类扫描中至少通过8类
    max_needs_clarification: 3  # 最多3个待澄清标记
  
  # /5-实施前检测: 一致性阈值
  consistency:
    max_critical_issues: 0  # 严重问题: 0 容忍
    max_high_issues: 3      # 高优问题上限
    min_coverage_percent: 90  # 需求-任务覆盖率下限
  
  # /6-编写代码: 自愈循环配置
  self_healing:
    max_rounds: 3           # 最大自愈轮次
    min_quality_score: 90   # 综合评分阈值(%)
    auto_fix_severity: ["critical", "high"]  # 自动修复的严重性级别
  
  # /9-测试验证: 测试阈值
  testing:
    min_pass_rate_p0: 100   # P0 用例必须 100% 通过
    min_pass_rate_overall: 85  # 整体通过率下限
    max_skip_rate: 20       # 跳过率上限(%)

# --- 确定性验证配置 ---
linting:
  enabled: true
  rules:
    required_files: ["requirement.md", "spec.md"]
    required_spec_sections: ["用户故事", "功能需求", "成功标准"]
    forbidden_words: ["快速", "高效", "可扩展", "安全", "健壮", "合理", "适当", "TODO", "TKTK", "???"]
    max_task_hours: 4
    min_task_hours: 0.5

# --- 安全配置 ---
security:
  sensitive_patterns:
    - '(password|secret|api_key|token)\s*=\s*["\x27][^"\x27]+["\x27]'
    - 'BEGIN (RSA|DSA|EC) PRIVATE KEY'
    - 'AKIA[0-9A-Z]{16}'  # AWS Access Key
  dangerous_commands:
    - 'rm -rf /'
    - 'DROP TABLE'
    - 'DROP DATABASE'
    - 'FORMAT C:'
  file_access_whitelist:
    - "specs/"
    - "src/"
    - ".specify/"
    - ".windsurf/"

# --- 可观测性配置 ---
observability:
  execution_log:
    enabled: true
    max_entries: 100      # 活跃记录上限
    archive_threshold: 100
  quality_metrics:
    enabled: true
    update_on: ["/9", "/11"]  # 更新时机
  audit_log:
    enabled: true
    retention_days: 90

# --- 工作流编排配置 ---
orchestration:
  # 合法的命令转换路径
  workflow_transitions:
    "/0": ["/1"]
    "/1": ["/1", "/2"]        # 可自我循环修订
    "/2": ["/1", "/3", "/4"]  # 可回退到 /1
    "/3": ["/3", "/4"]        # 可自我循环修订
    "/4": ["/5"]
    "/5": ["/2", "/3", "/4", "/6"]  # 可回退修复
    "/6": ["/8"]
    "/8": ["/9"]
    "/9": ["/6", "/10", "/11"]  # 可回退修复 Bug
    "/10": ["/11"]
    "/11": ["/1"]              # 循环: 新需求开始
  
  # 需要新对话的转换
  require_new_session:
    - ["/2", "/3"]    # BA/PM → Architect
    - ["/5", "/6"]    # Architect → Developer
    - ["/6", "/8"]    # Developer → QA
```

### 4.2 配置读取集成

在每个命令模板的「加载上下文」步骤中添加：

```markdown
**加载 Harness 配置**（如果存在）:

```bash
cat .specify/harness/config.yml 2>/dev/null
```

从配置中提取当前命令相关的阈值参数，用于后续质量检查。
如果配置文件不存在，使用命令内置的默认值。
```

---

## 五、P1 — 工作流编排引擎

> **解决 GAP-M1**: 提升工作流的自动化和可靠性

### 5.1 工作流进度文件

**目标**: 跨会话持久化工作流进度（参考 Anthropic 的 `claude-progress.txt`）。

**实现**: 创建 `.specify/harness/progress.md`

```markdown
# 工作流进度

<!-- 
  跨会话的工作流状态追踪。
  每次命令执行时读取和更新。
  新对话开始时，Agent 必须首先读取此文件。
-->

## 当前活跃需求

### 001-user-auth

| 属性 | 值 |
|------|------|
| **状态** | 🔄 实施中 |
| **当前阶段** | /6-编写代码 |
| **最后执行** | 2026-03-30T10:15:00 |
| **已完成步骤** | /1 ✅ → /2 ✅ → /3 ✅ → /4 ✅ → /5 ✅ → /6 🔄 |
| **未完成步骤** | /8 ⏳ → /9 ⏳ → /11 ⏳ |
| **阻塞项** | 无 |
| **下一步操作** | 继续 `/6-编写代码 001-user-auth`（任务 T015 起） |

### 002-payment-module

| 属性 | 值 |
|------|------|
| **状态** | 📝 需求阶段 |
| **当前阶段** | /2-需求规范 |
| **最后执行** | 2026-03-29T16:30:00 |
| **已完成步骤** | /1 ✅ → /2 🔄 |
| **阻塞项** | 3 个待澄清项 |
| **下一步操作** | 回到 `/1-需求分析 002-payment-module` 补充需求 |
```

### 5.2 前置条件自动验证

**目标**: 在工作流编排层（非命令内部）验证前置条件。

在每个命令的开头添加编排验证步骤：

```markdown
### 步骤 0.1: 工作流编排检查（自动）

1. 读取 `.specify/harness/progress.md`
2. 读取 `.specify/harness/config.yml` 中的 `workflow_transitions`
3. 检查当前命令是否是上一个完成命令的合法后续：
   - ✅ 合法 → 继续执行
   - ❌ 非法 → 警告用户，建议正确的命令序列
4. 如果配置了 `require_new_session`，检查是否在新对话中
5. 更新 progress.md：标记当前命令为「🔄 执行中」
```

### 5.3 进度恢复机制

新对话开始时的标准化恢复流程：

```markdown
### 新对话恢复协议

每次开启新的 AI 对话时，按以下顺序加载上下文：

1. 读取 `.specify/harness/progress.md` — 了解当前工作状态
2. 读取 `.specify/harness/config.yml` — 加载 Harness 配置
3. 读取 `.windsurf/skills/project-context/SKILL.md` — 项目规范
4. 根据 progress.md 中的「下一步操作」，自动建议用户执行的命令
```

---

## 六、P2 — 安全 Harness

> **解决 GAP-M4**: 降低 Agent 自主操作的安全风险

### 6.1 敏感信息检测

**实现**: 创建 `.specify/scripts/harness/security-scan.sh`

```bash
#!/bin/bash
# 安全扫描: 检测代码中的敏感信息
# 用法: security-scan.sh [目录]

TARGET="${1:-.}"
ISSUES=0

echo "🔒 安全扫描: ${TARGET}"

# 1. 硬编码密码/密钥
echo "--- 检查硬编码凭据 ---"
results=$(grep -rn -E \
    '(password|secret|api_key|token|apikey|access_key)\s*[:=]\s*["\x27][^"\x27]{8,}["\x27]' \
    --include="*.py" --include="*.js" --include="*.ts" --include="*.sh" \
    --include="*.java" --include="*.go" --include="*.yml" --include="*.yaml" \
    --exclude-dir=".git" --exclude-dir="node_modules" --exclude-dir=".venv" \
    "$TARGET" 2>/dev/null)
if [[ -n "$results" ]]; then
    echo "❌ 发现硬编码凭据:"
    echo "$results"
    ((ISSUES++))
fi

# 2. 私钥文件
echo "--- 检查私钥文件 ---"
if grep -rn "BEGIN.*PRIVATE KEY" --include="*.pem" --include="*.key" \
    --exclude-dir=".git" "$TARGET" 2>/dev/null; then
    echo "❌ 发现私钥文件"
    ((ISSUES++))
fi

# 3. AWS 凭据
echo "--- 检查云凭据 ---"
if grep -rn -E 'AKIA[0-9A-Z]{16}' --exclude-dir=".git" "$TARGET" 2>/dev/null; then
    echo "❌ 发现 AWS Access Key"
    ((ISSUES++))
fi

echo ""
echo "========================================"
echo "  安全扫描: 发现 ${ISSUES} 个安全问题"
echo "========================================"

[[ $ISSUES -eq 0 ]] && exit 0 || exit 1
```

### 6.2 权限声明模型

在每个命令模板开头添加权限声明：

```markdown
### 权限声明

| 权限 | 范围 | 说明 |
|------|------|------|
| **读取** | specs/, .specify/, .windsurf/, src/ | 加载上下文和制品 |
| **写入** | specs/[ID]/ | 仅限当前需求目录 |
| **执行** | .specify/scripts/harness/ | 运行验证脚本 |
| **禁止** | rm -rf, DROP TABLE, 生产环境操作 | 不可执行的危险操作 |
```

---

## 七、P2 — Agent 快照/回滚

> **解决 GAP-M2**: 支持安全实验和错误恢复

### 7.1 制品快照命令

**实现**: 创建新的工具命令 `.specify/scripts/harness/snapshot.sh`

```bash
#!/bin/bash
# 制品快照: 保存当前 specs/ 目录状态
# 用法: snapshot.sh <REQ_ID> [描述]

REQ_ID="$1"
DESC="${2:-checkpoint}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SNAPSHOT_DIR=".specify/harness/snapshots/${REQ_ID}/${TIMESTAMP}_${DESC}"

mkdir -p "$SNAPSHOT_DIR"
cp -r "specs/${REQ_ID}/" "$SNAPSHOT_DIR/"

echo "✅ 快照已保存: ${SNAPSHOT_DIR}"
echo "   恢复命令: bash .specify/scripts/harness/restore.sh ${REQ_ID} ${TIMESTAMP}_${DESC}"
```

### 7.2 制品恢复命令

```bash
#!/bin/bash
# 制品恢复: 从快照恢复 specs/ 目录
# 用法: restore.sh <REQ_ID> <SNAPSHOT_NAME>

REQ_ID="$1"
SNAPSHOT_NAME="$2"
SNAPSHOT_DIR=".specify/harness/snapshots/${REQ_ID}/${SNAPSHOT_NAME}"

if [[ ! -d "$SNAPSHOT_DIR" ]]; then
    echo "❌ 快照不存在: ${SNAPSHOT_DIR}"
    exit 1
fi

# 备份当前状态
BACKUP_DIR=".specify/harness/snapshots/${REQ_ID}/pre_restore_$(date +%Y%m%d_%H%M%S)"
cp -r "specs/${REQ_ID}/" "$BACKUP_DIR/"

# 恢复
cp -r "${SNAPSHOT_DIR}/${REQ_ID}/"* "specs/${REQ_ID}/"
echo "✅ 已恢复到快照: ${SNAPSHOT_NAME}"
echo "   恢复前备份: ${BACKUP_DIR}"
```

### 7.3 自动快照时机

| 命令 | 快照时机 | 快照描述 |
|------|---------|---------|
| `/2-需求规范` 完成后 | spec.md 生成后 | `post-spec` |
| `/3-开发设计` 完成后 | design.md 生成后 | `post-design` |
| `/4-实施步骤` 完成后 | tasks.md 生成后 | `post-tasks` |
| `/5-实施前检测` 通过后 | 一致性验证通过 | `pre-implement` |
| `/6-编写代码` 完成后 | 代码实现完成 | `post-implement` |

---

## 八、P3 — Prompt 版本管理

> **解决 GAP-M3**: 持续优化命令模板质量

### 8.1 命令模板变更日志

**实现**: 创建 `templates/commands/CHANGELOG.md`

```markdown
# 命令模板变更日志

## [v1.1] - 2026-03-30

### 变更
- `/6-编写代码`: 添加确定性验证集成点
- `/2-需求规范`: 增强覆盖扫描的模糊词检测
- 所有命令: 添加执行日志记录步骤

### 新增
- `/harness-report`: 生成 Harness 质量报告

## [v1.0] - 初始版本

### 包含命令
- /0 到 /11 全套 SDD 工作流命令
- api-skill-extract, business-rules-extract 工具命令
```

### 8.2 Prompt 效果评估

在 `/11-归档需求` 的记忆精炼阶段添加：

```markdown
### 阶段 X: Prompt 效果评估

回顾本需求的执行日志，评估各命令的效果：

1. **自愈循环轮次**: 如果 > 2 轮，分析原因，考虑改进命令模板
2. **手动干预次数**: 如果 > 3 次，分析哪些步骤需要更好的指导
3. **一致性检查问题**: 如果 > 5 个，分析哪些模板的约束不够

将评估结果追加到 `templates/commands/CHANGELOG.md` 的改进建议章节。
```

---

## 九、P3 — 跨项目学习与 Dry-run

### 9.1 Dry-run 模式

在 Harness 配置中添加 dry-run 支持：

```yaml
# config.yml 中添加
execution:
  dry_run: false  # true 时所有写操作变为预览
```

命令模板中添加 dry-run 检查：

```markdown
### Dry-run 检查

如果 `.specify/harness/config.yml` 中 `execution.dry_run` 为 true：
- 所有文件写入操作改为输出预览（显示将要写入的内容，但不实际写入）
- 所有脚本执行改为输出命令（显示将要执行的命令，但不实际执行）
- 在输出中标注 `[DRY-RUN]` 前缀
```

### 9.2 跨项目最佳实践导出

在 `/11-归档需求` 后添加可选的导出步骤：

```markdown
### 可选: 导出跨项目最佳实践

如果本需求产出了有价值的通用经验（满足: 技术栈无关 + 可泛化 + 已验证）：

1. 提取到 `.specify/harness/shared-practices.md`
2. 格式:
   - **实践标题**: [简短标题]
   - **来源项目**: [项目名]
   - **来源需求**: [需求ID]
   - **适用场景**: [什么时候用]
   - **实践内容**: [具体做法]
```

---

## 十、实施路线图

### Phase 1 (Week 1-2): P0 基础设施

| 任务 | 产出 | 工作量 |
|------|------|--------|
| 创建 `lint-specs.sh` | 制品结构 Linter | 1天 |
| 创建 `consistency-check.sh` | 跨制品一致性测试 | 1天 |
| 创建 `pre-commit-hook.sh` | Git Hook 集成 | 0.5天 |
| 创建 `execution-log.md` | 执行日志模板 | 0.5天 |
| 创建 `quality-metrics.md` | 质量指标模板 | 0.5天 |
| 创建 `audit-log.md` | 审计日志模板 | 0.5天 |
| 更新命令模板（集成验证+日志） | 14个命令模板更新 | 2天 |

### Phase 2 (Week 3-4): P1 配置与编排

| 任务 | 产出 | 工作量 |
|------|------|--------|
| 创建 `config.yml` | Harness 配置文件 | 1天 |
| 创建 `progress.md` | 工作流进度文件 | 0.5天 |
| 实现前置条件自动验证 | 命令模板更新 | 1天 |
| 实现进度恢复机制 | 新对话恢复协议 | 0.5天 |
| 集成配置读取到所有命令 | 命令模板更新 | 1天 |

### Phase 3 (Week 5-6): P2 安全与快照

| 任务 | 产出 | 工作量 |
|------|------|--------|
| 创建 `security-scan.sh` | 安全扫描脚本 | 1天 |
| 实现权限声明模型 | 命令模板更新 | 0.5天 |
| 创建 `snapshot.sh` / `restore.sh` | 快照/恢复脚本 | 1天 |
| 集成自动快照时机 | 命令模板更新 | 0.5天 |

### Phase 4 (Week 7-8): P3 优化与迭代

| 任务 | 产出 | 工作量 |
|------|------|--------|
| 创建命令模板 CHANGELOG | Prompt 版本管理 | 0.5天 |
| 实现 Prompt 效果评估 | /11 命令更新 | 0.5天 |
| 实现 Dry-run 模式 | 命令模板更新 | 1天 |
| 创建 Harness 报告命令 | 新命令模板 | 1天 |

---

## 十一、目录结构变更

### 新增文件和目录

```
.specify/
├── harness/                          # [新增] Harness Engineering 核心
│   ├── config.yml                    # [新增] 集中配置文件
│   ├── execution-log.md              # [新增] 工作流执行日志
│   ├── quality-metrics.md            # [新增] 质量指标仪表板
│   ├── audit-log.md                  # [新增] 决策审计日志
│   ├── progress.md                   # [新增] 工作流进度追踪
│   ├── shared-practices.md           # [新增] 跨项目最佳实践
│   └── snapshots/                    # [新增] 制品快照目录
│       └── [REQ_ID]/
│           └── [TIMESTAMP]_[DESC]/
├── scripts/
│   ├── harness/                      # [新增] Harness 验证脚本
│   │   ├── lint-specs.sh             # [新增] 制品结构 Linter
│   │   ├── consistency-check.sh      # [新增] 跨制品一致性测试
│   │   ├── security-scan.sh          # [新增] 安全扫描
│   │   ├── pre-commit-hook.sh        # [新增] Git Hook
│   │   ├── snapshot.sh               # [新增] 制品快照
│   │   └── restore.sh               # [新增] 制品恢复
│   └── ...（现有脚本不变）
└── templates/
    └── commands/
        ├── CHANGELOG.md              # [新增] 命令模板变更日志
        └── ...（现有命令模板更新）
```

### 现有命令模板变更摘要

| 命令 | 变更内容 |
|------|---------|
| 所有命令 | 添加步骤0（执行日志记录）和步骤N（结束日志记录） |
| 所有命令 | 添加 Harness 配置读取 |
| 所有命令 | 添加权限声明章节 |
| `/2-需求规范` | 步骤3后添加确定性验证调用 |
| `/4-实施步骤` | 步骤5后添加一致性检查脚本调用 |
| `/5-实施前检测` | 步骤4后添加确定性验证调用 |
| `/6-编写代码` | 自愈循环后添加 Lint 检查；关键节点自动快照 |
| `/9-测试验证` | 完成时更新质量指标 |
| `/11-归档需求` | 添加 Prompt 效果评估；更新质量指标 |

---

## 十二、预期成效

### 量化目标

| 指标 | 当前 | 目标 | 提升 |
|------|------|------|------|
| Harness 综合评分 | ⭐⭐⭐ (3.1/5) | ⭐⭐⭐⭐½ (4.5/5) | +45% |
| 确定性验证覆盖 | 0% | 80%+ | 从0到1 |
| 可观测性成熟度 | Level 1 (事后报告) | Level 3 (实时追踪+趋势) | +2级 |
| 跨制品一致性问题检出率 | ~60% (仅LLM) | 95%+ (LLM+确定性) | +58% |
| 工作流恢复时间 | 手动回忆 (~10min) | 自动恢复 (~1min) | -90% |
| 安全漏洞检出 | 无检测 | 提交时自动检测 | 从0到1 |

### 五大支柱预期评分

| 支柱 | 当前 | 目标 | 提升措施 |
|------|------|------|---------|
| 工具编排 | ⭐⭐⭐ | ⭐⭐⭐⭐ | +配置层 +权限模型 +工具注册 |
| 护栏与安全约束 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +确定性Linter +安全扫描 +CI Hook |
| 错误恢复与反馈 | ⭐⭐⭐½ | ⭐⭐⭐⭐½ | +快照回滚 +进度恢复 +循环检测 |
| 可观测性 | ⭐⭐ | ⭐⭐⭐⭐ | +执行日志 +质量指标 +审计追踪 |
| 人机协作 | ⭐⭐⭐ | ⭐⭐⭐⭐ | +决策记录 +可配置门控 +Dry-run |

---

## 参考文献

1. [OpenAI - Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
2. [Martin Fowler - Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)
3. [Anthropic - Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
4. [NxCode - What Is Harness Engineering? Complete Guide (2026)](https://www.nxcode.io/resources/news/what-is-harness-engineering-complete-guide-2026)
5. [LangChain - Improving Deep Agents with Harness Engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)
