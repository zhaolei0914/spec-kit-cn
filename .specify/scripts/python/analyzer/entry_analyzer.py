# -*- coding: utf-8 -*-
"""
入口分析器

基于入口（API/定时任务）分析业务规则
- 识别 API 入口（View 类）
- 识别定时任务入口（Handler 类）
- 追踪调用链
- 提取业务条件和状态变更
"""
import ast
import os
import re
import sys
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class EntryPoint:
    """入口点"""
    type: str                       # api, cron, handler
    name: str                       # 类名或函数名
    file_path: str                  # 文件路径
    line: int                       # 行号
    method: str = ""                # HTTP 方法 (get/post/put/delete)
    path: str = ""                  # API 路径（如果能推断）
    description: str = ""           # 描述（从文档字符串）
    decorators: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FunctionCall:
    """函数调用"""
    caller: str                     # 调用者
    callee: str                     # 被调用者
    file_path: str                  # 文件路径
    line: int                       # 行号
    arguments: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BusinessCondition:
    """业务条件"""
    expression: str                 # 条件表达式
    file_path: str                  # 文件路径
    line: int                       # 行号
    context: str = ""               # 上下文（函数名）
    branch_type: str = "if"         # if/elif/else

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StateChange:
    """状态变更"""
    target: str                     # 目标对象
    field: str                      # 字段名
    value: str                      # 新值
    file_path: str                  # 文件路径
    line: int                       # 行号
    context: str = ""               # 上下文（函数名）

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BusinessFlow:
    """业务流程"""
    entry: EntryPoint               # 入口点
    call_chain: List[FunctionCall]  # 调用链
    conditions: List[BusinessCondition]  # 业务条件
    state_changes: List[StateChange]     # 状态变更
    parameters: List[Dict] = field(default_factory=list)  # 参数校验

    def to_dict(self) -> dict:
        return {
            'entry': self.entry.to_dict(),
            'call_chain': [c.to_dict() for c in self.call_chain],
            'conditions': [c.to_dict() for c in self.conditions],
            'state_changes': [s.to_dict() for s in self.state_changes],
            'parameters': self.parameters,
        }


class EntryAnalyzer:
    """入口分析器"""

    def __init__(self):
        self.entries: List[EntryPoint] = []
        self.functions: Dict[str, ast.FunctionDef] = {}  # 函数名 -> AST 节点
        self.classes: Dict[str, ast.ClassDef] = {}       # 类名 -> AST 节点
        self.file_asts: Dict[str, ast.AST] = {}          # 文件路径 -> AST
        self.file_contents: Dict[str, List[str]] = {}    # 文件路径 -> 行列表

    def analyze(self, source_dir: str, exclude_patterns: List[str] = None) -> List[BusinessFlow]:
        """分析源代码目录"""
        exclude_patterns = exclude_patterns or [
            '*/__pycache__/*', '*/.git/*', '*/migrations/*', '*/Thrift/*'
        ]

        # Step 1: 解析所有文件
        self._parse_directory(source_dir, exclude_patterns)

        # Step 2: 识别入口点
        self._identify_entries()

        # Step 3: 分析每个入口的业务流程
        flows = []
        for entry in self.entries:
            flow = self._analyze_entry(entry)
            if flow:
                flows.append(flow)

        return flows

    def _parse_directory(self, source_dir: str, exclude_patterns: List[str]):
        """解析目录下所有 Python 文件"""
        import fnmatch

        for root, dirs, files in os.walk(source_dir):
            # 排除目录
            dirs[:] = [d for d in dirs if not any(
                fnmatch.fnmatch(os.path.join(root, d), p) for p in exclude_patterns
            )]

            for filename in files:
                if not filename.endswith('.py'):
                    continue

                filepath = os.path.join(root, filename)

                # 排除文件
                if any(fnmatch.fnmatch(filepath, p) for p in exclude_patterns):
                    continue

                self._parse_file(filepath)

    def _parse_file(self, filepath: str):
        """解析单个文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self.file_contents[filepath] = content.split('\n')
        except Exception:
            return

        try:
            tree = ast.parse(content)
            self.file_asts[filepath] = tree
        except SyntaxError:
            return

        # 收集类和函数定义
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                key = f"{filepath}:{node.name}"
                self.classes[key] = node
                self.classes[node.name] = node  # 简化查找
            elif isinstance(node, ast.FunctionDef):
                key = f"{filepath}:{node.name}"
                self.functions[key] = node

    def _identify_entries(self):
        """识别入口点"""
        for filepath, tree in self.file_asts.items():
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    entry = self._check_entry_class(node, filepath)
                    if entry:
                        self.entries.append(entry)

    def _check_entry_class(self, node: ast.ClassDef, filepath: str) -> Optional[EntryPoint]:
        """检查是否是入口类"""
        # 检查基类
        bases = self._get_base_names(node)

        # API 入口：继承 View、APIView、ViewSet 等
        view_bases = ['View', 'APIView', 'GenericAPIView', 'ViewSet', 'ModelViewSet',
                      'GenericViewSet', 'CreateAPIView', 'ListAPIView', 'RetrieveAPIView',
                      'UpdateAPIView', 'DestroyAPIView', 'ListCreateAPIView']
        if any(any(vb in base for vb in view_bases) for base in bases):
            # 检查是否有 HTTP 方法
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    # 支持标准 HTTP 方法和 DRF action
                    http_methods = ('get', 'post', 'put', 'delete', 'patch', 'list', 'create', 'retrieve', 'update', 'destroy')
                    if item.name in http_methods:
                        decorators = [self._get_decorator_name(d) for d in item.decorator_list]
                        docstring = ast.get_docstring(item) or ""

                        # 尝试从文档字符串提取路径
                        path = self._extract_api_path(docstring)

                        # 映射 DRF action 到 HTTP 方法
                        method_map = {'list': 'GET', 'create': 'POST', 'retrieve': 'GET',
                                      'update': 'PUT', 'destroy': 'DELETE'}
                        method = method_map.get(item.name, item.name.upper())

                        return EntryPoint(
                            type='api',
                            name=node.name,
                            file_path=filepath,
                            line=node.lineno,
                            method=method,
                            path=path,
                            description=docstring.split('\n')[0] if docstring else "",
                            decorators=decorators,
                        )

        # 定时任务/Handler 入口
        handler_bases = ['Handler', 'BaseHandler', 'RequestHandler', 'Command', 'BaseCommand']
        if any(any(hb in base for hb in handler_bases) for base in bases) or 'Handler' in node.name:
            docstring = ast.get_docstring(node) or ""
            return EntryPoint(
                type='handler',
                name=node.name,
                file_path=filepath,
                line=node.lineno,
                description=docstring.split('\n')[0] if docstring else "",
            )

        return None

    def _get_base_names(self, node: ast.ClassDef) -> List[str]:
        """获取基类名称"""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)
        return bases

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

    def _extract_api_path(self, docstring: str) -> str:
        """从文档字符串提取 API 路径"""
        if not docstring:
            return ""

        # 匹配 GET /api/xxx 或 POST /api/xxx 格式
        match = re.search(r'(GET|POST|PUT|DELETE|PATCH)\s+(/\S+)', docstring, re.IGNORECASE)
        if match:
            return match.group(2)

        # 匹配 /api/xxx 格式
        match = re.search(r'(/api/\S+)', docstring)
        if match:
            return match.group(1)

        return ""

    def _analyze_entry(self, entry: EntryPoint) -> Optional[BusinessFlow]:
        """分析入口的业务流程"""
        call_chain = []
        conditions = []
        state_changes = []
        parameters = []

        # 获取入口类
        class_node = self.classes.get(f"{entry.file_path}:{entry.name}")
        if not class_node:
            return None

        # 分析入口方法
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                if entry.type == 'api' and item.name == entry.method.lower():
                    # 分析 API 方法
                    self._analyze_function(item, entry.file_path, call_chain, conditions, state_changes)
                elif entry.type == 'handler' and item.name in ('_run', 'run', 'handle', '__call__'):
                    # 分析 Handler 方法
                    self._analyze_function(item, entry.file_path, call_chain, conditions, state_changes)

        # 追踪调用链（深度优先，最多 3 层）
        visited = set()
        for call in list(call_chain):
            self._trace_calls(call.callee, entry.file_path, call_chain, conditions, state_changes, visited, depth=0)

        return BusinessFlow(
            entry=entry,
            call_chain=call_chain,
            conditions=conditions,
            state_changes=state_changes,
            parameters=parameters,
        )

    def _analyze_function(self, node: ast.FunctionDef, filepath: str,
                          call_chain: List[FunctionCall],
                          conditions: List[BusinessCondition],
                          state_changes: List[StateChange]):
        """分析函数"""
        context = node.name

        for child in ast.walk(node):
            # 提取函数调用
            if isinstance(child, ast.Call):
                callee = self._get_call_name(child)
                if callee and not callee.startswith('_'):
                    call_chain.append(FunctionCall(
                        caller=context,
                        callee=callee,
                        file_path=filepath,
                        line=child.lineno,
                        arguments=self._get_call_arguments(child),
                    ))

            # 提取条件判断
            if isinstance(child, ast.If):
                condition_str = self._expr_to_string(child.test)
                if condition_str and len(condition_str) < 200:
                    conditions.append(BusinessCondition(
                        expression=condition_str,
                        file_path=filepath,
                        line=child.lineno,
                        context=context,
                        branch_type='if',
                    ))

            # 提取状态变更
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Attribute):
                        if target.attr in ('status', 'state', 'is_active', 'is_deleted'):
                            state_changes.append(StateChange(
                                target=self._expr_to_string(target.value),
                                field=target.attr,
                                value=self._expr_to_string(child.value),
                                file_path=filepath,
                                line=child.lineno,
                                context=context,
                            ))

    def _trace_calls(self, callee: str, current_file: str,
                     call_chain: List[FunctionCall],
                     conditions: List[BusinessCondition],
                     state_changes: List[StateChange],
                     visited: Set[str], depth: int):
        """追踪调用链"""
        if depth > 2 or callee in visited:
            return

        visited.add(callee)

        # 查找被调用的函数
        func_node = None
        func_file = current_file

        # 尝试在当前文件查找
        key = f"{current_file}:{callee}"
        if key in self.functions:
            func_node = self.functions[key]
        elif callee in self.functions:
            func_node = self.functions[callee]

        # 尝试在类方法中查找
        if not func_node and '.' in callee:
            parts = callee.split('.')
            if len(parts) >= 2:
                method_name = parts[-1]
                # 查找所有类
                for class_key, class_node in self.classes.items():
                    for item in class_node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == method_name:
                            func_node = item
                            if ':' in class_key:
                                func_file = class_key.split(':')[0]
                            break
                    if func_node:
                        break

        if func_node:
            self._analyze_function(func_node, func_file, call_chain, conditions, state_changes)

    def _get_call_name(self, node: ast.Call) -> str:
        """获取调用名称"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            value = self._expr_to_string(node.func.value)
            return f"{value}.{node.func.attr}"
        return ""

    def _get_call_arguments(self, node: ast.Call) -> List[str]:
        """获取调用参数"""
        args = []
        for arg in node.args[:3]:  # 最多 3 个参数
            args.append(self._expr_to_string(arg))
        return args

    def _expr_to_string(self, node) -> str:
        """将表达式转为字符串"""
        if node is None:
            return ""

        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._expr_to_string(node.value)
            return f"{value}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Compare):
            left = self._expr_to_string(node.left)
            ops = []
            for op, comp in zip(node.ops, node.comparators):
                op_str = self._op_to_string(op)
                comp_str = self._expr_to_string(comp)
                ops.append(f"{op_str} {comp_str}")
            return f"{left} {' '.join(ops)}"
        elif isinstance(node, ast.BoolOp):
            op_str = 'and' if isinstance(node.op, ast.And) else 'or'
            values = [self._expr_to_string(v) for v in node.values]
            return f" {op_str} ".join(values)
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return f"not {self._expr_to_string(node.operand)}"
        elif isinstance(node, ast.Call):
            return self._get_call_name(node) + "()"
        elif isinstance(node, ast.Subscript):
            value = self._expr_to_string(node.value)
            slice_str = self._expr_to_string(node.slice)
            return f"{value}[{slice_str}]"

        return ""

    def _op_to_string(self, op) -> str:
        """操作符转字符串"""
        op_map = {
            ast.Eq: '==',
            ast.NotEq: '!=',
            ast.Lt: '<',
            ast.LtE: '<=',
            ast.Gt: '>',
            ast.GtE: '>=',
            ast.Is: 'is',
            ast.IsNot: 'is not',
            ast.In: 'in',
            ast.NotIn: 'not in',
        }
        return op_map.get(type(op), '?')

    def get_entries_summary(self) -> Dict:
        """获取入口摘要"""
        api_entries = [e for e in self.entries if e.type == 'api']
        handler_entries = [e for e in self.entries if e.type == 'handler']

        return {
            'total': len(self.entries),
            'api_count': len(api_entries),
            'handler_count': len(handler_entries),
            'apis': [e.to_dict() for e in api_entries[:20]],
            'handlers': [e.to_dict() for e in handler_entries[:10]],
        }


def analyze_entries(source_dir: str) -> Tuple[List[BusinessFlow], Dict]:
    """分析入口的便捷函数"""
    analyzer = EntryAnalyzer()
    flows = analyzer.analyze(source_dir)
    summary = analyzer.get_entries_summary()
    return flows, summary
