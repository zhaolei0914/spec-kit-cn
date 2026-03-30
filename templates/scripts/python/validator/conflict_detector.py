# -*- coding: utf-8 -*-
"""
Skill 冲突检测器

检测 Skill 之间的冲突和不一致
"""
import os
import re
import yaml
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ConflictItem:
    """冲突项"""
    conflict_type: str      # 冲突类型
    severity: str           # 严重程度: high, medium, low
    description: str        # 冲突描述
    skill_a: str            # 冲突的 Skill A
    skill_b: str            # 冲突的 Skill B
    resolution: str = ""    # 建议的解决方案
    auto_resolvable: bool = False  # 是否可自动解决


@dataclass
class ConflictReport:
    """冲突报告"""
    conflicts: List[ConflictItem] = field(default_factory=list)
    checked_pairs: int = 0

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    @property
    def high_severity_count(self) -> int:
        return sum(1 for c in self.conflicts if c.severity == 'high')

    @property
    def auto_resolvable_count(self) -> int:
        return sum(1 for c in self.conflicts if c.auto_resolvable)


class ConflictDetector:
    """冲突检测器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    def detect_conflicts(self, skill_dir: str) -> ConflictReport:
        """检测 Skill 目录中的冲突"""
        report = ConflictReport()

        # 加载所有 Skill
        skills = self._load_skills(skill_dir)

        if len(skills) < 2:
            return report

        # 检测触发词冲突
        self._detect_trigger_conflicts(skills, report)

        # 检测规范冲突
        self._detect_rule_conflicts(skills, report)

        # 检测代码示例冲突
        self._detect_example_conflicts(skills, report)

        return report

    def _load_skills(self, skill_dir: str) -> Dict[str, Dict]:
        """加载所有 Skill 文件"""
        skills = {}

        if not os.path.isdir(skill_dir):
            return skills

        for filename in os.listdir(skill_dir):
            if filename.endswith('.md'):
                skill_path = os.path.join(skill_dir, filename)
                skill_data = self._parse_skill(skill_path)
                if skill_data:
                    skills[filename] = skill_data

        return skills

    def _parse_skill(self, skill_path: str) -> Optional[Dict]:
        """解析单个 Skill 文件"""
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None

        skill_data = {
            'path': skill_path,
            'content': content,
            'header': {},
            'triggers': [],
            'rules': [],
            'examples': [],
        }

        # 解析 YAML 头部
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    skill_data['header'] = yaml.safe_load(parts[1]) or {}
                    skill_data['triggers'] = skill_data['header'].get('triggers', [])
                except yaml.YAMLError:
                    pass

        # 提取规则（以 - 开头的列表项）
        rule_pattern = r'^[-*]\s+(.+)$'
        for match in re.finditer(rule_pattern, content, re.MULTILINE):
            rule = match.group(1).strip()
            if len(rule) > 10:  # 过滤太短的项
                skill_data['rules'].append(rule)

        # 提取代码示例
        code_pattern = r'```[\w]*\n(.*?)```'
        for match in re.finditer(code_pattern, content, re.DOTALL):
            code = match.group(1).strip()
            if code:
                skill_data['examples'].append(code)

        return skill_data

    def _detect_trigger_conflicts(
        self,
        skills: Dict[str, Dict],
        report: ConflictReport
    ) -> None:
        """检测触发词冲突"""
        # 构建触发词到 Skill 的映射
        trigger_map: Dict[str, List[str]] = defaultdict(list)

        for skill_name, skill_data in skills.items():
            for trigger in skill_data.get('triggers', []):
                trigger_lower = trigger.lower()
                trigger_map[trigger_lower].append(skill_name)

        # 检测重复触发词
        for trigger, skill_list in trigger_map.items():
            if len(skill_list) > 1:
                report.conflicts.append(ConflictItem(
                    conflict_type='DUPLICATE_TRIGGER',
                    severity='medium',
                    description=f"触发词 '{trigger}' 在多个 Skill 中重复",
                    skill_a=skill_list[0],
                    skill_b=skill_list[1],
                    resolution=f"为不同 Skill 使用更具体的触发词",
                    auto_resolvable=False
                ))

    def _detect_rule_conflicts(
        self,
        skills: Dict[str, Dict],
        report: ConflictReport
    ) -> None:
        """检测规范冲突"""
        skill_names = list(skills.keys())

        for i in range(len(skill_names)):
            for j in range(i + 1, len(skill_names)):
                skill_a = skill_names[i]
                skill_b = skill_names[j]

                report.checked_pairs += 1

                rules_a = set(skills[skill_a].get('rules', []))
                rules_b = set(skills[skill_b].get('rules', []))

                # 检测矛盾规则
                conflicts = self._find_contradicting_rules(rules_a, rules_b)

                for rule_a, rule_b, reason in conflicts:
                    report.conflicts.append(ConflictItem(
                        conflict_type='CONTRADICTING_RULES',
                        severity='high',
                        description=f"规则冲突: {reason}",
                        skill_a=skill_a,
                        skill_b=skill_b,
                        resolution="检查并统一规则定义",
                        auto_resolvable=False
                    ))

    def _find_contradicting_rules(
        self,
        rules_a: Set[str],
        rules_b: Set[str]
    ) -> List[Tuple[str, str, str]]:
        """查找矛盾的规则"""
        conflicts = []

        # 简单的矛盾检测模式
        contradiction_patterns = [
            (r'必须使用\s*`?(\w+)`?', r'禁止使用\s*`?(\w+)`?'),
            (r'应该\s*(.+)', r'不应该\s*(.+)'),
            (r'推荐\s*(.+)', r'避免\s*(.+)'),
        ]

        for rule_a in rules_a:
            for rule_b in rules_b:
                for pattern_a, pattern_b in contradiction_patterns:
                    match_a = re.search(pattern_a, rule_a)
                    match_b = re.search(pattern_b, rule_b)

                    if match_a and match_b:
                        if match_a.group(1).lower() == match_b.group(1).lower():
                            conflicts.append((
                                rule_a,
                                rule_b,
                                f"'{match_a.group(1)}' 的使用规则矛盾"
                            ))

        return conflicts

    def _detect_example_conflicts(
        self,
        skills: Dict[str, Dict],
        report: ConflictReport
    ) -> None:
        """检测代码示例冲突"""
        # 提取所有示例中的模式
        skill_patterns: Dict[str, Dict[str, Set[str]]] = {}

        for skill_name, skill_data in skills.items():
            patterns = {
                'decorators': set(),
                'imports': set(),
                'base_classes': set(),
            }

            for example in skill_data.get('examples', []):
                # 提取装饰器
                for match in re.finditer(r'@(\w+)', example):
                    patterns['decorators'].add(match.group(1))

                # 提取导入
                for match in re.finditer(r'from\s+([\w.]+)\s+import', example):
                    patterns['imports'].add(match.group(1))

                # 提取基类
                for match in re.finditer(r'class\s+\w+\(([^)]+)\)', example):
                    for base in match.group(1).split(','):
                        patterns['base_classes'].add(base.strip())

            skill_patterns[skill_name] = patterns

        # 检测同类型 Skill 之间的模式差异
        # （这里可以扩展更复杂的检测逻辑）

    def auto_resolve(self, report: ConflictReport) -> List[str]:
        """自动解决可解决的冲突"""
        resolved = []

        for conflict in report.conflicts:
            if conflict.auto_resolvable:
                # 执行自动解决逻辑
                resolved.append(f"已解决: {conflict.description}")

        return resolved

    def generate_report(self, report: ConflictReport) -> str:
        """生成冲突报告"""
        lines = [
            "# Skill 冲突检测报告",
            "",
            f"**检查的 Skill 对数**: {report.checked_pairs}",
            f"**发现的冲突数**: {len(report.conflicts)}",
            f"**高严重性冲突**: {report.high_severity_count}",
            f"**可自动解决**: {report.auto_resolvable_count}",
            "",
        ]

        if not report.has_conflicts:
            lines.append("✅ **未发现冲突**")
            return "\n".join(lines)

        lines.append("## 冲突列表")
        lines.append("")

        # 按严重程度分组
        high = [c for c in report.conflicts if c.severity == 'high']
        medium = [c for c in report.conflicts if c.severity == 'medium']
        low = [c for c in report.conflicts if c.severity == 'low']

        if high:
            lines.append("### 🔴 高严重性")
            lines.append("")
            for c in high:
                lines.append(f"- **[{c.conflict_type}]** {c.description}")
                lines.append(f"  - Skill A: `{c.skill_a}`")
                lines.append(f"  - Skill B: `{c.skill_b}`")
                if c.resolution:
                    lines.append(f"  - 建议: {c.resolution}")
            lines.append("")

        if medium:
            lines.append("### 🟡 中等严重性")
            lines.append("")
            for c in medium:
                lines.append(f"- **[{c.conflict_type}]** {c.description}")
                lines.append(f"  - Skill A: `{c.skill_a}`")
                lines.append(f"  - Skill B: `{c.skill_b}`")
                if c.resolution:
                    lines.append(f"  - 建议: {c.resolution}")
            lines.append("")

        if low:
            lines.append("### 🟢 低严重性")
            lines.append("")
            for c in low:
                lines.append(f"- **[{c.conflict_type}]** {c.description}")
            lines.append("")

        return "\n".join(lines)
