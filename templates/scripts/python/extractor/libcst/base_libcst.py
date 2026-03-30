# -*- coding: utf-8 -*-
"""
LibCST 提取器基类

提供基于 LibCST 的代码分析基础能力
"""
import os
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

try:
    import libcst as cst
    from libcst.metadata import MetadataWrapper, PositionProvider
    HAS_LIBCST = True
except ImportError:
    HAS_LIBCST = False
    cst = None


class ConfidenceLevel(Enum):
    """置信度层级"""
    FACT = "fact"           # 事实层：100% 可信，直接从代码提取
    STATISTIC = "statistic" # 统计层：基于统计的规范
    INFERRED = "inferred"   # 推断层：基于模式推断
    SUGGESTION = "suggestion"  # 建议层：基于最佳实践


@dataclass
class CodeLocation:
    """代码位置信息"""
    file_path: str
    start_line: int
    end_line: int
    start_col: int = 0
    end_col: int = 0

    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "start_col": self.start_col,
            "end_col": self.end_col,
        }


@dataclass
class CodeUnit:
    """代码单元 - 提取的基本单位"""
    # 基本信息
    name: str
    type: str  # class, function, constant, import, etc.

    # 位置信息
    location: CodeLocation

    # 代码内容
    source_code: str = ""
    signature: str = ""  # 函数/类签名

    # 文档
    docstring: str = ""
    comments: List[str] = field(default_factory=list)

    # 装饰器
    decorators: List[str] = field(default_factory=list)

    # 继承/实现
    bases: List[str] = field(default_factory=list)

    # 参数（函数）
    parameters: List[Dict] = field(default_factory=list)
    return_type: str = ""

    # 属性（类）
    attributes: List[Dict] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)

    # 值（常量）
    value: Any = None
    value_type: str = ""

    # 导入信息
    module: str = ""
    imported_names: List[str] = field(default_factory=list)
    is_from_import: bool = False

    # 异常信息
    exception_type: str = ""
    raised_exceptions: List[str] = field(default_factory=list)
    caught_exceptions: List[str] = field(default_factory=list)

    # 元数据
    metadata: Dict = field(default_factory=dict)
    confidence: float = 1.0
    confidence_level: str = "fact"

    # 关联
    dependencies: List[str] = field(default_factory=list)
    used_by: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            "name": self.name,
            "type": self.type,
            "location": self.location.to_dict(),
            "confidence": self.confidence,
            "confidence_level": self.confidence_level,
        }

        # 只添加非空字段
        if self.source_code:
            result["source_code"] = self.source_code
        if self.signature:
            result["signature"] = self.signature
        if self.docstring:
            result["docstring"] = self.docstring
        if self.comments:
            result["comments"] = self.comments
        if self.decorators:
            result["decorators"] = self.decorators
        if self.bases:
            result["bases"] = self.bases
        if self.parameters:
            result["parameters"] = self.parameters
        if self.return_type:
            result["return_type"] = self.return_type
        if self.attributes:
            result["attributes"] = self.attributes
        if self.methods:
            result["methods"] = self.methods
        if self.value is not None:
            result["value"] = self.value
        if self.value_type:
            result["value_type"] = self.value_type
        if self.module:
            result["module"] = self.module
        if self.imported_names:
            result["imported_names"] = self.imported_names
        if self.is_from_import:
            result["is_from_import"] = self.is_from_import
        if self.exception_type:
            result["exception_type"] = self.exception_type
        if self.raised_exceptions:
            result["raised_exceptions"] = self.raised_exceptions
        if self.caught_exceptions:
            result["caught_exceptions"] = self.caught_exceptions
        if self.metadata:
            result["metadata"] = self.metadata
        if self.dependencies:
            result["dependencies"] = self.dependencies
        if self.used_by:
            result["used_by"] = self.used_by

        return result


@dataclass
class ExtractorResult:
    """提取器结果"""
    extractor_name: str
    file_path: str
    units: List[CodeUnit] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "extractor_name": self.extractor_name,
            "file_path": self.file_path,
            "units": [u.to_dict() for u in self.units],
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "summary": {
                "total_units": len(self.units),
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
            }
        }


class LibCSTExtractor(ABC):
    """LibCST 提取器基类"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化提取器

        Args:
            config: 提取器配置
        """
        if not HAS_LIBCST:
            raise ImportError("libcst is required. Install with: pip install libcst")

        self.config = config or {}
        self._file_cache: Dict[str, str] = {}  # 文件内容缓存
        self._hash_cache: Dict[str, str] = {}  # 文件 hash 缓存

        # 敏感信息过滤配置
        self.sensitive_patterns = self.config.get('sensitive_patterns', [
            r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
            r'(?i)(api_key|apikey|secret|token)\s*=\s*["\'][^"\']+["\']',
            r'(?i)(aws_access_key|aws_secret)',
            r'["\'][A-Za-z0-9+/]{40,}["\']',
        ])

        # 文件大小限制
        self.max_file_lines = self.config.get('max_file_lines', 10000)

    @property
    @abstractmethod
    def name(self) -> str:
        """提取器名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """提取器描述"""
        pass

    @abstractmethod
    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """
        从 CST 树中提取代码单元

        Args:
            tree: LibCST 解析树
            file_path: 文件路径
            source_code: 源代码
            wrapper: MetadataWrapper 用于遍历

        Returns:
            提取的代码单元列表
        """
        pass

    def extract_file(self, file_path: str) -> ExtractorResult:
        """
        从单个文件提取

        Args:
            file_path: 文件路径

        Returns:
            提取结果
        """
        result = ExtractorResult(
            extractor_name=self.name,
            file_path=file_path
        )

        try:
            # 读取文件
            source_code = self._read_file(file_path)
            if source_code is None:
                result.errors.append(f"Failed to read file: {file_path}")
                return result

            # 检查文件大小
            line_count = source_code.count('\n') + 1
            if line_count > self.max_file_lines:
                result.warnings.append(
                    f"File too large ({line_count} lines), extracting signatures only"
                )
                result.metadata['large_file'] = True

            # 解析 CST
            try:
                tree = cst.parse_module(source_code)
            except cst.ParserSyntaxError as e:
                result.errors.append(f"Syntax error: {str(e)}")
                return result

            # 使用 MetadataWrapper 遍历
            wrapper = cst.MetadataWrapper(tree)

            # 提取代码单元
            units = self.extract_from_tree(tree, file_path, source_code, wrapper)
            result.units = units

            # 添加元数据
            result.metadata['line_count'] = line_count
            result.metadata['file_hash'] = self._get_file_hash(file_path, source_code)

        except Exception as e:
            result.errors.append(f"Extraction error: {str(e)}")

        return result

    def extract_directory(
        self,
        directory: str,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[ExtractorResult]:
        """
        从目录提取

        Args:
            directory: 目录路径
            exclude_patterns: 排除的文件模式

        Returns:
            提取结果列表
        """
        results = []
        exclude_patterns = exclude_patterns or [
            '__pycache__', '.git', '.venv', 'venv', 'node_modules',
            'migrations', 'tests', 'test_*.py', '*_test.py'
        ]

        for root, dirs, files in os.walk(directory):
            # 过滤目录
            dirs[:] = [d for d in dirs if not self._should_exclude(d, exclude_patterns)]

            for file in files:
                if not file.endswith('.py'):
                    continue
                if self._should_exclude(file, exclude_patterns):
                    continue

                file_path = os.path.join(root, file)
                result = self.extract_file(file_path)
                results.append(result)

        return results

    def _read_file(self, file_path: str) -> Optional[str]:
        """读取文件内容"""
        if file_path in self._file_cache:
            return self._file_cache[file_path]

        try:
            # 尝试多种编码
            encodings = ['utf-8', 'latin-1', 'gbk']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                        self._file_cache[file_path] = content
                        return content
                except UnicodeDecodeError:
                    continue
            return None
        except Exception:
            return None

    def _get_file_hash(self, file_path: str, content: Optional[str] = None) -> str:
        """获取文件 hash"""
        if file_path in self._hash_cache:
            return self._hash_cache[file_path]

        if content is None:
            content = self._read_file(file_path) or ""

        file_hash = hashlib.md5(content.encode()).hexdigest()
        self._hash_cache[file_path] = file_hash
        return file_hash

    def _should_exclude(self, name: str, patterns: List[str]) -> bool:
        """检查是否应该排除"""
        import fnmatch
        for pattern in patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False

    def _get_node_source(self, node: 'cst.CSTNode') -> str:
        """获取节点的源代码"""
        try:
            return node.code if hasattr(node, 'code') else cst.Module([]).code_for_node(node)
        except Exception:
            return ""

    def _get_docstring(self, body: 'cst.BaseSuite') -> str:
        """从函数/类体中提取 docstring"""
        if isinstance(body, cst.IndentedBlock):
            statements = body.body
            if statements:
                first_stmt = statements[0]
                if isinstance(first_stmt, cst.SimpleStatementLine):
                    if first_stmt.body and isinstance(first_stmt.body[0], cst.Expr):
                        expr = first_stmt.body[0].value
                        if isinstance(expr, (cst.SimpleString, cst.ConcatenatedString, cst.FormattedString)):
                            return self._extract_string_value(expr)
        return ""

    def _extract_string_value(self, node: 'cst.BaseExpression') -> str:
        """提取字符串值"""
        if isinstance(node, cst.SimpleString):
            # 去除引号
            value = node.value
            if value.startswith(('"""', "'''")):
                return value[3:-3]
            elif value.startswith(('"', "'")):
                return value[1:-1]
            return value
        elif isinstance(node, cst.ConcatenatedString):
            parts = []
            for part in node.left, node.right:
                parts.append(self._extract_string_value(part))
            return "".join(parts)
        return ""

    def _get_annotation_string(self, annotation: Optional['cst.Annotation']) -> str:
        """获取类型注解字符串"""
        if annotation is None:
            return ""
        try:
            return cst.Module([]).code_for_node(annotation.annotation)
        except Exception:
            return ""

    def _get_name_string(self, node: 'cst.BaseExpression') -> str:
        """获取名称字符串"""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            return f"{self._get_name_string(node.value)}.{node.attr.value}"
        elif isinstance(node, cst.Subscript):
            return f"{self._get_name_string(node.value)}[...]"
        return ""
