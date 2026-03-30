# -*- coding: utf-8 -*-
"""
Shell Skill 生成器 - 动态生成项目上下文
"""
import os
import re
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor.fusion import ShellKnowledgeBase
from extractor.base import ShellFunction, ShellVariable, ShellPattern


class ShellProjectPatterns:
    """Shell 项目模式分析器"""

    def __init__(self, kb: ShellKnowledgeBase):
        self.kb = kb
        self._analyze()

    def _analyze(self):
        self.function_naming = self._analyze_function_naming()
        self.variable_naming = self._analyze_variable_naming()
        self.logging_functions = self._analyze_logging_functions()
        self.error_handling = self._analyze_error_handling()
        self.header_pattern = self._analyze_header_pattern()
        self.directory_structure = self._analyze_directory_structure()
        self.core_files = self._analyze_core_files()
        self.tech_stack = self._analyze_tech_stack()
        self.dev_principles = self._analyze_dev_principles()

    def _analyze_function_naming(self) -> Dict:
        patterns = {'camel_case': 0, 'snake_case': 0, 'examples': []}
        for func in self.kb.functions:
            name = func.name
            if name and name[0].isupper() and '_' not in name:
                patterns['camel_case'] += 1
            elif '_' in name and name.islower():
                patterns['snake_case'] += 1
            if len(patterns['examples']) < 5:
                patterns['examples'].append(name)
        if patterns['camel_case'] > patterns['snake_case']:
            patterns['primary_style'] = 'CamelCase'
        else:
            patterns['primary_style'] = 'snake_case'
        return patterns

    def _analyze_variable_naming(self) -> Dict:
        patterns = {'constant_examples': [], 'path_examples': []}
        for var in self.kb.variables:
            if var.category == 'constant' and len(patterns['constant_examples']) < 3:
                patterns['constant_examples'].append(var.name)
            if var.category == 'path' and len(patterns['path_examples']) < 3:
                patterns['path_examples'].append(var.name)
        return patterns

    def _analyze_logging_functions(self) -> Dict:
        log_funcs = []
        # 典型的日志函数命名模式
        log_patterns = ['_log', 'log_', 'message_', '_message']
        for func in self.kb.functions:
            name_lower = func.name.lower()
            # 检查是否匹配日志函数命名模式
            is_log_func = any(p in name_lower for p in log_patterns)
            is_log_func = is_log_func or name_lower.endswith('_log') or name_lower.endswith('log')
            # 排除名称过长或不像日志函数的
            if is_log_func and len(func.name) < 20:
                log_funcs.append({'name': func.name, 'file': func.file_path})
        # 如果没找到，使用默认值
        if not log_funcs:
            log_funcs = [{'name': 'log_info', 'file': ''}, {'name': 'log_error', 'file': ''}, {'name': 'log_warn', 'file': ''}]
        return {'functions': log_funcs[:5]}

    def _analyze_error_handling(self) -> Dict:
        patterns = {'set_e_used': False, 'exit_check_used': False}
        for pattern in self.kb.patterns:
            if pattern.pattern_type == 'error_handling':
                if pattern.pattern_name == 'set_e' and pattern.count > 0:
                    patterns['set_e_used'] = True
                elif pattern.pattern_name == 'exit_check' and pattern.count > 0:
                    patterns['exit_check_used'] = True
        return patterns

    def _analyze_header_pattern(self) -> Dict:
        common_sources = []
        for source in self.kb.sources[:5]:
            common_sources.append(source.target_file)
        return {'common_sources': list(set(common_sources))[:3]}

    def _analyze_directory_structure(self) -> Dict:
        """分析目录结构"""
        dirs = set()
        for func in self.kb.functions:
            rel_path = os.path.relpath(func.file_path, self.kb.project_path)
            parts = rel_path.split(os.sep)
            if len(parts) > 1:
                dirs.add(parts[0])
        return {'top_dirs': sorted(list(dirs))[:10]}

    def _analyze_core_files(self) -> List[Dict]:
        """分析核心文件"""
        file_func_count = defaultdict(int)
        for func in self.kb.functions:
            file_func_count[func.file_path] += 1

        sorted_files = sorted(file_func_count.items(), key=lambda x: -x[1])[:5]
        core_files = []
        for file_path, count in sorted_files:
            rel_path = os.path.relpath(file_path, self.kb.project_path)
            core_files.append({'path': rel_path})
        return core_files

    def _analyze_dev_principles(self) -> List[str]:
        """从代码模式中提取检测到的模式类型"""
        detected_patterns = []
        pattern_types = set()

        for p in self.kb.patterns:
            if p.count > 0:
                pattern_types.add(p.pattern_type)

        # 映射模式类型到可读名称
        type_names = {
            'file_operation': '文件操作（备份、复制、删除）',
            'service_management': '服务管理（启停、状态检查）',
            'error_handling': '错误处理（set -e、返回值检查）',
            'logging': '日志记录',
            'config_read': '配置读取',
        }

        for pt in sorted(pattern_types):
            name = type_names.get(pt, pt)
            detected_patterns.append(name)

        return detected_patterns

    def _analyze_tech_stack(self) -> Dict:
        """分析技术栈"""
        tech = {
            'script_type': 'Bash Shell',
            'build_tools': [],
            'service_mgmt': [],
            'log_framework': [],
        }

        # 检测构建工具
        if os.path.exists(os.path.join(self.kb.project_path, 'CMakeLists.txt')):
            tech['build_tools'].append('CMake')
        if os.path.exists(os.path.join(self.kb.project_path, 'Makefile')):
            tech['build_tools'].append('Make')
        jenkinsfile_paths = ['Jenkinsfile', 'ci/Jenkinsfile', '.jenkins/Jenkinsfile']
        for jf in jenkinsfile_paths:
            if os.path.exists(os.path.join(self.kb.project_path, jf)):
                tech['build_tools'].append('Jenkins')
                break

        # 检测服务管理
        for func in self.kb.functions:
            if func.raw_code:
                if 'systemctl' in func.raw_code:
                    if 'systemctl' not in tech['service_mgmt']:
                        tech['service_mgmt'].append('systemctl')
                if 'service ' in func.raw_code:
                    if 'service' not in tech['service_mgmt']:
                        tech['service_mgmt'].append('service')

        # 检测日志框架
        log_funcs = self.logging_functions.get('functions', [])
        if log_funcs:
            tech['log_framework'] = [f['name'] for f in log_funcs[:3]]

        return tech


class ShellSkillGenerator:
    """Shell Skill 生成器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.patterns: Optional[ShellProjectPatterns] = None

    def generate_all(self, kb: ShellKnowledgeBase, output_dir: str) -> Dict[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        self.patterns = ShellProjectPatterns(kb)
        self.kb = kb
        generated_files = {}

        skill_path = os.path.join(output_dir, 'SKILL.md')
        self._generate_main_skill(skill_path)
        generated_files['SKILL.md'] = skill_path

        func_path = os.path.join(output_dir, 'shell-functions.md')
        self._generate_functions_skill(func_path)
        generated_files['shell-functions.md'] = func_path

        var_path = os.path.join(output_dir, 'shell-variables.md')
        self._generate_variables_skill(var_path)
        generated_files['shell-variables.md'] = var_path

        error_path = os.path.join(output_dir, 'shell-error.md')
        self._generate_error_skill(error_path)
        generated_files['shell-error.md'] = error_path

        log_path = os.path.join(output_dir, 'shell-logging.md')
        self._generate_logging_skill(log_path)
        generated_files['shell-logging.md'] = log_path

        index_path = os.path.join(output_dir, 'index.yaml')
        self._generate_index(index_path)
        generated_files['index.yaml'] = index_path

        return generated_files

    def _format_principles(self) -> str:
        """格式化开发原则为 Markdown"""
        lines = []
        lines.append("{{LLM_DEV_PRINCIPLES}}")
        lines.append('<!-- 填充指导: 根据项目代码分析推断开发原则。格式: ### 编号. 原则名称 + 原则描述（使用"必须"/"禁止"等明确词汇） -->')
        return chr(10).join(lines)

    def _generate_main_skill(self, output_path: str):
        """生成主 Skill 文件 - 项目上下文"""
        func_style = self.patterns.function_naming['primary_style']
        func_examples = self.patterns.function_naming['examples'][:10]
        # 根据风格选择合适的示例
        if func_style == 'CamelCase':
            style_examples = [e for e in func_examples if e and e[0].isupper() and '_' not in e]
            func_example = style_examples[0] if style_examples else 'MyFunction'
        else:
            style_examples = [e for e in func_examples if '_' in e and e.islower()]
            func_example = style_examples[0] if style_examples else 'my_function'

        var_naming = self.patterns.variable_naming
        const_examples = var_naming.get('constant_examples', ['MY_CONSTANT', 'APP_PATH'])
        path_examples = var_naming.get('path_examples', ['MY_PATH'])

        log_funcs = self.patterns.logging_functions.get('functions', [])
        log_func_names = [f['name'] for f in log_funcs[:3]] if log_funcs else ['log_info', 'log_error']

        tech = self.patterns.tech_stack
        common_sources = self.patterns.header_pattern.get('common_sources', [])
        source_example = common_sources[0] if common_sources else 'func.sh'

        top_dirs = self.patterns.directory_structure.get('top_dirs', [])
        core_files = self.patterns.core_files

        # 构建技术栈部分
        tech_lines = [f'- **脚本类型**: {tech["script_type"]} (`#!/bin/bash`)']
        if tech['build_tools']:
            tech_lines.append(f'- **构建工具**: {", ".join(tech["build_tools"])}')
        if tech['service_mgmt']:
            tech_lines.append(f'- **服务管理**: {", ".join(tech["service_mgmt"])}')
        if tech['log_framework']:
            tech_lines.append(f'- **日志框架**: 自定义日志函数 (`{", ".join(tech["log_framework"])}`)')

        # 构建目录结构部分
        dir_lines = []
        for d in top_dirs[:6]:
            dir_lines.append(f'├── {d}/')

        # 构建核心文件部分
        core_file_lines = []
        for cf in core_files[:5]:
            core_file_lines.append(f'| `{cf["path"]}` | {{{{LLM_FILE_DESC:{cf["path"]}}}}} <!-- 填充指导: 简述文件用途，10-20字 --> |')

        content = f'''---
name: shell-scripting
description: "{{{{LLM_PROJECT_DESCRIPTION}}}}"
<!-- 填充指导: 一句话描述项目用途，20-50字 -->
---

# {{{{LLM_PROJECT_NAME}}}} 项目上下文
<!-- 填充指导: 项目名称，简洁明了 -->

## 项目概述

{{{{LLM_PROJECT_OVERVIEW}}}}
<!-- 填充指导: 2-3句话概述项目功能和特点 -->

## 业务场景

{{{{LLM_BUSINESS_CONTEXT}}}}
<!-- 填充指导: 说明适用场景和典型使用流程 -->

---

<!-- 以下内容由脚本自动分析生成 -->

## 技术栈

{chr(10).join(tech_lines)}

## 开发原则

{self._format_principles()}

## 目录结构

```
{self.kb.project_name}/
{chr(10).join(dir_lines)}
```

## 核心文件

| 文件 | 说明 |
|------|------|
{chr(10).join(core_file_lines) if core_file_lines else '| - | - |'}

## 开发规范

| 规范 | 要求 | 详细文档 |
|------|------|----------|
| **函数命名** | {func_style} 风格，如 `{func_example}` | [shell-functions.md](shell-functions.md) |
| **变量命名** | 常量全大写，路径含 PATH/DIR，局部用 `local` | [shell-variables.md](shell-variables.md) |
| **日志规范** | **禁止** `echo`，**必须**用 `{log_func_names[0]}` | [shell-logging.md](shell-logging.md) |
| **错误处理** | **必须**用 `set -e`，检查返回值 | [shell-error.md](shell-error.md) |

## 禁止事项

| 禁止 | 应该 |
|------|------|
| `echo "日志"` | `{log_func_names[0]} "日志"` |
| `result=""` (函数内) | `local result=""` |
| 忽略命令返回值 | `set -e` 或检查 `$?` |
'''
        self._write_file(output_path, content)

    def _generate_functions_skill(self, output_path: str):
        """生成函数规范 Skill"""
        func_style = self.patterns.function_naming['primary_style']
        func_examples = self.patterns.function_naming['examples'][:5]

        # 选择符合风格的示例
        if func_style == 'CamelCase':
            style_examples = [e for e in func_examples if e and e[0].isupper() and '_' not in e]
        else:
            style_examples = [e for e in func_examples if '_' in e]
        display_examples = style_examples[:3] if style_examples else func_examples[:3]

        content = f'''---
name: shell-functions
description: Shell 函数定义规范。定义或修改函数时使用。
---

# Shell 函数规范

## 1. 函数命名

**必须**使用 **{func_style}** 风格：

示例: {", ".join([f"`{e}`" for e in display_examples]) if display_examples else "`StopService`, `CheckStatus`"}

## 2. 函数定义格式

```bash
# 函数说明：描述函数功能
# 参数：$1 - 参数说明
# 返回：0 成功，1 失败
FunctionName()
{{
    local param1="$1"
    return 0
}}
```

## 3. 参数使用

| 参数 | 说明 |
|------|------|
| `$1`, `$2` | 位置参数 |
| `$@` | 所有参数（独立字符串） |
| `$#` | 参数个数 |

## 4. 局部变量

```bash
# ✅ 正确
MyFunction()
{{
    local result=""
}}

# ❌ 错误 - 污染全局命名空间
MyFunction()
{{
    result=""  # 这会成为全局变量！
}}
```

## 检查清单

- [ ] 函数名使用 {func_style} 风格
- [ ] 函数前有注释说明
- [ ] 局部变量使用 `local` 声明
'''
        self._write_file(output_path, content)

    def _generate_variables_skill(self, output_path: str):
        """生成变量规范 Skill"""
        var_naming = self.patterns.variable_naming
        const_examples = var_naming.get('constant_examples', ['LOG_INFO', 'APP_PATH'])
        path_examples = var_naming.get('path_examples', ['INSTALL_PATH', 'LOG_DIR'])

        content = f'''---
name: shell-variables
description: Shell 变量命名规范。定义变量或常量时使用。
---

# Shell 变量规范

## 1. 常量命名

常量**必须**使用全大写 + 下划线：

```bash
# ✅ 正确
{const_examples[0] if const_examples else 'LOG_INFO'}="INFO"
MAX_RETRY_COUNT=3

# ❌ 错误
logInfo="INFO"
```

**项目中的常量示例**: {", ".join([f"`{c}`" for c in const_examples[:3]]) if const_examples else "`LOG_INFO`, `APP_PATH`"}

## 2. 路径变量

路径变量**必须**包含 PATH/DIR/FILE 关键词：

```bash
# ✅ 正确
{path_examples[0] if path_examples else 'INSTALL_PATH'}="/opt/app"
LOG_DIR="/var/log/app"

# ❌ 错误
INSTALL="/opt/app"
```

**项目中的路径变量示例**: {", ".join([f"`{p}`" for p in path_examples[:3]]) if path_examples else "`INSTALL_PATH`, `LOG_DIR`"}

## 3. 环境变量

跨脚本使用的变量**必须**使用 `export`：

```bash
export APP_HOME="/opt/app"
```

## 4. 变量引用

变量引用**必须**使用双引号：

```bash
# ✅ 正确
echo "$VAR_NAME"

# ❌ 错误
echo $VAR_NAME
```

## 检查清单

- [ ] 常量使用全大写 + 下划线
- [ ] 路径变量包含 PATH/DIR/FILE
- [ ] 变量引用使用双引号
'''
        self._write_file(output_path, content)

    def _generate_error_skill(self, output_path: str):
        """生成错误处理规范 Skill"""
        error_patterns = self.patterns.error_handling
        set_e_note = "（项目中已使用）" if error_patterns.get('set_e_used') else ""

        content = f'''---
name: shell-error-handling
description: Shell 错误处理规范。处理错误或添加错误检测时使用。
---

# Shell 错误处理规范

## 1. 启用错误检测

脚本开头**必须**使用 `set -e`{set_e_note}：

```bash
#!/bin/bash
set -e
set -o pipefail
```

## 2. 返回值检查

关键命令**必须**检查返回值：

```bash
# ✅ 正确
if [ $? -ne 0 ]; then
    echo "命令执行失败"
    exit 1
fi

# ❌ 错误
command_that_may_fail
```

## 3. 条件执行

```bash
command && echo "成功" || echo "失败"
command || exit 1
```

## 4. trap 信号处理

```bash
cleanup() {{
    rm -f "$TEMP_FILE"
}}

trap cleanup EXIT
trap 'echo "脚本被中断"; exit 1' INT TERM
```

## 检查清单

- [ ] 脚本开头使用 `set -e`
- [ ] 关键命令检查返回值
- [ ] 长时间脚本使用 `trap`
'''
        self._write_file(output_path, content)

    def _generate_logging_skill(self, output_path: str):
        """生成日志规范 Skill"""
        log_funcs = self.patterns.logging_functions.get('functions', [])
        log_func_names = [f['name'] for f in log_funcs[:3]] if log_funcs else ['Message_log', 'Error_log', 'Warning_log']

        # 构建日志函数表格
        func_table_lines = []
        for func in log_funcs[:5]:
            rel_path = os.path.relpath(func['file'], self.kb.project_path) if func.get('file') else ''
            func_table_lines.append(f"| `{func['name']}` | `{rel_path}` |")

        content = f'''---
name: shell-logging
description: Shell 日志规范。添加日志输出或调试脚本时使用。
---

# Shell 日志规范

## 1. 禁止直接使用 echo

**禁止**直接使用 `echo`，**必须**使用项目日志函数：

```bash
# ❌ 错误
echo "开始处理..."

# ✅ 正确
{log_func_names[0]} "开始处理..."
```

## 2. 项目日志函数

| 函数名 | 来源文件 |
|--------|----------|
{chr(10).join(func_table_lines) if func_table_lines else '| `Message_log` | `func.sh` |'}

## 3. 日志级别

| 级别 | 函数 | 用途 |
|------|------|------|
| INFO | `{log_func_names[0]}` | 普通信息 |
| ERROR | `{log_func_names[1] if len(log_func_names) > 1 else "Error_log"}` | 错误信息 |
| WARN | `{log_func_names[2] if len(log_func_names) > 2 else "Warning_log"}` | 警告信息 |

## 使用示例

```bash
{log_func_names[0]} "开始停止服务..."
if systemctl stop myservice; then
    {log_func_names[0]} "服务停止成功"
else
    {log_func_names[1] if len(log_func_names) > 1 else "Error_log"} "服务停止失败"
    exit 1
fi
```

## 检查清单

- [ ] 不直接使用 `echo` 输出日志
- [ ] 使用项目日志函数
- [ ] 关键操作有日志记录
'''
        self._write_file(output_path, content)

    def _generate_index(self, output_path: str):
        """生成索引文件"""
        content = f'''# Shell Skill 索引
version: "1.0"
project: "{self.kb.project_name}"
language: "shell"
generated_at: "{datetime.now().isoformat()}"

skills:
  - name: shell-scripting
    path: SKILL.md
    description: "Shell 脚本项目上下文"

  - name: shell-functions
    path: shell-functions.md
    description: "函数定义规范"

  - name: shell-variables
    path: shell-variables.md
    description: "变量命名规范"

  - name: shell-error-handling
    path: shell-error.md
    description: "错误处理规范"

  - name: shell-logging
    path: shell-logging.md
    description: "日志规范"
'''
        self._write_file(output_path, content)

    def _write_file(self, path: str, content: str):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
