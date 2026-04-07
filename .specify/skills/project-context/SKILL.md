---
skill_id: project-context/SKILL
title: "specify-cn-cli 项目上下文"
description: "项目的技术栈、结构、方案、规范和环境的完整上下文，让 LLM 真正理解整个项目"
triggers:
  - 项目
  - 概述
  - 结构
  - 技术栈
  - 规范
  - 上下文
  - 入门
generated_at: "2026-04-02T13:24:32.624976"
generator: "gitnexus + project-scanner"
---

# specify-cn-cli 项目上下文

> {{LLM_PROJECT_SUMMARY}}
> <!-- 填充指导: 一句话概述项目用途和特点（20-50字） -->

---

## 一、技术栈上下文（用什么技术？）

### 编程语言

| 语言 | 文件数 | 占比 |
|------|--------|------|
| **Python** | 146 | 80% |
| **Shell/Bash** | 32 | 17% |
| **PowerShell** | 5 | 3% |

### 框架

{{LLM_FRAMEWORKS}}
<!-- 填充指导: 阅读代码中的 import 语句和配置文件，识别使用的框架 -->

### 中间件与数据存储

{{LLM_MIDDLEWARE}}
<!-- 填充指导: 从配置文件和依赖中识别使用的数据库、缓存、消息队列等中间件 -->

### 构建与工具链

- **构建**: Python, Hatch, pip
- **CI/CD**: GitHub Actions
- **容器化**: Docker

### 版本约束

- **Python**: `>=3.11`
- **项目版本**: `0.0.92`

---

## 二、项目结构上下文（代码怎么组织？）

### 整体架构

**架构类型**: CLI 工具 / 库 + 工具包 / 模板集

{{LLM_ARCHITECTURE_DETAIL}}
<!-- 填充指导: 基于上方自动检测的架构类型，补充 1-2 句描述：
     项目的分层方式、核心模块职责划分、前后端关系等 -->

### 目录结构

```
specify-cn-cli/
├── AGENTS.md
├── CLAUDE.md
├── ECC-INTEGRATION.md
├── LICENSE
├── build.sh
├── pyproject.toml
├── spec-driven.md
├── docs/              # 文档
├── ecc-components/    # ECC组件
├── media/             # 媒体资源
├── memory/            # 项目记忆
├── scripts/           # 分析/生成脚本
├── src/               # 核心源代码
├── templates/         # 模板文件
```

### 功能模块映射

物理目录与功能职责的对应关系：

| 目录 | 功能聚类 | 核心职责 | 文件数 |
|------|----------|----------|--------|
| `src/` | specify-cli | Specify_cli | 1 |
| `scripts/` | analyzer, django, extractor | Analyzer / Django | 131 |
| `templates/` | analyzer, django, extractor | Analyzer / Django | 115 |
| `ecc-components/` | scripts, tests | Scripts / Tests | 25 |

> 注：聚类名（如 Analyzer, Generator）是 GitNexus 根据代码调用关系自动识别的功能模块，详见各模块详情文件（`analyzer.md`, `generator.md` 等）

---

## 三、技术方案上下文（业务怎么实现？）

技术方案详情见各模块文件（入口点、执行流、关键符号）：

- `analyzer.md` — Analyzer — 5 入口点, 11 执行流
- `django.md` — Django — 5 入口点, 11 执行流
- `extractor.md` — Extractor — 5 入口点, 11 执行流
- `generator.md` — Generator — 5 入口点, 11 执行流
- `gitnexus.md` — Gitnexus — 5 入口点, 3 执行流

### 核心业务流程

{{LLM_BUSINESS_FLOWS}}
<!-- 填充指导: 根据上方入口点和执行流，用自然语言描述核心业务流程，例如：
     用户注册 → 参数校验 → 密码加密 → 入库 → 发送通知
     订单创建 → 库存检查 → 支付调用 → 状态更新 → 异步通知 -->

### 设计模式与架构决策

{{LLM_DESIGN_PATTERNS}}
<!-- 填充指导: 根据代码结构识别使用的设计模式，例如：
     - 工厂模式: XxxFactory 类
     - 策略模式: 多个 Handler 实现
     - 中间件模式: 请求处理链
     - 观察者模式: 事件发布/订阅 -->

---

## 四、开发规范上下文（代码怎么写才合规？）

### 项目核心原则

{{LLM_CORE_PRINCIPLES}}
<!-- 填充指导: 根据项目特点提炼 3-5 条核心原则，参考格式：
     1. **库优先**: 每个功能从独立库开始，自包含、可测试、有明确目的
     2. **CLI 接口**: 通过 CLI 暴露功能，stdin/args → stdout，错误 → stderr
     3. **测试优先**: TDD 强制要求，红-绿-重构循环
     4. **简单性**: 从简单开始，YAGNI 原则，复杂性需被证明
     5. **可观测性**: 文本 I/O 确保可调试，需要结构化日志 -->

### 命名规范

- **函数/方法**: `snake_case`
  — 如 `get_key`, `select_with_arrows`, `show_banner`, `callback`, `run_command`
- **类名**: `PascalCase`
  — 如 `StepTracker`, `BannerGroup`, `ShellProjectPatterns`, `ShellSkillGenerator`, `ShellFunctionExtractor`
- **文件名**: `snake_case`
- **常量**: `UPPER_SNAKE_CASE`

{{LLM_NAMING_EXTRA}}
<!-- 填充指导: 补充上述自动检测遗漏的命名规范（如接口路径前缀 /api/v1/ 等） -->

### 代码风格

- **缩进**: 4 空格缩进
- **文档注释**: 简单 docstring 风格
- **导入**: 绝对导入为主，分组排列
- **日志**: `print()`
- **错误处理**: `try/except` (226处), `raise` (33处)

{{LLM_CODE_STYLE_EXTRA}}
<!-- 填充指导: 补充上述自动检测遗漏的代码风格规范 -->

### 禁止规则

- ❌ 发现 389 处调试打印语句
- ❌ 发现 2 处裸 except:

{{LLM_FORBIDDEN_EXTRA}}
<!-- 填充指导: 补充上述自动检测遗漏的禁止规则 -->

---

## 五、环境与配置上下文（运行依赖什么？）

### 配置文件

- `pyproject.toml`

### 环境变量

**代码中使用的环境变量**:

- `ACTIVE_END`
- `ACTIVE_START`
- `AGENTS`
- `CLAUDE_CODE_ENTRYPOINT`
- `CLAUDE_PROJECT_DIR`
- `CLAUDE_SESSION_ID`
- `CLAUDE_TRANSCRIPT_PATH`
- `CLV2_CONFIG`
- `CLV2_IS_WINDOWS`
- `CLV2_OBSERVER_SENTINEL_FILE`
- `CLV2_PYTHON_CMD`
- `COMPACT_THRESHOLD`
- `ECC_HOOK_PROFILE`
- `ECC_OBSERVER_ALLOW_WINDOWS`
- `ECC_OBSERVER_ANALYSIS_COOLDOWN`
- `ECC_OBSERVER_MAX_ANALYSIS_LINES`
- `ECC_OBSERVER_MAX_TURNS`
- `ECC_OBSERVER_SIGNAL_EVERY_N`
- `ECC_OBSERVER_TIMEOUT_SECONDS`
- `ECC_OBSERVE_SKIP_PATHS`

（共 54 个，仅显示前 20 个）


### 部署方式

- **容器化**: Docker
- **CI/CD**: GitHub Actions

{{LLM_DEPLOYMENT}}
<!-- 填充指导: 描述项目的部署方式、运行命令和启动流程 -->

---

## 附录：模块详情导航

GitNexus 已识别出 15 个功能模块（如 analyzer, django...），
详见 `index.yaml` 或各模块 `.md` 文件（入口点、执行流、关键符号等详情）。
