# -*- coding: utf-8 -*-
"""
Shell 提取器基类和数据结构定义

复用 Python 提取器的核心概念，适配 Shell 脚本特点
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ShellKnowledgeType(Enum):
    """Shell 知识类型枚举"""
    # 代码结构
    FUNCTION = "function"
    VARIABLE = "variable"
    CONSTANT = "constant"

    # 引用关系
    SOURCE = "source"
    DEPENDENCY = "dependency"

    # 文档
    COMMENT = "comment"
    HEADER = "header"

    # 模式
    PATTERN = "pattern"
    LOGGING = "logging"
    ERROR_HANDLING = "error_handling"


class VariableCategory(Enum):
    """变量分类"""
    CONSTANT = "constant"      # 常量（全大写）
    PATH = "path"              # 路径变量
    CONFIG = "config"          # 配置变量
    ENV = "env"                # 环境变量（export）
    LOCAL = "local"            # 局部变量
    OTHER = "other"


@dataclass
class ShellFunction:
    """Shell 函数信息"""
    name: str
    file_path: str
    line: int
    end_line: int
    params_used: List[str] = field(default_factory=list)  # $1, $2, $@, $*
    local_vars: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)  # 调用的外部命令
    docstring: str = ""
    raw_code: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "file_path": self.file_path,
            "line": self.line,
            "end_line": self.end_line,
            "params_used": self.params_used,
            "local_vars": self.local_vars,
            "calls": self.calls,
            "docstring": self.docstring,
            "raw_code": self.raw_code,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ShellFunction':
        return cls(
            name=data.get("name", ""),
            file_path=data.get("file_path", ""),
            line=data.get("line", 0),
            end_line=data.get("end_line", 0),
            params_used=data.get("params_used", []),
            local_vars=data.get("local_vars", []),
            calls=data.get("calls", []),
            docstring=data.get("docstring", ""),
            raw_code=data.get("raw_code", ""),
        )


@dataclass
class ShellVariable:
    """Shell 变量信息"""
    name: str
    value: str
    file_path: str
    line: int
    category: str = "other"
    is_export: bool = False
    is_readonly: bool = False
    comment: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "file_path": self.file_path,
            "line": self.line,
            "category": self.category,
            "is_export": self.is_export,
            "is_readonly": self.is_readonly,
            "comment": self.comment,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ShellVariable':
        return cls(
            name=data.get("name", ""),
            value=data.get("value", ""),
            file_path=data.get("file_path", ""),
            line=data.get("line", 0),
            category=data.get("category", "other"),
            is_export=data.get("is_export", False),
            is_readonly=data.get("is_readonly", False),
            comment=data.get("comment", ""),
        )


@dataclass
class ShellComment:
    """Shell 注释信息"""
    content: str
    file_path: str
    line: int
    comment_type: str = "inline"  # header, function_doc, inline, todo
    related_to: str = ""  # 关联的函数或变量名

    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "file_path": self.file_path,
            "line": self.line,
            "comment_type": self.comment_type,
            "related_to": self.related_to,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ShellComment':
        return cls(
            content=data.get("content", ""),
            file_path=data.get("file_path", ""),
            line=data.get("line", 0),
            comment_type=data.get("comment_type", "inline"),
            related_to=data.get("related_to", ""),
        )


@dataclass
class ShellSource:
    """Shell source/. 引用信息"""
    source_file: str  # 当前文件
    target_file: str  # 被引用的文件
    line: int
    resolved_path: str = ""  # 解析后的绝对路径

    def to_dict(self) -> Dict:
        return {
            "source_file": self.source_file,
            "target_file": self.target_file,
            "line": self.line,
            "resolved_path": self.resolved_path,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ShellSource':
        return cls(
            source_file=data.get("source_file", ""),
            target_file=data.get("target_file", ""),
            line=data.get("line", 0),
            resolved_path=data.get("resolved_path", ""),
        )


@dataclass
class ShellPattern:
    """Shell 代码模式"""
    pattern_type: str  # logging, error_handling, service_management, file_operation
    pattern_name: str
    count: int
    examples: List[Dict] = field(default_factory=list)  # [{file, line, code}]

    def to_dict(self) -> Dict:
        return {
            "pattern_type": self.pattern_type,
            "pattern_name": self.pattern_name,
            "count": self.count,
            "examples": self.examples,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ShellPattern':
        return cls(
            pattern_type=data.get("pattern_type", ""),
            pattern_name=data.get("pattern_name", ""),
            count=data.get("count", 0),
            examples=data.get("examples", []),
        )


class BaseShellExtractor(ABC):
    """Shell 提取器基类"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.errors: List[str] = []

    @abstractmethod
    def extract(self, file_path: str, content: str) -> List[Any]:
        """
        从单个文件提取知识

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            提取的知识项列表
        """
        pass

    @abstractmethod
    def extract_all(self, source_dir: str) -> List[Any]:
        """
        从目录提取所有知识

        Args:
            source_dir: 源码目录

        Returns:
            提取的知识项列表
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """提取器名称"""
        pass

    def _find_shell_files(self, source_dir: str) -> List[str]:
        """查找所有 Shell 文件"""
        import os
        import glob

        shell_files = []

        # 查找 .sh 文件
        for pattern in ['**/*.sh', '**/*.bash']:
            shell_files.extend(glob.glob(
                os.path.join(source_dir, pattern),
                recursive=True
            ))

        # 过滤排除目录
        exclude_patterns = self.config.get('exclude_patterns') or [
            '__pycache__', '.git', 'node_modules', 'venv', '.venv'
        ]

        filtered_files = []
        for f in shell_files:
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in f:
                    should_exclude = True
                    break
            if not should_exclude:
                filtered_files.append(f)

        return sorted(filtered_files)

    def _read_file(self, file_path: str) -> Optional[str]:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            self.errors.append(f"读取文件失败 {file_path}: {e}")
            return None
