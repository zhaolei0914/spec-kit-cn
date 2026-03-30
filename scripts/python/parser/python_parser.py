# -*- coding: utf-8 -*-
"""
智能规范提取系统 - Python 代码解析器

使用 AST 解析 Python 代码，提取类、函数等代码单元
"""
import ast
import os
from typing import List, Optional
from .base import BaseParser, CodeUnit


class PythonParser(BaseParser):
    """Python 代码解析器"""

    def get_language(self) -> str:
        return "python"

    def get_file_extensions(self) -> List[str]:
        return ['.py']

    def parse_file(self, file_path: str) -> List[CodeUnit]:
        """解析单个 Python 文件"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            print(f"Warning: Syntax error in {file_path}: {e}")
            return []

        units = []

        # 解析顶层类和函数
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_unit = self._parse_class(node, file_path, source)
                units.append(class_unit)

                # 解析类中的方法
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                        method_unit = self._parse_function(item, file_path, source, parent=node.name)
                        units.append(method_unit)

            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                units.append(self._parse_function(node, file_path, source))

        return units

    def _parse_class(self, node: ast.ClassDef, file_path: str, source: str) -> CodeUnit:
        """解析类定义"""
        return CodeUnit(
            type='class',
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            parent='',
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            bases=[self._get_base_name(b) for b in node.bases],
            params=[],
            docstring=ast.get_docstring(node) or '',
            body_hash=self._hash_node(node, source),
            metadata={
                'is_abstract': self._is_abstract_class(node),
                'method_count': sum(1 for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))),
            },
        )

    def _parse_function(self, node, file_path: str, source: str, parent: str = '') -> CodeUnit:
        """解析函数/方法定义"""
        is_async = isinstance(node, ast.AsyncFunctionDef)

        return CodeUnit(
            type='function',
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            parent=parent,
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            bases=[],
            params=self._get_function_params(node),
            docstring=ast.get_docstring(node) or '',
            body_hash=self._hash_node(node, source),
            metadata={
                'is_async': is_async,
                'is_private': node.name.startswith('_'),
                'is_dunder': node.name.startswith('__') and node.name.endswith('__'),
                'return_annotation': self._get_return_annotation(node),
            },
        )

    def _get_decorator_name(self, decorator) -> str:
        """获取装饰器名称"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return self._get_attribute_name(decorator)
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return self._get_attribute_name(decorator.func)
        return 'unknown'

    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """获取属性访问的完整名称"""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return '.'.join(reversed(parts))

    def _get_base_name(self, base) -> str:
        """获取基类名称"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return self._get_attribute_name(base)
        elif isinstance(base, ast.Subscript):
            # 处理泛型类型如 Generic[T]
            if isinstance(base.value, ast.Name):
                return base.value.id
            elif isinstance(base.value, ast.Attribute):
                return self._get_attribute_name(base.value)
        return 'unknown'

    def _get_function_params(self, node) -> List[str]:
        """获取函数参数列表"""
        params = []
        for arg in node.args.args:
            params.append(arg.arg)
        return params

    def _get_return_annotation(self, node) -> Optional[str]:
        """获取返回类型注解"""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return None

    def _is_abstract_class(self, node: ast.ClassDef) -> bool:
        """判断是否是抽象类"""
        # 检查是否继承自 ABC 或有 abstractmethod 装饰器
        for base in node.bases:
            base_name = self._get_base_name(base)
            if base_name in ('ABC', 'ABCMeta'):
                return True

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in item.decorator_list:
                    dec_name = self._get_decorator_name(dec)
                    if dec_name in ('abstractmethod', 'abstractproperty'):
                        return True

        return False

    def _hash_node(self, node, source: str) -> str:
        """计算节点代码的哈希值"""
        try:
            lines = source.split('\n')
            start = node.lineno - 1
            end = node.end_lineno or node.lineno
            code = '\n'.join(lines[start:end])
            return self.hash_code(code)
        except Exception:
            return ''
