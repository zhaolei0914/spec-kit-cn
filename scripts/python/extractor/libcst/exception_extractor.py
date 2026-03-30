# -*- coding: utf-8 -*-
"""
异常提取器

提取自定义异常类、raise 语句、try-except 模式
"""
from typing import Dict, List, Optional, Set

try:
    import libcst as cst
except ImportError:
    cst = None

from .base_libcst import LibCSTExtractor, CodeUnit, CodeLocation


class ExceptionExtractor(LibCSTExtractor):
    """异常提取器"""

    @property
    def name(self) -> str:
        return "exception_extractor"

    @property
    def description(self) -> str:
        return "提取自定义异常类、raise 语句和 try-except 模式"

    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """从 CST 树中提取异常相关信息"""
        visitor = ExceptionVisitor(file_path, source_code, self)
        if wrapper:
            wrapper.visit(visitor)
        return visitor.exceptions


class ExceptionVisitor(cst.CSTVisitor):
    """异常访问器"""

    # 标准异常基类
    EXCEPTION_BASES = {
        'Exception', 'BaseException', 'ValueError', 'TypeError', 'KeyError',
        'AttributeError', 'RuntimeError', 'IOError', 'OSError', 'ImportError',
        'IndexError', 'StopIteration', 'AssertionError', 'NotImplementedError',
        'PermissionError', 'FileNotFoundError', 'ConnectionError', 'TimeoutError',
    }

    def __init__(self, file_path: str, source_code: str, extractor: ExceptionExtractor):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.extractor = extractor
        self.exceptions: List[CodeUnit] = []
        self._current_function = ""
        self._current_class = ""

    def visit_ClassDef(self, node: 'cst.ClassDef') -> Optional[bool]:
        """访问类定义，检查是否是异常类"""
        class_name = node.name.value
        self._current_class = class_name

        # 检查是否继承自异常类
        bases = self._get_bases(node.bases)
        is_exception = any(
            base in self.EXCEPTION_BASES or base.endswith('Error') or base.endswith('Exception')
            for base in bases
        )

        if is_exception:
            location = self._get_location_for_class(class_name)
            docstring = self.extractor._get_docstring(node.body)

            try:
                source_code = cst.Module([]).code_for_node(node)
            except Exception:
                source_code = ""

            # 提取异常类的属性
            attributes = self._extract_exception_attributes(node.body)

            unit = CodeUnit(
                name=class_name,
                type="exception_class",
                location=location,
                source_code=source_code,
                docstring=docstring,
                bases=bases,
                exception_type=bases[0] if bases else "Exception",
                attributes=attributes,
                confidence=1.0,
                confidence_level="fact",
                metadata={
                    "is_custom_exception": True,
                    "base_exception": bases[0] if bases else "Exception",
                }
            )

            self.exceptions.append(unit)

        return True

    def leave_ClassDef(self, node: 'cst.ClassDef') -> None:
        """离开类定义"""
        self._current_class = ""

    def visit_FunctionDef(self, node: 'cst.FunctionDef') -> Optional[bool]:
        """进入函数定义"""
        self._current_function = node.name.value
        return True

    def leave_FunctionDef(self, node: 'cst.FunctionDef') -> None:
        """离开函数定义"""
        self._current_function = ""

    def visit_Raise(self, node: 'cst.Raise') -> None:
        """访问 raise 语句"""
        if node.exc is None:
            # 裸 raise
            return

        exc_name, exc_args = self._extract_raise_info(node.exc)
        if not exc_name:
            return

        location = self._get_location_for_raise(exc_name)

        try:
            source_code = cst.Module([]).code_for_node(node)
        except Exception:
            source_code = f"raise {exc_name}"

        # 构建上下文名称
        context = ""
        if self._current_class:
            context = self._current_class
            if self._current_function:
                context += f".{self._current_function}"
        elif self._current_function:
            context = self._current_function

        unit = CodeUnit(
            name=f"raise_{exc_name}_{location.start_line}",
            type="raise_statement",
            location=location,
            source_code=source_code,
            exception_type=exc_name,
            raised_exceptions=[exc_name],
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "exception_name": exc_name,
                "exception_args": exc_args,
                "context": context,
                "has_cause": node.cause is not None,
            }
        )

        self.exceptions.append(unit)

    def visit_Try(self, node: 'cst.Try') -> None:
        """访问 try-except 语句"""
        caught_exceptions = []

        for handler in node.handlers:
            if handler.type:
                exc_types = self._extract_handler_types(handler.type)
                for exc_type in exc_types:
                    caught_exceptions.append({
                        "type": exc_type,
                        "alias": handler.name.value if handler.name else None,
                    })

        if not caught_exceptions:
            return

        location = self._get_location_for_try()

        try:
            # 只获取 try 头部
            source_code = "try: ..."
        except Exception:
            source_code = "try: ..."

        # 构建上下文名称
        context = ""
        if self._current_class:
            context = self._current_class
            if self._current_function:
                context += f".{self._current_function}"
        elif self._current_function:
            context = self._current_function

        unit = CodeUnit(
            name=f"try_except_{location.start_line}",
            type="try_except",
            location=location,
            source_code=source_code,
            caught_exceptions=[e["type"] for e in caught_exceptions],
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "handlers": caught_exceptions,
                "has_else": node.orelse is not None,
                "has_finally": node.finalbody is not None,
                "context": context,
                "is_bare_except": any(e["type"] == "Exception" for e in caught_exceptions),
            }
        )

        self.exceptions.append(unit)

    def _get_bases(self, bases) -> List[str]:
        """获取基类列表"""
        result = []
        for base in bases:
            name = self._get_name(base.value)
            if name:
                result.append(name)
        return result

    def _get_name(self, node) -> str:
        """获取名称"""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            return f"{self._get_name(node.value)}.{node.attr.value}"
        return ""

    def _extract_raise_info(self, exc_node) -> tuple:
        """提取 raise 语句信息"""
        if isinstance(exc_node, cst.Call):
            exc_name = self._get_name(exc_node.func)
            exc_args = []
            for arg in exc_node.args:
                try:
                    arg_str = cst.Module([]).code_for_node(arg.value)
                    exc_args.append(arg_str)
                except Exception:
                    pass
            return exc_name, exc_args
        else:
            exc_name = self._get_name(exc_node)
            return exc_name, []

    def _extract_handler_types(self, type_node) -> List[str]:
        """提取 except 处理的异常类型"""
        if isinstance(type_node, cst.Tuple):
            types = []
            for elem in type_node.elements:
                name = self._get_name(elem.value)
                if name:
                    types.append(name)
            return types
        else:
            name = self._get_name(type_node)
            return [name] if name else []

    def _extract_exception_attributes(self, body: 'cst.BaseSuite') -> List[Dict]:
        """提取异常类的属性"""
        attributes = []

        if not isinstance(body, cst.IndentedBlock):
            return attributes

        for stmt in body.body:
            if isinstance(stmt, cst.FunctionDef):
                if stmt.name.value == '__init__':
                    # 从 __init__ 中提取属性
                    for param in stmt.params.params:
                        if param.name.value != 'self':
                            attributes.append({
                                "name": param.name.value,
                                "type": self.extractor._get_annotation_string(param.annotation) if param.annotation else "",
                            })

        return attributes

    def _get_location_for_class(self, class_name: str) -> CodeLocation:
        """获取类位置"""
        start_line = 1
        for i, line in enumerate(self.source_lines, 1):
            if f"class {class_name}" in line:
                start_line = i
                break

        return CodeLocation(
            file_path=self.file_path,
            start_line=start_line,
            end_line=start_line
        )

    def _get_location_for_raise(self, exc_name: str) -> CodeLocation:
        """获取 raise 语句位置"""
        start_line = 1
        for i, line in enumerate(self.source_lines, 1):
            if 'raise' in line and exc_name in line:
                start_line = i
                break

        return CodeLocation(
            file_path=self.file_path,
            start_line=start_line,
            end_line=start_line
        )

    def _get_location_for_try(self) -> CodeLocation:
        """获取 try 语句位置"""
        # 简化处理，返回当前位置
        return CodeLocation(
            file_path=self.file_path,
            start_line=1,
            end_line=1
        )
