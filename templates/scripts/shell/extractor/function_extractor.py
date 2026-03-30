# -*- coding: utf-8 -*-
"""
Shell 函数提取器

提取 Shell 脚本中的函数定义，包括：
- 函数名
- 函数体
- 参数使用
- 局部变量
- 调用的外部命令
- 函数注释
"""
import re
from typing import List, Optional, Dict, Tuple
from .base import BaseShellExtractor, ShellFunction


class ShellFunctionExtractor(BaseShellExtractor):
    """Shell 函数提取器"""

    # 函数定义模式
    # 支持: func_name() { 或 func_name () { 或 function func_name {
    FUNC_PATTERN = re.compile(r'^(\w+)\s*\(\s*\)\s*\{?\s*$')
    FUNC_PATTERN_ALT = re.compile(r'^function\s+(\w+)\s*\(?\s*\)?\s*\{?\s*$')

    # 参数使用模式
    PARAM_PATTERN = re.compile(r'\$([0-9]+|\@|\*|\#)')

    # 局部变量模式
    LOCAL_PATTERN = re.compile(r'^\s*local\s+(\w+)')

    # 常见外部命令
    COMMON_COMMANDS = {
        'echo', 'printf', 'cat', 'grep', 'awk', 'sed', 'cut', 'sort', 'uniq',
        'find', 'ls', 'cd', 'pwd', 'mkdir', 'rm', 'cp', 'mv', 'chmod', 'chown',
        'tar', 'gzip', 'gunzip', 'zip', 'unzip',
        'systemctl', 'service', 'ps', 'kill', 'pkill',
        'curl', 'wget', 'ssh', 'scp',
        'date', 'sleep', 'exit', 'return', 'read',
        'test', '[', '[[',
        'if', 'then', 'else', 'elif', 'fi',
        'for', 'while', 'do', 'done', 'case', 'esac',
    }

    @property
    def name(self) -> str:
        return "ShellFunctionExtractor"

    def extract(self, file_path: str, content: str) -> List[ShellFunction]:
        """从单个文件提取函数"""
        functions = []
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]

            # 检查是否是函数定义
            func_name = self._match_function_start(line)
            if func_name:
                # 获取函数注释（前一行或前几行的注释）
                docstring = self._get_function_docstring(lines, i)

                # 找到函数结束位置
                start_line = i + 1
                end_line, func_body = self._find_function_end(lines, i)

                # 分析函数体
                params_used = self._extract_params(func_body)
                local_vars = self._extract_local_vars(func_body)
                calls = self._extract_calls(func_body)

                func = ShellFunction(
                    name=func_name,
                    file_path=file_path,
                    line=start_line,
                    end_line=end_line + 1,
                    params_used=params_used,
                    local_vars=local_vars,
                    calls=calls,
                    docstring=docstring,
                    raw_code=func_body,
                )
                functions.append(func)

                i = end_line + 1
            else:
                i += 1

        return functions

    def extract_all(self, source_dir: str) -> List[ShellFunction]:
        """从目录提取所有函数"""
        all_functions = []

        for file_path in self._find_shell_files(source_dir):
            content = self._read_file(file_path)
            if content:
                functions = self.extract(file_path, content)
                all_functions.extend(functions)

        return all_functions

    def _match_function_start(self, line: str) -> Optional[str]:
        """匹配函数定义开始"""
        line = line.strip()

        # 跳过注释
        if line.startswith('#'):
            return None

        # 尝试匹配 func_name() 格式
        match = self.FUNC_PATTERN.match(line)
        if match:
            return match.group(1)

        # 尝试匹配 function func_name 格式
        match = self.FUNC_PATTERN_ALT.match(line)
        if match:
            return match.group(1)

        return None

    def _get_function_docstring(self, lines: List[str], func_line: int) -> str:
        """获取函数注释（函数定义前的连续注释行）"""
        comments = []
        i = func_line - 1

        while i >= 0:
            line = lines[i].strip()
            if line.startswith('#'):
                # 去掉 # 和前导空格
                comment = line.lstrip('#').strip()
                if comment:
                    comments.insert(0, comment)
                i -= 1
            elif line == '':
                # 空行，继续向上查找
                i -= 1
            else:
                # 遇到非注释非空行，停止
                break

        return '\n'.join(comments)

    def _find_function_end(self, lines: List[str], start: int) -> Tuple[int, str]:
        """找到函数结束位置，返回 (结束行号, 函数体)"""
        brace_count = 0
        func_lines = []
        in_function = False

        for i in range(start, len(lines)):
            line = lines[i]
            func_lines.append(line)

            # 统计大括号（简化处理，不考虑字符串内的括号）
            # 去掉注释部分
            code_part = line.split('#')[0] if '#' in line else line

            brace_count += code_part.count('{')
            brace_count -= code_part.count('}')

            if '{' in code_part:
                in_function = True

            # 函数结束
            if in_function and brace_count <= 0:
                return i, '\n'.join(func_lines)

        # 如果没找到结束，返回到文件末尾
        return len(lines) - 1, '\n'.join(func_lines)

    def _extract_params(self, func_body: str) -> List[str]:
        """提取函数中使用的参数"""
        params = set()
        for match in self.PARAM_PATTERN.finditer(func_body):
            param = match.group(0)
            params.add(param)
        return sorted(list(params))

    def _extract_local_vars(self, func_body: str) -> List[str]:
        """提取局部变量"""
        local_vars = []
        for line in func_body.split('\n'):
            match = self.LOCAL_PATTERN.match(line)
            if match:
                local_vars.append(match.group(1))
        return local_vars

    def _extract_calls(self, func_body: str) -> List[str]:
        """提取调用的外部命令"""
        calls = set()

        # 简单的命令提取：每行开头的命令或管道后的命令
        for line in func_body.split('\n'):
            line = line.strip()

            # 跳过注释
            if line.startswith('#'):
                continue

            # 提取命令
            # 处理管道
            parts = re.split(r'\s*\|\s*', line)
            for part in parts:
                # 获取第一个词作为命令
                words = part.split()
                if words:
                    cmd = words[0].strip('$()')
                    # 过滤掉变量赋值
                    if '=' not in cmd and cmd not in ['', '{', '}', 'then', 'do', 'else', 'fi', 'done', 'esac']:
                        # 只保留常见命令
                        if cmd in self.COMMON_COMMANDS or cmd.startswith('./') or cmd.startswith('/'):
                            calls.add(cmd)

        return sorted(list(calls))
