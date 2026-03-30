# -*- coding: utf-8 -*-
"""
骨架数据生成器

生成项目的结构化骨架数据（JSON），供 AI 生成规范文档
"""
import os
import sys
import json
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.base import CodeUnit, CodePattern


# 默认聚类规则（当配置文件不存在时使用）
DEFAULT_CLUSTER_RULES = {
    'models': ['Model', 'BaseModel', 'models', 'Entity'],
    'web': ['View', 'formatting', 'authenticated', 'route', 'api'],
    'service': ['Service', 'transaction', 'atomic', 'Manager'],
    'error': ['Exception', 'Error', 'errorcode'],
    'config': ['config', 'settings', 'Config', 'appconfig'],
    'handler': ['Handler', 'Worker', 'Processor'],
    'test': ['test', 'Test', 'mock'],
    'common': ['Common', 'utils', 'func', 'thrift', 'etcd', 'i18n'],
    'constants': ['constants', 'CHOICES', 'Status', 'Type', 'Level'],
}


def load_cluster_rules(config_path: str = None) -> Dict[str, List[str]]:
    """从配置文件加载聚类规则"""
    if config_path is None:
        # 默认配置路径 - 先尝试 scripts/python/config，再尝试 .specify/config
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(script_dir, 'config', 'clusters.yaml')

        if not os.path.exists(config_path):
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'config', 'clusters.yaml'
            )

    if not os.path.exists(config_path):
        return DEFAULT_CLUSTER_RULES

    if not HAS_YAML:
        print(f"警告: 未安装 PyYAML，使用默认聚类规则")
        return DEFAULT_CLUSTER_RULES

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        if rules and isinstance(rules, dict):
            # 支持两种格式:
            # 1. 简单格式: cluster_name: [keywords]
            # 2. 扩展格式: cluster_name: {keywords: [...], description: ...}
            result = {}
            for cluster_name, value in rules.items():
                if isinstance(value, list):
                    result[cluster_name] = value
                elif isinstance(value, dict) and 'keywords' in value:
                    result[cluster_name] = value['keywords']
                else:
                    result[cluster_name] = []
            return result if result else DEFAULT_CLUSTER_RULES
    except Exception as e:
        print(f"警告: 加载聚类配置失败 ({e})，使用默认规则")

    return DEFAULT_CLUSTER_RULES


class SkeletonGenerator:
    """骨架数据生成器"""

    def __init__(self, config_path: str = None):
        self.cluster_rules = load_cluster_rules(config_path)

    def generate(self, units: List[CodeUnit], patterns: List[CodePattern],
                 source_dir: str, entries_summary: Dict = None,
                 antipatterns: List = None) -> Dict[str, Any]:
        """生成骨架数据"""

        # 1. 项目基本信息
        project_info = self._detect_project_info(source_dir, units)

        # 2. 聚类模式
        clusters = self._cluster_patterns(patterns)

        # 3. 代码单元统计
        unit_stats = self._analyze_units(units)

        # 4. 入口信息
        entries = entries_summary or {}

        # 5. 反模式
        antipattern_summary = self._summarize_antipatterns(antipatterns) if antipatterns else {}

        # 6. 目录结构
        dir_structure = self._analyze_directory(source_dir)

        skeleton = {
            "generated_at": datetime.now().isoformat(),
            "project": project_info,
            "directory_structure": dir_structure,
            "unit_statistics": unit_stats,
            "clusters": clusters,
            "entries": entries,
            "antipatterns": antipattern_summary,
        }

        return skeleton

    def _detect_project_info(self, source_dir: str, units: List[CodeUnit]) -> Dict:
        """检测项目信息"""
        # 检测语言
        language = "Python"  # 当前只支持 Python

        # 检测框架
        framework = self._detect_framework(units)

        # 检测项目名称
        project_name = os.path.basename(os.path.dirname(source_dir))
        if project_name in ('src', 'source', 'app'):
            project_name = os.path.basename(os.path.dirname(os.path.dirname(source_dir)))

        # 检测服务模块
        services = self._detect_services(source_dir)

        return {
            "name": project_name,
            "language": language,
            "framework": framework,
            "services": services,
            "source_dir": source_dir,
        }

    def _detect_framework(self, units: List[CodeUnit]) -> Dict:
        """检测使用的框架"""
        frameworks = {
            "django": False,
            "flask": False,
            "fastapi": False,
            "thrift": False,
            "sqlalchemy": False,
        }

        for unit in units:
            # 检查基类
            for base in unit.bases:
                if 'View' in base or 'Model' in base:
                    frameworks["django"] = True
                if 'Flask' in base:
                    frameworks["flask"] = True
                if 'Base' in base and 'Model' not in base:
                    frameworks["sqlalchemy"] = True

            # 检查装饰器
            for dec in unit.decorators:
                if 'app.route' in dec or 'router' in dec:
                    frameworks["fastapi"] = True

            # 检查文件路径
            if 'Thrift' in unit.file_path:
                frameworks["thrift"] = True

        detected = [k for k, v in frameworks.items() if v]
        return {
            "detected": detected,
            "primary": detected[0] if detected else "unknown",
        }

    def _detect_services(self, source_dir: str) -> List[Dict]:
        """检测服务模块"""
        services = []

        for item in os.listdir(source_dir):
            item_path = os.path.join(source_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.') and not item.startswith('_'):
                # 检查是否是服务目录
                has_models = os.path.exists(os.path.join(item_path, 'models.py'))
                has_web = os.path.exists(os.path.join(item_path, 'web'))
                has_service = os.path.exists(os.path.join(item_path, 'service'))

                if has_models or has_web or has_service:
                    services.append({
                        "name": item,
                        "path": item_path,
                        "has_models": has_models,
                        "has_web": has_web,
                        "has_service": has_service,
                    })

        return services

    def _cluster_patterns(self, patterns: List[CodePattern]) -> Dict[str, Dict]:
        """聚类模式"""
        clusters = defaultdict(lambda: {"patterns": [], "examples": []})
        unclustered = []

        for pattern in patterns:
            clustered = False
            key_lower = pattern.pattern_key.lower()

            for cluster_name, keywords in self.cluster_rules.items():
                for keyword in keywords:
                    if keyword.lower() in key_lower:
                        clusters[cluster_name]["patterns"].append({
                            "type": pattern.pattern_type,
                            "key": pattern.pattern_key,
                            "count": pattern.occurrences,
                            "confidence": round(pattern.confidence, 3),
                            "description": pattern.description,
                        })
                        # 添加示例
                        for ex in pattern.examples[:2]:
                            clusters[cluster_name]["examples"].append({
                                "name": ex.name,
                                "type": ex.type,
                                "file": ex.file_path,
                                "line": ex.line_start,
                                "bases": ex.bases,
                                "decorators": ex.decorators,
                                "docstring": ex.docstring[:100] if ex.docstring else "",
                            })
                        clustered = True
                        break
                if clustered:
                    break

            if not clustered:
                if pattern.pattern_type == 'naming':
                    clusters['naming']["patterns"].append({
                        "type": pattern.pattern_type,
                        "key": pattern.pattern_key,
                        "count": pattern.occurrences,
                        "confidence": round(pattern.confidence, 3),
                    })
                else:
                    unclustered.append({
                        "type": pattern.pattern_type,
                        "key": pattern.pattern_key,
                        "count": pattern.occurrences,
                    })

        if unclustered:
            clusters['other']["patterns"] = unclustered

        # 按出现次数排序
        for cluster_name in clusters:
            clusters[cluster_name]["patterns"] = sorted(
                clusters[cluster_name]["patterns"],
                key=lambda x: x.get("count", 0),
                reverse=True
            )[:20]  # 只保留前 20 个
            # 去重示例
            seen = set()
            unique_examples = []
            for ex in clusters[cluster_name]["examples"]:
                key = (ex["name"], ex["file"])
                if key not in seen:
                    seen.add(key)
                    unique_examples.append(ex)
            clusters[cluster_name]["examples"] = unique_examples[:10]

        return dict(clusters)

    def _analyze_units(self, units: List[CodeUnit]) -> Dict:
        """分析代码单元"""
        stats = {
            "total": len(units),
            "classes": 0,
            "functions": 0,
            "by_file": defaultdict(int),
        }

        for unit in units:
            if unit.type == 'class':
                stats["classes"] += 1
            else:
                stats["functions"] += 1

            # 按文件统计
            rel_path = unit.file_path.split('/')[-2] if '/' in unit.file_path else 'root'
            stats["by_file"][rel_path] += 1

        # 转换为列表
        stats["by_file"] = [
            {"directory": k, "count": v}
            for k, v in sorted(stats["by_file"].items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        return stats

    def _summarize_antipatterns(self, antipatterns: List) -> Dict:
        """汇总反模式"""
        if not antipatterns:
            return {"total": 0, "by_severity": {}, "by_category": {}, "top_issues": []}

        by_severity = defaultdict(int)
        by_category = defaultdict(int)
        issues = []

        for ap in antipatterns:
            severity = getattr(ap, 'severity', 'warning')
            category = getattr(ap, 'category', 'general')
            by_severity[severity] += 1
            by_category[category] += 1

            if len(issues) < 20:
                issues.append({
                    "rule": getattr(ap, 'rule_id', 'unknown'),
                    "message": getattr(ap, 'message', str(ap))[:100],
                    "severity": severity,
                    "category": category,
                })

        return {
            "total": len(antipatterns),
            "by_severity": dict(by_severity),
            "by_category": dict(by_category),
            "top_issues": issues,
        }

    def _analyze_directory(self, source_dir: str) -> Dict:
        """分析目录结构"""
        structure = {
            "root": source_dir,
            "directories": [],
            "key_files": [],
        }

        for item in os.listdir(source_dir):
            item_path = os.path.join(source_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.') and not item.startswith('_'):
                # 统计子目录
                sub_items = []
                try:
                    for sub in os.listdir(item_path):
                        if not sub.startswith('.') and not sub.startswith('_'):
                            sub_items.append(sub)
                except:
                    pass

                structure["directories"].append({
                    "name": item,
                    "items": sub_items[:10],
                    "item_count": len(sub_items),
                })
            elif os.path.isfile(item_path):
                if item.endswith('.py') or item in ('manage.py', 'settings.py', 'urls.py'):
                    structure["key_files"].append(item)

        return structure

    def save(self, skeleton: Dict, output_path: str):
        """保存骨架数据"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(skeleton, f, ensure_ascii=False, indent=2)


def generate_skeleton(units: List[CodeUnit], patterns: List[CodePattern],
                      source_dir: str, entries_summary: Dict = None,
                      antipatterns: List = None) -> Dict:
    """生成骨架数据的便捷函数"""
    generator = SkeletonGenerator()
    return generator.generate(units, patterns, source_dir, entries_summary, antipatterns)
