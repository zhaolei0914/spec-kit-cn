# -*- coding: utf-8 -*-
"""
错误码提取器

从项目代码中提取错误码定义，生成完整的错误码文档
"""
import os
import re
import ast
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class ErrorCodeDefinition:
    """错误码定义"""
    code: str                    # 错误码字符串，如 'Upgrade.Job.NotFound'
    variable_name: str           # 变量名，如 Upgrade_Job_NotFound
    description: str = ""        # 描述
    cause: str = ""              # 原因
    solution: str = ""           # 解决方案
    file_path: str = ""          # 定义文件路径
    line: int = 0                # 行号
    module: str = ""             # 所属模块

    def to_dict(self) -> Dict:
        return {
            "code": self.code,
            "variable_name": self.variable_name,
            "description": self.description,
            "cause": self.cause,
            "solution": self.solution,
            "file_path": self.file_path,
            "line": self.line,
            "module": self.module,
        }


@dataclass
class ExceptionClassDefinition:
    """异常类定义"""
    name: str                    # 类名
    base_class: str              # 基类
    docstring: str = ""          # 文档字符串
    file_path: str = ""          # 定义文件路径
    line: int = 0                # 行号

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "base_class": self.base_class,
            "docstring": self.docstring,
            "file_path": self.file_path,
            "line": self.line,
        }


class ErrorCodeExtractor:
    """错误码提取器"""

    # 错误码文件名模式
    ERRORCODE_FILE_PATTERNS = [
        r'.*_errorcode\.py$',
        r'.*errorcode.*\.py$',
        r'.*error_code.*\.py$',
        r'errors\.py$',
    ]

    # 异常定义文件名模式
    EXCEPTION_FILE_PATTERNS = [
        r'defines\.py$',
        r'exceptions\.py$',
        r'exception\.py$',
    ]

    def __init__(self):
        self.error_codes: List[ErrorCodeDefinition] = []
        self.exception_classes: List[ExceptionClassDefinition] = []
        self.errorcode_files: List[str] = []

    def extract(self, source_dir: str) -> Tuple[List[ErrorCodeDefinition], List[ExceptionClassDefinition]]:
        """
        从源码目录提取错误码和异常类定义

        参数:
            source_dir: 源码目录

        返回: (错误码列表, 异常类列表)
        """
        self.error_codes = []
        self.exception_classes = []
        self.errorcode_files = []

        # 1. 查找错误码文件
        self._find_errorcode_files(source_dir)

        # 2. 提取错误码定义
        for file_path in self.errorcode_files:
            self._extract_from_file(file_path)

        # 3. 查找异常定义文件
        exception_files = self._find_exception_files(source_dir)

        # 4. 提取异常类定义
        for file_path in exception_files:
            self._extract_exception_classes(file_path)

        return self.error_codes, self.exception_classes

    def _find_errorcode_files(self, source_dir: str) -> List[str]:
        """查找错误码定义文件"""
        for root, dirs, files in os.walk(source_dir):
            # 跳过不需要的目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'Thrift', 'migrations')]

            for file in files:
                if file.endswith('.py'):
                    for pattern in self.ERRORCODE_FILE_PATTERNS:
                        if re.match(pattern, file):
                            self.errorcode_files.append(os.path.join(root, file))
                            break

        return self.errorcode_files

    def _find_exception_files(self, source_dir: str) -> List[str]:
        """查找异常定义文件"""
        exception_files = []

        for root, dirs, files in os.walk(source_dir):
            # 跳过不需要的目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'Thrift', 'migrations')]

            # 只在 exception 或 Common/exception 目录下查找
            if 'exception' in root.lower():
                for file in files:
                    if file.endswith('.py'):
                        for pattern in self.EXCEPTION_FILE_PATTERNS:
                            if re.match(pattern, file):
                                exception_files.append(os.path.join(root, file))
                                break

        return exception_files

    def _extract_from_file(self, file_path: str):
        """从单个文件提取错误码"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return

        # 提取模块名（从文件名推断）
        filename = os.path.basename(file_path)
        module = filename.replace('_errorcode.py', '').replace('errorcode.py', '').replace('.py', '')
        module = module.title().replace('_', '')

        # 方法1: 使用正则表达式匹配带注释的错误码定义
        # 匹配格式:
        # '''
        #     {
        #         "errorcode": "Upgrade.Job.NotFound",
        #         "description": "作业不存在。",
        #         ...
        #     }
        # '''
        # Upgrade_Job_NotFound = 'Upgrade.Job.NotFound'

        pattern = r"'''[\s\S]*?\"errorcode\":\s*\"([^\"]+)\"[\s\S]*?\"description\":\s*\"([^\"]+)\"[\s\S]*?(?:\"cause\":\s*\"([^\"]+)\")?[\s\S]*?(?:\"solution\":\s*\"([^\"]+)\")?[\s\S]*?'''\s*\n(\w+)\s*=\s*['\"]([^'\"]+)['\"]"

        for match in re.finditer(pattern, content):
            errorcode = match.group(1)
            description = match.group(2)
            cause = match.group(3) or ""
            solution = match.group(4) or ""
            variable_name = match.group(5)

            # 计算行号
            line = content[:match.start()].count('\n') + 1

            self.error_codes.append(ErrorCodeDefinition(
                code=errorcode,
                variable_name=variable_name,
                description=description,
                cause=cause,
                solution=solution,
                file_path=file_path,
                line=line,
                module=module,
            ))

        # 方法2: 使用 AST 解析简单的赋值语句
        # 匹配格式: Upgrade_Job_NotFound = 'Upgrade.Job.NotFound'
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            # 检查是否是错误码变量（包含 Error 或以大写字母开头且包含下划线）
                            if self._is_errorcode_variable(var_name):
                                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                    code = node.value.value
                                    # 检查是否已经通过正则提取过
                                    if not any(ec.variable_name == var_name for ec in self.error_codes):
                                        self.error_codes.append(ErrorCodeDefinition(
                                            code=code,
                                            variable_name=var_name,
                                            file_path=file_path,
                                            line=node.lineno,
                                            module=module,
                                        ))
        except SyntaxError:
            pass

    def _is_errorcode_variable(self, name: str) -> bool:
        """判断是否是错误码变量名"""
        # 错误码变量通常是大写字母开头，包含下划线，如 Upgrade_Job_NotFound
        if not name[0].isupper():
            return False
        if '_' not in name:
            return False
        # 排除一些常见的非错误码变量
        exclude_patterns = ['APP_', 'SVC_', 'LOG_', 'THRIFT_', 'DEFAULT_']
        for pattern in exclude_patterns:
            if name.startswith(pattern):
                return False
        return True

    def _extract_exception_classes(self, file_path: str):
        """从文件中提取异常类定义"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
        except Exception:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否是异常类
                for base in node.bases:
                    base_name = self._get_base_name(base)
                    if 'Exception' in base_name or 'Error' in base_name:
                        docstring = ast.get_docstring(node) or ""
                        self.exception_classes.append(ExceptionClassDefinition(
                            name=node.name,
                            base_class=base_name,
                            docstring=docstring,
                            file_path=file_path,
                            line=node.lineno,
                        ))
                        break

    def _get_base_name(self, node) -> str:
        """获取基类名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ""

    def get_summary(self) -> Dict:
        """获取提取结果摘要"""
        # 按模块分组错误码
        by_module = {}
        for ec in self.error_codes:
            module = ec.module or 'other'
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(ec.to_dict())

        # 按基类分组异常类
        by_base = {}
        for exc in self.exception_classes:
            base = exc.base_class
            if base not in by_base:
                by_base[base] = []
            by_base[base].append(exc.to_dict())

        return {
            "total_error_codes": len(self.error_codes),
            "total_exception_classes": len(self.exception_classes),
            "errorcode_files": self.errorcode_files,
            "error_codes_by_module": by_module,
            "exception_classes_by_base": by_base,
        }


def extract_error_codes(source_dir: str) -> Tuple[List[ErrorCodeDefinition], List[ExceptionClassDefinition]]:
    """提取错误码的便捷函数"""
    extractor = ErrorCodeExtractor()
    return extractor.extract(source_dir)
