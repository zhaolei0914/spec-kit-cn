# 智能化项目上下文提取系统设计

## 一、核心目标

构建一个**LLM 驱动**的智能系统，能够：

1. **真正理解**项目的架构、设计决策、业务逻辑
2. **自动生成**完整的开发规范、技术规范、最佳实践
3. **输出的规范**能够直接指导 AI 生成符合项目要求的代码

## 二、系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           智能提取系统架构                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Phase 1: 代码理解                             │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │   │
│  │  │ 结构分析  │  │ 依赖分析  │  │ 模式识别  │  │ 语义提取  │        │   │
│  │  │ (AST)     │  │ (Import)  │  │ (统计)    │  │ (LLM)     │        │   │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Phase 2: 知识构建                             │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │   │
│  │  │ 架构知识  │  │ 规范知识  │  │ 业务知识  │  │ 约束知识  │        │   │
│  │  │ 图谱      │  │ 图谱      │  │ 图谱      │  │ 图谱      │        │   │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Phase 3: 规范生成                             │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │   │
│  │  │ 开发指南  │  │ 技术规范  │  │ API 契约  │  │ 代码模板  │        │   │
│  │  │ (LLM)     │  │ (LLM)     │  │ (LLM)     │  │ (LLM)     │        │   │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Phase 4: 质量保证                             │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │   │
│  │  │ 一致性    │  │ 完整性    │  │ 可用性    │  │ 反馈闭环  │        │   │
│  │  │ 检查      │  │ 检查      │  │ 验证      │  │ 优化      │        │   │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 三、Phase 1: 代码理解

### 3.1 智能代码分析流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           代码理解流程                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: 项目扫描                                                           │
│  ├── 目录结构分析                                                           │
│  ├── 文件类型统计                                                           │
│  ├── 依赖文件解析 (requirements.txt, setup.py)                              │
│  └── 配置文件识别                                                           │
│                                                                             │
│  Step 2: 代码采样                                                           │
│  ├── 识别关键文件 (入口、模型、配置、工具类)                                 │
│  ├── 按类型采样代表性代码                                                   │
│  └── 提取高频模式的示例                                                     │
│                                                                             │
│  Step 3: LLM 深度分析                                                       │
│  ├── 分析项目架构和设计模式                                                 │
│  ├── 理解业务领域和核心概念                                                 │
│  ├── 识别编码规范和约定                                                     │
│  └── 发现隐含的设计决策                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 LLM 分析 Prompt 设计

#### Prompt 1: 项目架构分析

```markdown
# 任务：分析项目架构

## 输入信息
- 项目目录结构：{directory_tree}
- 依赖列表：{dependencies}
- 入口文件内容：{entry_files}
- 配置文件内容：{config_files}

## 分析要求
请分析这个项目的架构，输出以下信息：

1. **项目类型**：Web 服务 / CLI 工具 / 库 / 其他
2. **技术栈**：
   - 主框架：
   - 数据库：
   - 缓存：
   - 消息队列：
   - 其他组件：
3. **架构模式**：MVC / 分层架构 / 微服务 / 其他
4. **模块划分**：
   - 核心模块：
   - 业务模块：
   - 工具模块：
5. **数据流向**：请求如何流经各层
6. **关键设计决策**：项目中体现的重要设计选择

## 输出格式
请以 JSON 格式输出，便于后续处理。
```

#### Prompt 2: 编码规范分析

```markdown
# 任务：分析编码规范

## 输入信息
- 代码示例（按类型分组）：
  - View 类示例：{view_samples}
  - Model 类示例：{model_samples}
  - Service 类示例：{service_samples}
  - 工具函数示例：{util_samples}

## 分析要求
请分析这些代码，提取编码规范：

1. **命名规范**：
   - 类命名：
   - 函数命名：
   - 变量命名：
   - 文件命名：
2. **代码结构**：
   - 类的组织方式：
   - 函数的组织方式：
   - 模块的组织方式：
3. **装饰器使用**：
   - 常用装饰器及其用途：
   - 装饰器组合模式：
4. **错误处理**：
   - 异常类型：
   - 错误码格式：
   - 异常处理模式：
5. **日志规范**：
   - Logger 获取方式：
   - 日志级别使用：
   - 日志格式：
6. **注释规范**：
   - Docstring 格式：
   - 行内注释风格：

## 输出格式
请以 JSON 格式输出，包含具体的代码示例。
```

#### Prompt 3: 业务领域分析

```markdown
# 任务：分析业务领域

## 输入信息
- 数据模型定义：{model_definitions}
- API 端点列表：{api_endpoints}
- 业务处理类：{handler_samples}

## 分析要求
请分析这个项目的业务领域：

1. **核心业务概念**：
   - 主要实体：
   - 实体关系：
   - 业务状态：
2. **业务流程**：
   - 主要流程：
   - 流程步骤：
   - 状态转换：
3. **领域术语表**：
   - 术语：定义
4. **业务规则**：
   - 验证规则：
   - 约束条件：
   - 计算逻辑：

## 输出格式
请以 JSON 格式输出。
```

## 四、Phase 2: 知识构建

### 4.1 知识图谱结构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           项目知识图谱                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         架构知识                                     │   │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │   │
│  │  │ 服务    │───→│ 模块    │───→│ 组件    │───→│ 类/函数 │          │   │
│  │  └─────────┘    └─────────┘    └─────────┘    └─────────┘          │   │
│  │       │              │              │              │                │   │
│  │       ↓              ↓              ↓              ↓                │   │
│  │  [依赖关系]     [调用关系]     [组合关系]     [继承关系]            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         规范知识                                     │   │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │   │
│  │  │ 命名    │    │ 结构    │    │ 错误    │    │ 日志    │          │   │
│  │  │ 规范    │    │ 规范    │    │ 规范    │    │ 规范    │          │   │
│  │  └─────────┘    └─────────┘    └─────────┘    └─────────┘          │   │
│  │       │              │              │              │                │   │
│  │       ↓              ↓              ↓              ↓                │   │
│  │  [示例代码]     [模式模板]     [错误码表]     [日志模板]            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         业务知识                                     │   │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │   │
│  │  │ 实体    │───→│ 关系    │───→│ 流程    │───→│ 规则    │          │   │
│  │  └─────────┘    └─────────┘    └─────────┘    └─────────┘          │   │
│  │       │              │              │              │                │   │
│  │       ↓              ↓              ↓              ↓                │   │
│  │  [模型定义]     [ER 图]       [流程图]       [验证逻辑]            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 知识存储格式

```json
{
  "project": {
    "name": "v7tov8Service",
    "type": "web_service",
    "framework": "django",
    "description": "V7 到 V8 管理数据迁移服务"
  },

  "architecture": {
    "pattern": "layered",
    "layers": [
      {"name": "web", "responsibility": "HTTP 请求处理", "components": ["views", "urls"]},
      {"name": "service", "responsibility": "业务逻辑", "components": ["services", "managers"]},
      {"name": "data", "responsibility": "数据访问", "components": ["models", "repositories"]}
    ],
    "modules": [
      {"name": "v7tov8Service", "type": "core", "description": "核心升级服务"},
      {"name": "DeploymentService", "type": "support", "description": "部署支持服务"}
    ]
  },

  "coding_standards": {
    "naming": {
      "class": {"pattern": "PascalCase", "suffix_rules": {"View": "视图类", "Service": "服务类"}},
      "function": {"pattern": "snake_case", "prefix_rules": {"get_": "获取", "create_": "创建"}},
      "constant": {"pattern": "UPPER_SNAKE_CASE"}
    },
    "structure": {
      "view_class": {
        "decorators": ["@formatting()", "@authenticated()"],
        "methods": ["get", "post", "put", "delete"],
        "example": "..."
      }
    },
    "error_handling": {
      "base_exception": "ABGeneralPurposeException",
      "error_code_format": "Module.SubModule.ErrorType",
      "error_code_file": "exception/*_errorcode.py",
      "throw_pattern": "raise ABGeneralPurposeException(I18nErrorData(...))"
    }
  },

  "business_domain": {
    "entities": [
      {"name": "Job", "description": "迁移作业", "states": ["pending", "running", "completed", "failed"]},
      {"name": "SubJob", "description": "子作业", "parent": "Job"}
    ],
    "processes": [
      {"name": "数据迁移", "steps": ["创建作业", "执行子作业", "汇总结果"]}
    ],
    "glossary": {
      "Job": "迁移作业，包含多个子作业",
      "SubJob": "子作业，执行具体的迁移任务"
    }
  }
}
```

## 五、Phase 3: 规范生成

### 5.1 生成的文档类型

| 文档类型 | 目标读者 | 内容 | 用途 |
|----------|----------|------|------|
| **开发指南** | 新人开发者 | 项目概述、环境搭建、开发流程 | 快速上手 |
| **技术规范** | 所有开发者 | 编码规范、架构规范、API 规范 | 代码审查 |
| **API 契约** | 前端/调用方 | 接口定义、参数说明、示例 | 接口对接 |
| **代码模板** | AI 代码生成 | 各类代码的标准模板 | 指导生成 |

### 5.2 代码模板设计（关键！）

代码模板是指导 AI 生成代码的核心，需要包含：

```markdown
# 代码模板：创建新的 API 接口

## 场景
当需要创建一个新的 HTTP API 接口时，使用此模板。

## 模板

```python
# 文件位置: {service_name}/views/{module_name}.py

import json
import logging
from django.views import View

# 装饰器导入（必须使用 V8 版本）
from Common.web.auth_v8 import authenticated
from Common.web.http_v8 import formatting

# 异常处理导入
from Common.exception.defines import ABGeneralPurposeException, I18nErrorData
from exception.upgrade_errorcode import {相关错误码}

logger = logging.getLogger('{service_name}')


class {ClassName}View(View):
    """
    {接口描述}

    URL: {url_path}
    Methods: {methods}
    """

    @formatting()
    @authenticated()
    def {method}(self, request, *args, **kwargs):
        """
        {方法描述}

        Args:
            request: HTTP 请求对象

        Returns:
            dict: 响应数据

        Raises:
            ABGeneralPurposeException: 业务异常
        """
        try:
            # 1. 参数解析
            data = json.loads(request.body) if request.body else {}
            {param_name} = data.get('{param_key}')

            # 2. 参数校验
            if not {param_name}:
                raise ABGeneralPurposeException(I18nErrorData(
                    error_code=Upgrade_ParamsError,
                    description="参数 {param_key} 不能为空",
                ))

            # 3. 业务处理
            result = self._do_business_logic({param_name})

            # 4. 返回结果
            return {'data': result}

        except ABGeneralPurposeException:
            raise
        except Exception as e:
            logger.exception("处理请求失败")
            raise ABGeneralPurposeException(I18nErrorData(
                error_code=Upgrade_InternalError,
                description=str(e),
            ))

    def _do_business_logic(self, {param_name}):
        """业务逻辑处理"""
        # TODO: 实现业务逻辑
        pass
```

## 检查清单

- [ ] 使用了正确的装饰器组合 `@formatting()` + `@authenticated()`
- [ ] 导入了正确版本的装饰器（V8 版本）
- [ ] 使用了项目定义的错误码
- [ ] 添加了适当的日志记录
- [ ] 异常处理符合规范
- [ ] Docstring 完整

## 相关规范

- 错误处理：参见 error.md
- 日志规范：参见 logging.md
- API 规范：参见 api.md
```

### 5.3 LLM 生成 Prompt

#### Prompt: 生成开发指南

```markdown
# 任务：生成项目开发指南

## 输入信息
- 项目知识图谱：{knowledge_graph}
- 代码示例：{code_samples}

## 生成要求
请生成一份完整的开发指南，包含以下章节：

1. **项目概述**
   - 项目背景和目标
   - 技术栈介绍
   - 架构概览

2. **环境搭建**
   - 依赖安装
   - 配置说明
   - 启动步骤

3. **开发流程**
   - 代码组织
   - 分支管理
   - 提交规范

4. **常见开发场景**
   - 如何添加新的 API 接口
   - 如何添加新的数据模型
   - 如何添加新的业务逻辑
   - 如何添加新的错误码

5. **调试和测试**
   - 本地调试方法
   - 单元测试编写
   - 集成测试

6. **常见问题**
   - FAQ

## 输出要求
- 使用 Markdown 格式
- 包含具体的代码示例（来自项目实际代码）
- 语言简洁清晰
- 适合新人阅读
```

## 六、Phase 4: 质量保证

### 6.1 一致性检查

```python
def check_consistency(knowledge_graph, generated_docs):
    """
    检查生成的文档与知识图谱的一致性

    检查项：
    1. 文档中的代码示例是否与知识图谱中的规范一致
    2. 文档中的术语是否与知识图谱中的定义一致
    3. 文档中的流程是否与知识图谱中的流程一致
    """
    issues = []

    # 检查代码示例
    for doc in generated_docs:
        for code_sample in doc.code_samples:
            if not matches_coding_standards(code_sample, knowledge_graph.coding_standards):
                issues.append(f"代码示例不符合规范: {code_sample}")

    return issues
```

### 6.2 完整性检查

```python
def check_completeness(knowledge_graph, generated_docs):
    """
    检查生成的文档是否完整覆盖所有知识点

    检查项：
    1. 所有模块是否都有对应的文档
    2. 所有规范是否都有说明
    3. 所有业务流程是否都有描述
    """
    coverage = {
        "modules": [],
        "standards": [],
        "processes": [],
    }

    # 统计覆盖率
    for module in knowledge_graph.modules:
        if module_documented(module, generated_docs):
            coverage["modules"].append(module)

    return coverage
```

### 6.3 可用性验证

```python
def validate_usability(generated_docs, test_scenarios):
    """
    验证生成的文档是否能指导 AI 生成正确的代码

    方法：
    1. 使用生成的文档作为上下文
    2. 让 AI 根据文档生成代码
    3. 检查生成的代码是否符合项目规范
    """
    results = []

    for scenario in test_scenarios:
        # 使用文档作为上下文
        context = build_context(generated_docs, scenario)

        # 让 AI 生成代码
        generated_code = llm.generate_code(scenario.prompt, context)

        # 检查代码质量
        quality = evaluate_code(generated_code, scenario.expected)
        results.append(quality)

    return results
```

## 七、实现计划

### 7.1 MVP 版本（2 周）

**目标**：验证 LLM 驱动的提取方案可行性

1. **Week 1**
   - 实现代码采样逻辑
   - 设计并测试 LLM 分析 Prompt
   - 构建基础知识图谱

2. **Week 2**
   - 实现规范文档生成
   - 实现代码模板生成
   - 基础质量检查

### 7.2 完整版本（4 周）

**目标**：生产可用的智能提取系统

3. **Week 3**
   - 完善知识图谱
   - 增加业务领域分析
   - 实现一致性检查

4. **Week 4**
   - 实现可用性验证
   - 反馈闭环优化
   - 文档和测试

## 八、技术选型

| 组件 | 选型 | 理由 |
|------|------|------|
| LLM | Claude / GPT-4 | 代码理解能力强 |
| 代码解析 | AST + Tree-sitter | 多语言支持 |
| 知识存储 | JSON + SQLite | 简单高效 |
| 文档生成 | Jinja2 + Markdown | 灵活可定制 |

## 九、成本估算

假设项目代码量 10 万行：

| 阶段 | Token 消耗 | 成本（GPT-4） |
|------|------------|---------------|
| 架构分析 | ~50K | ~$1.5 |
| 规范分析 | ~100K | ~$3 |
| 业务分析 | ~100K | ~$3 |
| 文档生成 | ~200K | ~$6 |
| **总计** | ~450K | **~$13.5** |

## 十、预期产出

### 10.1 文档产出

```
.specify/skills/
├── project-context/
│   ├── SKILL.md              # 项目概述（AI 生成）
│   ├── architecture.md       # 架构说明（AI 生成）
│   ├── quick-start.md        # 快速入门（AI 生成）
│   │
│   ├── standards/
│   │   ├── coding.md         # 编码规范（AI 生成）
│   │   ├── naming.md         # 命名规范（AI 生成）
│   │   ├── error.md          # 错误处理（AI 生成）
│   │   └── logging.md        # 日志规范（AI 生成）
│   │
│   ├── templates/
│   │   ├── view.md           # View 模板（AI 生成）
│   │   ├── model.md          # Model 模板（AI 生成）
│   │   ├── service.md        # Service 模板（AI 生成）
│   │   └── handler.md        # Handler 模板（AI 生成）
│   │
│   └── business/
│       ├── glossary.md       # 业务术语表（AI 生成）
│       ├── entities.md       # 业务实体（AI 生成）
│       └── processes.md      # 业务流程（AI 生成）
│
└── knowledge-base/
    └── project.json          # 知识图谱（结构化数据）
```

### 10.2 使用效果

**场景**：AI 需要为项目添加一个新的 API 接口

**输入**：
```
请为 v7tov8Service 添加一个查询作业详情的 API 接口
```

**AI 行为**：
1. 读取 `SKILL.md` 了解项目概述
2. 读取 `templates/view.md` 获取 View 模板
3. 读取 `standards/error.md` 了解错误处理规范
4. 根据模板和规范生成代码

**输出**：符合项目规范的代码

---

**版本**: 2.0.0 | **最后更新**: 2025-01-22
