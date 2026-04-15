# -*- coding: utf-8 -*-
"""
智能规范提取系统 - 基础数据结构

提供代码单元和代码模式的数据结构定义
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import hashlib
import json


@dataclass
class CodeUnit:
    """
    代码单元（类/函数/模块）

    表示代码中的一个独立单元，可以是类、函数或模块
    """
    type: str                          # class, function, module
    name: str                          # 名称
    file_path: str                     # 文件路径
    line_start: int                    # 起始行
    line_end: int                      # 结束行
    parent: str = ''                   # 父级名称（如函数所属的类）
    decorators: List[str] = field(default_factory=list)  # 装饰器列表
    bases: List[str] = field(default_factory=list)       # 基类列表（仅类）
    params: List[str] = field(default_factory=list)      # 参数列表（仅函数）
    docstring: str = ''                # 文档字符串
    body_hash: str = ''                # 代码体哈希，用于相似度比较
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CodeUnit':
        """从字典创建"""
        return cls(**data)

    def get_full_name(self) -> str:
        """获取完整名称（包含父级）"""
        if self.parent:
            return f"{self.parent}.{self.name}"
        return self.name


@dataclass
class CodePattern:
    """
    代码模式

    表示代码中发现的重复模式
    """
    pattern_type: str                  # inheritance, decorator, naming, structure, import
    pattern_key: str                   # 模式标识（如 extends:BaseModel, @formatting）
    occurrences: int                   # 出现次数
    examples: List[CodeUnit] = field(default_factory=list)  # 示例代码单元
    confidence: float = 0.0            # 置信度（出现次数/总数）
    description: str = ''              # 模式描述
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据

    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            'pattern_type': self.pattern_type,
            'pattern_key': self.pattern_key,
            'occurrences': self.occurrences,
            'confidence': self.confidence,
            'description': self.description,
            'metadata': self.metadata,
            'examples': [ex.to_dict() for ex in self.examples],
        }
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> 'CodePattern':
        """从字典创建"""
        examples = [CodeUnit.from_dict(ex) for ex in data.get('examples', [])]
        return cls(
            pattern_type=data['pattern_type'],
            pattern_key=data['pattern_key'],
            occurrences=data['occurrences'],
            examples=examples,
            confidence=data.get('confidence', 0.0),
            description=data.get('description', ''),
            metadata=data.get('metadata', {}),
        )

    def is_significant(self, min_occurrences: int = 2, min_confidence: float = 0.05) -> bool:
        """判断模式是否显著"""
        return self.occurrences >= min_occurrences and self.confidence >= min_confidence


class BaseParser(ABC):
    """
    解析器基类

    定义代码解析器的接口
    """

    @abstractmethod
    def parse_file(self, file_path: str) -> List[CodeUnit]:
        """
        解析单个文件

        Args:
            file_path: 文件路径

        Returns:
            代码单元列表
        """
        pass

    @abstractmethod
    def get_language(self) -> str:
        """
        返回支持的语言

        Returns:
            语言名称（如 python, javascript）
        """
        pass

    @abstractmethod
    def get_file_extensions(self) -> List[str]:
        """
        返回支持的文件扩展名

        Returns:
            扩展名列表（如 ['.py']）
        """
        pass

    def parse_directory(self, directory: str, exclude_patterns: List[str] = None) -> List[CodeUnit]:
        """
        解析目录下的所有文件

        Args:
            directory: 目录路径
            exclude_patterns: 排除的路径模式

        Returns:
            代码单元列表
        """
        import os
        import fnmatch

        exclude_patterns = exclude_patterns or ['*/__pycache__/*', '*/node_modules/*', '*/.git/*']
        units = []
        extensions = self.get_file_extensions()

        for root, dirs, files in os.walk(directory):
            # 检查是否应该排除此目录
            should_exclude = False
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(root, pattern):
                    should_exclude = True
                    break

            if should_exclude:
                continue

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)

                    # 检查文件是否应该排除
                    should_exclude_file = False
                    for pattern in exclude_patterns:
                        if fnmatch.fnmatch(file_path, pattern):
                            should_exclude_file = True
                            break

                    if not should_exclude_file:
                        try:
                            file_units = self.parse_file(file_path)
                            units.extend(file_units)
                        except Exception as e:
                            print(f"Warning: Failed to parse {file_path}: {e}")

        return units

    @staticmethod
    def hash_code(code: str) -> str:
        """
        计算代码哈希

        Args:
            code: 代码字符串

        Returns:
            哈希值
        """
        return hashlib.md5(code.encode('utf-8')).hexdigest()[:16]


def save_units(units: List[CodeUnit], output_path: str):
    """保存代码单元到 JSON 文件"""
    data = [unit.to_dict() for unit in units]
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_units(input_path: str) -> List[CodeUnit]:
    """从 JSON 文件加载代码单元"""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [CodeUnit.from_dict(item) for item in data]


def save_patterns(patterns: List[CodePattern], output_path: str):
    """保存代码模式到 JSON 文件"""
    data = [pattern.to_dict() for pattern in patterns]
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_patterns(input_path: str) -> List[CodePattern]:
    """从 JSON 文件加载代码模式"""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [CodePattern.from_dict(item) for item in data]
