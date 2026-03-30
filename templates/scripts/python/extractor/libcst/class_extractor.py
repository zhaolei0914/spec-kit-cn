# -*- coding: utf-8 -*-
"""
类提取器

提取类定义、继承关系、方法、属性等信息
"""
from typing import Dict, List, Optional, Sequence
from dataclasses import dataclass

try:
    import libcst as cst
    from libcst import matchers as m
except ImportError:
    cst = None
    m = None

from .base_libcst import LibCSTExtractor, CodeUnit, CodeLocation


class ClassExtractor(LibCSTExtractor):
    """类提取器"""

    @property
    def name(self) -> str:
        return "class_extractor"

    @property
    def description(self) -> str:
        return "提取类定义、继承关系、方法和属性"

    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """从 CST 树中提取类"""
        visitor = ClassVisitor(file_path, source_code, self)
        if wrapper:
            wrapper.visit(visitor)
        return visitor.classes


class ClassVisitor(cst.CSTVisitor):
    """类访问器"""

    def __init__(self, file_path: str, source_code: str, extractor: ClassExtractor):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.extractor = extractor
        self.classes: List[CodeUnit] = []
        self._current_class_stack: List[str] = []  # 支持嵌套类
        self._line_offset = 0

    def visit_ClassDef(self, node: 'cst.ClassDef') -> Optional[bool]:
        """访问类定义"""
        # 获取类名
        class_name = node.name.value

        # 处理嵌套类
        if self._current_class_stack:
            full_name = ".".join(self._current_class_stack + [class_name])
        else:
            full_name = class_name

        self._current_class_stack.append(class_name)

        # 获取位置信息
        location = self._get_location(node)

        # 获取装饰器
        decorators = self._get_decorators(node.decorators)

        # 获取基类
        bases = self._get_bases(node.bases)

        # 获取 docstring
        docstring = self.extractor._get_docstring(node.body)

        # 获取方法和属性
        methods, attributes = self._extract_members(node.body)

        # 获取源代码
        try:
            source_code = cst.Module([]).code_for_node(node)
        except Exception:
            source_code = ""

        # 生成签名
        signature = self._generate_signature(class_name, bases, decorators)

        # 创建 CodeUnit
        unit = CodeUnit(
            name=full_name,
            type="class",
            location=location,
            source_code=source_code,
            signature=signature,
            docstring=docstring,
            decorators=decorators,
            bases=bases,
            methods=methods,
            attributes=attributes,
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "is_nested": len(self._current_class_stack) > 1,
                "method_count": len(methods),
                "attribute_count": len(attributes),
            }
        )

        self.classes.append(unit)

        return True  # 继续访问子节点

    def leave_ClassDef(self, node: 'cst.ClassDef') -> None:
        """离开类定义"""
        if self._current_class_stack:
            self._current_class_stack.pop()

    def _get_location(self, node: 'cst.ClassDef') -> CodeLocation:
        """获取类的位置信息"""
        # 简单估算行号（LibCST 需要 MetadataWrapper 获取精确位置）
        try:
            code = cst.Module([]).code_for_node(node)
            # 在源码中查找类定义
            class_def_pattern = f"class {node.name.value}"
            start_line = 1
            for i, line in enumerate(self.source_lines, 1):
                if class_def_pattern in line:
                    start_line = i
                    break
            end_line = start_line + code.count('\n')
        except Exception:
            start_line = 1
            end_line = 1

        return CodeLocation(
            file_path=self.file_path,
            start_line=start_line,
            end_line=end_line
        )

    def _get_decorators(self, decorators: Sequence['cst.Decorator']) -> List[str]:
        """获取装饰器列表"""
        result = []
        for dec in decorators:
            try:
                dec_str = cst.Module([]).code_for_node(dec.decorator)
                result.append(f"@{dec_str}")
            except Exception:
                pass
        return result

    def _get_bases(self, bases: Sequence['cst.Arg']) -> List[str]:
        """获取基类列表"""
        result = []
        for base in bases:
            try:
                base_str = self.extractor._get_name_string(base.value)
                if base_str:
                    result.append(base_str)
            except Exception:
                pass
        return result

    def _extract_members(self, body: 'cst.BaseSuite') -> tuple:
        """提取类成员（方法和属性）"""
        methods = []
        attributes = []

        if not isinstance(body, cst.IndentedBlock):
            return methods, attributes

        for stmt in body.body:
            if isinstance(stmt, cst.FunctionDef):
                # 方法
                method_info = self._extract_method_info(stmt)
                methods.append(method_info)
            elif isinstance(stmt, cst.SimpleStatementLine):
                # 可能是属性定义
                for item in stmt.body:
                    if isinstance(item, (cst.Assign, cst.AnnAssign)):
                        attr_info = self._extract_attribute_info(item)
                        if attr_info:
                            attributes.append(attr_info)

        return methods, attributes

    def _extract_method_info(self, node: 'cst.FunctionDef') -> str:
        """提取方法信息"""
        name = node.name.value
        decorators = self._get_decorators(node.decorators)

        # 简化的方法签名
        params = []
        if node.params:
            for param in node.params.params:
                params.append(param.name.value)

        dec_prefix = ""
        if decorators:
            if any("@property" in d for d in decorators):
                dec_prefix = "@property "
            elif any("@staticmethod" in d for d in decorators):
                dec_prefix = "@staticmethod "
            elif any("@classmethod" in d for d in decorators):
                dec_prefix = "@classmethod "

        return f"{dec_prefix}{name}({', '.join(params)})"

    def _extract_attribute_info(self, node) -> Optional[Dict]:
        """提取属性信息"""
        if isinstance(node, cst.AnnAssign):
            # 带类型注解的属性
            if isinstance(node.target, cst.Name):
                name = node.target.value
                type_hint = self.extractor._get_annotation_string(
                    cst.Annotation(annotation=node.annotation)
                ) if node.annotation else ""
                return {"name": name, "type": type_hint}
        elif isinstance(node, cst.Assign):
            # 普通赋值
            for target in node.targets:
                if isinstance(target.target, cst.Name):
                    name = target.target.value
                    # 跳过私有属性的值提取
                    return {"name": name, "type": ""}
        return None

    def _generate_signature(
        self,
        name: str,
        bases: List[str],
        decorators: List[str]
    ) -> str:
        """生成类签名"""
        parts = []

        # 装饰器
        for dec in decorators:
            parts.append(dec)

        # 类定义
        if bases:
            parts.append(f"class {name}({', '.join(bases)}):")
        else:
            parts.append(f"class {name}:")

        return "\n".join(parts)
