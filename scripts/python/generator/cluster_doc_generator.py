# -*- coding: utf-8 -*-
"""
通用聚类文档生成器

从骨架数据的聚类信息动态生成规范文档，消除硬编码
"""
import os
from typing import List, Dict, Optional, Tuple
from collections import defaultdict


class ClusterDocGenerator:
    """通用的聚类文档生成器"""

    # 模式类型标题映射
    PATTERN_TYPE_TITLES = {
        'inheritance': '继承模式',
        'decorator': '装饰器模式',
        'naming': '命名模式',
        'structure': '结构模式',
        'param': '参数模式',
        'file': '文件组织模式',
        'import': '导入模式',
        'exception': '异常处理模式',
        'logging': '日志模式',
        'docstring': '文档字符串模式',
        'return_type': '返回类型模式',
    }

    # 聚类标题映射
    CLUSTER_TITLES = {
        'models': '数据模型规范',
        'web': 'Web 接口规范',
        'service': '服务层规范',
        'error': '错误处理规范',
        'config': '配置规范',
        'handler': '处理器规范',
        'test': '测试规范',
        'naming': '命名规范',
        'constants': '常量定义规范',
        'common': '公共库规范',
        'other': '其他规范',
    }

    def __init__(self, skeleton: Dict, source_root: str = ''):
        """
        初始化生成器

        参数:
            skeleton: 骨架数据
            source_root: 源代码根目录（用于读取代码示例）
        """
        self.skeleton = skeleton
        self.source_root = source_root

    def generate_cluster_doc(self, cluster_name: str) -> str:
        """
        从聚类数据生成文档

        参数:
            cluster_name: 聚类名称

        返回: Markdown 格式的文档
        """
        cluster = self.skeleton.get('clusters', {}).get(cluster_name, {})
        patterns = cluster.get('patterns', [])
        examples = cluster.get('examples', [])

        title = self.CLUSTER_TITLES.get(cluster_name, f'{cluster_name.title()} 规范')

        doc = f"# {title}\n\n"
        doc += "## 概述\n\n"
        doc += f"本文档描述了项目中 {title.lower()} 相关的代码模式和规范。\n\n"

        # 1. 生成模式表格
        if patterns:
            doc += self._generate_pattern_tables(patterns)

        # 2. 生成代码示例
        if examples:
            doc += self._generate_examples_section(cluster_name, examples)

        # 3. 生成使用建议
        doc += self._generate_recommendations(cluster_name, patterns)

        return doc

    def _generate_pattern_tables(self, patterns: List[Dict]) -> str:
        """根据模式类型生成表格"""
        # 按类型分组
        by_type = defaultdict(list)
        for p in patterns:
            pt = p.get('type', 'other')
            by_type[pt].append(p)

        result = ""
        for pt, items in by_type.items():
            type_title = self.PATTERN_TYPE_TITLES.get(pt, pt.title())
            result += f"## {type_title}\n\n"
            result += "| 模式 | 出现次数 | 置信度 |\n"
            result += "|------|----------|--------|\n"

            # 按出现次数排序，取前 10 个
            sorted_items = sorted(items, key=lambda x: x.get('count', 0), reverse=True)
            for item in sorted_items[:10]:
                key = item.get('key', '')
                count = item.get('count', 0)
                confidence = item.get('confidence', 0)
                result += f"| `{key}` | {count} | {confidence:.1%} |\n"

            result += "\n"

        return result

    def _generate_examples_section(self, cluster_name: str, examples: List[Dict]) -> str:
        """生成代码示例部分"""
        result = "## 代码示例（来自项目代码）\n\n"

        # 按服务分组
        grouped = self._group_examples_by_service(examples)

        for service, service_examples in grouped.items():
            result += f"### {service}\n\n"

            # 每个服务最多展示 2 个示例
            for ex in service_examples[:2]:
                code = self._extract_code(ex)
                if code:
                    result += f"**{ex.get('name', '')}** (`{ex.get('file', '')}:{ex.get('line', 0)}`)\n\n"
                    result += f"```python\n{code}\n```\n\n"

        return result

    def _group_examples_by_service(self, examples: List[Dict]) -> Dict[str, List[Dict]]:
        """按服务分组示例"""
        grouped = defaultdict(list)

        for ex in examples:
            file_path = ex.get('file', '')
            # 从文件路径提取服务名
            service = self._extract_service_name(file_path)
            grouped[service].append(ex)

        return dict(grouped)

    def _extract_service_name(self, file_path: str) -> str:
        """从文件路径提取服务名"""
        parts = file_path.replace('\\', '/').split('/')

        # 查找 src 目录后的第一个目录
        for i, part in enumerate(parts):
            if part == 'src' and i + 1 < len(parts):
                return parts[i + 1]

        # 查找包含 Service 的目录
        for part in parts:
            if 'Service' in part:
                return part

        # 返回第一个有意义的目录名
        for part in parts:
            if part and not part.startswith('.') and part not in ('..', 'src'):
                return part

        return 'other'

    def _extract_code(self, example: Dict) -> Optional[str]:
        """从源文件提取代码"""
        file_path = example.get('file', '')
        line = example.get('line', 0)

        if not file_path or not line:
            return None

        # 尝试多个可能的路径
        project_root = os.path.abspath(os.path.join(self.source_root, '..', '..', '..'))
        possible_paths = [
            file_path,
            os.path.join(project_root, file_path),
            os.path.join(self.source_root, '..', '..', '..', file_path),
        ]

        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                try:
                    return self._read_code_block(abs_path, line, example.get('type', 'function'))
                except Exception:
                    continue

        return None

    def _read_code_block(self, file_path: str, start_line: int,
                         unit_type: str, max_lines: int = 30) -> Optional[str]:
        """读取代码块"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            return None

        if start_line < 1 or start_line > len(lines):
            return None

        # 从起始行开始读取
        start_idx = start_line - 1
        result_lines = []
        base_indent = None

        for i in range(start_idx, min(start_idx + max_lines, len(lines))):
            line = lines[i]
            stripped = line.lstrip()

            # 确定基础缩进
            if base_indent is None and stripped:
                base_indent = len(line) - len(stripped)

            # 检测代码块结束
            if i > start_idx and stripped and not line.startswith(' ' * (base_indent + 1)):
                # 新的顶级定义，停止
                if stripped.startswith(('class ', 'def ', 'async def ', '@')):
                    if len(line) - len(stripped) <= base_indent:
                        break

            result_lines.append(line.rstrip())

            # 对于类，限制行数
            if unit_type == 'class' and len(result_lines) > 20:
                # 找到合适的截断点
                break

        # 移除尾部空行
        while result_lines and not result_lines[-1].strip():
            result_lines.pop()

        return '\n'.join(result_lines) if result_lines else None

    def _generate_recommendations(self, cluster_name: str, patterns: List[Dict]) -> str:
        """生成使用建议"""
        result = "## 使用规范\n\n"

        # 从高频模式生成建议
        high_freq = [p for p in patterns if p.get('count', 0) >= 5]

        if high_freq:
            result += "### 推荐的模式\n\n"
            for p in sorted(high_freq, key=lambda x: x.get('count', 0), reverse=True)[:5]:
                key = p.get('key', '')
                count = p.get('count', 0)
                confidence = p.get('confidence', 0)
                result += f"- **{key}**: 出现 {count} 次，置信度 {confidence:.1%}\n"
            result += "\n"

        # 根据聚类类型添加特定建议
        cluster_recommendations = {
            'models': [
                "- 所有模型应继承项目的基类",
                "- 使用一致的字段命名规范",
                "- 为模型添加文档字符串",
            ],
            'web': [
                "- 使用项目统一的装饰器组合",
                "- 遵循统一的响应格式",
                "- 添加适当的错误处理",
            ],
            'service': [
                "- 使用事务管理确保数据一致性",
                "- 添加适当的日志记录",
                "- 遵循单一职责原则",
            ],
            'error': [
                "- 使用项目统一的错误码定义",
                "- 禁止裸 except，必须指定异常类型",
                "- 错误信息应支持国际化",
            ],
            'handler': [
                "- Handler 应继承项目的基类",
                "- 添加适当的日志记录",
                "- 处理异常并记录错误",
            ],
            'test': [
                "- 测试类应继承 TestCase 或项目基类",
                "- 测试方法以 test_ 开头",
                "- 使用 setUp/tearDown 管理测试状态",
            ],
            'constants': [
                "- 使用枚举类定义常量",
                "- 禁止使用魔法数字",
                "- 常量名使用大写下划线格式",
            ],
        }

        if cluster_name in cluster_recommendations:
            result += "### 开发建议\n\n"
            for rec in cluster_recommendations[cluster_name]:
                result += f"{rec}\n"
            result += "\n"

        return result


def generate_cluster_doc(skeleton: Dict, cluster_name: str, source_root: str = '') -> str:
    """生成聚类文档的便捷函数"""
    generator = ClusterDocGenerator(skeleton, source_root)
    return generator.generate_cluster_doc(cluster_name)
