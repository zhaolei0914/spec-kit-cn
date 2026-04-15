# -*- coding: utf-8 -*-
"""
智能 Skill 演化中心 - 模式到 Skill 转换器

将代码模式 (CodePattern) 转换为 MCP Skill
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Optional
from parser.base import CodePattern, CodeUnit
from .skill_schema import Skill, SkillParameter, SkillExample, SkillMetadata


class SkillConverter:
    """模式到 Skill 转换器"""

    def __init__(self):
        self.category_mapping = {
            'inheritance': 'models',
            'decorator': 'web',
            'naming': 'convention',
            'structure': 'architecture',
            'param': 'interface',
            'file': 'structure',
        }

        self.skill_type_mapping = {
            'inheritance': 'pattern',
            'decorator': 'pattern',
            'naming': 'convention',
            'structure': 'guideline',
            'param': 'convention',
            'file': 'guideline',
        }

    def convert_pattern(self, pattern: CodePattern) -> Skill:
        """
        将单个 CodePattern 转换为 Skill

        Args:
            pattern: 代码模式

        Returns:
            Skill 对象
        """
        # 生成 Skill 名称
        name = self._generate_skill_name(pattern)

        # 生成描述
        description = self._generate_description(pattern)

        # 确定分类
        category = self._determine_category(pattern)

        # 确定类型
        skill_type = self.skill_type_mapping.get(pattern.pattern_type, 'pattern')

        # 转换示例
        examples = self._convert_examples(pattern.examples)

        # 生成上下文模式
        context_patterns = self._generate_context_patterns(pattern)

        # 生成参数（如果适用）
        parameters = self._generate_parameters(pattern)

        # 创建元数据
        metadata = SkillMetadata(
            source='ast_analysis',
            confidence=pattern.confidence,
            occurrences=pattern.occurrences,
            tags=self._generate_tags(pattern),
        )

        return Skill(
            name=name,
            description=description,
            skill_type=skill_type,
            category=category,
            language='python',
            parameters=parameters,
            examples=examples,
            context_patterns=context_patterns,
            metadata=metadata,
        )

    def convert_patterns(self, patterns: List[CodePattern],
                         min_confidence: float = 0.05,
                         min_occurrences: int = 3) -> List[Skill]:
        """
        批量转换模式为 Skill

        Args:
            patterns: 代码模式列表
            min_confidence: 最小置信度
            min_occurrences: 最小出现次数

        Returns:
            Skill 列表
        """
        skills = []

        for pattern in patterns:
            # 过滤低质量模式
            if pattern.confidence < min_confidence:
                continue
            if pattern.occurrences < min_occurrences:
                continue

            skill = self.convert_pattern(pattern)
            skills.append(skill)

        return skills

    def _generate_skill_name(self, pattern: CodePattern) -> str:
        """生成 Skill 名称"""
        key = pattern.pattern_key

        # 处理不同类型的模式
        if key.startswith('extends:'):
            base = key.replace('extends:', '')
            return f"use_{base.lower()}_base"
        elif key.startswith('@'):
            decorator = key.replace('@', '').replace('class:', '')
            return f"apply_{decorator.lower()}_decorator"
        elif key.startswith('prefix:'):
            prefix = key.replace('prefix:', '')
            return f"naming_prefix_{prefix.rstrip('_')}"
        elif key.startswith('suffix:'):
            suffix = key.replace('suffix:', '')
            return f"naming_suffix_{suffix.lower()}"
        elif key.startswith('combo:'):
            combo = key.replace('combo:', '').replace('@', '').replace(' + ', '_')
            return f"decorator_combo_{combo.lower()}"
        elif key.startswith('param:'):
            param = key.replace('param:', '')
            return f"param_convention_{param}"
        elif key.startswith('file:'):
            file_type = key.replace('file:', '')
            return f"file_organization_{file_type}"
        else:
            # 默认处理
            return f"skill_{key.lower().replace('.', '_').replace(' ', '_')}"

    def _generate_description(self, pattern: CodePattern) -> str:
        """生成 Skill 描述"""
        key = pattern.pattern_key

        if key.startswith('extends:'):
            base = key.replace('extends:', '')
            return f"所有相关类必须继承 {base} 基类。该模式在项目中出现 {pattern.occurrences} 次，置信度 {pattern.confidence:.1%}。"
        elif key.startswith('@'):
            decorator = key.replace('@', '').replace('class:', '')
            return f"使用 @{decorator} 装饰器。该模式在项目中出现 {pattern.occurrences} 次。"
        elif key.startswith('prefix:'):
            prefix = key.replace('prefix:', '')
            return f"函数命名应以 '{prefix}' 开头。这是项目的命名约定。"
        elif key.startswith('suffix:'):
            suffix = key.replace('suffix:', '')
            return f"类命名应以 '{suffix}' 结尾。这是项目的命名约定。"
        elif key.startswith('combo:'):
            combo = key.replace('combo:', '')
            return f"使用装饰器组合 {combo}。这是项目的标准模式。"
        elif key.startswith('param:'):
            param = key.replace('param:', '')
            return f"常用参数名 '{param}'。在项目中广泛使用。"
        else:
            return pattern.description or f"代码模式: {key}"

    def _determine_category(self, pattern: CodePattern) -> str:
        """确定 Skill 分类"""
        key = pattern.pattern_key.lower()

        # 根据关键词判断
        if 'model' in key or 'basemodel' in key:
            return 'models'
        elif 'view' in key or 'formatting' in key or 'authenticated' in key:
            return 'web'
        elif 'service' in key or 'transaction' in key:
            return 'service'
        elif 'exception' in key or 'error' in key:
            return 'error'
        elif 'handler' in key or 'worker' in key:
            return 'handler'
        elif 'test' in key:
            return 'test'
        elif 'config' in key:
            return 'config'
        else:
            return self.category_mapping.get(pattern.pattern_type, 'other')

    def _convert_examples(self, units: List[CodeUnit]) -> List[SkillExample]:
        """转换代码示例"""
        examples = []

        for unit in units[:3]:  # 最多 3 个示例
            # 生成示例代码
            if unit.type == 'class':
                decorators = ''.join(f"@{d}\n" for d in unit.decorators)
                bases = ', '.join(unit.bases) if unit.bases else ''
                code = f"{decorators}class {unit.name}({bases}):\n    ..."
            else:
                decorators = ''.join(f"@{d}\n" for d in unit.decorators)
                params = ', '.join(unit.params[:5])
                if len(unit.params) > 5:
                    params += ', ...'
                code = f"{decorators}def {unit.name}({params}):\n    ..."

            examples.append(SkillExample(
                title=unit.name,
                code=code,
                file_path=unit.file_path,
                line_start=unit.line_start,
                description=unit.docstring[:100] if unit.docstring else '',
                is_positive=True,
            ))

        return examples

    def _generate_context_patterns(self, pattern: CodePattern) -> List[str]:
        """生成上下文模式（用于语义匹配）"""
        contexts = []
        key = pattern.pattern_key

        if 'model' in key.lower():
            contexts.extend(['定义数据模型', '创建数据库表', 'Django Model'])
        elif 'view' in key.lower():
            contexts.extend(['处理 HTTP 请求', '定义 API 接口', 'Web 视图'])
        elif 'service' in key.lower():
            contexts.extend(['业务逻辑', '服务层', '事务处理'])
        elif 'formatting' in key.lower():
            contexts.extend(['API 响应格式化', '统一响应格式'])
        elif 'authenticated' in key.lower():
            contexts.extend(['用户认证', '权限验证', '登录检查'])
        elif 'exception' in key.lower() or 'error' in key.lower():
            contexts.extend(['错误处理', '异常定义', '错误码'])

        # 添加通用上下文
        if pattern.examples:
            for ex in pattern.examples[:2]:
                if ex.file_path:
                    # 从文件路径提取上下文
                    path_parts = ex.file_path.split('/')
                    for part in path_parts:
                        if part in ['web', 'service', 'models', 'handler', 'common']:
                            contexts.append(f"在 {part} 目录下")

        return list(set(contexts))

    def _generate_parameters(self, pattern: CodePattern) -> List[SkillParameter]:
        """生成 Skill 参数"""
        params = []
        key = pattern.pattern_key

        if key.startswith('extends:'):
            base = key.replace('extends:', '')
            params.append(SkillParameter(
                name='class_name',
                type='string',
                description='要创建的类名',
                required=True,
            ))
            params.append(SkillParameter(
                name='base_class',
                type='string',
                description='基类名称',
                required=False,
                default=base,
            ))
        elif key.startswith('@'):
            decorator = key.replace('@', '').replace('class:', '')
            params.append(SkillParameter(
                name='decorator',
                type='string',
                description='装饰器名称',
                required=False,
                default=decorator,
            ))

        return params

    def _generate_tags(self, pattern: CodePattern) -> List[str]:
        """生成标签"""
        tags = [pattern.pattern_type]
        key = pattern.pattern_key.lower()

        if 'model' in key:
            tags.append('model')
        if 'view' in key:
            tags.append('view')
        if 'service' in key:
            tags.append('service')
        if 'decorator' in key or key.startswith('@'):
            tags.append('decorator')
        if 'naming' in pattern.pattern_type:
            tags.append('naming')

        return tags


def convert_patterns_to_skills(patterns_file: str, output_file: str,
                               min_confidence: float = 0.05,
                               min_occurrences: int = 3):
    """
    将模式文件转换为 Skill 文件

    Args:
        patterns_file: 模式 JSON 文件路径
        output_file: 输出 Skill JSON 文件路径
        min_confidence: 最小置信度
        min_occurrences: 最小出现次数
    """
    from parser.base import load_patterns
    from .skill_schema import save_skills

    patterns = load_patterns(patterns_file)
    converter = SkillConverter()
    skills = converter.convert_patterns(patterns, min_confidence, min_occurrences)
    save_skills(skills, output_file)

    print(f"转换完成: {len(patterns)} 个模式 -> {len(skills)} 个 Skill")
    return skills
