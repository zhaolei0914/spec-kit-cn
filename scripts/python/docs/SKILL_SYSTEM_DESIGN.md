# Skill 体系设计

## 一、Skill 的定义

**Skill** 是一个自包含的知识单元，大模型可以根据任务需求**动态加载**相关的 Skill 来获取上下文。

### 1.1 Skill 的特点

| 特点 | 说明 |
|------|------|
| **自包含** | 每个 Skill 包含完成特定任务所需的全部信息 |
| **可索引** | 通过元数据可以快速定位需要的 Skill |
| **可组合** | 多个 Skill 可以组合使用 |
| **可更新** | 独立更新，不影响其他 Skill |

### 1.2 Skill 的结构

```yaml
# SKILL.md 头部元数据
---
skill_id: project-context/web
skill_name: Web 接口开发规范
skill_type: coding_standard
triggers:
  - "创建 API"
  - "添加接口"
  - "View 类"
  - "HTTP 请求"
dependencies:
  - project-context/error
  - project-context/imports
priority: high
version: 1.0.0
---

# 正文内容
...
```

## 二、Skill 分类体系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Skill 分类体系                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Level 1: 项目级 Skill                             │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  project-context/SKILL.md                                     │  │   │
│  │  │  - 项目概述、技术栈、架构、模块划分                             │  │   │
│  │  │  - 触发词: "项目", "概述", "架构"                               │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Level 2: 规范类 Skill                             │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │ web.md  │  │models.md│  │service  │  │handler  │  │ error   │   │   │
│  │  │         │  │         │  │  .md    │  │  .md    │  │  .md    │   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│  │  触发词:     触发词:      触发词:      触发词:      触发词:         │   │
│  │  API,View   Model,数据库  Service     Handler     异常,错误码      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Level 3: 辅助类 Skill                             │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │imports  │  │constants│  │ naming  │  │ config  │  │ logging │   │   │
│  │  │  .md    │  │  .md    │  │  .md    │  │  .md    │  │  .md    │   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│  │  触发词:     触发词:      触发词:      触发词:      触发词:         │   │
│  │  import    常量,枚举     命名         配置         日志            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Level 4: 业务类 Skill                             │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                │   │
│  │  │glossary │  │entities │  │processes│  │ rules   │                │   │
│  │  │  .md    │  │  .md    │  │  .md    │  │  .md    │                │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘                │   │
│  │  触发词:     触发词:      触发词:      触发词:                      │   │
│  │  术语,概念   实体,模型    流程,状态    规则,校验                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Level 5: 模板类 Skill                             │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                │   │
│  │  │template/│  │template/│  │template/│  │template/│                │   │
│  │  │view.md  │  │model.md │  │service  │  │handler  │                │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘                │   │
│  │  触发词:     触发词:      触发词:      触发词:                      │   │
│  │  新建View   新建Model    新建Service  新建Handler                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 三、Skill 索引设计

### 3.1 索引文件结构

```yaml
# .specify/skills/index.yaml
version: "1.0"
project: "v7tov8Service"
last_updated: "2025-01-22"

skills:
  # 项目级
  - id: project-context
    path: project-context/SKILL.md
    type: overview
    triggers: ["项目", "概述", "架构", "技术栈"]
    priority: 1

  # 规范类
  - id: project-context/web
    path: project-context/web.md
    type: coding_standard
    triggers: ["API", "接口", "View", "HTTP", "请求", "响应"]
    dependencies: [project-context/error, project-context/imports]
    priority: 2

  - id: project-context/models
    path: project-context/models.md
    type: coding_standard
    triggers: ["Model", "模型", "数据库", "字段", "ORM"]
    dependencies: [project-context/imports]
    priority: 2

  - id: project-context/error
    path: project-context/error.md
    type: coding_standard
    triggers: ["异常", "错误", "错误码", "Exception", "raise"]
    dependencies: []
    priority: 2

  # 辅助类
  - id: project-context/imports
    path: project-context/imports.md
    type: reference
    triggers: ["import", "导入", "引用"]
    dependencies: []
    priority: 3

  - id: project-context/constants
    path: project-context/constants.md
    type: reference
    triggers: ["常量", "枚举", "Enum", "状态码"]
    dependencies: []
    priority: 3

  # 业务类
  - id: project-context/glossary
    path: project-context/glossary.md
    type: business
    triggers: ["术语", "概念", "定义", "Job", "SubJob"]
    dependencies: []
    priority: 4

  # 模板类
  - id: project-context/template/view
    path: project-context/templates/view.md
    type: template
    triggers: ["新建View", "创建接口", "添加API"]
    dependencies: [project-context/web, project-context/error]
    priority: 5
```

### 3.2 动态加载逻辑

```python
class SkillLoader:
    """Skill 动态加载器"""

    def __init__(self, index_path: str):
        self.index = self._load_index(index_path)
        self.cache = {}

    def find_relevant_skills(self, user_request: str) -> List[str]:
        """
        根据用户请求找到相关的 Skill

        Args:
            user_request: 用户的请求文本

        Returns:
            相关 Skill ID 列表（按优先级排序）
        """
        matched = []

        for skill in self.index['skills']:
            # 检查触发词
            for trigger in skill['triggers']:
                if trigger.lower() in user_request.lower():
                    matched.append({
                        'id': skill['id'],
                        'priority': skill['priority'],
                        'dependencies': skill.get('dependencies', [])
                    })
                    break

        # 按优先级排序
        matched.sort(key=lambda x: x['priority'])

        # 解析依赖
        result = []
        for skill in matched:
            # 先加载依赖
            for dep in skill['dependencies']:
                if dep not in result:
                    result.append(dep)
            # 再加载自身
            if skill['id'] not in result:
                result.append(skill['id'])

        return result

    def load_skills(self, skill_ids: List[str]) -> str:
        """
        加载指定的 Skill 内容

        Args:
            skill_ids: Skill ID 列表

        Returns:
            合并后的 Skill 内容
        """
        contents = []

        for skill_id in skill_ids:
            if skill_id in self.cache:
                contents.append(self.cache[skill_id])
            else:
                skill_info = self._find_skill(skill_id)
                if skill_info:
                    content = self._read_skill(skill_info['path'])
                    self.cache[skill_id] = content
                    contents.append(content)

        return '\n\n---\n\n'.join(contents)
```

## 四、Skill 内容规范

### 4.1 SKILL.md 模板（项目级）

```markdown
---
skill_id: project-context
skill_name: 项目上下文
skill_type: overview
triggers:
  - "项目"
  - "概述"
  - "架构"
  - "技术栈"
  - "v7tov8"
dependencies: []
priority: 1
version: 1.0.0
last_updated: 2025-01-22
---

# {项目名称} 项目上下文

## 项目概述

{项目描述，1-2 段}

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Django | 3.x |
| 数据库 | MySQL | 8.0 |
| ... | ... | ... |

## 架构概览

{架构图或描述}

## 模块划分

| 模块 | 职责 | 关键文件 |
|------|------|----------|
| ... | ... | ... |

## 开发规范导航

根据你的开发任务，加载对应的 Skill：

| 任务 | 需要加载的 Skill |
|------|------------------|
| 创建 API 接口 | `web.md`, `error.md`, `imports.md` |
| 定义数据模型 | `models.md`, `imports.md` |
| 编写业务逻辑 | `service.md`, `error.md` |
| 处理后台任务 | `handler.md`, `error.md` |
```

### 4.2 规范类 Skill 模板

```markdown
---
skill_id: project-context/web
skill_name: Web 接口开发规范
skill_type: coding_standard
triggers:
  - "API"
  - "接口"
  - "View"
  - "HTTP"
dependencies:
  - project-context/error
  - project-context/imports
priority: 2
version: 1.0.0
---

# Web 接口开发规范

## 适用场景

当你需要：
- 创建新的 HTTP API 接口
- 修改现有接口
- 理解接口实现方式

## 核心规范

### 1. View 类定义

**必须**：
- 继承 `django.views.View`
- 使用 `@formatting()` 装饰器
- 使用 `@authenticated()` 装饰器

**示例**：
```python
{来自项目的真实代码示例}
```

### 2. 装饰器顺序

```python
@formatting()      # 外层：响应格式化
@authenticated()   # 内层：认证检查
def get(self, request):
    ...
```

### 3. 参数处理

{参数处理规范}

### 4. 响应格式

{响应格式规范}

## 检查清单

在提交代码前，确保：
- [ ] 使用了正确的装饰器组合
- [ ] 导入了 V8 版本的装饰器
- [ ] 异常处理符合规范
- [ ] 添加了日志记录

## 相关 Skill

- 错误处理：`error.md`
- Import 模板：`imports.md`
```

### 4.3 模板类 Skill 模板

```markdown
---
skill_id: project-context/template/view
skill_name: View 代码模板
skill_type: template
triggers:
  - "新建View"
  - "创建接口"
  - "添加API"
dependencies:
  - project-context/web
  - project-context/error
  - project-context/imports
priority: 5
version: 1.0.0
---

# View 代码模板

## 使用说明

当你需要创建一个新的 API 接口时，使用此模板。

## 完整模板

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
        """
        try:
            # 1. 参数解析
            data = json.loads(request.body) if request.body else {}

            # 2. 参数校验
            # TODO: 添加参数校验逻辑

            # 3. 业务处理
            result = self._do_business({参数})

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

    def _do_business(self, {参数}):
        """业务逻辑"""
        pass
```

## 占位符说明

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{service_name}` | 服务名称 | `v7tov8Service` |
| `{module_name}` | 模块名称 | `job` |
| `{ClassName}` | 类名（PascalCase） | `JobDetail` |
| `{url_path}` | URL 路径 | `/api/v1/jobs/<job_id>` |
| `{methods}` | HTTP 方法 | `GET, POST` |
| `{method}` | 方法名（小写） | `get` |
| `{相关错误码}` | 需要的错误码 | `Upgrade_Job_NotFound` |

## 生成检查

生成代码后，检查：
1. 文件位置是否正确
2. 导入是否完整
3. 错误码是否存在
4. URL 是否已注册
```

### 4.4 业务类 Skill 模板

```markdown
---
skill_id: project-context/glossary
skill_name: 业务术语表
skill_type: business
triggers:
  - "术语"
  - "概念"
  - "Job"
  - "SubJob"
  - "迁移"
dependencies: []
priority: 4
version: 1.0.0
---

# 业务术语表

## 核心概念

### Job（迁移作业）

**定义**：一次完整的 V7 到 V8 数据迁移任务。

**属性**：
- `id`: 作业唯一标识
- `status`: 作业状态（pending/running/completed/failed）
- `create_time`: 创建时间
- `update_time`: 更新时间

**状态流转**：
```
pending → running → completed
              ↓
           failed
```

**相关代码**：
- 模型定义：`v7tov8Service/models.py::Job`
- 服务类：`v7tov8Service/services/job_service.py`

### SubJob（子作业）

**定义**：Job 下的具体迁移任务，如用户迁移、任务迁移等。

**类型**：
- `UserImport`: 用户数据迁移
- `TenantImport`: 租户数据迁移
- `TaskImport`: 任务数据迁移
- `ClientUpgrade`: 客户端升级

**与 Job 的关系**：一个 Job 包含多个 SubJob

## 业务流程

### 数据迁移流程

1. **创建作业**：用户发起迁移请求，创建 Job
2. **分解任务**：系统根据迁移类型创建 SubJob
3. **执行迁移**：逐个执行 SubJob
4. **汇总结果**：所有 SubJob 完成后，更新 Job 状态

## 在代码中使用

当你看到以下代码时：
```python
job = Job.objects.get(id=job_id)
sub_jobs = job.sub_jobs.all()
```

这表示：获取一个迁移作业及其所有子作业。
```

## 五、Skill 生成流程

### 5.1 LLM 生成 Prompt

```markdown
# 任务：生成 {skill_type} 类型的 Skill 文档

## 输入信息

### 项目知识
{knowledge_graph}

### 代码示例
{code_samples}

### 已有 Skill
{existing_skills}

## 生成要求

请生成一个符合以下格式的 Skill 文档：

1. **YAML 头部**（必须包含）
   - skill_id: 唯一标识
   - skill_name: 名称
   - skill_type: 类型
   - triggers: 触发词列表（用于动态加载）
   - dependencies: 依赖的其他 Skill
   - priority: 优先级（1-5）
   - version: 版本号

2. **正文内容**
   - 适用场景：什么时候需要这个 Skill
   - 核心规范：具体的规范内容
   - 代码示例：来自项目的真实代码
   - 检查清单：使用前的检查项
   - 相关 Skill：关联的其他 Skill

## 输出格式

直接输出 Markdown 文档，包含 YAML 头部。

## 注意事项

1. triggers 要覆盖用户可能使用的各种表达方式
2. 代码示例必须来自项目实际代码
3. 规范要具体、可操作
4. 内容要自包含，不依赖外部知识
```

### 5.2 生成流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Skill 生成流程                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: 知识提取                                                           │
│  ├── 代码分析（AST + 统计）                                                 │
│  ├── 模式识别（高频模式）                                                   │
│  └── 语义理解（LLM）                                                        │
│                     ↓                                                       │
│  Step 2: 知识图谱构建                                                       │
│  ├── 架构知识                                                               │
│  ├── 规范知识                                                               │
│  ├── 业务知识                                                               │
│  └── 约束知识                                                               │
│                     ↓                                                       │
│  Step 3: Skill 规划                                                         │
│  ├── 确定 Skill 列表                                                        │
│  ├── 确定 Skill 类型                                                        │
│  ├── 确定依赖关系                                                           │
│  └── 确定触发词                                                             │
│                     ↓                                                       │
│  Step 4: Skill 生成（LLM）                                                  │
│  ├── 逐个生成 Skill 内容                                                    │
│  ├── 填充代码示例                                                           │
│  └── 生成检查清单                                                           │
│                     ↓                                                       │
│  Step 5: 索引生成                                                           │
│  ├── 生成 index.yaml                                                        │
│  └── 验证依赖关系                                                           │
│                     ↓                                                       │
│  Step 6: 质量验证                                                           │
│  ├── 一致性检查                                                             │
│  ├── 完整性检查                                                             │
│  └── 可用性测试                                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 六、动态加载示例

### 6.1 场景：用户请求创建 API 接口

**用户输入**：
```
请为 v7tov8Service 添加一个查询作业详情的 API 接口
```

**Skill 加载过程**：

```python
# 1. 分析用户请求
request = "请为 v7tov8Service 添加一个查询作业详情的 API 接口"

# 2. 匹配触发词
matched_triggers = {
    "API": ["project-context/web"],
    "接口": ["project-context/web"],
    "作业": ["project-context/glossary"],
}

# 3. 确定需要加载的 Skill
skills_to_load = [
    "project-context/web",      # 直接匹配
    "project-context/glossary", # 直接匹配
    "project-context/error",    # web 的依赖
    "project-context/imports",  # web 的依赖
    "project-context/template/view",  # 创建接口需要模板
]

# 4. 加载 Skill 内容
context = skill_loader.load_skills(skills_to_load)

# 5. 提供给 LLM
llm_prompt = f"""
{context}

用户请求：{request}

请根据以上规范生成代码。
"""
```

### 6.2 场景：用户请求定义错误码

**用户输入**：
```
添加一个新的错误码：作业不存在
```

**Skill 加载过程**：

```python
# 匹配的 Skill
skills_to_load = [
    "project-context/error",     # 错误处理规范
    "project-context/constants", # 常量定义规范
]
```

## 七、完整 Skill 目录结构

```
.specify/skills/
├── index.yaml                    # Skill 索引文件
│
├── project-context/              # 项目上下文 Skill 集
│   ├── SKILL.md                  # 项目概述（入口）
│   │
│   ├── standards/                # 规范类 Skill
│   │   ├── web.md                # Web 接口规范
│   │   ├── models.md             # 数据模型规范
│   │   ├── service.md            # 服务层规范
│   │   ├── handler.md            # 处理器规范
│   │   ├── error.md              # 错误处理规范
│   │   ├── constants.md          # 常量定义规范
│   │   ├── config.md             # 配置规范
│   │   ├── logging.md            # 日志规范
│   │   └── test.md               # 测试规范
│   │
│   ├── references/               # 辅助类 Skill
│   │   ├── imports.md            # Import 模板
│   │   ├── urls.md               # URL 路由
│   │   └── models_reference.md   # 模型速查
│   │
│   ├── business/                 # 业务类 Skill
│   │   ├── glossary.md           # 业务术语表
│   │   ├── entities.md           # 业务实体
│   │   ├── processes.md          # 业务流程
│   │   └── rules.md              # 业务规则
│   │
│   └── templates/                # 模板类 Skill
│       ├── view.md               # View 模板
│       ├── model.md              # Model 模板
│       ├── service.md            # Service 模板
│       ├── handler.md            # Handler 模板
│       └── test.md               # Test 模板
│
├── api-skill/                    # API Skill 集（可选）
│   ├── SKILL.md
│   └── endpoints/
│
└── business-rules/               # 业务规则 Skill 集（可选）
    └── SKILL.md
```

## 八、实现优先级

### Phase 1: 基础 Skill 体系（1 周）

1. 设计并实现 Skill 索引格式
2. 实现 Skill 动态加载器
3. 手动创建核心 Skill（web, models, error）

### Phase 2: LLM 生成 Skill（2 周）

4. 实现知识提取流程
5. 设计 LLM Prompt
6. 实现 Skill 自动生成

### Phase 3: 质量保证（1 周）

7. 实现一致性检查
8. 实现可用性测试
9. 反馈闭环优化

---

**版本**: 1.0.0 | **最后更新**: 2025-01-22
