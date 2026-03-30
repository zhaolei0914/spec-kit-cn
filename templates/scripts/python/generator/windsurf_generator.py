# -*- coding: utf-8 -*-
"""
Windsurf IDE 集成生成器

生成 Windsurf IDE 所需的配置文件
"""
import os
from typing import Dict, List, Optional
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extractor.libcst.knowledge_base import KnowledgeBase


class WindsurfGenerator:
    """Windsurf 集成生成器"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化生成器

        Args:
            config: 配置选项
        """
        self.config = config or {}
        self.project_root = self.config.get('project_root', '.')

    def generate_all(
        self,
        kb: KnowledgeBase,
        skills_dir: str,
        project_root: Optional[str] = None
    ) -> Dict[str, str]:
        """
        生成所有 Windsurf 集成文件

        Args:
            kb: 知识库
            skills_dir: Skill 目录
            project_root: 项目根目录

        Returns:
            生成的文件路径字典
        """
        project_root = project_root or self.project_root
        generated_files = {}

        # 生成 .windsurfrules
        rules_path = os.path.join(project_root, '.windsurfrules')
        content = self.generate_windsurfrules(kb, skills_dir)
        self._write_file(rules_path, content)
        generated_files['.windsurfrules'] = rules_path

        # 生成 windsurf_rules.md
        ide_dir = os.path.join(project_root, '.specify', 'ide')
        os.makedirs(ide_dir, exist_ok=True)
        rules_md_path = os.path.join(ide_dir, 'windsurf_rules.md')
        content = self.generate_windsurf_rules_md(kb, skills_dir)
        self._write_file(rules_md_path, content)
        generated_files['windsurf_rules.md'] = rules_md_path

        # 生成 constitution.md
        memory_dir = os.path.join(project_root, '.specify', 'memory')
        os.makedirs(memory_dir, exist_ok=True)
        constitution_path = os.path.join(memory_dir, 'constitution.md')
        content = self.generate_constitution(kb)
        self._write_file(constitution_path, content)
        generated_files['constitution.md'] = constitution_path

        return generated_files

    def generate_windsurfrules(self, kb: KnowledgeBase, skills_dir: str) -> str:
        """生成 .windsurfrules 文件"""
        lines = [
            f"# {kb.project_name} 项目规则",
            "",
            "## 开发前置（强制）",
            "",
            "进行代码开发前，**必须**按以下顺序读取项目规范：",
            "",
            f"1. **读取项目概述**：`{skills_dir}/SKILL.md`",
            "2. **根据任务类型读取对应规范**：",
        ]

        # 添加任务类型映射
        task_mappings = [
            ("开发 API 接口", "web.md"),
            ("定义数据模型", "models.md"),
            ("编写业务逻辑", "service.md"),
            ("后台任务处理", "handler.md"),
            ("定义错误码", "error.md"),
            ("定义常量枚举", "constants.md"),
            ("使用公共库", "common.md"),
            ("配置文件", "config.md"),
        ]

        for task, skill_file in task_mappings:
            lines.append(f"   - {task} → `{skill_file}`")

        lines.extend([
            "",
            "## 开发检查",
            "",
        ])

        # 根据知识库生成检查项
        checks = self._generate_checks(kb)
        for check in checks:
            lines.append(f"- {check}")

        lines.append("")

        return "\n".join(lines)

    def generate_windsurf_rules_md(self, kb: KnowledgeBase, skills_dir: str) -> str:
        """生成 windsurf_rules.md 文件"""
        lines = [
            f"# {kb.project_name} IDE 规则",
            "",
            f"**生成时间**: {datetime.now().isoformat()}",
            "",
            "## 项目概述",
            "",
            f"- **项目名称**: {kb.project_name}",
            f"- **Python 文件数**: {kb.statistics.get('file_count', 0)}",
            f"- **类定义数**: {kb.statistics.get('class_count', 0)}",
            f"- **函数定义数**: {kb.statistics.get('function_count', 0)}",
            "",
            "## Skill 文件位置",
            "",
            f"所有 Skill 文件位于 `{skills_dir}/` 目录下。",
            "",
            "## 开发规范摘要",
            "",
        ]

        # 添加装饰器规范
        top_decorators = kb.statistics.get('top_decorators', [])
        if top_decorators:
            lines.append("### 常用装饰器")
            lines.append("")
            for dec in top_decorators[:5]:
                lines.append(f"- `@{dec['name']}` ({dec['count']} 次使用)")
            lines.append("")

        # 添加基类规范
        top_bases = kb.statistics.get('top_base_classes', [])
        if top_bases:
            lines.append("### 常用基类")
            lines.append("")
            for base in top_bases[:5]:
                lines.append(f"- `{base['name']}` ({base['count']} 次继承)")
            lines.append("")

        return "\n".join(lines)

    def generate_constitution(self, kb: KnowledgeBase) -> str:
        """生成 constitution.md 项目章程"""
        lines = [
            f"# {kb.project_name} 项目章程",
            "",
            f"**生成时间**: {datetime.now().isoformat()}",
            "",
            "## 项目背景",
            "",
            f"本项目包含 {kb.statistics.get('file_count', 0)} 个 Python 文件，",
            f"定义了 {kb.statistics.get('class_count', 0)} 个类和 {kb.statistics.get('function_count', 0)} 个函数。",
            "",
        ]

        # Django 特定信息
        django_stats = kb.statistics.get('django', {})
        if any(django_stats.values()):
            lines.extend([
                "## Django 项目结构",
                "",
                f"- **模型数量**: {django_stats.get('model_count', 0)}",
                f"- **视图数量**: {django_stats.get('view_count', 0)}",
                f"- **URL 路由数**: {django_stats.get('url_count', 0)}",
                f"- **中间件数**: {django_stats.get('middleware_count', 0)}",
                "",
            ])

        # 技术栈
        top_imports = kb.statistics.get('top_imports', [])
        if top_imports:
            lines.extend([
                "## 技术栈",
                "",
            ])
            for imp in top_imports[:10]:
                lines.append(f"- {imp['name']}")
            lines.append("")

        # 核心原则
        lines.extend([
            "## 核心原则",
            "",
            "1. **代码规范**: 遵循项目现有的代码风格和模式",
            "2. **文档完整**: 所有公共 API 必须有文档字符串",
            "3. **测试覆盖**: 新功能必须有对应的测试用例",
            "4. **错误处理**: 使用项目定义的异常类",
            "",
        ])

        return "\n".join(lines)

    def _generate_checks(self, kb: KnowledgeBase) -> List[str]:
        """根据知识库生成检查项"""
        checks = []

        # 基于装饰器模式生成检查项
        top_decorators = kb.statistics.get('top_decorators', [])
        decorator_names = [d['name'] for d in top_decorators[:5]]

        if 'formatting' in decorator_names:
            checks.append("新增 API 必须使用 `@formatting()` 装饰器")
        if 'authenticated' in decorator_names:
            checks.append("需要认证的接口必须使用 `@authenticated()` 装饰器")

        # 基于基类模式生成检查项
        top_bases = kb.statistics.get('top_base_classes', [])
        base_names = [b['name'] for b in top_bases[:5]]

        if any('Model' in b for b in base_names):
            checks.append("新增模型必须继承正确的基类")
        if any('View' in b for b in base_names):
            checks.append("新增视图必须继承正确的视图基类")

        # 通用检查项
        checks.extend([
            "代码必须符合对应规范文件的要求",
            "禁止使用 `print()`，使用 `logger`",
            "禁止裸 `except:`，必须指定异常类型",
        ])

        return checks

    def _write_file(self, path: str, content: str) -> None:
        """写入文件"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
