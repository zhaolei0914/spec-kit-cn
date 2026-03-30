# -*- coding: utf-8 -*-
"""
智能 Skill 演化中心 - Skill 数据结构定义

基于 MCP (Model Context Protocol) 协议设计的 Skill 描述格式
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum
import json
import hashlib
from datetime import datetime


class SkillType(Enum):
    """Skill 类型"""
    PATTERN = "pattern"           # 代码模式（如继承、装饰器）
    CONVENTION = "convention"     # 命名约定
    RULE = "rule"                 # 强制规则
    GUIDELINE = "guideline"       # 建议性指南
    TEMPLATE = "template"         # 代码模板


class SkillSource(Enum):
    """Skill 来源"""
    AST_ANALYSIS = "ast_analysis"     # AST 静态分析
    GIT_MR = "git_mr"                 # Git MR 分析
    DOCUMENT = "document"             # 文档提取
    MANUAL = "manual"                 # 人工定义
    FEEDBACK = "feedback"             # 反馈学习


@dataclass
class SkillParameter:
    """Skill 参数定义"""
    name: str                          # 参数名
    type: str                          # 参数类型
    description: str                   # 参数描述
    required: bool = True              # 是否必需
    default: Any = None                # 默认值
    enum: List[str] = field(default_factory=list)  # 枚举值


@dataclass
class SkillExample:
    """Skill 使用示例"""
    title: str                         # 示例标题
    code: str                          # 示例代码
    file_path: str = ""                # 来源文件
    line_start: int = 0                # 起始行
    description: str = ""              # 示例说明
    is_positive: bool = True           # 是否正例（False 为反例）


@dataclass
class SkillMetadata:
    """Skill 元数据"""
    created_at: str = ""               # 创建时间
    updated_at: str = ""               # 更新时间
    version: str = "1.0.0"             # 版本号
    source: str = "ast_analysis"       # 来源
    confidence: float = 0.0            # 置信度
    occurrences: int = 0               # 出现次数
    acceptance_rate: float = 1.0       # 接受率（用于反馈闭环）
    tags: List[str] = field(default_factory=list)  # 标签


@dataclass
class Skill:
    """
    Skill 定义 - MCP Tool 格式

    遵循 MCP 协议的 Tool 定义规范
    """
    # MCP Tool 必需字段
    name: str                          # Skill 名称（唯一标识）
    description: str                   # Skill 描述

    # MCP Tool 可选字段
    parameters: List[SkillParameter] = field(default_factory=list)  # 输入参数

    # Skill 扩展字段
    skill_type: str = "pattern"        # Skill 类型
    category: str = ""                 # 分类（models, web, service 等）
    language: str = "python"           # 适用语言

    # 示例和上下文
    examples: List[SkillExample] = field(default_factory=list)  # 代码示例
    context_patterns: List[str] = field(default_factory=list)   # 适用上下文模式

    # 元数据
    metadata: SkillMetadata = field(default_factory=SkillMetadata)

    def __post_init__(self):
        """初始化后处理"""
        if not self.metadata.created_at:
            self.metadata.created_at = datetime.now().isoformat()
        if not self.metadata.updated_at:
            self.metadata.updated_at = self.metadata.created_at

    def get_id(self) -> str:
        """生成唯一 ID"""
        content = f"{self.name}:{self.category}:{self.language}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def to_mcp_tool(self) -> Dict:
        """
        转换为 MCP Tool 格式

        符合 MCP 协议的 tools/list 响应格式
        """
        properties = {}
        required = []

        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            if param.default is not None:
                prop["default"] = param.default
            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.get_id(),
            "name": self.name,
            "description": self.description,
            "skill_type": self.skill_type,
            "category": self.category,
            "language": self.language,
            "parameters": [asdict(p) for p in self.parameters],
            "examples": [asdict(e) for e in self.examples],
            "context_patterns": self.context_patterns,
            "metadata": asdict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Skill':
        """从字典创建"""
        parameters = [SkillParameter(**p) for p in data.get('parameters', [])]
        examples = [SkillExample(**e) for e in data.get('examples', [])]
        metadata = SkillMetadata(**data.get('metadata', {}))

        return cls(
            name=data['name'],
            description=data['description'],
            skill_type=data.get('skill_type', 'pattern'),
            category=data.get('category', ''),
            language=data.get('language', 'python'),
            parameters=parameters,
            examples=examples,
            context_patterns=data.get('context_patterns', []),
            metadata=metadata,
        )

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Skill':
        """从 JSON 字符串创建"""
        return cls.from_dict(json.loads(json_str))

    def get_embedding_text(self) -> str:
        """
        获取用于向量化的文本

        用于 Skill-RAG 的语义检索
        """
        parts = [
            f"Skill: {self.name}",
            f"Description: {self.description}",
            f"Category: {self.category}",
            f"Type: {self.skill_type}",
        ]

        if self.context_patterns:
            parts.append(f"Context: {', '.join(self.context_patterns)}")

        if self.examples:
            parts.append("Examples:")
            for ex in self.examples[:3]:
                parts.append(f"  - {ex.title}: {ex.description}")

        return "\n".join(parts)


def save_skills(skills: List[Skill], output_path: str):
    """保存 Skill 列表到 JSON 文件"""
    data = [skill.to_dict() for skill in skills]
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_skills(input_path: str) -> List[Skill]:
    """从 JSON 文件加载 Skill 列表"""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [Skill.from_dict(item) for item in data]
