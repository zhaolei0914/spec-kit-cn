# 智能化项目上下文提取系统 - 完整方案

> **版本**: 1.0.0
> **日期**: 2025-01-22
> **目标**: 构建一个能够真正理解项目、自动生成开发规范、指导 AI 生成代码的智能系统

---

## 目录

1. [问题定义](#一问题定义)
2. [解决方案概述](#二解决方案概述)
3. [系统架构](#三系统架构)
4. [Skill 体系设计](#四skill-体系设计)
5. [代码分析方案](#五代码分析方案)
6. [防幻觉机制](#六防幻觉机制)
7. [实现路线图](#七实现路线图)
8. [预期产出](#八预期产出)

---

## 一、问题定义

### 1.1 当前痛点

| 痛点 | 描述 | 影响 |
|------|------|------|
| **被动式提取** | 需要预定义关键词，发现一个问题修一个 | 无法自动发现项目特有规范 |
| **结构分析局限** | 只分析代码结构，不理解内容和语义 | 遗漏错误码、常量、业务规则 |
| **单文件视角** | 每个文件独立分析 | 无法发现跨文件关系和模式 |
| **LLM 幻觉风险** | 大型项目 LLM 只能看到 <5% 代码 | 可能生成不存在的规范 |

### 1.2 目标

1. **自动发现**：无需预定义，自动发现项目中的所有开发规范
2. **深度理解**：理解代码结构、内容、语义、关系
3. **可信输出**：生成的规范 100% 有代码证据支撑
4. **指导生成**：输出的 Skill 能直接指导 AI 生成符合规范的代码

---

## 二、解决方案概述

### 2.1 核心理念

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           核心理念                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   代码分析（100% 准确）  +  LLM 辅助（受限使用）  =  可信的 Skill 文档       │
│                                                                             │
│   ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐    │
│   │  LibCST 全量    │      │  LLM 只做表达   │      │  每条规范都有   │    │
│   │  代码分析       │  →   │  不做创造       │  →   │  代码证据       │    │
│   └─────────────────┘      └─────────────────┘      └─────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 方案特点

| 特点 | 说明 |
|------|------|
| **代码驱动** | 所有数据来自代码分析，不是 LLM 推断 |
| **可验证** | 每条规范都有文件路径、行号、代码片段作为证据 |
| **动态加载** | Skill 按需加载，AI 只获取相关上下文 |
| **分层信任** | 区分事实层（100%）、统计层（95%）、推断层（70%）、建议层（50%） |

---

## 三、系统架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           系统整体架构                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Layer 1: 数据源                                   │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │ 源代码  │  │ 配置文件│  │ 文档    │  │ Git历史 │  │ 依赖文件│   │   │
│  │  │ *.py    │  │ *.yaml  │  │ *.md    │  │ commits │  │ req.txt │   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Layer 2: 代码分析（LibCST）                       │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │ 类提取  │  │ 函数    │  │ 常量    │  │ Import  │  │ 注释    │   │   │
│  │  │ 器      │  │ 提取器  │  │ 提取器  │  │ 提取器  │  │ 提取器  │   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Layer 3: 知识构建                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │ 模式挖掘    │  │ 关系分析    │  │ 统计汇总    │                  │   │
│  │  │ (高频模式)  │  │ (依赖/调用) │  │ (覆盖率)    │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Layer 4: Skill 生成                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │ 模板填充    │  │ LLM 描述    │  │ 验证检查    │                  │   │
│  │  │ (数据驱动)  │  │ (受限生成)  │  │ (防幻觉)    │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Layer 5: Skill 输出                               │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │ 项目级  │  │ 规范类  │  │ 辅助类  │  │ 业务类  │  │ 模板类  │   │   │
│  │  │ Skill   │  │ Skill   │  │ Skill   │  │ Skill   │  │ Skill   │   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 数据流

```
源代码 → LibCST解析 → 结构化数据 → 模式挖掘 → 知识库 → 模板填充 → Skill文档
                ↓                        ↓              ↓
           保留注释/格式            统计验证        LLM描述(可选)
                ↓                        ↓              ↓
           精确位置信息            置信度计算        验证检查
```

---

## 四、Skill 体系设计

### 4.1 Skill 定义

**Skill** 是一个自包含的知识单元，具有以下特点：

| 特点 | 说明 |
|------|------|
| **自包含** | 包含完成特定任务所需的全部信息 |
| **可索引** | 通过触发词可以快速定位 |
| **可组合** | 多个 Skill 可以组合使用 |
| **可验证** | 每条信息都有代码证据 |

### 4.2 Skill 分类

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Skill 分类体系                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Level 1: 项目级 Skill                                                      │
│  └── SKILL.md - 项目概述、技术栈、架构、模块划分                            │
│      触发词: "项目", "概述", "架构"                                          │
│                                                                             │
│  Level 2: 规范类 Skill                                                      │
│  ├── web.md - Web 接口开发规范                                              │
│  │   触发词: "API", "接口", "View", "HTTP", "请求", "响应"                 │
│  ├── models.md - 数据模型规范                                               │
│  │   触发词: "Model", "模型", "数据库", "字段", "ORM"                       │
│  ├── service.md - 服务层规范                                                │
│  │   触发词: "Service", "服务", "业务逻辑"                                  │
│  ├── handler.md - 处理器规范                                                │
│  │   触发词: "Handler", "处理器", "后台任务"                                │
│  ├── error.md - 错误处理规范                                                │
│  │   触发词: "异常", "错误", "错误码", "Exception", "raise"                │
│  ├── urls.md - URL 路由规范                                                 │
│  │   触发词: "URL", "路由", "path", "urlpatterns", "endpoint"              │
│  ├── middleware.md - 中间件规范                                             │
│  │   触发词: "中间件", "middleware", "拦截"                                 │
│  └── migrations.md - 数据库迁移规范                                         │
│      触发词: "迁移", "migration", "makemigrations", "migrate"               │
│                                                                             │
│  Level 3: 辅助类 Skill                                                      │
│  ├── imports.md - Import 模板                                               │
│  │   触发词: "import", "导入", "引用", "from"                               │
│  ├── constants.md - 常量定义规范                                            │
│  │   触发词: "常量", "枚举", "Enum", "状态码", "CONSTANT"                   │
│  ├── config.md - 配置规范                                                   │
│  │   触发词: "配置", "settings", "config", "环境变量"                       │
│  ├── logging.md - 日志规范                                                  │
│  │   触发词: "日志", "logger", "logging", "log"                            │
│  ├── naming.md - 命名规范                                                   │
│  │   触发词: "命名", "名称", "变量名", "函数名", "类名"                     │
│  └── test.md - 测试规范                                                     │
│      触发词: "测试", "test", "pytest", "unittest", "mock"                  │
│                                                                             │
│  Level 4: 业务类 Skill（待定，需明确业务需求后再实现）                      │
│  ├── glossary.md - 业务术语表                                               │
│  ├── entities.md - 业务实体                                                 │
│  ├── processes.md - 业务流程                                                │
│  └── rules.md - 业务规则                                                    │
│                                                                             │
│  注：模板类 Skill 已移除，代码模板整合到各规范类 Skill 的代码示例中         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Skill 结构

每个 Skill 文件包含：

```markdown
---
# YAML 头部 - 元数据
skill_id: project-context/web
skill_name: Web 接口开发规范
skill_type: coding_standard
triggers:                    # 触发词（用于动态加载）
  - "API"
  - "接口"
  - "View"
dependencies:                # 依赖的其他 Skill
  - project-context/error
  - project-context/imports
priority: 2                  # 优先级（1-5）
confidence: 0.95             # 整体置信度
version: 1.0.0
---

# 正文内容

## 适用场景
当你需要：创建 API 接口、修改接口、理解接口实现

## 核心规范 `[事实层 ✓]`

### 装饰器规范

**规范**：所有 View 类必须使用 `@formatting()` + `@authenticated()` 装饰器

**证据**：
- 来源：`v7tov8Service/views/job.py:15-30`
- 示例：
```python
# 来自 v7tov8Service/views/job.py:15-20
@formatting()
@authenticated()
def get(self, request):
    ...
```

## 检查清单
- [ ] 使用了正确的装饰器组合
- [ ] 导入了 V8 版本的装饰器
- [ ] 异常处理符合规范

## 相关 Skill
- 错误处理：`error.md`
- Import 模板：`imports.md`
```

### 4.4 触发词设计原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **覆盖多种表达** | 同一概念的不同说法 | API、接口、View、HTTP、请求 |
| **包含中英文** | 支持中英文混合表达 | Model、模型、数据库 |
| **包含动词** | 支持任务描述 | 创建、添加、修改、查询 |
| **避免过于通用** | 防止误匹配 | 避免单独使用 "的"、"是" |
| **包含框架术语** | Django 特定术语 | urlpatterns、makemigrations |

### 4.5 动态加载机制

```
用户请求: "创建一个查询作业的 API 接口"
                    ↓
            触发词匹配
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
 "API"           "接口"          "作业"
    ↓               ↓               ↓
 web.md          web.md        glossary.md
                    ↓
            依赖解析
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
 error.md      imports.md    template/view.md
                    ↓
            合并加载
                    ↓
    提供给 AI 作为上下文
```

### 4.6 索引文件

```yaml
# .specify/skills/index.yaml
version: "1.0"
project: "v7tov8Service"

skills:
  - id: project-context
    path: project-context/SKILL.md
    type: overview
    triggers: ["项目", "概述", "架构"]
    priority: 1

  - id: project-context/web
    path: project-context/web.md
    type: coding_standard
    triggers: ["API", "接口", "View", "HTTP"]
    dependencies: [project-context/error, project-context/imports]
    priority: 2

  # ... 其他 Skill
```

---

## 五、代码分析方案

### 5.1 技术选型：LibCST

| 对比项 | Python AST | LibCST |
|--------|------------|--------|
| 保留注释 | ❌ | ✅ |
| 保留格式 | ❌ | ✅ |
| 精确位置 | ⚠️ 行号 | ✅ 字符级 |
| 代码修改 | ❌ | ✅ |
| 性能 | ✅ 快 | ⚠️ 2-3x 慢 |

**选择 LibCST 的原因**：
1. 需要提取注释作为规范说明
2. 需要精确位置信息用于验证
3. 需要原始代码片段作为示例

### 5.2 提取器设计

#### 5.2.1 核心提取器（必须）

| 提取器 | 提取内容 | 输出 |
|--------|----------|------|
| **ClassExtractor** | 类定义、基类、装饰器、方法、属性、docstring | 类信息列表 |
| **FunctionExtractor** | 函数定义、参数、返回类型、装饰器、docstring | 函数信息列表 |
| **ConstantExtractor** | 模块级常量、类常量、枚举、值、类型、注释 | 常量信息列表（自动分类） |
| **ImportExtractor** | import 语句、模块路径、别名、相对导入 | 导入信息列表 |
| **CommentExtractor** | 行内注释、块注释、docstring、TODO/FIXME | 注释信息列表 |
| **ExceptionExtractor** | 异常类定义、继承层次、raise 语句、异常处理模式 | 异常层次图 |
| **PatternMiner** | 装饰器组合、命名模式、继承模式、代码结构模式 | 模式统计 |

#### 5.2.2 关系提取器（重要）

| 提取器 | 提取内容 | 输出 |
|--------|----------|------|
| **DependencyExtractor** | import 分析、模块依赖、循环依赖检测 | 依赖关系图 |
| **InheritanceExtractor** | 类继承关系、多重继承、Mixin 模式 | 继承关系图 |
| **CallGraphExtractor** | 函数调用关系、方法调用链 | 调用关系图 |

#### 5.2.3 Django 特定提取器（必须）

| 提取器 | 提取内容 | 输出 |
|--------|----------|------|
| **DjangoModelExtractor** | Model 字段、字段类型、关系（ForeignKey/ManyToMany）、Meta 选项、Manager | 模型详情列表 |
| **DjangoViewExtractor** | View 类、HTTP 方法、装饰器、URL 映射 | View 信息列表 |
| **DjangoURLExtractor** | urlpatterns、path/re_path、include、namespace | 路由表 |
| **DjangoMiddlewareExtractor** | 中间件类、process_* 方法 | 中间件列表 |
| **DjangoSignalExtractor** | @receiver 装饰器、signal.connect | 信号列表 |
| **DjangoAdminExtractor** | ModelAdmin 配置、list_display、search_fields | Admin 配置列表 |

#### 5.2.4 配置提取器（重要）

| 提取器 | 提取内容 | 文件类型 |
|--------|----------|----------|
| **SettingsExtractor** | Django settings 配置项、数据库配置、中间件配置 | settings.py |
| **YamlConfigExtractor** | YAML 配置项、嵌套结构 | *.yaml, *.yml |
| **EnvConfigExtractor** | 环境变量、敏感配置 | .env |

### 5.3 Django 特定模式识别

| 模式 | 识别方法 | 生成的 Skill |
|------|----------|-------------|
| **View 模式** | 继承 `View`/`APIView` + 实现 `get`/`post` 等方法 | web.md |
| **Model 模式** | 继承 `models.Model` + 定义字段 | models.md |
| **Admin 模式** | 继承 `admin.ModelAdmin` + `@admin.register` | admin.md |
| **Middleware 模式** | 实现 `__call__` 或 `process_request`/`process_response` | middleware.md |
| **Signal 模式** | `@receiver` 装饰器或 `signal.connect()` | signals.md |
| **URL 模式** | `urlpatterns` 列表 + `path()`/`re_path()` | urls.md |
| **Migration 模式** | 继承 `migrations.Migration` | migrations.md |
| **Form 模式** | 继承 `forms.Form`/`forms.ModelForm` | forms.md |
| **Serializer 模式** | 继承 `serializers.Serializer` (DRF) | serializers.md |

### 5.4 分析流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           代码分析流程                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1: 文件扫描                                                          │
│  ├── 遍历项目目录                                                           │
│  ├── 过滤 .py 文件                                                          │
│  ├── 排除 __pycache__、venv 等                                              │
│  └── 输出：文件列表（约 200 个文件）                                        │
│                                                                             │
│  Phase 2: 并行解析                                                          │
│  ├── 多进程解析（4-8 核）                                                   │
│  ├── LibCST 解析每个文件                                                    │
│  ├── 错误处理（语法错误跳过）                                               │
│  └── 输出：CST 树列表                                                       │
│                                                                             │
│  Phase 3: 信息提取                                                          │
│  ├── 运行所有提取器                                                         │
│  ├── 收集结构化数据                                                         │
│  └── 输出：原始知识数据                                                     │
│                                                                             │
│  Phase 4: 模式挖掘                                                          │
│  ├── 统计高频模式                                                           │
│  ├── 计算覆盖率                                                             │
│  ├── 识别项目规范                                                           │
│  └── 输出：模式库 + 统计数据                                                │
│                                                                             │
│  Phase 5: 知识融合                                                          │
│  ├── 去重合并                                                               │
│  ├── 置信度计算                                                             │
│  ├── 优先级排序                                                             │
│  └── 输出：知识库（JSON）                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.5 性能优化

| 优化策略 | 说明 | 效果 |
|----------|------|------|
| **并行处理** | 多进程解析文件 | 4x 加速 |
| **增量分析** | 只分析变更文件 | 90% 减少 |
| **缓存机制** | 缓存解析结果 | 重复分析 0 成本 |

### 5.6 增量更新策略

| 变更类型 | 更新范围 | 触发条件 |
|----------|----------|----------|
| **新增文件** | 分析新文件，更新相关 Skill | 文件 hash 不存在 |
| **修改文件** | 重新分析该文件，更新引用该文件的 Skill | 文件 hash 变化 |
| **删除文件** | 移除相关引用，更新受影响的 Skill | 文件不存在 |
| **依赖变化** | 重新检测框架版本，可能触发全量更新 | requirements.txt 变化 |

---

## 六、防幻觉机制

### 6.1 核心原则

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           防幻觉核心原则                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. 数据来自代码分析，不是 LLM 推断                                         │
│  2. LLM 只做表达，不做创造                                                  │
│  3. 所有信息可验证，有来源有证据                                            │
│  4. 标注可信度，让使用者知道风险                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 五大防幻觉策略

#### 策略一：强制引用

每条规范必须有代码证据：

```markdown
## ❌ 错误的写法（可能幻觉）

所有 View 类必须使用 `@api_view` 装饰器。

## ✅ 正确的写法（有引用）

所有 View 类必须使用 `@formatting()` + `@authenticated()` 装饰器。

**证据**：
- 来源：`v7tov8Service/views/job.py:15-20`
- 示例：[代码片段]
```

#### 策略二：模板化生成

LLM 只填充模板，不自由发挥：

```
模板结构（固定）  +  数据（代码分析）  +  描述（LLM 可选）  =  Skill 内容
```

#### 策略三：置信度标注

```markdown
## 装饰器规范 `[事实层 ✓]`     ← 100% 可信
## 参数处理建议 `[推断层 ⚠]`   ← 70% 可信
## 性能优化建议 `[建议层 ?]`   ← 50% 可信
```

#### 策略四：验证管道

自动验证生成的 Skill：

| 验证项 | 验证规则 | 失败处理 |
|--------|----------|----------|
| **文件引用** | 文件路径必须存在 | 移除该引用或标记为过期 |
| **行号引用** | 行号必须在文件范围内 | 更新为正确行号 |
| **代码片段** | 片段内容必须与文件匹配 | 重新提取代码片段 |
| **统计数据** | 实际统计误差 < 10% | 重新统计并更新 |
| **类/函数名** | 名称必须在代码中存在 | 移除该引用 |
| **Import 路径** | 模块路径必须可导入 | 标记为待验证 |

#### 策略五：分层信任

| 层级 | 来源 | 可信度 | 内容 |
|------|------|--------|------|
| **事实层** | 代码分析 | 100% | 类名、函数名、文件路径、代码片段 |
| **推断层** | 模式推断 | 70% | 命名规范、设计模式 |
| **建议层** | LLM 生成 | 50% | 改进建议、文档描述 |

### 6.3 Skill 生成流程（防幻觉版）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        防幻觉 Skill 生成流程                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: 全量代码分析（无 LLM）                                             │
│  └── 输出：结构化知识库（100% 准确）                                        │
│                                                                             │
│  Step 2: 知识组织（无 LLM）                                                 │
│  └── 输出：分类知识数据 + 统计数据                                          │
│                                                                             │
│  Step 3: 模板填充（少量 LLM）                                               │
│  ├── 数据部分：不经过 LLM                                                   │
│  └── 描述部分：LLM 生成（可选，有约束）                                     │
│                                                                             │
│  Step 4: 验证（无 LLM）                                                     │
│  ├── 验证代码引用                                                           │
│  ├── 验证统计数据                                                           │
│  └── 验证名称存在                                                           │
│                                                                             │
│  Step 5: 人工审核（可选）                                                   │
│  └── 审核 LLM 生成的描述                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 七、实现路线图

> **重要**：Phase 1 聚焦 **Python + Django**，Go/Shell 扩展延后到 Phase 5+

### 7.1 Phase 1: 基础能力（2 周）—— 仅 Python + Django

| 任务 | 说明 | 产出 |
|------|------|------|
| LibCST 分析器 | 实现核心提取器（Class/Function/Constant/Import/Comment/Exception） | 结构化知识数据 |
| Django 提取器 | Model/View/URL/Middleware 提取器 | Django 特定数据 |
| 知识库格式 | 定义 JSON Schema | 知识库规范 |
| 基础 Skill 模板 | 设计 Skill 结构 | 模板文件 |

### 7.2 Phase 2: Skill 生成（2 周）

| 任务 | 说明 | 产出 |
|------|------|------|
| 模板填充引擎 | 数据驱动的 Skill 生成（纯模板，无 LLM） | 生成器代码 |
| 验证管道 | 防幻觉验证 | 验证器代码 |
| 核心 Skill | 生成 web, models, error, imports 等 | Skill 文件 |
| Windsurf 集成 | 生成 .windsurfrules 和 memory 文件 | IDE 集成文件 |

### 7.3 Phase 3: 动态加载 + 冲突检测（1 周）

| 任务 | 说明 | 产出 |
|------|------|------|
| 索引系统 | Skill 索引和触发词 | index.yaml |
| 加载器 | 动态加载逻辑 | 加载器代码 |
| 冲突检测 | 自动检测 + Git 时间线分析 | 冲突报告 |
| 集成测试 | 验证端到端流程 | 测试用例 |

### 7.4 Phase 4: 优化完善（1 周）

| 任务 | 说明 | 产出 |
|------|------|------|
| 增量更新 | 只更新变更部分 | 增量逻辑 |
| 性能优化 | 并行处理、缓存 | 优化代码 |
| 反馈收集 | 基础反馈机制 | 反馈收集器 |
| 文档完善 | 使用说明 | 文档 |

### 7.5 Phase 5+: 扩展（可选，根据需要）

| 任务 | 说明 | 工作量 |
|------|------|--------|
| Go 语言支持 | go/parser + Gin 适配器 | 2-3 周 |
| Shell 支持 | bashlex + 正则 | 1 周 |
| LLM 增强模式 | 可选的描述生成 | 0.5 周 |
| 跨项目复用 | 公司级 Skill 库 | 1 周 |

---

## 八、预期产出

### 8.1 目录结构

```
.specify/skills/
├── index.yaml                    # Skill 索引
│
├── project-context/              # 项目上下文 Skill 集
│   ├── SKILL.md                  # 项目概述
│   │
│   ├── standards/                # 规范类
│   │   ├── web.md                # Web 接口规范
│   │   ├── models.md             # 数据模型规范
│   │   ├── service.md            # 服务层规范
│   │   ├── handler.md            # 处理器规范
│   │   ├── error.md              # 错误处理规范
│   │   ├── constants.md          # 常量定义规范
│   │   ├── config.md             # 配置规范
│   │   └── logging.md            # 日志规范
│   │
│   ├── references/               # 辅助类
│   │   ├── imports.md            # Import 模板
│   │   ├── urls.md               # URL 路由
│   │   └── models_reference.md   # 模型速查
│   │
│   ├── business/                 # 业务类
│   │   ├── glossary.md           # 业务术语表
│   │   ├── entities.md           # 业务实体
│   │   └── processes.md          # 业务流程
│   │
│   └── templates/                # 模板类
│       ├── view.md               # View 模板
│       ├── model.md              # Model 模板
│       ├── service.md            # Service 模板
│       └── handler.md            # Handler 模板
│
└── knowledge-base/
    └── project.json              # 知识库（结构化数据）
```

### 8.2 使用效果示例

**场景**：AI 需要为项目添加一个新的 API 接口

**用户输入**：
```
请为 v7tov8Service 添加一个查询作业详情的 API 接口
```

**系统行为**：
1. 匹配触发词 → 确定需要加载的 Skill
2. 加载 `web.md` + `error.md` + `imports.md` + `template/view.md` + `glossary.md`
3. 合并为上下文提供给 AI

**AI 获得的上下文**：
- Web 接口规范（装饰器、参数处理、响应格式）
- 错误处理规范（错误码、异常类）
- Import 模板（正确的导入路径）
- View 代码模板（完整的代码结构）
- 业务术语（Job、SubJob 的定义）

**AI 输出**：符合项目规范的代码

### 8.3 质量指标

| 指标 | 目标 |
|------|------|
| **代码引用准确率** | 100%（所有引用都可验证） |
| **规范覆盖率** | >90%（覆盖主要开发场景） |
| **Skill 加载精准度** | >85%（加载的 Skill 与任务相关） |
| **生成代码合规率** | >95%（AI 生成的代码符合规范） |

---

## 附录

### A. 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| 代码解析 | LibCST | 精确的代码分析（保留注释、格式） |
| 知识存储 | JSON | 结构化数据存储 |
| 模板引擎 | Jinja2 | Skill 文档生成 |
| LLM | Claude/GPT-4 | 描述生成（可选，受限使用） |
| 并行处理 | multiprocessing | 多进程文件解析 |
| 缓存 | 文件 hash | 增量更新支持 |

### B. 知识库 Schema

```json
{
  "version": "1.0",
  "project": {
    "name": "string",
    "framework": "django",
    "django_version": "string",
    "python_version": "string",
    "description": "string"
  },

  "code_units": {
    "classes": [
      {
        "name": "string",
        "file_path": "string",
        "line": "number",
        "bases": ["string"],
        "decorators": ["string"],
        "methods": ["string"],
        "docstring": "string",
        "raw_code": "string"
      }
    ],
    "functions": [
      {
        "name": "string",
        "file_path": "string",
        "line": "number",
        "params": [{"name": "string", "type": "string", "default": "string"}],
        "return_type": "string",
        "decorators": ["string"],
        "docstring": "string"
      }
    ],
    "constants": [
      {
        "name": "string",
        "value": "string",
        "category": "error_code|status|type|config|other",
        "file_path": "string",
        "line": "number",
        "comment": "string"
      }
    ],
    "imports": [
      {
        "module": "string",
        "names": ["string"],
        "alias": "string",
        "file_path": "string",
        "line": "number"
      }
    ],
    "exceptions": [
      {
        "name": "string",
        "base_class": "string",
        "file_path": "string",
        "line": "number",
        "docstring": "string"
      }
    ]
  },

  "django_specific": {
    "models": [
      {
        "name": "string",
        "file_path": "string",
        "fields": [
          {
            "name": "string",
            "field_type": "CharField|IntegerField|ForeignKey|...",
            "options": {}
          }
        ],
        "meta": {},
        "managers": ["string"]
      }
    ],
    "views": [
      {
        "name": "string",
        "file_path": "string",
        "base_class": "string",
        "methods": ["get", "post", "put", "delete"],
        "decorators": ["string"],
        "url_pattern": "string"
      }
    ],
    "urls": [
      {
        "pattern": "string",
        "view": "string",
        "name": "string",
        "file_path": "string"
      }
    ],
    "middlewares": [
      {
        "name": "string",
        "file_path": "string",
        "methods": ["string"]
      }
    ],
    "signals": [
      {
        "signal": "string",
        "receiver": "string",
        "sender": "string",
        "file_path": "string"
      }
    ],
    "admin": [
      {
        "model": "string",
        "admin_class": "string",
        "list_display": ["string"],
        "search_fields": ["string"]
      }
    ]
  },

  "patterns": {
    "decorators": [
      {
        "pattern": "string",
        "count": "number",
        "examples": ["string"]
      }
    ],
    "naming": [
      {
        "type": "prefix|suffix",
        "pattern": "string",
        "count": "number",
        "examples": ["string"]
      }
    ],
    "error_handling": [
      {
        "pattern": "string",
        "count": "number",
        "examples": ["string"]
      }
    ],
    "logging": [
      {
        "logger_name": "string",
        "count": "number",
        "levels": ["string"]
      }
    ]
  },

  "relations": {
    "model_relations": {
      "model_name": {
        "foreign_keys": [{"field": "string", "to": "string"}],
        "many_to_many": [{"field": "string", "to": "string"}],
        "one_to_one": [{"field": "string", "to": "string"}]
      }
    },
    "module_dependencies": {
      "module_path": ["imported_module_path"]
    },
    "inheritance": {
      "class_name": ["base_class"]
    }
  },

  "statistics": {
    "total_files": "number",
    "total_classes": "number",
    "total_functions": "number",
    "total_constants": "number",
    "total_models": "number",
    "total_views": "number",
    "analysis_time": "string",
    "last_updated": "string"
  }
}
```

### C. 成本估算

| 阶段 | 人力 | LLM 成本 |
|------|------|----------|
| 代码分析 | 2 周 | $0 |
| Skill 生成 | 2 周 | ~$15（可选） |
| 动态加载 | 1 周 | $0 |
| 优化完善 | 1 周 | $0 |
| **总计** | **6 周** | **~$15** |

### D. 风险与应对

| 风险 | 应对 |
|------|------|
| LibCST 解析失败 | 回退到 AST，跳过问题文件，记录错误日志 |
| 模式识别不准 | 人工审核 + 反馈优化 + 置信度标注 |
| Skill 加载不精准 | 优化触发词 + 用户反馈 + 依赖解析 |
| 大型项目性能问题 | 并行处理 + 增量更新 + 缓存机制 |
| 代码风格不一致 | 统计多种模式，标注覆盖率 |
| Django 版本差异 | 检测 Django 版本，适配不同 API |

### E. 完整 Skill 列表

| Skill | 类型 | 必要性 | 主要内容 |
|-------|------|--------|----------|
| **SKILL.md** | 项目级 | 必须 | 项目概述、技术栈、架构、导航 |
| **web.md** | 规范类 | 必须 | View 类规范、装饰器、参数处理、响应格式 |
| **models.md** | 规范类 | 必须 | Model 定义、字段规范、关系、查询 |
| **service.md** | 规范类 | 重要 | 服务层规范、业务逻辑组织 |
| **handler.md** | 规范类 | 重要 | 后台任务处理器规范 |
| **error.md** | 规范类 | 必须 | 异常类、错误码、错误处理模式 |
| **urls.md** | 规范类 | 必须 | URL 路由规范、命名规范 |
| **middleware.md** | 规范类 | 重要 | 中间件开发规范 |
| **migrations.md** | 规范类 | 重要 | 数据库迁移规范 |
| **imports.md** | 辅助类 | 必须 | Import 模板、路径规范 |
| **constants.md** | 辅助类 | 必须 | 常量定义、枚举规范 |
| **config.md** | 辅助类 | 重要 | 配置规范、settings 使用 |
| **logging.md** | 辅助类 | 重要 | 日志规范、Logger 使用 |
| **naming.md** | 辅助类 | 重要 | 命名规范（类、函数、变量） |
| **test.md** | 辅助类 | 重要 | 测试规范、测试模式 |
| **glossary.md** | 业务类 | 待定 | 业务术语表（需明确业务需求后实现） |
| **entities.md** | 业务类 | 待定 | 业务实体说明 |
| **processes.md** | 业务类 | 待定 | 业务流程说明 |
| **rules.md** | 业务类 | 待定 | 业务规则说明 |

> **注**：模板类 Skill 已移除，代码模板整合到各规范类 Skill 的代码示例中。业务规则中已提供原始代码，无需单独生成模板。

### F. 多语言支持（Python、Go、Shell）

当前方案针对 **Django** 项目设计，同时支持扩展到 **Go** 和 **Shell** 脚本。

#### F.1 支持的语言和框架

| 语言 | 解析器 | 支持的框架/场景 | 优先级 |
|------|--------|----------------|--------|
| **Python** | LibCST | Django, Flask, FastAPI, Click | 高（当前） |
| **Go** | go/parser | Gin, Echo, 标准库 | 中 |
| **Shell** | 正则 + bashlex | Bash 脚本 | 低 |

#### F.2 扩展架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        核心层（语言无关）                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Skill 体系  │  知识库 Schema  │  动态加载  │  防幻觉验证           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↑
┌─────────────────────────────────────────────────────────────────────────────┐
│                        适配器层（可插拔）                                    │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐       │
│  │  Python Adapter   │  │    Go Adapter     │  │   Shell Adapter   │       │
│  │  Django/Flask/... │  │   Gin/Echo/...    │  │   Bash Scripts    │       │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↑
┌─────────────────────────────────────────────────────────────────────────────┐
│                        解析器层（语言特定）                                  │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐       │
│  │      LibCST       │  │    go/parser      │  │  正则 + bashlex   │       │
│  │      Python       │  │       Go          │  │      Shell        │       │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### F.3 Python 框架支持

| 框架 | 需要新增的提取器 | 需要新增的 Skill | 工作量 |
|------|------------------|----------------|--------|
| **Django** | 已实现 | 已实现 | - |
| **Flask** | FlaskRouteExtractor, FlaskBlueprintExtractor | routes.md, blueprints.md | 1 周 |
| **FastAPI** | FastAPIEndpointExtractor, PydanticExtractor | endpoints.md, schemas.md | 1 周 |
| **Click** | ClickCommandExtractor | commands.md | 0.5 周 |

#### F.4 Go 语言支持

| 提取器 | 提取内容 | 说明 |
|--------|----------|------|
| **GoStructExtractor** | struct 定义、字段、tag | 类似 Python 的 ClassExtractor |
| **GoFunctionExtractor** | 函数、方法、接收者 | 包括接口方法 |
| **GoConstExtractor** | const、iota、枚举 | 常量定义 |
| **GoImportExtractor** | import 语句 | 包导入 |
| **GoCommentExtractor** | 注释、godoc | 文档注释 |
| **GinRouteExtractor** | Gin 路由、中间件 | 框架特定 |

**Go Skill 列表**：
- `SKILL.md` - 项目概述
- `structs.md` - 结构体规范
- `functions.md` - 函数规范
- `error.md` - 错误处理（error 接口）
- `imports.md` - 包导入规范
- `api.md` - HTTP 接口规范（Gin/Echo）
- `templates/handler.md` - Handler 模板

**工作量**：2-3 周

#### F.5 Shell 脚本支持

| 提取器 | 提取内容 | 说明 |
|--------|----------|------|
| **ShellFunctionExtractor** | 函数定义 | function name() 或 name() |
| **ShellVariableExtractor** | 变量定义、环境变量 | export、readonly |
| **ShellCommentExtractor** | 注释 | # 开头的行 |
| **ShellCommandExtractor** | 常用命令模式 | 如 curl、grep、awk |

**Shell Skill 列表**：
- `SKILL.md` - 脚本概述
- `functions.md` - 函数规范
- `variables.md` - 变量规范
- `error.md` - 错误处理（set -e、trap）
- `templates/script.md` - 脚本模板

**工作量**：1 周

#### F.6 扩展步骤

1. **实现语言解析器**：
   - Python: LibCST（已实现）
   - Go: go/parser（Go 标准库，需用 Go 编写或调用）
   - Shell: bashlex + 正则（Python 库）

2. **实现核心提取器**：
   - 每种语言实现：Class/Struct, Function, Constant, Import, Comment

3. **实现框架适配器**：
   - Python: Django, Flask, FastAPI
   - Go: Gin, Echo
   - Shell: 通用脚本

4. **设计语言特定 Skill**：
   - 根据语言特点设计规范文档

5. **复用核心层**：
   - Skill 体系、动态加载、防幻觉验证（语言无关）

### G. LLM 使用边界与 Fallback 机制

> **重要**：**默认关闭 LLM**，仅在 `--enhance` 模式下启用，最大限度压缩成本

#### G.1 LLM 使用范围

| 场景 | 是否使用 LLM | 说明 |
|------|------------|------|
| 代码解析 | ❌ 不使用 | 使用 LibCST，100% 准确 |
| 模式统计 | ❌ 不使用 | 统计算法，100% 准确 |
| 知识库构建 | ❌ 不使用 | 结构化数据，100% 准确 |
| Skill 数据填充 | ❌ 不使用 | 模板填充，100% 准确 |
| **Skill 描述生成** | ⚠️ 仅 --enhance | 生成概述、说明文字 |
| **业务术语解释** | ⚠️ 仅 --enhance | 解释业务概念 |

#### G.2 默认模式（无 LLM，零成本）

```bash
# 默认模式：纯模板，无 LLM 调用，零成本
python main.py generate-skills \
    --knowledge ./cache/knowledge.json \
    --output ./skills/

# 增强模式：启用 LLM 生成描述（有成本）
python main.py generate-skills \
    --knowledge ./cache/knowledge.json \
    --output ./skills/ \
    --enhance  # 启用 LLM
```

#### G.3 LLM 缓存机制（压缩成本）

```
知识库 hash ──▶ 检查缓存 ──▶ 命中 ──▶ 使用缓存的描述
                              │
                              └──▶ 未命中 ──▶ 调用 LLM ──▶ 存入缓存
```

| 缓存策略 | 说明 |
|----------|------|
| **知识库 hash** | 相同知识库不重复生成描述 |
| **分块缓存** | 按 Skill 分块缓存，部分更新时只重新生成变化部分 |
| **缓存有效期** | 7 天，过期后重新生成 |

**纯模板模式的输出**：
- 所有数据部分：完整保留
- 描述部分：使用预定义模板文字
- 业务术语：只列出名称，不生成解释

#### G.3 Fallback 机制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LLM Fallback 流程                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  需要生成描述                                                               │
│       │                                                                     │
│       ▼                                                                     │
│  检查 LLM 是否可用                                                          │
│       │                                                                     │
│       ├─── 可用 ───▶ 调用 LLM 生成描述                                     │
│       │                    │                                                │
│       │                    ├─── 成功 ───▶ 使用 LLM 生成的描述              │
│       │                    │                                                │
│       │                    └─── 失败 ───▶ Fallback Level 1                 │
│       │                                                                     │
│       └─── 不可用 ──▶ Fallback Level 1                                     │
│                                                                             │
│  Fallback Level 1: 使用预定义模板                                          │
│       │                                                                     │
│       ├─── 有匹配模板 ──▶ 使用模板文字                                     │
│       │                                                                     │
│       └─── 无匹配模板 ──▶ Fallback Level 2                                 │
│                                                                             │
│  Fallback Level 2: 使用通用描述                                            │
│       │                                                                     │
│       └───▶ 使用 "详见代码示例" 等通用文字                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### G.4 LLM 不可用场景处理

| 场景 | 处理方式 | 用户影响 |
|------|----------|----------|
| **网络断开** | 自动切换到纯模板模式 | 描述文字简化，数据完整 |
| **配额耗尽** | 自动切换到纯模板模式 | 描述文字简化，数据完整 |
| **API 错误** | 重试 3 次，失败后 fallback | 可能延迟，最终成功 |
| **超时** | 重试 2 次，失败后 fallback | 可能延迟，最终成功 |
| **内容过滤** | 使用模板文字 | 无影响 |

#### G.5 配置选项

```yaml
# config.yaml
llm:
  enabled: false             # 默认关闭 LLM
  provider: "openai"         # openai / anthropic / local
  model: "gpt-4"             # 模型名称
  timeout: 30                # 超时时间（秒）
  max_retries: 3             # 最大重试次数
  fallback_on_error: true    # 错误时是否 fallback

  # 缓存配置
  cache:
    enabled: true            # 启用缓存
    ttl_days: 7              # 缓存有效期
    path: ".specify/cache/llm/"

  # 使用场景控制（仅 --enhance 模式生效）
  use_for:
    skill_description: true  # Skill 描述生成
    glossary_explanation: true  # 术语解释
    code_summary: false      # 代码摘要（禁用，防止幻觉）
```

#### G.6 成本估算

| 模式 | LLM 调用次数 | 估算成本 | 适用场景 |
|------|------------|----------|----------|
| **默认模式** | 0 | $0 | CI/CD、日常更新 |
| **增强模式（首次）** | ~50 | ~$5 | 项目初始化 |
| **增强模式（缓存命中）** | ~5 | ~$0.5 | 增量更新 |

#### G.7 输出对比

| 内容 | 有 LLM | 无 LLM |
|------|--------|--------|
| **规范数据** | ✅ 完整 | ✅ 完整 |
| **代码示例** | ✅ 完整 | ✅ 完整 |
| **统计数据** | ✅ 完整 | ✅ 完整 |
| **规范描述** | ✅ 自然语言 | ⚠️ 模板文字 |
| **术语解释** | ✅ 详细解释 | ⚠️ 只有名称 |
| **整体可用性** | ★★★★★ | ★★★★☆ |

**结论**：默认模式（无 LLM）可生成完全可用的 Skill 文档，零成本，适合 CI/CD。

### N. Windsurf IDE 集成

#### N.1 集成方式

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Windsurf 集成架构                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Skill 生成器 ──▶ 输出文件                                              │
│       │                                                                 │
│       ├──▶ .windsurfrules          # Windsurf 全局规则                   │
│       │                                                                 │
│       ├──▶ .specify/ide/windsurf_rules.md  # IDE 特定规则              │
│       │                                                                 │
│       ├──▶ .specify/memory/         # Memory 文件                       │
│       │   ├── constitution.md        # 项目章程                         │
│       │   └── project_rules.md       # 项目规则                         │
│       │                                                                 │
│       └──▶ .windsurf/workflows/     # 工作流文件                       │
│           ├── create-api.md          # 创建 API 工作流                  │
│           ├── create-model.md        # 创建 Model 工作流                │
│           └── ...                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### N.2 生成的文件

| 文件 | 用途 | 内容来源 |
|------|------|----------|
| **.windsurfrules** | Windsurf 全局规则 | 项目概述 + 核心规范 |
| **windsurf_rules.md** | IDE 特定规则 | 开发前置要求 |
| **constitution.md** | 项目章程 | 项目背景、技术栈、架构 |
| **project_rules.md** | 项目规则 | 从 Skill 提取的核心规范 |
| **workflows/*.md** | 工作流 | 基于 Skill 生成的操作指南 |

#### N.3 .windsurfrules 示例

```markdown
# V7 到 V8 管理数据迁移服务 项目规则

## 开发前置（强制）

进行代码开发前，**必须**按以下顺序读取项目规范：

1. **读取项目概述**：`.specify/skills/project-context/SKILL.md`
2. **根据任务类型读取对应规范**：
   - 开发 API 接口 → `web.md`
   - 定义数据模型 → `models.md`
   - 编写业务逻辑 → `service.md`
   - 定义错误码 → `error.md`

## 开发检查

- 代码必须符合对应规范文件的要求
- 新增 API 必须使用 `@formatting()` + `@authenticated()` 装饰器
- 新增模型必须继承 `BaseModel`
- 禁止使用 `print()`，使用 `logger`
- 禁止裸 `except:`，必须指定异常类型
```

#### N.4 生成命令

```bash
# 生成 Skill + Windsurf 集成文件
python main.py generate-skills \
    --knowledge ./cache/knowledge.json \
    --output ./skills/project-context/ \
    --windsurf  # 生成 Windsurf 集成文件

# 仅更新 Windsurf 文件（不重新分析）
python main.py sync-windsurf \
    --skills ./skills/project-context/
```

### H. 测试策略

#### H.1 测试层次

| 层次 | 测试内容 | 方法 |
|------|----------|------|
| **单元测试** | 各提取器的正确性 | pytest + 固定测试用例 |
| **集成测试** | 端到端流程 | 真实项目 + 快照对比 |
| **回归测试** | 代码变更后的稳定性 | CI/CD 自动化 |
| **验证测试** | Skill 内容的准确性 | 自动验证 + 人工抽检 |

#### H.2 提取器测试

```python
# 测试用例示例
def test_class_extractor():
    code = '''
    class MyView(View):
        @formatting()
        def get(self, request):
            pass
    '''
    extractor = ClassExtractor()
    result = extractor.extract(code)

    assert len(result) == 1
    assert result[0].name == "MyView"
    assert result[0].bases == ["View"]
    assert "@formatting()" in result[0].decorators
```

#### H.3 Skill 验证测试

| 验证项 | 自动化 | 说明 |
|--------|--------|------|
| 文件引用存在 | ✅ | 检查引用的文件是否存在 |
| 行号有效 | ✅ | 检查行号是否在文件范围内 |
| 代码片段匹配 | ✅ | 检查代码片段是否与文件内容一致 |
| 统计数据准确 | ✅ | 重新统计并对比 |
| 触发词覆盖 | ⚠️ | 人工检查触发词是否合理 |
| 描述准确性 | ⚠️ | 人工抽检描述是否准确 |

#### H.4 测试数据

- **固定测试用例**：手工编写的代码片段，覆盖各种边界情况
- **真实项目快照**：v7tov8Service 项目的快照，用于回归测试
- **生成结果快照**：Skill 文档的快照，用于对比变更

### I. 错误处理

#### I.1 错误分类

| 错误类型 | 处理方式 | 影响范围 |
|----------|----------|----------|
| **语法错误** | 跳过该文件，记录日志 | 单文件 |
| **编码错误** | 尝试多种编码，失败则跳过 | 单文件 |
| **解析超时** | 跳过该文件，记录日志 | 单文件 |
| **内存不足** | 减少并行数，重试 | 全局 |
| **LLM 错误** | Fallback 到模板 | 单 Skill |
| **验证失败** | 标记为待审核 | 单条规范 |

#### I.2 错误日志

```json
{
  "timestamp": "2025-01-22T10:00:00Z",
  "level": "ERROR",
  "type": "parse_error",
  "file": "src/views/broken.py",
  "line": 15,
  "message": "Syntax error: unexpected token",
  "action": "skipped"
}
```

#### I.3 错误恢复

- **增量模式**：失败的文件在下次运行时重试
- **手动修复**：提供命令行工具手动触发单文件重新分析
- **降级模式**：关键功能失败时自动降级到基础模式

### J. 跨项目 Skill 复用机制

#### J.1 复用场景

| 场景 | 说明 | 示例 |
|------|------|------|
| **公司级规范** | 所有项目共享的基础规范 | 错误码格式、日志规范、命名规范 |
| **微服务共享** | 多个微服务共享的接口规范 | API 响应格式、认证方式 |
| **框架模板** | 特定框架的通用规范 | Django View 模板、Go Gin Handler 模板 |

#### J.2 Skill 层次结构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Skill 层次结构                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Level 0: 公司级 Skill（全局共享）                                          │
│  └── .specify/skills/company/                                               │
│      ├── error-codes.md      # 公司统一错误码                               │
│      ├── logging.md          # 公司日志规范                                 │
│      └── naming.md           # 公司命名规范                                 │
│                                                                             │
│  Level 1: 框架级 Skill（框架共享）                                          │
│  └── .specify/skills/frameworks/                                            │
│      ├── django/             # Django 通用规范                              │
│      ├── go-gin/             # Go Gin 通用规范                              │
│      └── shell/              # Shell 通用规范                               │
│                                                                             │
│  Level 2: 项目级 Skill（项目特定）                                          │
│  └── .specify/skills/project-context/                                       │
│      ├── SKILL.md            # 项目概述                                     │
│      ├── web.md              # 项目 Web 规范（可覆盖框架级）                │
│      └── ...                                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### J.3 Skill 继承与覆盖

```yaml
# 项目级 Skill 可以继承和覆盖上级 Skill
---
skill_id: project-context/error
extends: company/error-codes    # 继承公司级错误码规范
overrides:                      # 覆盖部分内容
  - error_code_prefix: "V7V8"   # 项目特定前缀
---
```

#### J.4 复用机制实现

```bash
# 初始化项目时链接公司级 Skill
python main.py init \
    --company-skills /path/to/company/skills \
    --framework django

# 生成时自动合并多级 Skill
python main.py generate-skills \
    --inherit company,django \
    --output ./skills/project-context/
```

### K. Skill 冲突检测与解决

#### K.1 冲突类型

| 冲突类型 | 描述 | 示例 |
|----------|------|------|
| **模式冲突** | 同一场景存在多种实现方式 | 部分 View 用 `@api_view`，部分用类视图 |
| **版本冲突** | 新旧代码使用不同版本 | V7 装饰器 vs V8 装饰器 |
| **命名冲突** | 命名规范不一致 | `get_xxx` vs `fetch_xxx` |
| **继承冲突** | 上下级 Skill 定义矛盾 | 公司规范 vs 项目规范 |

#### K.2 冲突检测

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        冲突检测流程                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  模式统计                                                                   │
│       │                                                                     │
│       ▼                                                                     │
│  计算各模式占比                                                             │
│       │                                                                     │
│       ├─── 单一模式 > 90% ───▶ 无冲突，采用主流模式                        │
│       │                                                                     │
│       ├─── 主流模式 70-90% ──▶ 轻微冲突，标注为"推荐"                      │
│       │                                                                     │
│       └─── 无主流模式 < 70% ─▶ 严重冲突，需要人工决策                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### K.3 冲突解决策略（自动化优先）

| 策略 | 适用场景 | 处理方式 | 自动化 |
|------|----------|----------|--------|
| **多数优先** | 主流模式 > 70% | 采用主流模式，标注其他为"遗留" | ✅ 全自动 |
| **Git 时间线** | 版本迁移中 | 通过 Git 历史判断新旧，自动标注 | ✅ 全自动 |
| **文件路径推断** | legacy 目录 | 路径含 legacy/old/deprecated 自动标记 | ✅ 全自动 |
| **并列展示** | 无明显主流且无时间线 | 同时展示多种模式 | ✅ 全自动 |
| **人工决策** | 仅当上述策略均无法判断 | 生成冲突报告，等待确认 | ⚠️ 需人工 |

#### K.4 Git 时间线自动分析

```bash
# 自动分析代码时间线
git log --format="%H %ai" --follow -- "$file" | head -1
```

| 判断规则 | 标记 |
|----------|------|
| 最后修改 > 1年 + 占比 < 30% | `[遗留模式]` |
| 最后修改 < 3个月 + 占比增长 | `[新规范]` |
| 路径含 legacy/old/v1 | `[待迁移]` |

#### K.4 冲突报告示例

```markdown
## 冲突报告

### 1. View 实现方式冲突 `[严重]`

**发现的模式**：
- 类视图 (Class-based View): 35 个文件 (61%)
- 函数视图 (@api_view): 22 个文件 (39%)

**建议**：需要人工决策，选择统一的实现方式

**相关文件**：
- 类视图: `views/job.py`, `views/task.py`, ...
- 函数视图: `views/legacy/*.py`, ...
```

### L. 非 Python 文件处理（SQL、Protobuf 等）

#### L.1 支持的文件类型

| 文件类型 | 解析方式 | 提取内容 | 生成的 Skill |
|----------|----------|----------|--------------|
| **.sql** | sqlparse | 表结构、索引、存储过程 | database.md |
| **.proto** | protobuf 编译器 | 消息定义、服务定义 | grpc.md |
| **Makefile** | 正则解析 | 目标、依赖 | build.md |
| **Dockerfile** | 正则解析 | 基础镜像、构建步骤 | docker.md |
| **.graphql** | graphql-core | 类型、查询、变更 | graphql.md |

#### L.2 SQL 文件处理

| 提取器 | 提取内容 | 说明 |
|--------|----------|------|
| **SQLTableExtractor** | CREATE TABLE 语句 | 表名、字段、类型、约束 |
| **SQLIndexExtractor** | CREATE INDEX 语句 | 索引名、字段、类型 |
| **SQLProcedureExtractor** | 存储过程、函数 | 名称、参数、逻辑 |
| **SQLCommentExtractor** | 注释 | 表注释、字段注释 |

**SQL Skill 示例**：
```markdown
## 数据库规范 (database.md)

### 表命名规范 `[统计层 ✓]`
- 前缀：`t_` 表示业务表，`r_` 表示关系表
- 统计：45/50 个表使用此规范（90%）

### 字段命名规范 `[统计层 ✓]`
- 主键：`id`
- 创建时间：`created_at`
- 更新时间：`updated_at`
```

#### L.3 Protobuf 文件处理

| 提取器 | 提取内容 | 说明 |
|--------|----------|------|
| **ProtoMessageExtractor** | message 定义 | 字段、类型、编号 |
| **ProtoServiceExtractor** | service 定义 | RPC 方法、请求/响应类型 |
| **ProtoEnumExtractor** | enum 定义 | 枚举值 |
| **ProtoCommentExtractor** | 注释 | 文档注释 |

**gRPC Skill 示例**：
```markdown
## gRPC 接口规范 (grpc.md)

### 服务定义 `[事实层 ✓]`
- JobService: 作业管理服务
  - CreateJob(CreateJobRequest) -> CreateJobResponse
  - GetJob(GetJobRequest) -> GetJobResponse
```

### M. 用户反馈闭环机制

#### M.1 反馈收集

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        反馈闭环流程                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Skill 生成 ──▶ AI 使用 Skill ──▶ 生成代码 ──▶ 开发者审核                  │
│       ▲                                              │                      │
│       │                                              ▼                      │
│       │                                         反馈收集                    │
│       │                                              │                      │
│       │         ┌────────────────────────────────────┤                      │
│       │         │                                    │                      │
│       │         ▼                                    ▼                      │
│       │    代码被接受                           代码被拒绝                  │
│       │         │                                    │                      │
│       │         ▼                                    ▼                      │
│       │    正向反馈                             负向反馈                    │
│       │    (Skill 有效)                         (Skill 需优化)             │
│       │         │                                    │                      │
│       └─────────┴────────────────────────────────────┘                      │
│                              │                                              │
│                              ▼                                              │
│                         Skill 优化                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### M.2 反馈类型

| 反馈类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| **代码接受** | AI 生成的代码被直接使用 | 增加 Skill 置信度 |
| **代码修改** | AI 生成的代码被修改后使用 | 分析修改内容，更新 Skill |
| **代码拒绝** | AI 生成的代码被完全丢弃 | 降低 Skill 置信度，标记待审核 |
| **显式反馈** | 开发者主动标记 Skill 问题 | 立即触发 Skill 审核 |

#### M.3 反馈数据收集

```json
{
  "feedback_id": "fb_001",
  "timestamp": "2025-01-22T10:00:00Z",
  "skill_id": "project-context/web",
  "action": "code_modified",
  "original_code": "...",
  "modified_code": "...",
  "diff": "...",
  "developer": "anonymous",
  "context": "创建 API 接口"
}
```

#### M.4 Skill 自动优化

| 触发条件 | 优化动作 |
|----------|----------|
| 接受率 < 50% | 标记为待审核，暂停使用 |
| 同一修改出现 3+ 次 | 自动更新 Skill 内容 |
| 新模式出现 5+ 次 | 建议添加新规范 |
| 旧模式消失 | 建议标记为"遗留" |

#### M.5 反馈报告

```markdown
## Skill 效果报告（周报）

### 整体统计
- 总使用次数：156 次
- 代码接受率：78%
- 代码修改率：18%
- 代码拒绝率：4%

### 需要关注的 Skill
| Skill | 接受率 | 问题 |
|-------|--------|------|
| error.md | 45% | 错误码格式与实际不符 |
| imports.md | 52% | 缺少新增的模块路径 |

### 建议优化
1. 更新 error.md 中的错误码格式
2. 添加 Common.utils.v8 到 imports.md
```

### O. 边界情况与特殊处理

#### O.1 代码变更时 Skill 自动同步

**问题**：代码改了但 Skill 没更新，AI 使用过时规范

**解决方案**：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Git Hook 自动同步                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  git commit ──▶ pre-commit hook ──▶ 检测变更文件                           │
│                                          │                                  │
│                                          ▼                                  │
│                                    影响 Skill？                             │
│                                          │                                  │
│                    ┌─────────────────────┼─────────────────────┐           │
│                    ▼                     ▼                     ▼           │
│                   否                  轻微变更              重大变更        │
│                    │                     │                     │           │
│                    ▼                     ▼                     ▼           │
│                  跳过              标记待更新            阻止提交          │
│                                    (CI 中更新)          (需先更新 Skill)   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**配置**：
```yaml
# .specify/config.yaml
sync:
  mode: "warn"  # warn | block | auto
  auto_update_threshold: 10  # 变更文件数 < 10 时自动更新
  ci_update: true  # CI 中自动更新
```

#### O.2 敏感信息过滤

**问题**：API Key、密码、Token 可能被提取到 Skill

**解决方案**：

| 过滤规则 | 示例 | 处理方式 |
|----------|------|----------|
| **环境变量引用** | `os.environ['API_KEY']` | 保留变量名，隐藏值 |
| **硬编码密钥** | `password = "abc123"` | 替换为 `[REDACTED]` |
| **配置文件路径** | `/etc/secrets/key.pem` | 保留路径结构，隐藏文件名 |
| **URL 中的凭证** | `mysql://user:pass@host` | 替换为 `mysql://[REDACTED]@host` |

**敏感信息检测规则**：
```python
SENSITIVE_PATTERNS = [
    r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
    r'(?i)(api_key|apikey|secret|token)\s*=\s*["\'][^"\']+["\']',
    r'(?i)(aws_access_key|aws_secret)',
    r'["\'][A-Za-z0-9+/]{40,}["\']',  # Base64 长字符串
]
```

#### O.3 大文件/大项目处理

**问题**：超大文件或超大项目可能导致内存溢出或超时

| 场景 | 阈值 | 处理方式 |
|------|------|----------|
| **单文件过大** | > 10,000 行 | 分块解析，只提取签名 |
| **项目文件过多** | > 1,000 文件 | 分批处理，增量合并 |
| **单次分析超时** | > 5 分钟 | 中断并保存进度，下次继续 |
| **内存超限** | > 2GB | 减少并行数，启用流式处理 |

**配置**：
```yaml
limits:
  max_file_lines: 10000
  max_files_per_batch: 100
  timeout_seconds: 300
  max_memory_mb: 2048
```

#### O.4 并发安全

**问题**：多人同时生成/更新 Skill 可能冲突

**解决方案**：

| 策略 | 说明 |
|------|------|
| **文件锁** | 生成时创建 `.specify/.lock` 文件 |
| **原子写入** | 先写临时文件，再原子重命名 |
| **冲突检测** | 检测 Skill 文件的 mtime，变更则警告 |
| **合并策略** | 数据部分自动合并，描述部分保留最新 |

#### O.5 Skill 版本回滚

**问题**：生成错误的 Skill 需要回滚

**解决方案**：

```bash
# 查看 Skill 历史版本
python main.py skill-history --skill web.md

# 回滚到指定版本
python main.py skill-rollback --skill web.md --version 2

# 对比版本差异
python main.py skill-diff --skill web.md --v1 2 --v2 3
```

**版本存储**：
```
.specify/skills/
├── project-context/
│   ├── web.md              # 当前版本
│   └── .history/
│       ├── web.md.v1       # 历史版本 1
│       ├── web.md.v2       # 历史版本 2
│       └── web.md.v3       # 历史版本 3
```

#### O.6 动态代码处理

**问题**：exec/eval/动态导入的代码无法静态分析

**处理方式**：

| 动态代码类型 | 检测方式 | 处理 |
|--------------|----------|------|
| `exec()`/`eval()` | AST 检测 | 标记为"动态代码，需人工审核" |
| `__import__()` | AST 检测 | 尝试解析字符串参数 |
| `importlib.import_module()` | AST 检测 | 尝试解析字符串参数 |
| `getattr()`/`setattr()` | 不处理 | 忽略 |

#### O.7 第三方库规范

**问题**：项目使用的第三方库如何处理

**策略**：

| 策略 | 说明 |
|------|------|
| **不分析源码** | 不分析 site-packages 中的代码 |
| **提取使用模式** | 分析项目中如何使用第三方库 |
| **生成使用指南** | 基于使用模式生成 `third_party.md` |

#### O.8 多分支支持

**问题**：不同分支可能有不同规范

**解决方案**：

```bash
# 为特定分支生成 Skill
python main.py generate-skills --branch feature/v2

# Skill 存储在分支特定目录
.specify/skills/
├── main/                    # main 分支
│   └── project-context/
├── feature-v2/              # feature/v2 分支
│   └── project-context/
└── index.yaml               # 分支索引
```

#### O.9 Skill 依赖循环检测

**问题**：A 依赖 B，B 依赖 A

**解决方案**：
- 构建依赖图时检测循环
- 发现循环时警告并打破循环（移除优先级低的依赖）

#### O.10 触发词冲突处理

**问题**：多个 Skill 有相同触发词

**解决方案**：
- 按优先级排序，高优先级 Skill 优先加载
- 相同优先级时，加载所有匹配的 Skill
- 生成时检测并警告触发词冲突

#### O.11 代码示例长度控制

**配置**：
```yaml
examples:
  max_lines: 30           # 单个示例最大行数
  max_examples: 3         # 每个规范最多示例数
  truncate_strategy: "head_tail"  # 超长时保留头尾
```

#### O.12 废弃代码检测

**策略**：
- 检测 `@deprecated` 装饰器
- 检测 `# TODO: remove` 等注释
- 检测未被引用的代码（可选，需要调用图分析）
- 废弃代码生成到 `deprecated.md`，不混入正常规范

### P. 安全与合规

#### P.1 数据安全

| 安全措施 | 说明 |
|----------|------|
| **本地处理** | 所有分析在本地完成，不上传代码 |
| **敏感信息过滤** | 自动过滤密钥、密码等（见 O.2） |
| **LLM 数据** | 仅发送脱敏后的结构化数据给 LLM |
| **输出审计** | 可配置输出前人工审核 |

#### P.2 合规检查

```yaml
compliance:
  audit_log: true           # 记录所有操作
  require_review: false     # 是否需要人工审核
  sensitive_scan: true      # 敏感信息扫描
  license_check: false      # 检查代码许可证
```

---

**文档版本**: 1.4.0
**最后更新**: 2025-01-22
**作者**: AI Assistant
