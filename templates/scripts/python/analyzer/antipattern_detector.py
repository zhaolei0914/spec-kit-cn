# -*- coding: utf-8 -*-
"""
Antipattern 检测器

检测代码中的违规模式（反模式）
"""
import ast
import os
import sys
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parser.base import CodeUnit


@dataclass
class Violation:
    """违规记录"""
    rule_id: str                    # 规则 ID
    rule_name: str                  # 规则名称
    severity: str                   # 严重程度: error, warning, info
    file_path: str                  # 文件路径
    line: int                       # 行号
    column: int = 0                 # 列号
    message: str = ""               # 违规消息
    suggestion: str = ""            # 修复建议
    code_snippet: str = ""          # 代码片段

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AntipatternRule:
    """反模式规则"""
    rule_id: str                    # 规则 ID
    name: str                       # 规则名称
    description: str                # 规则描述
    severity: str                   # 严重程度
    category: str                   # 分类
    suggestion: str                 # 修复建议
    enabled: bool = True            # 是否启用

    # 检测条件
    file_pattern: str = ""          # 文件路径模式
    ast_pattern: str = ""           # AST 模式
    code_pattern: str = ""          # 代码正则模式


def load_antipattern_rules(config_path: str = None) -> List['AntipatternRule']:
    """从配置文件加载反模式规则"""
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'config', 'antipatterns.yaml'
        )

    if not os.path.exists(config_path) or not HAS_YAML:
        return None  # 使用默认规则

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        rules = []
        rule_id = 1
        for category, category_rules in config.items():
            if not isinstance(category_rules, list):
                continue
            for rule_config in category_rules:
                rules.append(AntipatternRule(
                    rule_id=rule_config.get('id', f'AP{rule_id:03d}'),
                    name=rule_config.get('message', ''),
                    description=rule_config.get('message', ''),
                    severity=rule_config.get('severity', 'warning'),
                    category=rule_config.get('category', category),
                    suggestion='',
                    file_pattern=rule_config.get('file_pattern', ''),
                    code_pattern=rule_config.get('pattern', ''),
                ))
                rule_id += 1
        return rules if rules else None
    except Exception as e:
        print(f"警告: 加载反模式配置失败 ({e})，使用默认规则")
        return None


class AntipatternDetector:
    """反模式检测器"""

    def __init__(self, config_path: str = None):
        loaded_rules = load_antipattern_rules(config_path)
        self.rules = loaded_rules if loaded_rules else self._get_default_rules()
        self.violations: List[Violation] = []

    def _get_default_rules(self) -> List[AntipatternRule]:
        """获取默认规则"""
        return [
            # 通用规则
            AntipatternRule(
                rule_id="AP001",
                name="禁止使用 print()",
                description="生产代码中禁止使用 print()，应使用 logger",
                severity="warning",
                category="logging",
                suggestion="使用 logger.info() 或 logger.debug() 替代",
                ast_pattern="print_call",
            ),
            AntipatternRule(
                rule_id="AP002",
                name="禁止裸 except",
                description="禁止使用裸 except:，应指定具体异常类型",
                severity="error",
                category="exception",
                suggestion="使用 except Exception as e: 或更具体的异常类型",
                ast_pattern="bare_except",
            ),
            AntipatternRule(
                rule_id="AP003",
                name="禁止硬编码密码",
                description="禁止在代码中硬编码密码或密钥",
                severity="error",
                category="security",
                suggestion="使用配置文件或环境变量",
                code_pattern=r"(password|passwd|secret|api_key)\s*=\s*['\"][^'\"]+['\"]",
            ),

            # Handler 规则
            AntipatternRule(
                rule_id="AP101",
                name="Handler 禁止直接操作 DB",
                description="Handler 中不应直接使用 .objects 操作数据库",
                severity="error",
                category="architecture",
                suggestion="通过 Service 层操作数据库",
                file_pattern=r".*/handler/.*\.py$",
                code_pattern=r"\.objects\.(filter|get|create|update|delete|all)",
            ),
            AntipatternRule(
                rule_id="AP102",
                name="Handler 缺少日志",
                description="Handler 的主要方法应有日志记录",
                severity="info",
                category="logging",
                suggestion="在关键操作处添加 logger.info()",
                file_pattern=r".*/handler/.*\.py$",
                ast_pattern="handler_no_logging",
            ),

            # Web 规则
            AntipatternRule(
                rule_id="AP201",
                name="View 缺少 @authenticated",
                description="View 的公开方法应使用 @authenticated 装饰器",
                severity="error",
                category="security",
                suggestion="添加 @authenticated() 装饰器",
                file_pattern=r".*/web/.*\.py$",
                ast_pattern="view_no_auth",
            ),
            AntipatternRule(
                rule_id="AP202",
                name="View 缺少 @formatting",
                description="View 方法应使用 @formatting 装饰器",
                severity="warning",
                category="convention",
                suggestion="添加 @formatting() 装饰器",
                file_pattern=r".*/web/.*\.py$",
                ast_pattern="view_no_formatting",
            ),
            AntipatternRule(
                rule_id="AP203",
                name="装饰器顺序错误",
                description="@formatting 应在 @authenticated 之前",
                severity="error",
                category="convention",
                suggestion="调整顺序为 @formatting() 然后 @authenticated()",
                file_pattern=r".*/web/.*\.py$",
                ast_pattern="decorator_order",
            ),

            # Service 规则
            AntipatternRule(
                rule_id="AP301",
                name="多表操作缺少事务",
                description="涉及多表操作应使用 @transaction.atomic",
                severity="warning",
                category="data_integrity",
                suggestion="添加 @transaction.atomic 装饰器",
                file_pattern=r".*/service/.*\.py$",
                ast_pattern="multi_table_no_transaction",
            ),

            # Model 规则
            AntipatternRule(
                rule_id="AP401",
                name="Model 未继承 BaseModel",
                description="数据模型应继承 BaseModel",
                severity="warning",
                category="convention",
                suggestion="将基类改为 BaseModel",
                file_pattern=r".*models\.py$",
                ast_pattern="model_no_base",
            ),
        ]

    def detect(self, source_dir: str, exclude_patterns: List[str] = None) -> List[Violation]:
        """检测所有违规"""
        self.violations = []
        exclude_patterns = exclude_patterns or ['*/__pycache__/*', '*/.git/*', '*/migrations/*', '*/Thrift/*']

        for root, dirs, files in os.walk(source_dir):
            # 排除目录
            dirs[:] = [d for d in dirs if not any(
                self._match_pattern(os.path.join(root, d), p) for p in exclude_patterns
            )]

            for filename in files:
                if not filename.endswith('.py'):
                    continue

                filepath = os.path.join(root, filename)

                # 排除文件
                if any(self._match_pattern(filepath, p) for p in exclude_patterns):
                    continue

                self._detect_file(filepath)

        return self.violations

    def _detect_file(self, filepath: str):
        """检测单个文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return

        # 解析 AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        for rule in self.rules:
            if not rule.enabled:
                continue

            # 检查文件模式（支持 glob 和 regex）
            if rule.file_pattern:
                # 将 glob 模式转换为 regex
                pattern = rule.file_pattern
                if '*' in pattern and not pattern.startswith('^'):
                    # glob 模式：*/handler/* -> .*/handler/.*
                    pattern = pattern.replace('*', '.*')
                try:
                    if not re.search(pattern, filepath):
                        continue
                except re.error:
                    continue

            # 代码正则检测
            if rule.code_pattern:
                self._detect_code_pattern(filepath, content, lines, rule)

            # AST 模式检测
            if rule.ast_pattern:
                self._detect_ast_pattern(filepath, tree, lines, rule)

    def _detect_code_pattern(self, filepath: str, content: str, lines: List[str], rule: AntipatternRule):
        """检测代码正则模式"""
        for i, line in enumerate(lines, 1):
            if re.search(rule.code_pattern, line, re.IGNORECASE):
                self.violations.append(Violation(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    file_path=filepath,
                    line=i,
                    message=rule.description,
                    suggestion=rule.suggestion,
                    code_snippet=line.strip(),
                ))

    def _detect_ast_pattern(self, filepath: str, tree: ast.AST, lines: List[str], rule: AntipatternRule):
        """检测 AST 模式"""
        if rule.ast_pattern == "print_call":
            self._detect_print_calls(filepath, tree, lines, rule)
        elif rule.ast_pattern == "bare_except":
            self._detect_bare_except(filepath, tree, lines, rule)
        elif rule.ast_pattern == "view_no_auth":
            self._detect_view_no_auth(filepath, tree, lines, rule)
        elif rule.ast_pattern == "view_no_formatting":
            self._detect_view_no_formatting(filepath, tree, lines, rule)
        elif rule.ast_pattern == "decorator_order":
            self._detect_decorator_order(filepath, tree, lines, rule)
        elif rule.ast_pattern == "model_no_base":
            self._detect_model_no_base(filepath, tree, lines, rule)

    def _detect_print_calls(self, filepath: str, tree: ast.AST, lines: List[str], rule: AntipatternRule):
        """检测 print() 调用"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    self.violations.append(Violation(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        file_path=filepath,
                        line=node.lineno,
                        column=node.col_offset,
                        message=rule.description,
                        suggestion=rule.suggestion,
                        code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                    ))

    def _detect_bare_except(self, filepath: str, tree: ast.AST, lines: List[str], rule: AntipatternRule):
        """检测裸 except"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.violations.append(Violation(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        file_path=filepath,
                        line=node.lineno,
                        message=rule.description,
                        suggestion=rule.suggestion,
                        code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                    ))

    def _detect_view_no_auth(self, filepath: str, tree: ast.AST, lines: List[str], rule: AntipatternRule):
        """检测 View 缺少 @authenticated"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否是 View 类
                is_view = any(
                    (isinstance(base, ast.Name) and 'View' in base.id) or
                    (isinstance(base, ast.Attribute) and 'View' in base.attr)
                    for base in node.bases
                )

                if not is_view:
                    continue

                # 检查方法
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name in ('get', 'post', 'put', 'delete', 'patch'):
                            # 检查是否有 authenticated 装饰器
                            has_auth = any(
                                self._get_decorator_name(d) == 'authenticated'
                                for d in item.decorator_list
                            )

                            if not has_auth:
                                self.violations.append(Violation(
                                    rule_id=rule.rule_id,
                                    rule_name=rule.name,
                                    severity=rule.severity,
                                    file_path=filepath,
                                    line=item.lineno,
                                    message=f"方法 {node.name}.{item.name} 缺少 @authenticated",
                                    suggestion=rule.suggestion,
                                ))

    def _detect_view_no_formatting(self, filepath: str, tree: ast.AST, lines: List[str], rule: AntipatternRule):
        """检测 View 缺少 @formatting"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_view = any(
                    (isinstance(base, ast.Name) and 'View' in base.id) or
                    (isinstance(base, ast.Attribute) and 'View' in base.attr)
                    for base in node.bases
                )

                if not is_view:
                    continue

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name in ('get', 'post', 'put', 'delete', 'patch'):
                            has_formatting = any(
                                self._get_decorator_name(d) == 'formatting'
                                for d in item.decorator_list
                            )

                            if not has_formatting:
                                self.violations.append(Violation(
                                    rule_id=rule.rule_id,
                                    rule_name=rule.name,
                                    severity=rule.severity,
                                    file_path=filepath,
                                    line=item.lineno,
                                    message=f"方法 {node.name}.{item.name} 缺少 @formatting",
                                    suggestion=rule.suggestion,
                                ))

    def _detect_decorator_order(self, filepath: str, tree: ast.AST, lines: List[str], rule: AntipatternRule):
        """检测装饰器顺序"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                decorators = [self._get_decorator_name(d) for d in node.decorator_list]

                if 'formatting' in decorators and 'authenticated' in decorators:
                    formatting_idx = decorators.index('formatting')
                    auth_idx = decorators.index('authenticated')

                    # formatting 应该在 authenticated 之前（索引更小）
                    if formatting_idx > auth_idx:
                        self.violations.append(Violation(
                            rule_id=rule.rule_id,
                            rule_name=rule.name,
                            severity=rule.severity,
                            file_path=filepath,
                            line=node.lineno,
                            message=f"方法 {node.name} 的装饰器顺序错误",
                            suggestion=rule.suggestion,
                        ))

    def _detect_model_no_base(self, filepath: str, tree: ast.AST, lines: List[str], rule: AntipatternRule):
        """检测 Model 未继承 BaseModel"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否是 Model 类（继承 models.Model 但不是 BaseModel）
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Attribute):
                        bases.append(f"{base.value.id if isinstance(base.value, ast.Name) else ''}.{base.attr}")
                    elif isinstance(base, ast.Name):
                        bases.append(base.id)

                # 如果继承 models.Model 但不是 BaseModel 或其子类
                if 'models.Model' in bases and 'BaseModel' not in bases:
                    # 排除 BaseModel 自身的定义
                    if node.name not in ('BaseModel', 'BaseModelWithUpdateTime'):
                        self.violations.append(Violation(
                            rule_id=rule.rule_id,
                            rule_name=rule.name,
                            severity=rule.severity,
                            file_path=filepath,
                            line=node.lineno,
                            message=f"类 {node.name} 应继承 BaseModel 而非 models.Model",
                            suggestion=rule.suggestion,
                        ))

    def _get_decorator_name(self, decorator) -> str:
        """获取装饰器名称"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        return ""

    def _match_pattern(self, path: str, pattern: str) -> bool:
        """匹配路径模式"""
        import fnmatch
        return fnmatch.fnmatch(path, pattern)

    def get_summary(self) -> Dict:
        """获取检测摘要"""
        by_severity = defaultdict(int)
        by_rule = defaultdict(int)
        by_category = defaultdict(int)

        for v in self.violations:
            by_severity[v.severity] += 1
            by_rule[v.rule_id] += 1

            # 获取规则分类
            for rule in self.rules:
                if rule.rule_id == v.rule_id:
                    by_category[rule.category] += 1
                    break

        return {
            'total': len(self.violations),
            'by_severity': dict(by_severity),
            'by_rule': dict(by_rule),
            'by_category': dict(by_category),
        }

    def generate_report(self) -> str:
        """生成 Markdown 报告"""
        summary = self.get_summary()

        lines = [
            "# Antipattern 检测报告",
            "",
            f"**检测时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 摘要",
            "",
            f"- **总违规数**: {summary['total']}",
            f"- **错误**: {summary['by_severity'].get('error', 0)}",
            f"- **警告**: {summary['by_severity'].get('warning', 0)}",
            f"- **提示**: {summary['by_severity'].get('info', 0)}",
            "",
        ]

        if summary['by_category']:
            lines.append("### 按分类")
            lines.append("")
            lines.append("| 分类 | 数量 |")
            lines.append("|------|------|")
            for cat, count in sorted(summary['by_category'].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"| {cat} | {count} |")
            lines.append("")

        if self.violations:
            lines.append("## 详细违规")
            lines.append("")

            # 按严重程度分组
            for severity in ['error', 'warning', 'info']:
                severity_violations = [v for v in self.violations if v.severity == severity]
                if not severity_violations:
                    continue

                severity_icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[severity]
                lines.append(f"### {severity_icon} {severity.upper()} ({len(severity_violations)})")
                lines.append("")

                for v in severity_violations[:20]:  # 最多显示 20 条
                    lines.append(f"**{v.rule_id}: {v.rule_name}**")
                    lines.append(f"- 位置: `{v.file_path}:{v.line}`")
                    lines.append(f"- 消息: {v.message}")
                    if v.code_snippet:
                        lines.append(f"- 代码: `{v.code_snippet[:80]}`")
                    lines.append(f"- 建议: {v.suggestion}")
                    lines.append("")

                if len(severity_violations) > 20:
                    lines.append(f"*... 还有 {len(severity_violations) - 20} 条 {severity} 级别违规*")
                    lines.append("")

        return '\n'.join(lines)


def detect_antipatterns(source_dir: str, output_file: str = None) -> Dict:
    """检测反模式的便捷函数"""
    detector = AntipatternDetector()
    violations = detector.detect(source_dir)
    summary = detector.get_summary()

    if output_file:
        report = detector.generate_report()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

    return {
        'violations': [v.to_dict() for v in violations],
        'summary': summary,
    }
