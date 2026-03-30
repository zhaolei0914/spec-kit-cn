# -*- coding: utf-8 -*-
"""
知识库融合器

将多个提取器的结果融合成统一的知识库
"""
import os
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import multiprocessing
import libcst as cst

from .base_libcst import CodeUnit, ExtractorResult, LibCSTExtractor
from .class_extractor import ClassExtractor
from .function_extractor import FunctionExtractor
from .constant_extractor import ConstantExtractor
from .import_extractor import ImportExtractor
from .comment_extractor import CommentExtractor
from .exception_extractor import ExceptionExtractor
from .decorator_extractor import DecoratorExtractor
from .django.model_extractor import DjangoModelExtractor
from .django.view_extractor import DjangoViewExtractor
from .django.url_extractor import DjangoURLExtractor
from .django.middleware_extractor import DjangoMiddlewareExtractor


@dataclass
class KnowledgeBase:
    """知识库"""

    # 元数据
    project_name: str = ""
    project_path: str = ""
    generated_at: str = ""
    version: str = "1.0.0"

    # 统计信息
    statistics: Dict = field(default_factory=dict)

    # 代码单元
    classes: List[Dict] = field(default_factory=list)
    functions: List[Dict] = field(default_factory=list)
    constants: List[Dict] = field(default_factory=list)
    imports: List[Dict] = field(default_factory=list)
    comments: List[Dict] = field(default_factory=list)
    exceptions: List[Dict] = field(default_factory=list)
    decorators: List[Dict] = field(default_factory=list)

    # Django 特定
    django_models: List[Dict] = field(default_factory=list)
    django_views: List[Dict] = field(default_factory=list)
    django_urls: List[Dict] = field(default_factory=list)
    django_middlewares: List[Dict] = field(default_factory=list)

    # 模式统计
    patterns: Dict = field(default_factory=dict)

    # 关系图
    relations: Dict = field(default_factory=dict)

    # 文件信息
    files: List[Dict] = field(default_factory=list)

    # 错误和警告
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "metadata": {
                "project_name": self.project_name,
                "project_path": self.project_path,
                "generated_at": self.generated_at,
                "version": self.version,
            },
            "statistics": self.statistics,
            "code_units": {
                "classes": self.classes,
                "functions": self.functions,
                "constants": self.constants,
                "imports": self.imports,
                "comments": self.comments,
                "exceptions": self.exceptions,
                "decorators": self.decorators,
            },
            "django": {
                "models": self.django_models,
                "views": self.django_views,
                "urls": self.django_urls,
                "middlewares": self.django_middlewares,
            },
            "patterns": self.patterns,
            "relations": self.relations,
            "files": self.files,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def to_json(self, indent: int = 2) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: str) -> None:
        """保存到文件"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, path: str) -> 'KnowledgeBase':
        """从文件加载"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        kb = cls()
        kb.project_name = data.get("metadata", {}).get("project_name", "")
        kb.project_path = data.get("metadata", {}).get("project_path", "")
        kb.generated_at = data.get("metadata", {}).get("generated_at", "")
        kb.version = data.get("metadata", {}).get("version", "1.0.0")
        kb.statistics = data.get("statistics", {})

        code_units = data.get("code_units", {})
        kb.classes = code_units.get("classes", [])
        kb.functions = code_units.get("functions", [])
        kb.constants = code_units.get("constants", [])
        kb.imports = code_units.get("imports", [])
        kb.comments = code_units.get("comments", [])
        kb.exceptions = code_units.get("exceptions", [])
        kb.decorators = code_units.get("decorators", [])

        django = data.get("django", {})
        kb.django_models = django.get("models", [])
        kb.django_views = django.get("views", [])
        kb.django_urls = django.get("urls", [])
        kb.django_middlewares = django.get("middlewares", [])

        kb.patterns = data.get("patterns", {})
        kb.relations = data.get("relations", {})
        kb.files = data.get("files", [])
        kb.errors = data.get("errors", [])
        kb.warnings = data.get("warnings", [])

        return kb


class KnowledgeBaseFusion:
    """知识库融合器"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化融合器

        Args:
            config: 配置选项
        """
        self.config = config or {}

        # 初始化提取器
        self.extractors: Dict[str, LibCSTExtractor] = {
            'class': ClassExtractor(config),
            'function': FunctionExtractor(config),
            'constant': ConstantExtractor(config),
            'import': ImportExtractor(config),
            'comment': CommentExtractor(config),
            'exception': ExceptionExtractor(config),
            'decorator': DecoratorExtractor(config),
            'django_model': DjangoModelExtractor(config),
            'django_view': DjangoViewExtractor(config),
            'django_url': DjangoURLExtractor(config),
            'django_middleware': DjangoMiddlewareExtractor(config),
        }

        # 排除模式
        self.exclude_patterns = self.config.get('exclude_patterns') or [
            '__pycache__', '.git', '.venv', 'venv', 'node_modules',
            'migrations', '.pytest_cache', '.mypy_cache',
            'Thrift', 'thrift', 'generated', 'proto',  # 跳过生成的代码
        ]

        # 文件大小限制（跳过超大文件）
        self.max_file_lines = self.config.get('max_file_lines', 5000)

    def analyze_project(self, project_path: str, parallel: bool = True) -> KnowledgeBase:
        """
        分析整个项目（优化版：并行处理 + 单次解析）

        Args:
            project_path: 项目路径
            parallel: 是否启用并行处理

        Returns:
            知识库
        """
        kb = KnowledgeBase()
        kb.project_path = os.path.abspath(project_path)
        kb.project_name = os.path.basename(kb.project_path)
        kb.generated_at = datetime.now().isoformat()

        # 收集所有 Python 文件
        python_files = self._collect_python_files(project_path)

        # 并行处理
        max_workers = self.config.get('max_workers') or min(8, multiprocessing.cpu_count())
        all_results: Dict[str, List[ExtractorResult]] = defaultdict(list)

        if parallel and len(python_files) > 10:
            # 使用线程池并行处理文件
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._process_single_file, fp, project_path): fp
                    for fp in python_files
                }

                for future in as_completed(futures):
                    file_path = futures[future]
                    try:
                        file_info, file_results, errors, warnings = future.result()
                        kb.files.append(file_info)

                        for extractor_name, result in file_results.items():
                            all_results[extractor_name].append(result)

                        kb.errors.extend(errors)
                        kb.warnings.extend(warnings)
                    except Exception as e:
                        kb.errors.append(f"Error processing {file_path}: {str(e)}")
        else:
            # 串行处理（小项目或禁用并行）
            for file_path in python_files:
                try:
                    file_info, file_results, errors, warnings = self._process_single_file(
                        file_path, project_path
                    )
                    kb.files.append(file_info)

                    for extractor_name, result in file_results.items():
                        all_results[extractor_name].append(result)

                    kb.errors.extend(errors)
                    kb.warnings.extend(warnings)
                except Exception as e:
                    kb.errors.append(f"Error processing {file_path}: {str(e)}")

        # 融合结果
        self._fuse_results(kb, all_results)

        # 分析模式
        self._analyze_patterns(kb)

        # 构建关系图
        self._build_relations(kb)

        # 计算统计信息
        self._compute_statistics(kb)

        return kb

    def _process_single_file(
        self,
        file_path: str,
        project_path: str
    ) -> Tuple[Dict, Dict[str, ExtractorResult], List[str], List[str]]:
        """
        处理单个文件（优化：只解析一次 CST）

        Returns:
            (file_info, results_dict, errors, warnings)
        """
        errors = []
        warnings = []
        results: Dict[str, ExtractorResult] = {}

        file_info = {
            "path": file_path,
            "relative_path": os.path.relpath(file_path, project_path),
            "hash": self._get_file_hash(file_path),
        }

        # 读取文件一次
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source_code = f.read()
        except Exception as e:
            errors.append(f"Failed to read {file_path}: {str(e)}")
            return file_info, results, errors, warnings

        # 跳过超大文件
        line_count = source_code.count('\n')
        if line_count > self.max_file_lines:
            warnings.append(f"Skipped large file ({line_count} lines): {file_path}")
            return file_info, results, errors, warnings

        # 解析 CST 一次（延迟创建 wrapper）
        try:
            tree = cst.parse_module(source_code)
        except cst.ParserSyntaxError as e:
            errors.append(f"Syntax error in {file_path}: {str(e)}")
            return file_info, results, errors, warnings
        except Exception as e:
            errors.append(f"Parse error in {file_path}: {str(e)}")
            return file_info, results, errors, warnings

        # 使用快速提取模式（不使用 MetadataWrapper）
        try:
            file_results = self._fast_extract_all(tree, file_path, source_code)
            for extractor_name, units in file_results.items():
                result = ExtractorResult(
                    extractor_name=extractor_name,
                    file_path=file_path
                )
                result.units = units
                results[extractor_name] = result
        except Exception as e:
            errors.append(f"Fast extraction error for {file_path}: {str(e)}")

        return file_info, results, errors, warnings

    def _fast_extract_all(
        self,
        tree: cst.Module,
        file_path: str,
        source_code: str
    ) -> Dict[str, List[CodeUnit]]:
        """
        快速提取所有代码单元（单次遍历）

        通过一次遍历同时提取所有类型的代码单元，避免多次遍历开销
        """
        from .base_libcst import CodeLocation

        results: Dict[str, List[CodeUnit]] = {
            'class': [],
            'function': [],
            'constant': [],
            'import': [],
            'decorator': [],
            'exception': [],
            'django_model': [],
            'django_view': [],
            'django_url': [],
            'django_middleware': [],
        }

        source_lines = source_code.split('\n')

        def make_location(start_line=1, end_line=1):
            return CodeLocation(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line
            )

        # Django 相关基类
        DJANGO_MODEL_BASES = {'Model', 'models.Model', 'BaseModel'}
        DJANGO_VIEW_BASES = {'View', 'TemplateView', 'ListView', 'DetailView',
                            'CreateView', 'UpdateView', 'DeleteView', 'FormView',
                            'APIView', 'ViewSet', 'ModelViewSet', 'GenericAPIView'}
        MIDDLEWARE_METHODS = {'__call__', 'process_request', 'process_response',
                             'process_view', 'process_exception'}
        EXCEPTION_BASES = {'Exception', 'BaseException', 'ValueError', 'TypeError',
                          'KeyError', 'RuntimeError', 'IOError'}

        def get_node_source(node) -> str:
            """获取节点源码"""
            try:
                return tree.code_for_node(node)
            except Exception:
                return ""

        def get_decorators(node) -> List[str]:
            """获取装饰器列表"""
            decorators = []
            if hasattr(node, 'decorators'):
                for dec in node.decorators:
                    try:
                        decorators.append('@' + tree.code_for_node(dec.decorator).strip())
                    except Exception:
                        pass
            return decorators

        def get_bases(node) -> List[str]:
            """获取基类列表"""
            bases = []
            if hasattr(node, 'bases') and node.bases:
                for arg in node.bases:
                    try:
                        bases.append(tree.code_for_node(arg.value).strip())
                    except Exception:
                        pass
            return bases

        def get_docstring(node) -> str:
            """获取文档字符串"""
            if hasattr(node, 'body') and isinstance(node.body, cst.IndentedBlock):
                if node.body.body:
                    first_stmt = node.body.body[0]
                    if isinstance(first_stmt, cst.SimpleStatementLine):
                        if first_stmt.body and isinstance(first_stmt.body[0], cst.Expr):
                            expr = first_stmt.body[0].value
                            if isinstance(expr, (cst.SimpleString, cst.ConcatenatedString)):
                                try:
                                    return tree.code_for_node(expr).strip().strip('\"\'')
                                except Exception:
                                    pass
            return ""

        def visit_node(node, depth=0):
            """递归遍历节点"""
            # 类定义
            if isinstance(node, cst.ClassDef):
                name = node.name.value
                bases = get_bases(node)
                decorators = get_decorators(node)
                docstring = get_docstring(node)
                source = get_node_source(node)

                unit = CodeUnit(
                    name=name,
                    type='class',
                    location=make_location(),
                    source_code=source[:500] if len(source) > 500 else source,
                    docstring=docstring,
                    bases=bases,
                    decorators=decorators,
                )
                results['class'].append(unit)

                # 检查是否是 Django Model
                if any(b in DJANGO_MODEL_BASES for b in bases):
                    # 提取模型字段
                    fields = []
                    if hasattr(node, 'body') and isinstance(node.body, cst.IndentedBlock):
                        for stmt in node.body.body:
                            if isinstance(stmt, cst.SimpleStatementLine):
                                for item in stmt.body:
                                    if isinstance(item, cst.Assign):
                                        for target in item.targets:
                                            if isinstance(target.target, cst.Name):
                                                field_name = target.target.value
                                                try:
                                                    field_def = tree.code_for_node(item.value).strip()
                                                    if 'models.' in field_def or 'Field' in field_def:
                                                        fields.append({
                                                            'name': field_name,
                                                            'definition': field_def[:100]
                                                        })
                                                except Exception:
                                                    pass

                    model_unit = CodeUnit(
                        name=name,
                        type='django_model',
                        location=make_location(),
                        source_code=source[:500] if len(source) > 500 else source,
                        docstring=docstring,
                        bases=bases,
                        decorators=decorators,
                        attributes=fields,
                    )
                    results['django_model'].append(model_unit)

                # 检查是否是 Django View
                elif any(b in DJANGO_VIEW_BASES for b in bases):
                    # 提取 HTTP 方法
                    http_methods = []
                    HTTP_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options'}
                    if hasattr(node, 'body') and isinstance(node.body, cst.IndentedBlock):
                        for stmt in node.body.body:
                            if isinstance(stmt, cst.FunctionDef):
                                method_name = stmt.name.value.lower()
                                if method_name in HTTP_METHODS:
                                    http_methods.append(method_name)

                    # 确定视图类型
                    view_type = 'class_based'
                    if 'APIView' in str(bases) or 'ViewSet' in str(bases):
                        view_type = 'drf_api'
                    elif 'TemplateView' in str(bases) or 'ListView' in str(bases):
                        view_type = 'generic'

                    view_unit = CodeUnit(
                        name=name,
                        type='django_view',
                        location=make_location(),
                        source_code=source[:500] if len(source) > 500 else source,
                        docstring=docstring,
                        bases=bases,
                        decorators=decorators,
                        methods=http_methods,
                        metadata={'view_type': view_type},
                    )
                    results['django_view'].append(view_unit)

                # 检查是否是异常类
                elif any(b in EXCEPTION_BASES for b in bases):
                    exc_unit = CodeUnit(
                        name=name,
                        type='exception',
                        location=make_location(),
                        source_code=source[:300] if len(source) > 300 else source,
                        docstring=docstring,
                        bases=bases,
                    )
                    results['exception'].append(exc_unit)

                # 检查是否是中间件
                methods = set()
                if hasattr(node, 'body') and isinstance(node.body, cst.IndentedBlock):
                    for stmt in node.body.body:
                        if isinstance(stmt, cst.FunctionDef):
                            methods.add(stmt.name.value)
                if methods & MIDDLEWARE_METHODS:
                    mw_unit = CodeUnit(
                        name=name,
                        type='django_middleware',
                        location=make_location(),
                        source_code=source[:500] if len(source) > 500 else source,
                        docstring=docstring,
                        methods=list(methods),
                    )
                    results['django_middleware'].append(mw_unit)

            # 函数定义（只提取顶层函数）
            elif isinstance(node, cst.FunctionDef) and depth <= 1:
                name = node.name.value
                decorators = get_decorators(node)
                docstring = get_docstring(node)
                source = get_node_source(node)

                unit = CodeUnit(
                    name=name,
                    type='function',
                    location=make_location(),
                    source_code=source[:500] if len(source) > 500 else source,
                    docstring=docstring,
                    decorators=decorators,
                )
                results['function'].append(unit)

                # 提取装饰器使用
                for dec in decorators:
                    dec_unit = CodeUnit(
                        name=dec,
                        type='decorator',
                        location=make_location(),
                        metadata={'target': name, 'target_type': 'function'}
                    )
                    results['decorator'].append(dec_unit)

            # 导入语句
            elif isinstance(node, cst.Import):
                for name_item in node.names if isinstance(node.names, tuple) else []:
                    if isinstance(name_item, cst.ImportAlias):
                        module_name = tree.code_for_node(name_item.name).strip()
                        unit = CodeUnit(
                            name=module_name,
                            type='import',
                            location=make_location(),
                            module=module_name,
                        )
                        results['import'].append(unit)

            elif isinstance(node, cst.ImportFrom):
                if node.module:
                    module_name = tree.code_for_node(node.module).strip()
                    # 提取导入的具体名称
                    imported_names = []
                    if isinstance(node.names, cst.ImportStar):
                        imported_names = ['*']
                    elif isinstance(node.names, (tuple, list)):
                        for name_item in node.names:
                            if isinstance(name_item, cst.ImportAlias):
                                try:
                                    imported_names.append(tree.code_for_node(name_item.name).strip())
                                except Exception:
                                    pass
                    unit = CodeUnit(
                        name=module_name,
                        type='import',
                        location=make_location(),
                        module=module_name,
                        is_from_import=True,
                        imported_names=imported_names,  # 新增：导入的具体名称
                    )
                    results['import'].append(unit)

            # 常量赋值（顶层）
            elif isinstance(node, cst.Assign) and depth == 0:
                for target in node.targets:
                    if isinstance(target.target, cst.Name):
                        name = target.target.value

                        # 检查是否是 urlpatterns
                        if name == 'urlpatterns':
                            self._extract_urlpatterns(node.value, tree, results, make_location)
                        # 检查是否是常量（全大写）
                        elif name.isupper() or (name[0].isupper() and '_' in name):
                            try:
                                value_str = tree.code_for_node(node.value).strip()
                            except Exception:
                                value_str = ""
                            unit = CodeUnit(
                                name=name,
                                type='constant',
                                location=make_location(),
                                value=value_str[:100] if len(value_str) > 100 else value_str,
                            )
                            results['constant'].append(unit)

            # 递归遍历子节点
            for child in node.children:
                visit_node(child, depth + 1 if isinstance(node, (cst.ClassDef, cst.FunctionDef)) else depth)

        # 开始遍历
        visit_node(tree)

        return results

    def _extract_urlpatterns(self, node, tree, results, make_location):
        """提取 urlpatterns 中的 URL 配置"""
        URL_FUNCTIONS = {'path', 'url', 're_path', 'include'}

        def extract_url_call(call_node):
            """提取单个 URL 调用"""
            if not isinstance(call_node, cst.Call):
                return None

            # 获取函数名
            func_name = ''
            if isinstance(call_node.func, cst.Name):
                func_name = call_node.func.value
            elif isinstance(call_node.func, cst.Attribute):
                func_name = call_node.func.attr.value

            if func_name not in URL_FUNCTIONS:
                return None

            # 解析参数
            pattern = ''
            view = ''
            name = ''

            positional_args = []
            for arg in call_node.args:
                try:
                    if arg.keyword:
                        key = arg.keyword.value
                        value = tree.code_for_node(arg.value).strip()
                        if key == 'name':
                            name = value.strip("'\"")
                    else:
                        value = tree.code_for_node(arg.value).strip()
                        positional_args.append(value)
                except Exception:
                    pass

            if len(positional_args) >= 1:
                pattern = positional_args[0].strip("'\"")
            if len(positional_args) >= 2:
                view = positional_args[1]

            return {
                'function': func_name,
                'pattern': pattern,
                'view': view,
                'name': name,
            }

        # 处理列表
        if isinstance(node, cst.List):
            for elem in node.elements:
                if isinstance(elem, cst.Element):
                    url_info = extract_url_call(elem.value)
                    if url_info:
                        unit = CodeUnit(
                            name=url_info.get('name', '') or url_info.get('pattern', 'unnamed'),
                            type='django_url',
                            location=make_location(),
                            metadata={
                                'function': url_info.get('function', ''),
                                'pattern': url_info.get('pattern', ''),
                                'view': url_info.get('view', ''),
                                'name': url_info.get('name', ''),
                            }
                        )
                        results['django_url'].append(unit)

    def _collect_python_files(self, directory: str) -> List[str]:
        """收集所有 Python 文件"""
        python_files = []

        for root, dirs, files in os.walk(directory):
            # 过滤目录
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]

            for file in files:
                if file.endswith('.py') and not self._should_exclude(file):
                    python_files.append(os.path.join(root, file))

        return sorted(python_files)

    def _should_exclude(self, name: str) -> bool:
        """检查是否应该排除"""
        import fnmatch
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False

    def _get_file_hash(self, file_path: str) -> str:
        """获取文件 hash"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _fuse_results(
        self,
        kb: KnowledgeBase,
        all_results: Dict[str, List[ExtractorResult]]
    ) -> None:
        """融合提取结果"""
        # 类
        for result in all_results.get('class', []):
            for unit in result.units:
                kb.classes.append(unit.to_dict())

        # 函数
        for result in all_results.get('function', []):
            for unit in result.units:
                kb.functions.append(unit.to_dict())

        # 常量
        for result in all_results.get('constant', []):
            for unit in result.units:
                kb.constants.append(unit.to_dict())

        # 导入
        for result in all_results.get('import', []):
            for unit in result.units:
                kb.imports.append(unit.to_dict())

        # 注释
        for result in all_results.get('comment', []):
            for unit in result.units:
                # 只保留特殊标记（TODO/FIXME 等）
                if unit.type == 'comment_tag':
                    kb.comments.append(unit.to_dict())

        # 异常
        for result in all_results.get('exception', []):
            for unit in result.units:
                kb.exceptions.append(unit.to_dict())

        # 装饰器
        for result in all_results.get('decorator', []):
            for unit in result.units:
                kb.decorators.append(unit.to_dict())

        # Django 模型
        for result in all_results.get('django_model', []):
            for unit in result.units:
                kb.django_models.append(unit.to_dict())

        # Django 视图
        for result in all_results.get('django_view', []):
            for unit in result.units:
                kb.django_views.append(unit.to_dict())

        # Django URL
        for result in all_results.get('django_url', []):
            for unit in result.units:
                kb.django_urls.append(unit.to_dict())

        # Django 中间件
        for result in all_results.get('django_middleware', []):
            for unit in result.units:
                kb.django_middlewares.append(unit.to_dict())

    def _analyze_patterns(self, kb: KnowledgeBase) -> None:
        """分析代码模式"""
        patterns = {
            "decorators": defaultdict(int),
            "base_classes": defaultdict(int),
            "http_methods": defaultdict(int),
            "field_types": defaultdict(int),
            "exception_types": defaultdict(int),
            "import_modules": defaultdict(int),
        }

        # 装饰器模式
        for dec in kb.decorators:
            dec_name = dec.get('metadata', {}).get('decorator_name', '')
            if dec_name:
                patterns["decorators"][dec_name] += 1

        # 基类模式
        for cls in kb.classes:
            for base in cls.get('bases', []):
                patterns["base_classes"][base] += 1

        for model in kb.django_models:
            for base in model.get('bases', []):
                patterns["base_classes"][base] += 1

        # HTTP 方法模式
        for view in kb.django_views:
            for method in view.get('metadata', {}).get('http_methods', []):
                patterns["http_methods"][method] += 1

        # 字段类型模式
        for model in kb.django_models:
            for attr in model.get('attributes', []):
                field_type = attr.get('type', '')
                if field_type:
                    patterns["field_types"][field_type] += 1

        # 异常类型模式
        for exc in kb.exceptions:
            exc_type = exc.get('exception_type', '')
            if exc_type:
                patterns["exception_types"][exc_type] += 1

        # 导入模块模式
        for imp in kb.imports:
            module = imp.get('module', '')
            if module:
                root_module = module.split('.')[0]
                patterns["import_modules"][root_module] += 1

        # 转换为普通字典
        kb.patterns = {k: dict(v) for k, v in patterns.items()}

    def _build_relations(self, kb: KnowledgeBase) -> None:
        """构建关系图"""
        relations = {
            "inheritance": [],  # 继承关系
            "composition": [],  # 组合关系
            "dependency": [],   # 依赖关系
        }

        # 继承关系
        for cls in kb.classes:
            for base in cls.get('bases', []):
                relations["inheritance"].append({
                    "from": cls['name'],
                    "to": base,
                    "type": "extends"
                })

        for model in kb.django_models:
            for base in model.get('bases', []):
                relations["inheritance"].append({
                    "from": model['name'],
                    "to": base,
                    "type": "extends"
                })

        # 组合关系（模型关系）
        for model in kb.django_models:
            for rel in model.get('metadata', {}).get('relations', []):
                relations["composition"].append({
                    "from": model['name'],
                    "to": rel.get('related_model', ''),
                    "type": rel.get('relation_type', ''),
                    "field": rel.get('field_name', ''),
                })

        kb.relations = relations

    def _compute_statistics(self, kb: KnowledgeBase) -> None:
        """计算统计信息"""
        kb.statistics = {
            "file_count": len(kb.files),
            "class_count": len(kb.classes),
            "function_count": len(kb.functions),
            "constant_count": len(kb.constants),
            "import_count": len(kb.imports),
            "exception_count": len(kb.exceptions),
            "decorator_usage_count": len(kb.decorators),
            "django": {
                "model_count": len(kb.django_models),
                "view_count": len(kb.django_views),
                "url_count": len(kb.django_urls),
                "middleware_count": len(kb.django_middlewares),
            },
            "error_count": len(kb.errors),
            "warning_count": len(kb.warnings),
            "top_decorators": self._get_top_items(kb.patterns.get('decorators', {}), 10),
            "top_base_classes": self._get_top_items(kb.patterns.get('base_classes', {}), 10),
            "top_imports": self._get_top_items(kb.patterns.get('import_modules', {}), 10),
        }

    def _get_top_items(self, counter: Dict, n: int) -> List[Dict]:
        """获取出现次数最多的项"""
        sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        return [{"name": k, "count": v} for k, v in sorted_items[:n]]
