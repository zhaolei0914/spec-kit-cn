# 工作流修改示例：/6-编写代码

> **示例文件** - 展示如何将 Skill/Wiki 集成到工作流中

---

## 修改前后对比

### ❌ 修改前（原始版本）

```markdown
## 概要

1. 加载和分析实施上下文:
   - **必需**: 读取 `.windsurf/skills/project-context/SKILL.md`（项目技术栈、约定、开发规范、项目章程）
   - **必需**: 读取 `.specify/memory/MEMORY.md`，按读取协议加载编码规范和已知陷阱
   - **必需**: 读取 `specs/[ID]/tasks.md` 获取任务列表
   - **必需**: 读取 `specs/[ID]/design.md` 获取开发设计文档
```

### ✅ 修改后（集成版本）

```markdown
## 概要

> **前置条件**: 建议在执行本流程前先运行 `/5-实施前检测` 进行制品一致性分析

### 1. 加载上下文（三层加载策略）

#### L1: 全局上下文（必读）

```bash
# 技术栈、规范、模式
cat .windsurf/skills/project-context/SKILL.md

# 架构、模块关系、工作流
cat .specify/wikis/spec-kit-cn/overview.md
```

**从 SKILL.md 获取**：
- 技术栈版本（Python >=3.11, Typer, Rich, httpx）
- 命名规范（snake_case / PascalCase / UPPER_SNAKE_CASE）
- 禁止规则（不用 print()，不用裸 except，不用 import *）
- 错误处理规范（使用 raise / try/except）
- 代码风格（4 空格缩进，绝对导入，Google 风格注释）

**从 Wiki Overview 获取**：
- 架构类型（CLI 工具，脚本驱动架构）
- 模块协作方式（通过文件系统，无 Python 调用依赖）
- 核心工作流（init → 模板 → 文档站点）

#### L2: 角色上下文（Developer）

```bash
# 编码规范详解
cat .specify/wikis/spec-kit-cn/memory.md

# CLI 实现细节
cat .specify/wikis/spec-kit-cn/cli-core.md
```

**从 Wiki Memory 获取**：
- Memory 系统设计（constitution.md 固化工程共识）
- 编码规范详细说明（超出 SKILL.md 的细节）
- 已知陷阱和反模式

**从 Wiki CLI-Core 获取**：
- CLI 架构设计（Typer 驱动的命令式架构）
- 命令模式实现（@app.command() 装饰器）
- 交互式引导设计（rich.Live + readchar）
- GitHub 分发机制（速率限制处理）

#### L3: 任务上下文（编码实现）

```bash
# 按读取协议加载 Memory 文件
cat .specify/memory/MEMORY.md

# 编码规范（命名、格式、注释）
cat .specify/memory/coding-standards.md

# 已知陷阱和反模式
cat .specify/memory/known-pitfalls.md

# 可复用代码模式
cat .specify/memory/code-patterns.md

# 任务列表、函数规格
cat specs/[ID]/tasks.md

# 设计文档、接口定义
cat specs/[ID]/design.md
```

**从 Memory 获取**：
- **coding-standards.md**: 详细的编码规范（超出 SKILL.md 的细节）
- **known-pitfalls.md**: 已知陷阱列表（避免重复踩坑）
- **code-patterns.md**: 可复用的代码模式（减少重复实现）

**从 Tasks.md 获取**：
- 完整任务列表和执行计划
- 函数规格说明（函数签名、参数、返回值、行为、错误码）
- 错误码定义（实现时必须使用这些错误码）

**从 Design.md 获取**：
- **功能模块的代码脚手架**（章节 X.X.5）: 函数/类签名、参数类型、返回值、错误处理模式
- **数据库设计章节**: 所有表定义（表名、字段、类型、约束）
- **接口设计章节**: 所有接口定义（路径、方法、参数、响应）
- **功能流程章节**: 所有业务流程定义
- **这些是实现的唯一权威来源，实现必须与 design.md 完全一致**

---

### 2. 上下文使用指导（编码时严格遵守）

在编写代码时，**严格按以下优先级使用上下文**：

#### 优先级 1: 接口定义和业务规则（来自 Design.md）

**必须 100% 一致，不允许任何偏差！**

- ✅ **函数签名**: 函数名、参数类型、返回值类型 → **必须完全一致**
  ```python
  # Design.md 定义:
  def check_tool(tool: str, install_url: str) -> bool:
  
  # 实现时必须完全一致，不能改为:
  # def check_tool(tool_name: str, url: str) -> bool:  ❌ 错误！
  ```

- ✅ **数据库表结构**: 表名、字段名、类型、约束 → **必须完全一致**
  ```sql
  -- Design.md 定义:
  CREATE TABLE users (
      id INTEGER PRIMARY KEY,
      username VARCHAR(50) NOT NULL UNIQUE
  );
  
  -- 实现时必须完全一致，不能改为:
  -- CREATE TABLE user (  ❌ 错误！表名不一致
  --     user_id INTEGER PRIMARY KEY,  ❌ 错误！字段名不一致
  ```

- ✅ **API 接口**: 路径、方法、参数、响应格式 → **必须完全一致**
  ```python
  # Design.md 定义:
  @app.get("/api/v1/users/{user_id}")
  def get_user(user_id: int) -> UserResponse:
  
  # 实现时必须完全一致，不能改为:
  # @app.get("/users/{id}")  ❌ 错误！路径不一致
  ```

- ✅ **业务流程**: 状态机、错误码 → **必须完全一致**
  ```python
  # Design.md 定义的错误码:
  ERROR_USER_NOT_FOUND = 1001
  ERROR_INVALID_PASSWORD = 1002
  
  # 实现时必须使用这些错误码，不能自己定义:
  # ERROR_NOT_FOUND = 404  ❌ 错误！未在 design.md 中定义
  ```

#### 优先级 2: 编码规范（来自 SKILL.md + Memory）

**必须严格遵守，确保代码风格一致！**

- ✅ **命名规范**:
  ```python
  # ✅ 正确
  def get_user_by_id(user_id: int) -> User:  # 函数: snake_case
  class UserManager:                          # 类: PascalCase
  MAX_RETRY_COUNT = 3                         # 常量: UPPER_SNAKE_CASE
  
  # ❌ 错误
  def GetUserById(userId: int) -> User:       # 函数不应用 PascalCase
  class user_manager:                         # 类不应用 snake_case
  max_retry_count = 3                         # 常量不应用 snake_case
  ```

- ✅ **禁止规则**:
  ```python
  # ✅ 正确
  console.print("[green]Success[/green]")     # 使用 console.print()
  from pathlib import Path                    # 使用 Path 对象
  path = Path("src") / "file.py"
  
  # ❌ 错误
  print("Success")                            # 禁止使用 print()
  path = "src/" + "file.py"                   # 禁止字符串拼接路径
  ```

- ✅ **错误处理**:
  ```python
  # ✅ 正确
  try:
      result = risky_operation()
  except ValueError as e:                     # 捕获具体异常
      console.print(f"[red]Error:[/red] {e}")
      raise
  
  # ❌ 错误
  try:
      result = risky_operation()
  except:                                     # 禁止裸 except
      print("Error")                          # 禁止 print()
  ```

- ✅ **导入规范**:
  ```python
  # ✅ 正确
  from pathlib import Path                    # 绝对导入
  from rich.console import Console
  
  # ❌ 错误
  from pathlib import *                       # 禁止 import *
  from .utils import helper                   # 避免相对导入
  ```

#### 优先级 3: 架构模式（来自 Wiki Overview + CLI-Core）

**必须符合项目架构设计！**

- ✅ **模块协作**: 通过文件系统，不用 Python 调用
  ```python
  # ✅ 正确：通过文件系统协作
  def save_config(config: dict):
      with open(".specify/config.json", "w") as f:
          json.dump(config, f)
  
  # ❌ 错误：直接调用其他模块的函数
  from other_module import process_config
  process_config(config)  # 违反解耦原则
  ```

- ✅ **命令模式**: Typer 框架，`@app.command()`
  ```python
  # ✅ 正确
  @app.command()
  def init(ai_assistant: str = typer.Option(None, "--ai")):
      ...
  
  # ❌ 错误：不使用 Typer 装饰器
  def init(ai_assistant=None):
      ...
  ```

- ✅ **配置驱动**: 使用 `AGENT_CONFIG` 字典，不硬编码
  ```python
  # ✅ 正确
  AGENT_CONFIG = {
      "claude": {"name": "Claude Code", "folder": ".claude/"},
      "gemini": {"name": "Gemini CLI", "folder": ".gemini/"},
  }
  
  agent_folder = AGENT_CONFIG[agent_key]["folder"]
  
  # ❌ 错误：硬编码 Agent 映射
  if agent_key == "claude":
      agent_folder = ".claude/"
  elif agent_key == "gemini":
      agent_folder = ".gemini/"
  ```

#### 优先级 4: 代码复用（来自 Memory Code-Patterns）

**优先复用现有代码，避免重复实现！**

- ✅ **搜索现有函数**:
  ```bash
  # 在编码前，先搜索是否已有类似函数
  grep -r "def check_tool" src/
  grep -r "def download_template" src/
  ```

- ✅ **复用现有代码**:
  ```python
  # ✅ 正确：复用现有函数
  from specify_cli import check_tool
  
  if not check_tool("git", "https://git-scm.com/"):
      console.print("[red]Git is required[/red]")
  
  # ❌ 错误：重新实现已存在的函数
  def my_check_tool(tool_name):  # 已有 check_tool，不应重复实现
      return shutil.which(tool_name) is not None
  ```

- ✅ **完善现有代码**:
  ```python
  # 如果现有函数不完整，完善它而不是新建
  # 原函数:
  def check_tool(tool: str) -> bool:
      return shutil.which(tool) is not None
  
  # ✅ 正确：完善现有函数
  def check_tool(tool: str, install_url: str = None) -> bool:
      exists = shutil.which(tool) is not None
      if not exists and install_url:
          console.print(f"Install from: {install_url}")
      return exists
  
  # ❌ 错误：新建函数
  def check_tool_with_url(tool: str, url: str) -> bool:
      ...
  ```

#### 优先级 5: 避免陷阱（来自 Memory Known-Pitfalls）

**检查已知陷阱，避免重复踩坑！**

- ✅ **检查 known-pitfalls.md**:
  ```markdown
  # known-pitfalls.md 示例内容:
  
  ## 陷阱 1: 使用 cursor 作为 AGENT_CONFIG 键
  
  **问题**: 使用 "cursor" 作为键，但实际 CLI 工具是 "cursor-agent"
  **后果**: check_tool("cursor") 找不到工具，因为实际命令是 cursor-agent
  **解决**: 使用实际 CLI 工具名 "cursor-agent" 作为键
  
  ## 陷阱 2: 硬编码路径分隔符
  
  **问题**: 使用 "/" 或 "\\" 硬编码路径
  **后果**: 跨平台兼容性问题
  **解决**: 使用 Path 对象或 os.path.join()
  ```

- ✅ **在编码时避免这些陷阱**:
  ```python
  # ✅ 正确：使用实际 CLI 工具名
  AGENT_CONFIG = {
      "cursor-agent": {"name": "Cursor", ...},  # 不是 "cursor"
  }
  
  # ✅ 正确：使用 Path 对象
  config_path = Path(".specify") / "config.json"  # 不是 ".specify/config.json"
  ```

---

### 3. 实施代码编写

按 tasks.md 中的任务列表逐一实现，每个任务完成后：

1. **自检清单**:
   - [ ] 函数签名与 design.md 一致
   - [ ] 命名符合 SKILL.md 规范
   - [ ] 使用 `console.print()` 而非 `print()`
   - [ ] 使用 `Path` 对象而非字符串拼接
   - [ ] 捕获具体异常，不用裸 `except`
   - [ ] 复用了现有代码
   - [ ] 避免了 known-pitfalls.md 中的陷阱
   - [ ] 添加了追溯注释 `# FR-xxx, design.md X.X`

2. **更新 tasks.md**:
   ```markdown
   - [x] T001 [P] [US1] 实现 check_tool 函数
   ```

3. **提交代码**:
   ```bash
   git add src/specify_cli/__init__.py
   git commit -m "feat: implement check_tool function

   - Add check_tool function with install_url parameter
   - Follow SKILL.md naming convention (snake_case)
   - Use console.print() for output
   - Add FR-001 traceability comment

   Ref: specs/001-xxx/design.md section 3.2.1"
   ```

---

## 完整示例：实现 check_tool 函数

### 步骤 1: 读取上下文

```bash
# L1: 全局上下文
cat .windsurf/skills/project-context/SKILL.md
cat .specify/wikis/spec-kit-cn/overview.md

# L2: 角色上下文
cat .specify/wikis/spec-kit-cn/memory.md
cat .specify/wikis/spec-kit-cn/cli-core.md

# L3: 任务上下文
cat .specify/memory/coding-standards.md
cat .specify/memory/known-pitfalls.md
cat specs/001-xxx/design.md
```

### 步骤 2: 提取接口定义（来自 design.md）

```markdown
# design.md 章节 3.2.1: check_tool 函数

**函数签名**:
```python
def check_tool(tool: str, install_url: str = None) -> bool:
    """检查工具是否已安装
    
    Args:
        tool: 工具名称（CLI 命令）
        install_url: 安装 URL（可选）
    
    Returns:
        bool: 工具是否已安装
    """
```

**行为**:
1. 使用 shutil.which() 检查工具是否在 PATH 中
2. 如果未安装且提供了 install_url，显示安装提示
3. 返回布尔值
```

### 步骤 3: 检查编码规范（来自 SKILL.md）

```markdown
# SKILL.md 编码规范:
- 函数名: snake_case ✅
- 类型提示: 必须 ✅
- 输出: console.print() ✅
- 错误处理: try/except ✅
```

### 步骤 4: 检查已知陷阱（来自 known-pitfalls.md）

```markdown
# known-pitfalls.md:
- 陷阱 3: 使用 print() 而非 console.print() ✅ 已注意
- 陷阱 7: 未处理 shutil.which() 返回 None 的情况 ✅ 已注意
```

### 步骤 5: 搜索可复用代码

```bash
grep -r "def check_tool" src/
# 结果: 未找到现有实现，需要新建
```

### 步骤 6: 实现代码

```python
import shutil
from rich.console import Console

console = Console()

def check_tool(tool: str, install_url: str = None) -> bool:
    """检查工具是否已安装
    
    Args:
        tool: 工具名称（CLI 命令）
        install_url: 安装 URL（可选）
    
    Returns:
        bool: 工具是否已安装
    
    Traceability:
        FR-001, design.md 3.2.1
    """
    # 检查工具是否在 PATH 中
    tool_path = shutil.which(tool)
    
    if tool_path is None:
        # 工具未安装
        if install_url:
            console.print(f"[yellow]Warning:[/yellow] {tool} not found")
            console.print(f"Install from: {install_url}")
        return False
    
    # 工具已安装
    return True
```

### 步骤 7: 自检

- [x] 函数签名与 design.md 一致 ✅
- [x] 命名符合 snake_case ✅
- [x] 使用 console.print() ✅
- [x] 类型提示完整 ✅
- [x] 添加了追溯注释 ✅
- [x] 避免了已知陷阱 ✅

### 步骤 8: 更新 tasks.md

```markdown
- [x] T001 [P] [US1] 实现 check_tool 函数
```

### 步骤 9: 提交代码

```bash
git add src/specify_cli/__init__.py
git commit -m "feat: implement check_tool function

- Add check_tool function with install_url parameter
- Follow SKILL.md naming convention (snake_case)
- Use console.print() for output
- Add FR-001 traceability comment

Ref: specs/001-xxx/design.md section 3.2.1"
```

---

## 总结

通过三层上下文加载和五大优先级指导，确保：

1. **接口一致**: 与 design.md 100% 一致
2. **规范统一**: 符合 SKILL.md 编码规范
3. **架构对齐**: 符合 Wiki 架构模式
4. **代码复用**: 优先复用现有代码
5. **避免踩坑**: 参考 known-pitfalls.md

**这就是高质量代码的保障！** 🚀
