# -*- coding: utf-8 -*-
"""
Shell 变量提取器

提取 Shell 脚本中的变量定义，包括：
- 全局变量/常量
- 环境变量（export）
- 只读变量（readonly）
- 变量注释
"""
import re
from typing import List, Optional
from .base import BaseShellExtractor, ShellVariable, VariableCategory


class ShellVariableExtractor(BaseShellExtractor):
    """Shell 变量提取器"""

    # 变量赋值模式（排除函数内的局部变量）
    # 匹配: VAR=value 或 VAR="value" 或 VAR='value' 或 VAR=$(...)
    VAR_PATTERN = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$')

    # export 变量
    EXPORT_PATTERN = re.compile(r'^export\s+([A-Za-z_][A-Za-z0-9_]*)\s*=?\s*(.*)$')

    # readonly 变量
    READONLY_PATTERN = re.compile(r'^readonly\s+([A-Za-z_][A-Za-z0-9_]*)\s*=?\s*(.*)$')

    # 路径相关关键词
    PATH_KEYWORDS = {'PATH', 'DIR', 'FILE', 'ROOT', 'HOME', 'LOG', 'CONFIG', 'CONF'}

    @property
    def name(self) -> str:
        return "ShellVariableExtractor"

    def extract(self, file_path: str, content: str) -> List[ShellVariable]:
        """从单个文件提取变量"""
        variables = []
        lines = content.split('\n')

        # 跟踪是否在函数内部
        in_function = False
        brace_count = 0

        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()

            # 跳过注释行
            if line.startswith('#'):
                continue

            # 跟踪函数边界
            code_part = line.split('#')[0] if '#' in line else line

            # 检测函数开始
            if re.match(r'^(\w+)\s*\(\s*\)\s*\{?\s*$', line) or \
               re.match(r'^function\s+\w+', line):
                in_function = True

            brace_count += code_part.count('{')
            brace_count -= code_part.count('}')

            if in_function and brace_count <= 0:
                in_function = False

            # 只提取全局变量（不在函数内部）
            if in_function:
                continue

            # 获取前一行的注释
            comment = self._get_preceding_comment(lines, i)

            # 尝试匹配 export
            match = self.EXPORT_PATTERN.match(line)
            if match:
                var = self._create_variable(
                    name=match.group(1),
                    value=match.group(2),
                    file_path=file_path,
                    line=i + 1,
                    is_export=True,
                    comment=comment,
                )
                if var:
                    variables.append(var)
                continue

            # 尝试匹配 readonly
            match = self.READONLY_PATTERN.match(line)
            if match:
                var = self._create_variable(
                    name=match.group(1),
                    value=match.group(2),
                    file_path=file_path,
                    line=i + 1,
                    is_readonly=True,
                    comment=comment,
                )
                if var:
                    variables.append(var)
                continue

            # 尝试匹配普通变量赋值
            match = self.VAR_PATTERN.match(line)
            if match:
                var = self._create_variable(
                    name=match.group(1),
                    value=match.group(2),
                    file_path=file_path,
                    line=i + 1,
                    comment=comment,
                )
                if var:
                    variables.append(var)

        return variables

    def extract_all(self, source_dir: str) -> List[ShellVariable]:
        """从目录提取所有变量"""
        all_variables = []

        for file_path in self._find_shell_files(source_dir):
            content = self._read_file(file_path)
            if content:
                variables = self.extract(file_path, content)
                all_variables.extend(variables)

        return all_variables

    def _create_variable(
        self,
        name: str,
        value: str,
        file_path: str,
        line: int,
        is_export: bool = False,
        is_readonly: bool = False,
        comment: str = "",
    ) -> Optional[ShellVariable]:
        """创建变量对象"""
        # 过滤掉一些不需要的变量
        if name in ('_', 'OPTIND', 'OPTARG', 'REPLY'):
            return None

        # 清理值
        value = value.strip()

        # 判断分类
        category = self._categorize_variable(name, value, is_export)

        return ShellVariable(
            name=name,
            value=value,
            file_path=file_path,
            line=line,
            category=category,
            is_export=is_export,
            is_readonly=is_readonly,
            comment=comment,
        )

    def _categorize_variable(self, name: str, value: str, is_export: bool) -> str:
        """对变量进行分类"""
        # 环境变量
        if is_export:
            return VariableCategory.ENV.value

        # 常量（全大写）
        if name.isupper():
            # 检查是否是路径
            for keyword in self.PATH_KEYWORDS:
                if keyword in name:
                    return VariableCategory.PATH.value
            return VariableCategory.CONSTANT.value

        # 路径变量
        if any(keyword.lower() in name.lower() for keyword in self.PATH_KEYWORDS):
            return VariableCategory.PATH.value

        # 配置变量
        if 'config' in name.lower() or 'conf' in name.lower():
            return VariableCategory.CONFIG.value

        return VariableCategory.OTHER.value

    def _get_preceding_comment(self, lines: List[str], current_line: int) -> str:
        """获取变量前一行的注释"""
        if current_line > 0:
            prev_line = lines[current_line - 1].strip()
            if prev_line.startswith('#'):
                return prev_line.lstrip('#').strip()
        return ""
