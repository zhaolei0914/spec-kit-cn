# -*- coding: utf-8 -*-
"""
提取器基类和知识项定义

定义统一的提取器接口，所有具体提取器都需要实现这个接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class KnowledgeType(Enum):
    """知识类型枚举"""
    # 结构知识
    DIRECTORY = "directory"
    SERVICE = "service"
    TECH_STACK = "tech_stack"
    DEPENDENCY = "dependency"

    # 代码知识
    PATTERN = "pattern"
    CONSTANT = "constant"
    ERROR_CODE = "error_code"
    EXCEPTION = "exception"
    LOG = "log"
    CONFIG = "config"

    # 业务知识
    MODEL = "model"
    API = "api"
    FLOW = "flow"
    TERM = "term"

    # 文档知识
    README = "readme"
    DOCSTRING = "docstring"
    COMMENT = "comment"
    DESIGN = "design"


class Priority(Enum):
    """优先级（新人视角）"""
    MUST_KNOW = 1       # 必须知道：项目结构、技术栈、开发流程
    DEV_ESSENTIAL = 2   # 开发必备：代码模式、错误处理、API 规范
    DEEP_DIVE = 3       # 深入了解：业务流程、数据模型、配置规范
    ADVANCED = 4        # 进阶知识：性能优化、部署规范、监控规范


class SourceType(Enum):
    """来源类型（用于置信度计算）"""
    CODE = "code"           # 代码（最高权重）
    CONFIG = "config"       # 配置文件
    COMMENT = "comment"     # 注释
    DOCSTRING = "docstring" # 文档字符串
    INFERRED = "inferred"   # 推断（最低权重）


@dataclass
class KnowledgeItem:
    """知识项 - 系统中的基本知识单元"""

    # 必填字段
    type: str               # 知识类型（KnowledgeType 的值）
    key: str                # 唯一标识
    value: Any              # 知识内容

    # 来源信息
    source_file: str = ""   # 来源文件路径
    source_line: int = 0    # 行号
    source_type: str = "code"  # 来源类型（SourceType 的值）

    # 质量指标
    confidence: float = 1.0  # 置信度 (0-1)
    priority: int = 2        # 优先级 (1-4)

    # 元数据
    metadata: Dict = field(default_factory=dict)

    # 关联信息
    related_items: List[str] = field(default_factory=list)  # 关联的知识项 key

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "type": self.type,
            "key": self.key,
            "value": self.value,
            "source_file": self.source_file,
            "source_line": self.source_line,
            "source_type": self.source_type,
            "confidence": self.confidence,
            "priority": self.priority,
            "metadata": self.metadata,
            "related_items": self.related_items,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'KnowledgeItem':
        """从字典创建"""
        return cls(
            type=data.get("type", ""),
            key=data.get("key", ""),
            value=data.get("value"),
            source_file=data.get("source_file", ""),
            source_line=data.get("source_line", 0),
            source_type=data.get("source_type", "code"),
            confidence=data.get("confidence", 1.0),
            priority=data.get("priority", 2),
            metadata=data.get("metadata", {}),
            related_items=data.get("related_items", []),
        )


class BaseExtractor(ABC):
    """提取器基类 - 所有提取器必须实现这个接口"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化提取器

        Args:
            config: 提取器配置
        """
        self.config = config or {}
        self.items: List[KnowledgeItem] = []

    @abstractmethod
    def extract(self, source_dir: str) -> List[KnowledgeItem]:
        """
        从源码目录提取知识

        Args:
            source_dir: 源码目录路径

        Returns:
            提取的知识项列表
        """
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """
        返回该提取器支持的知识类型

        Returns:
            知识类型列表
        """
        pass

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

    def get_summary(self) -> Dict:
        """
        获取提取结果摘要

        Returns:
            摘要字典
        """
        if not self.items:
            return {"total": 0, "by_type": {}}

        by_type = {}
        for item in self.items:
            if item.type not in by_type:
                by_type[item.type] = 0
            by_type[item.type] += 1

        return {
            "total": len(self.items),
            "by_type": by_type,
            "extractor": self.name,
        }

    def filter_by_type(self, knowledge_type: str) -> List[KnowledgeItem]:
        """按类型过滤知识项"""
        return [item for item in self.items if item.type == knowledge_type]

    def filter_by_priority(self, max_priority: int) -> List[KnowledgeItem]:
        """按优先级过滤知识项（返回优先级 <= max_priority 的项）"""
        return [item for item in self.items if item.priority <= max_priority]

    def filter_by_confidence(self, min_confidence: float) -> List[KnowledgeItem]:
        """按置信度过滤知识项（返回置信度 >= min_confidence 的项）"""
        return [item for item in self.items if item.confidence >= min_confidence]


class ExtractorRegistry:
    """提取器注册表 - 管理所有提取器"""

    _extractors: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str):
        """注册提取器的装饰器"""
        def decorator(extractor_class: type):
            cls._extractors[name] = extractor_class
            return extractor_class
        return decorator

    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """获取提取器类"""
        return cls._extractors.get(name)

    @classmethod
    def get_all(cls) -> Dict[str, type]:
        """获取所有提取器"""
        return cls._extractors.copy()

    @classmethod
    def create(cls, name: str, config: Optional[Dict] = None) -> Optional[BaseExtractor]:
        """创建提取器实例"""
        extractor_class = cls.get(name)
        if extractor_class:
            return extractor_class(config)
        return None


def calculate_confidence(
    frequency: int,
    total: int,
    source_type: str = "code",
    consistency: float = 1.0
) -> float:
    """
    计算置信度

    置信度 = 频率权重 * 来源权重 * 一致性权重

    Args:
        frequency: 出现次数
        total: 总数
        source_type: 来源类型
        consistency: 一致性（0-1）

    Returns:
        置信度（0-1）
    """
    # 频率权重
    freq_weight = min(frequency / max(total * 0.1, 1), 1.0)

    # 来源权重
    source_weights = {
        "code": 1.0,
        "config": 0.9,
        "docstring": 0.8,
        "comment": 0.7,
        "inferred": 0.5,
    }
    source_weight = source_weights.get(source_type, 0.5)

    # 计算最终置信度
    confidence = freq_weight * source_weight * consistency

    return round(min(max(confidence, 0.0), 1.0), 3)


def determine_priority(knowledge_type: str) -> int:
    """
    根据知识类型确定优先级

    Args:
        knowledge_type: 知识类型

    Returns:
        优先级（1-4）
    """
    priority_map = {
        # 必须知道
        "directory": 1,
        "service": 1,
        "tech_stack": 1,

        # 开发必备
        "pattern": 2,
        "error_code": 2,
        "api": 2,
        "model": 2,

        # 深入了解
        "constant": 3,
        "config": 3,
        "flow": 3,
        "log": 3,

        # 进阶知识
        "dependency": 4,
        "term": 4,
        "design": 4,
    }

    return priority_map.get(knowledge_type, 3)
