# -*- coding: utf-8 -*-
"""
常量提取器

提取模块级常量、枚举定义等
"""
import re
from typing import Dict, List, Optional

try:
    import libcst as cst
except ImportError:
    cst = None

from .base_libcst import LibCSTExtractor, CodeUnit, CodeLocation


class ConstantExtractor(LibCSTExtractor):
    """常量提取器"""

    # 常量命名模式（全大写）
    CONSTANT_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')

    @property
    def name(self) -> str:
        return "constant_extractor"

    @property
    def description(self) -> str:
        return "提取模块级常量和枚举定义"

    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """从 CST 树中提取常量"""
        visitor = ConstantVisitor(file_path, source_code, self)
        if wrapper:
            wrapper.visit(visitor)
        return visitor.constants


class ConstantVisitor(cst.CSTVisitor):
    """常量访问器"""

    def __init__(self, file_path: str, source_code: str, extractor: ConstantExtractor):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.extractor = extractor
        self.constants: List[CodeUnit] = []
        self._in_class = False
        self._in_function = False
        self._class_name = ""
        self._current_line = 0

    def visit_ClassDef(self, node: 'cst.ClassDef') -> Optional[bool]:
        """进入类定义"""
        self._in_class = True
        self._class_name = node.name.value

        # 检查是否是枚举类
        bases = [self._get_base_name(b) for b in node.bases]
        if any(b in ('Enum', 'IntEnum', 'StrEnum', 'Flag', 'IntFlag') for b in bases):
            self._extract_enum_members(node)

        return True

    def leave_ClassDef(self, node: 'cst.ClassDef') -> None:
        """离开类定义"""
        self._in_class = False
        self._class_name = ""

    def visit_FunctionDef(self, node: 'cst.FunctionDef') -> Optional[bool]:
        """进入函数定义"""
        self._in_function = True
        return True

    def leave_FunctionDef(self, node: 'cst.FunctionDef') -> None:
        """离开函数定义"""
        self._in_function = False

    def visit_Assign(self, node: 'cst.Assign') -> None:
        """访问赋值语句"""
        # 只处理模块级常量
        if self._in_function:
            return

        for target in node.targets:
            if isinstance(target.target, cst.Name):
                name = target.target.value

                # 检查是否是常量（全大写命名）
                if self.extractor.CONSTANT_PATTERN.match(name):
                    self._add_constant(name, node.value, node)

    def visit_AnnAssign(self, node: 'cst.AnnAssign') -> None:
        """访问带注解的赋值语句"""
        if self._in_function:
            return

        if isinstance(node.target, cst.Name):
            name = node.target.value

            # 检查是否是常量
            if self.extractor.CONSTANT_PATTERN.match(name):
                self._add_constant(name, node.value, node, node.annotation)

    def _add_constant(
        self,
        name: str,
        value_node: Optional['cst.BaseExpression'],
        assign_node: 'cst.CSTNode',
        annotation: Optional['cst.Annotation'] = None
    ) -> None:
        """添加常量"""
        # 获取值
        value, value_type = self._extract_value(value_node)

        # 获取类型注解
        if annotation:
            value_type = self.extractor._get_annotation_string(annotation)

        # 获取位置
        location = self._get_location(name)

        # 获取源代码
        try:
            source_code = cst.Module([]).code_for_node(assign_node)
        except Exception:
            source_code = f"{name} = {value}"

        # 获取注释
        comments = self._get_inline_comment(assign_node)

        # 确定完整名称
        if self._in_class and self._class_name:
            full_name = f"{self._class_name}.{name}"
        else:
            full_name = name

        unit = CodeUnit(
            name=full_name,
            type="constant",
            location=location,
            source_code=source_code,
            value=value,
            value_type=value_type,
            comments=comments,
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "is_class_constant": self._in_class,
                "is_sensitive": self._is_sensitive(name, value),
            }
        )

        self.constants.append(unit)

    def _extract_value(self, node: Optional['cst.BaseExpression']) -> tuple:
        """提取值和类型"""
        if node is None:
            return None, ""

        try:
            if isinstance(node, cst.Integer):
                return int(node.value), "int"
            elif isinstance(node, cst.Float):
                return float(node.value), "float"
            elif isinstance(node, cst.SimpleString):
                value = self.extractor._extract_string_value(node)
                return value, "str"
            elif isinstance(node, (cst.Tuple, cst.List)):
                code = cst.Module([]).code_for_node(node)
                return code, "tuple" if isinstance(node, cst.Tuple) else "list"
            elif isinstance(node, cst.Dict):
                code = cst.Module([]).code_for_node(node)
                return code, "dict"
            elif isinstance(node, cst.Set):
                code = cst.Module([]).code_for_node(node)
                return code, "set"
            elif isinstance(node, cst.Name):
                if node.value in ('True', 'False'):
                    return node.value == 'True', "bool"
                elif node.value == 'None':
                    return None, "NoneType"
                return node.value, "reference"
            else:
                code = cst.Module([]).code_for_node(node)
                return code, "expression"
        except Exception:
            return None, ""

    def _get_location(self, name: str) -> CodeLocation:
        """获取常量位置"""
        start_line = 1
        for i, line in enumerate(self.source_lines, 1):
            if re.search(rf'\b{re.escape(name)}\s*[=:]', line):
                start_line = i
                break

        return CodeLocation(
            file_path=self.file_path,
            start_line=start_line,
            end_line=start_line
        )

    def _get_inline_comment(self, node: 'cst.CSTNode') -> List[str]:
        """获取行内注释"""
        comments = []
        if hasattr(node, 'trailing_comment') and node.trailing_comment:
            comments.append(node.trailing_comment.value)
        return comments

    def _get_base_name(self, arg: 'cst.Arg') -> str:
        """获取基类名称"""
        if isinstance(arg.value, cst.Name):
            return arg.value.value
        elif isinstance(arg.value, cst.Attribute):
            return arg.value.attr.value
        return ""

    def _extract_enum_members(self, node: 'cst.ClassDef') -> None:
        """提取枚举成员"""
        if not isinstance(node.body, cst.IndentedBlock):
            return

        class_name = node.name.value

        for stmt in node.body.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for item in stmt.body:
                    if isinstance(item, cst.Assign):
                        for target in item.targets:
                            if isinstance(target.target, cst.Name):
                                member_name = target.target.value
                                value, value_type = self._extract_value(item.value)

                                location = self._get_location(member_name)

                                unit = CodeUnit(
                                    name=f"{class_name}.{member_name}",
                                    type="enum_member",
                                    location=location,
                                    value=value,
                                    value_type=value_type,
                                    confidence=1.0,
                                    confidence_level="fact",
                                    metadata={
                                        "enum_class": class_name,
                                    }
                                )

                                self.constants.append(unit)

    def _is_sensitive(self, name: str, value) -> bool:
        """检查是否是敏感信息"""
        sensitive_keywords = [
            'password', 'passwd', 'pwd', 'secret', 'token',
            'api_key', 'apikey', 'private_key', 'credential'
        ]
        name_lower = name.lower()
        return any(kw in name_lower for kw in sensitive_keywords)
