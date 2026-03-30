# -*- coding: utf-8 -*-
"""
Skill 生成器

基于知识库生成 Skill 文档
"""
import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extractor.libcst.knowledge_base import KnowledgeBase


@dataclass
class SkillMetadata:
    """Skill 元数据"""
    skill_id: str
    title: str
    description: str
    triggers: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 2
    confidence: float = 1.0
    confidence_level: str = "fact"
    version: str = "1.0.0"
    generated_at: str = ""

    def to_yaml_header(self) -> str:
        """生成 YAML 头部 (符合 Anthropic Skills 规范)"""
        lines = [
            "---",
            f"name: {self.title}",  # Anthropic 规范使用 name
            f"description: {self.description}",
            f"triggers: {json.dumps(self.triggers, ensure_ascii=False)}",
            "---",
        ]
        return "\n".join(lines)


class ProjectPatterns:
    """项目模式分析器 - 从项目中提取实际使用的模式"""

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        # 兼容不同的知识库结构
        # 优先使用 kb.django 字典，然后是 kb 属性
        if hasattr(kb, 'django') and isinstance(kb.django, dict):
            self._django_views = kb.django.get('views', [])
            self._django_models = kb.django.get('models', [])
        else:
            self._django_views = getattr(kb, 'django_views', []) or []
            self._django_models = getattr(kb, 'django_models', []) or []

        if hasattr(kb, 'code_units') and isinstance(kb.code_units, dict):
            self._decorators = kb.code_units.get('decorators', [])
            self._imports = kb.code_units.get('imports', [])
        else:
            self._decorators = getattr(kb, 'decorators', []) or []
            self._imports = getattr(kb, 'imports', []) or []

        self._analyze()

    def _analyze(self):
        """分析项目模式"""
        # 构建导入名称到模块的映射
        self._import_map = self._build_import_map()
        # 分析视图装饰器
        self.view_decorators = self._analyze_view_decorators()
        # 分析模型基类
        self.model_base_class = self._analyze_model_base()
        # 分析常用导入
        self.common_imports = self._analyze_common_imports()
        # 分析主键模式
        self.primary_key_pattern = self._analyze_primary_key()
        # 分析 Manager
        self.manager_class = self._analyze_manager()
        # 分析字段类型模式
        self.field_types = self._analyze_field_types()
        # 分析请求处理模式
        self.request_patterns = self._analyze_request_patterns()
        # 分析 Model 完整模式
        self.model_patterns = self._analyze_model_patterns()
        # 分析 Service 模式
        self.service_patterns = self._analyze_service_patterns()

    def _build_import_map(self) -> Dict[str, str]:
        """构建导入名称到模块的映射 (自动关联)"""
        import_map = {}  # name -> "from module import name"
        for imp in self._imports:
            module = imp.get('module', '')
            imported_names = imp.get('imported_names', [])
            for name in imported_names:
                if name and name != '*':
                    import_map[name] = f"from {module} import {name}"
        return import_map

    def get_import_for(self, name: str) -> str:
        """获取名称对应的导入语句"""
        return self._import_map.get(name, '')

    def _analyze_view_decorators(self) -> List[Dict]:
        """分析视图中最常用的装饰器"""
        # 内置装饰器列表（需要过滤掉）
        builtin_decorators = {
            'classmethod', 'staticmethod', 'property', 'abstractmethod',
            'abstractproperty', 'cached_property', 'dataclass', 'wraps',
            'lru_cache', 'functools', 'contextmanager'
        }

        decorator_count = defaultdict(int)

        # 从视图源代码中提取装饰器
        import re
        for view in self._django_views:
            source = view.get('source_code', '')
            dec_matches = re.findall(r'@(\w+)\s*\(', source)
            for dec_name in dec_matches:
                if dec_name not in builtin_decorators:
                    decorator_count[dec_name] += 1

        # 也从装饰器列表中统计
        for dec in self._decorators:
            dec_name = dec.get('name', '').lstrip('@').split('(')[0]
            if dec_name and dec_name not in builtin_decorators:
                decorator_count[dec_name] += 1

        # 返回使用次数最多的装饰器
        result = []
        for dec_name, count in sorted(decorator_count.items(), key=lambda x: -x[1])[:5]:
            if dec_name:
                result.append({'name': dec_name, 'count': count})
        return result

    def _analyze_model_base(self) -> str:
        """分析模型最常用的基类"""
        base_count = defaultdict(int)
        for model in self._django_models:
            for base in model.get('bases', []):
                if base != 'object':
                    base_count[base] += 1

        if base_count:
            return max(base_count.items(), key=lambda x: x[1])[0]
        return 'models.Model'

    def _analyze_common_imports(self) -> List[str]:
        """分析最常用的本地导入"""
        import_count = defaultdict(int)
        for imp in self._imports:
            if imp.get('metadata', {}).get('is_local') or imp.get('metadata', {}).get('is_relative'):
                module = imp.get('module', '')
                if module:
                    import_count[module] += 1

        return [m for m, _ in sorted(import_count.items(), key=lambda x: -x[1])[:10]]

    def _analyze_primary_key(self) -> Dict:
        """分析主键模式"""
        for model in self._django_models:
            for field in model.get('fields', []):
                if field.get('primary_key'):
                    return {
                        'field_type': field.get('field_type', 'CharField'),
                        'default': field.get('default', ''),
                    }
        return {'field_type': 'AutoField', 'default': ''}

    def _analyze_manager(self) -> str:
        """分析最常用的 Manager"""
        manager_count = defaultdict(int)
        for model in self._django_models:
            for attr in model.get('attributes', []):
                if 'Manager' in str(attr.get('value', '')):
                    manager_count[attr.get('value', '')] += 1

        if manager_count:
            return max(manager_count.items(), key=lambda x: x[1])[0]
        return 'models.Manager()'

    def _analyze_field_types(self) -> List[Dict]:
        """分析模型中最常用的字段类型"""
        import re
        field_count = defaultdict(int)
        field_examples = defaultdict(list)

        for model in self._django_models:
            for attr in model.get('attributes', []):
                definition = attr.get('definition', '')
                # 提取字段类型 (如 models.CharField, models.IntegerField)
                match = re.search(r'models\.(\w+Field)', definition)
                if match:
                    field_type = match.group(1)
                    field_count[field_type] += 1
                    if len(field_examples[field_type]) < 2:
                        field_examples[field_type].append({
                            'name': attr.get('name', ''),
                            'definition': definition[:80]
                        })

        result = []
        for field_type, count in sorted(field_count.items(), key=lambda x: -x[1])[:10]:
            result.append({
                'type': field_type,
                'count': count,
                'examples': field_examples[field_type]
            })
        return result

    def _analyze_request_patterns(self) -> Dict:
        """分析请求处理模式"""
        import re
        patterns = {
            'body_parsing': [],      # request.body 解析
            'user_access': [],       # request.user 使用
            'query_params': [],      # request.GET 使用
            'response_format': [],   # 返回格式
        }

        for view in self._django_views:
            source = view.get('source_code', '')
            name = view.get('name', '')

            # 检测 request.body 解析
            if 'request.body' in source:
                if 'json.loads(request.body)' in source:
                    patterns['body_parsing'].append({'view': name, 'pattern': 'json.loads(request.body)'})

            # 检测 request.user 使用
            if 'request.user' in source:
                user_attrs = re.findall(r'request\.user\.(\w+)', source)
                for attr in set(user_attrs):
                    patterns['user_access'].append({'view': name, 'attr': attr})

            # 检测返回格式
            if 'return {' in source or 'return{' in source:
                patterns['response_format'].append({'view': name, 'format': 'dict'})

        return patterns

    def _analyze_model_patterns(self) -> Dict:
        """分析 Model 的完整模式（字段、关系、Meta、方法）"""
        import re
        patterns = {
            'field_definitions': [],    # 完整字段定义示例
            'relationships': [],        # 关系字段 (ForeignKey, ManyToMany 等)
            'meta_options': [],         # Meta 配置
            'model_methods': [],        # 模型方法
            'validators': [],           # 验证器
        }

        for model in self._django_models:
            source = model.get('source_code', '')
            name = model.get('name', '')

            # 提取关系字段
            fk_matches = re.findall(r'(\w+)\s*=\s*models\.(ForeignKey|OneToOneField|ManyToManyField)\s*\([^)]+\)', source)
            for field_name, rel_type in fk_matches:
                patterns['relationships'].append({
                    'model': name,
                    'field': field_name,
                    'type': rel_type,
                    'definition': re.search(rf'{field_name}\s*=\s*models\.{rel_type}\s*\([^)]+\)', source).group(0) if re.search(rf'{field_name}\s*=\s*models\.{rel_type}\s*\([^)]+\)', source) else ''
                })

            # 提取 Meta 配置
            meta_match = re.search(r'class\s+Meta\s*:\s*\n((?:\s+\w+\s*=\s*[^\n]+\n?)+)', source)
            if meta_match:
                meta_content = meta_match.group(1)
                meta_options = re.findall(r'(\w+)\s*=\s*([^\n]+)', meta_content)
                for opt_name, opt_value in meta_options:
                    patterns['meta_options'].append({
                        'model': name,
                        'option': opt_name,
                        'value': opt_value.strip()
                    })

            # 提取模型方法
            method_matches = re.findall(r'def\s+(\w+)\s*\(self[^)]*\)', source)
            for method_name in method_matches:
                if not method_name.startswith('_'):
                    patterns['model_methods'].append({
                        'model': name,
                        'method': method_name
                    })

        return patterns

    def _analyze_service_patterns(self) -> Dict:
        """分析 Service/Manager 类的模式"""
        import re
        patterns = {
            'service_classes': [],      # Service 类信息
            'common_methods': [],       # 常用方法模式
            'dependencies': [],         # 依赖注入模式
            'logging_patterns': [],     # 日志使用模式
            'db_operations': [],        # 数据库操作模式
        }

        # 从所有类中识别 Service/Manager 类（兼容不同的知识库结构）
        # KnowledgeBase.load() 后，classes 是直接属性
        classes = getattr(self.kb, 'classes', []) or []
        functions = getattr(self.kb, 'functions', []) or []

        # 识别 Service 类的特征（通用关键词 + 项目常见模式）
        service_keywords = ['Service', 'Manager', 'Handler', 'Helper', 'Util', 'Logic', 'Job', 'Task', 'Worker', 'Processor']
        # 排除的基类（枚举、异常等）
        exclude_bases = ['Enum', 'BaseEnum', 'IntEnum', 'Exception', 'BaseException']

        for cls in classes:
            name = cls.get('name', '')
            source = cls.get('source_code', '')
            bases = cls.get('bases', [])

            # 检测是否是 Service 类
            is_service = any(kw in name for kw in service_keywords)
            if not is_service:
                continue

            # 排除枚举类和异常类
            if any(eb in str(bases) for eb in exclude_bases):
                continue

            # 提取方法（从源码中提取）
            methods = cls.get('methods', [])
            if not methods and source:
                # 从源码中提取方法名
                method_matches = re.findall(r'def\s+(\w+)\s*\(', source)
                methods = [m for m in method_matches if not m.startswith('_')]

            # 添加到 service_classes（只要有源码或方法）
            if source or methods:
                # 获取文件路径，用于优先级排序
                location = cls.get('location', {})
                file_path = location.get('file_path', '')
                # 优先级：service 目录下的类 > 有方法的类 > 其他
                is_in_service_dir = '/service/' in file_path or '/services/' in file_path
                priority = 0
                if is_in_service_dir:
                    priority += 10
                if methods:
                    priority += 5

                patterns['service_classes'].append({
                    'name': name,
                    'bases': bases,
                    'methods': methods[:10] if methods else [],
                    'source': source[:500] if source else '',
                    'has_methods': len(methods) > 0,
                    'priority': priority,
                    'file_path': file_path
                })

            # 检测日志使用
            if source:
                if 'logger.' in source:
                    log_calls = re.findall(r'logger\.(info|error|warning|debug|exception)\s*\([^)]+\)', source)
                    for log_level in set(log_calls):
                        patterns['logging_patterns'].append({
                            'class': name,
                            'level': log_level
                        })

                # 检测数据库操作模式
                db_patterns = re.findall(r'(\w+)\.objects\.(filter|get|create|update|delete|all|first|last|count|exists|aggregate|annotate)\s*\(', source)
                for model_name, operation in db_patterns:
                    patterns['db_operations'].append({
                        'class': name,
                        'model': model_name,
                        'operation': operation
                    })

        # 分析独立函数中的 Service 模式
        for func in functions:
            source = func.get('source_code', '')
            if source and 'logger.' in source:
                patterns['logging_patterns'].append({
                    'function': func.get('name', ''),
                    'has_logging': True
                })

        return patterns


class SkillGenerator:
    """Skill 生成器"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化生成器

        Args:
            config: 配置选项
        """
        self.config = config or {}
        self.output_dir = self.config.get('output_dir', '.specify/skills/project-context')
        self.max_examples = self.config.get('max_examples', 3)
        self.max_example_lines = self.config.get('max_example_lines', 30)
        self.patterns: Optional[ProjectPatterns] = None

    def generate_all(self, kb: KnowledgeBase, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        生成所有 Skill 文档

        Args:
            kb: 知识库
            output_dir: 输出目录

        Returns:
            生成的文件路径字典
        """
        output_dir = output_dir or self.output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 分析项目模式（用于动态生成规范）
        self.patterns = ProjectPatterns(kb)

        generated_files = {}

        # 生成项目概述
        skill_path = os.path.join(output_dir, 'SKILL.md')
        content = self.generate_project_overview(kb)
        self._write_file(skill_path, content)
        generated_files['SKILL.md'] = skill_path

        # 生成 Web 规范
        if kb.django_views:
            skill_path = os.path.join(output_dir, 'web.md')
            content = self.generate_web_skill(kb)
            self._write_file(skill_path, content)
            generated_files['web.md'] = skill_path

        # 生成 Model 规范
        if kb.django_models:
            skill_path = os.path.join(output_dir, 'models.md')
            content = self.generate_models_skill(kb)
            self._write_file(skill_path, content)
            generated_files['models.md'] = skill_path

        # 生成错误处理规范
        if kb.exceptions:
            skill_path = os.path.join(output_dir, 'error.md')
            content = self.generate_error_skill(kb)
            self._write_file(skill_path, content)
            generated_files['error.md'] = skill_path

        # 生成常量规范
        if kb.constants:
            skill_path = os.path.join(output_dir, 'constants.md')
            content = self.generate_constants_skill(kb)
            self._write_file(skill_path, content)
            generated_files['constants.md'] = skill_path

        # 生成导入规范
        if kb.imports:
            skill_path = os.path.join(output_dir, 'imports.md')
            content = self.generate_imports_skill(kb)
            self._write_file(skill_path, content)
            generated_files['imports.md'] = skill_path

        # 生成装饰器规范
        if kb.decorators:
            skill_path = os.path.join(output_dir, 'decorators.md')
            content = self.generate_decorators_skill(kb)
            self._write_file(skill_path, content)
            generated_files['decorators.md'] = skill_path

        # 生成中间件规范
        if kb.django_middlewares:
            skill_path = os.path.join(output_dir, 'middleware.md')
            content = self.generate_middleware_skill(kb)
            self._write_file(skill_path, content)
            generated_files['middleware.md'] = skill_path

        # 生成 URL 路由规范
        if kb.django_urls:
            skill_path = os.path.join(output_dir, 'urls.md')
            content = self.generate_urls_skill(kb)
            self._write_file(skill_path, content)
            generated_files['urls.md'] = skill_path

        # 生成服务层规范
        service_classes = [c for c in kb.classes if 'Service' in c.get('name', '') or 'Manager' in c.get('name', '')]
        if service_classes:
            skill_path = os.path.join(output_dir, 'service.md')
            content = self.generate_service_skill(kb, service_classes)
            self._write_file(skill_path, content)
            generated_files['service.md'] = skill_path

        # 生成处理器规范
        handler_classes = [c for c in kb.classes if 'Handler' in c.get('name', '') or 'Task' in c.get('name', '')]
        if handler_classes:
            skill_path = os.path.join(output_dir, 'handler.md')
            content = self.generate_handler_skill(kb, handler_classes)
            self._write_file(skill_path, content)
            generated_files['handler.md'] = skill_path

        # 生成日志规范
        logging_patterns = [f for f in kb.functions if 'log' in f.get('name', '').lower() or 'logger' in str(f.get('source_code', '')).lower()]
        if logging_patterns or kb.imports:
            skill_path = os.path.join(output_dir, 'logging.md')
            content = self.generate_logging_skill(kb)
            self._write_file(skill_path, content)
            generated_files['logging.md'] = skill_path

        # 生成配置规范
        config_constants = [c for c in kb.constants if any(k in c.get('name', '').upper() for k in ['CONFIG', 'SETTING', 'PATH', 'DIR', 'URL', 'HOST', 'PORT'])]
        if config_constants:
            skill_path = os.path.join(output_dir, 'config.md')
            content = self.generate_config_skill(kb, config_constants)
            self._write_file(skill_path, content)
            generated_files['config.md'] = skill_path

        # 注：references/ 目录已移除，代码模板已整合到各主 Skill 文件中
        # - View 模板 -> web.md
        # - Model 模板 -> models.md

        # 生成索引文件
        index_path = os.path.join(output_dir, 'index.yaml')
        index_content = self.generate_index(kb, generated_files)
        self._write_file(index_path, index_content)
        generated_files['index.yaml'] = index_path

        return generated_files

    def generate_project_overview(self, kb: KnowledgeBase) -> str:
        """生成项目概述 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/SKILL",
            title=f"{kb.project_name} 项目概述",
            description="项目的整体结构、技术栈和核心概念",
            triggers=["项目", "概述", "结构", "技术栈", "入门"],
            dependencies=[],
            priority=1,
            generated_at=datetime.now().isoformat(),
        )

        sections = []

        # 头部
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append(f"# {kb.project_name} 开发规范")
        sections.append("")
        sections.append("本文档定义了项目的核心开发规范，AI 在生成代码时**必须**遵守这些规范。")
        sections.append("")

        # 技术栈概述（动态生成）
        sections.append("## 技术栈")
        sections.append("")
        sections.append("- **框架**: Django")

        # 动态获取项目模式
        base_class = self.patterns.model_base_class if self.patterns else 'models.Model'
        manager_class = self.patterns.manager_class if self.patterns else ''
        decorators = self.patterns.view_decorators[:2] if self.patterns and self.patterns.view_decorators else []
        dec_names = ', '.join([f"@{d['name']}" for d in decorators]) if decorators else ''

        if base_class != 'models.Model' or manager_class or dec_names:
            components = []
            if base_class != 'models.Model':
                components.append(base_class)
            if manager_class and manager_class != 'models.Manager()':
                components.append(manager_class.replace('()', ''))
            if dec_names:
                components.append(dec_names)
            sections.append(f"- **公共组件**: {', '.join(components)}")
        sections.append("")

        # 必须遵守的规范 - 动态生成
        sections.append("## 必须遵守的规范")
        sections.append("")

        sections.append("### 1. Web 接口开发")
        sections.append("")
        sections.append("**强制要求**:")
        sections.append("- 视图类**必须**继承 `View`")
        if decorators:
            dec_str = ' + '.join([f"`@{d['name']}()`" for d in decorators])
            sections.append(f"- 方法**必须**使用 {dec_str} 装饰器")
        sections.append("- 返回字典格式的响应")
        sections.append("")
        sections.append("详见: `web.md`")
        sections.append("")

        sections.append("### 2. 数据模型开发")
        sections.append("")
        sections.append("**强制要求**:")
        sections.append(f"- 模型**必须**继承 `{base_class}`")
        pk_pattern = self.patterns.primary_key_pattern if self.patterns else {}
        if pk_pattern.get('default'):
            sections.append(f"- 主键使用 `{pk_pattern.get('field_type', 'CharField')}` + `{pk_pattern.get('default')}` 默认值")
        if manager_class and manager_class != 'models.Manager()':
            sections.append(f"- 使用 `{manager_class}` 作为 objects 管理器")
        sections.append("")
        sections.append("详见: `models.md`")
        sections.append("")

        sections.append("### 3. 服务层开发")
        sections.append("")
        sections.append("**强制要求**:")
        sections.append("- Service/Manager 类处理业务逻辑")
        sections.append("- 使用 `logger` 记录日志，禁止 `print()`")
        sections.append("")
        sections.append("详见: `service.md`")
        sections.append("")

        sections.append("### 4. 错误处理")
        sections.append("")
        sections.append("**强制要求**:")
        sections.append("- 禁止裸 `except:`，必须指定异常类型")
        sections.append("- 使用 `logger.exception()` 记录异常")
        sections.append("")
        sections.append("详见: `error.md`")
        sections.append("")

        # 禁止事项
        sections.append("## 禁止事项")
        sections.append("")
        sections.append("- ❌ 禁止使用 `print()` 输出，使用 `logger`")
        sections.append("- ❌ 禁止裸 `except:`，必须指定异常类型")
        sections.append("- ❌ 禁止硬编码敏感信息")
        sections.append("- ❌ 禁止 `from xxx import *`")
        sections.append("")

        # 相关 Skill
        sections.append("## 相关 Skill")
        sections.append("")
        sections.append("### 规范类")
        sections.append("- `web.md` - Web 接口规范")
        sections.append("- `models.md` - 数据模型规范")
        sections.append("- `service.md` - 服务层规范")
        sections.append("- `handler.md` - 处理器规范")
        sections.append("- `error.md` - 错误处理规范")
        sections.append("- `constants.md` - 常量定义规范")
        sections.append("- `config.md` - 配置规范")
        sections.append("- `logging.md` - 日志规范")
        sections.append("")
        sections.append("### 辅助类")
        sections.append("- `imports.md` - 导入规范")
        sections.append("- `urls.md` - URL 路由")
        sections.append("- `middleware.md` - 中间件规范")
        sections.append("- `decorators.md` - 装饰器规范")
        sections.append("")

        return "\n".join(sections)

    def generate_web_skill(self, kb: KnowledgeBase) -> str:
        """生成 Web 接口规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/web",
            title="Web 接口规范",
            description="API 接口开发规范，包括视图、装饰器、响应格式等",
            triggers=["API", "接口", "视图", "View", "HTTP", "请求", "响应"],
            dependencies=["project-context/SKILL"],
            priority=2,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# Web 接口规范")
        sections.append("")
        sections.append("本文档定义了 Web 接口开发规范，AI 在生成 View 代码时**必须**遵守这些规范。")
        sections.append("")

        # 必须遵守的规范
        sections.append("## 必须遵守的规范")
        sections.append("")

        # 收集装饰器导入路径
        decorator_imports = []
        if self.patterns and self.patterns.view_decorators:
            for dec in self.patterns.view_decorators[:2]:
                imp = self.patterns.get_import_for(dec['name'])
                if imp:
                    decorator_imports.append(imp)

        sections.append("### 1. 必须的导入")
        sections.append("")
        sections.append("创建 View 时**必须**导入以下模块：")
        sections.append("")
        sections.append("```python")
        sections.append("from django.views import View")
        if decorator_imports:
            sections.append("")
            sections.append("# 装饰器导入")
            for imp in decorator_imports:
                sections.append(imp)
        sections.append("```")
        sections.append("")

        sections.append("### 2. 视图类继承")
        sections.append("")
        sections.append("所有视图类**必须**继承 `View`：")
        sections.append("")
        sections.append("```python")
        sections.append("class MyView(View):  # ✅ 正确")
        sections.append("    pass")
        sections.append("```")
        sections.append("")

        sections.append("### 3. 装饰器要求")
        sections.append("")
        sections.append("视图方法**必须**使用以下装饰器：")
        sections.append("")
        sections.append("| 装饰器 | 导入路径 | 必须 |")
        sections.append("|--------|----------|------|")
        # 动态生成装饰器列表（包含导入路径）
        if self.patterns and self.patterns.view_decorators:
            for i, dec in enumerate(self.patterns.view_decorators[:4]):
                required = "✅ 是" if i < 2 else "可选"
                imp = self.patterns.get_import_for(dec['name'])
                imp_path = imp.split(' import ')[0].replace('from ', '') if imp else '未检测'
                sections.append(f"| `@{dec['name']}()` | `{imp_path}` | {required} |")
        else:
            sections.append("| `@login_required` | `django.contrib.auth.decorators` | 视情况 |")
        sections.append("")

        sections.append("### 4. 装饰器顺序")
        sections.append("")
        sections.append("装饰器**必须**按以下顺序使用：")
        sections.append("")
        sections.append("```python")
        # 动态生成装饰器顺序
        if self.patterns and self.patterns.view_decorators:
            for i, dec in enumerate(self.patterns.view_decorators[:2]):
                comment = "# 最外层" if i == 0 else "# 第二层"
                sections.append(f"@{dec['name']}()  {comment}")
        else:
            sections.append("@decorator1()  # 最外层")
            sections.append("@decorator2()  # 第二层")
        sections.append("def get(self, request):")
        sections.append("    ...")
        sections.append("```")
        sections.append("")

        # 完整代码模板 - 从知识库中提取真实示例
        sections.append("## 项目代码示例")
        sections.append("")
        sections.append("以下是项目中的真实 View 代码，创建新 View 时参考此风格：")
        sections.append("")

        # 从知识库中提取真实的视图代码
        views = self.patterns._django_views if self.patterns else []
        example_count = 0
        for view in views[:3]:  # 最多3个示例
            source = view.get('source_code', '')
            if source and len(source) > 50:  # 过滤太短的代码
                name = view.get('name', 'View')
                location = view.get('location', {})
                file_path = location.get('file_path', '')
                line_start = location.get('line', 1)
                if file_path:
                    # 只显示相对路径
                    rel_path = file_path.split('/')[-2] + '/' + file_path.split('/')[-1] if '/' in file_path else file_path
                sections.append(f"### 示例: `{name}`")
                sections.append("")
                # 添加代码证据引用
                lines = source.strip().split('\n')
                line_end = line_start + len(lines) - 1
                sections.append(f"**来源**: `{rel_path}:{line_start}-{line_end}`")
                sections.append("")
                sections.append("```python")
                # 截断过长的代码
                if len(lines) > 30:
                    sections.append('\n'.join(lines[:25]))
                    sections.append("    # ... (省略)")
                else:
                    sections.append(source.strip())
                sections.append("```")
                sections.append("")
                example_count += 1
                if example_count >= 2:  # 最多2个示例
                    break

        if example_count == 0:
            # 如果没有真实示例，提供通用模板
            sections.append("```python")
            sections.append("# 项目中未找到 View 示例，请参考 Django 标准写法")
            sections.append("from django.views import View")
            sections.append("")
            sections.append("class MyView(View):")
            sections.append("    def get(self, request):")
            sections.append("        return {'status': 'success'}")
            sections.append("```")
            sections.append("")

        # 请求处理模式 - 从项目中自动提取
        request_patterns = self.patterns.request_patterns if self.patterns else {}
        if request_patterns.get('body_parsing') or request_patterns.get('user_access'):
            sections.append("## 请求处理模式")
            sections.append("")

            # 请求体解析
            if request_patterns.get('body_parsing'):
                sections.append("### 请求体解析")
                sections.append("")
                sections.append("项目中使用以下方式解析请求体：")
                sections.append("")
                sections.append("```python")
                sections.append("import json")
                sections.append("")
                sections.append("def post(self, request):")
                sections.append("    body = json.loads(request.body)  # 解析 JSON 请求体")
                sections.append("```")
                sections.append("")

            # 用户信息访问
            if request_patterns.get('user_access'):
                user_attrs = set(p.get('attr', '') for p in request_patterns['user_access'])
                if user_attrs:
                    sections.append("### 用户信息访问")
                    sections.append("")
                    sections.append("项目中常用的用户属性：")
                    sections.append("")
                    sections.append("```python")
                    for attr in list(user_attrs)[:5]:
                        sections.append(f"request.user.{attr}  # 获取用户 {attr}")
                    sections.append("```")
                    sections.append("")

        # 常见错误
        sections.append("## 常见错误")
        sections.append("")
        sections.append("### ❌ 错误：缺少装饰器")
        sections.append("")
        sections.append("```python")
        sections.append("class MyView(View):")
        dec_names = " 和 ".join([f"@{d['name']}" for d in self.patterns.view_decorators[:2]]) if self.patterns and self.patterns.view_decorators else "装饰器"
        sections.append(f"    def get(self, request):  # ❌ 缺少 {dec_names}")
        sections.append("        return {'status': 'success'}")
        sections.append("```")
        sections.append("")
        sections.append("### ✅ 正确：使用装饰器")
        sections.append("")
        sections.append("```python")
        sections.append("class MyView(View):")
        if self.patterns and self.patterns.view_decorators:
            for dec in self.patterns.view_decorators[:2]:
                sections.append(f"    @{dec['name']}()")
        sections.append("    def get(self, request):  # ✅ 正确")
        sections.append("        return {'status': 'success'}")
        sections.append("```")
        sections.append("")

        # 检查清单
        sections.append("## 检查清单")
        sections.append("")
        sections.append("- [ ] 继承 `View` 类")
        if self.patterns and self.patterns.view_decorators:
            for dec in self.patterns.view_decorators[:2]:
                sections.append(f"- [ ] 使用 `@{dec['name']}()` 装饰器")
        sections.append("- [ ] 返回字典格式响应")
        sections.append("- [ ] 使用 `logger` 记录日志")
        sections.append("")

        return "\n".join(sections)

    def generate_models_skill(self, kb: KnowledgeBase) -> str:
        """生成数据模型规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/models",
            title="数据模型规范",
            description="Django 模型定义规范，包括字段、关系、Meta 配置等",
            triggers=["模型", "Model", "数据库", "字段", "表", "ORM"],
            dependencies=["project-context/SKILL"],
            priority=2,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# 数据模型规范")
        sections.append("")
        sections.append("本文档定义了数据模型开发规范，AI 在生成 Model 代码时**必须**遵守这些规范。")
        sections.append("")

        # 动态获取模型基类和 Manager
        base_class = self.patterns.model_base_class if self.patterns else 'models.Model'
        manager_class = self.patterns.manager_class if self.patterns else 'models.Manager()'
        pk_pattern = self.patterns.primary_key_pattern if self.patterns else {'field_type': 'AutoField', 'default': ''}

        # 必须遵守的规范
        sections.append("## 必须遵守的规范")
        sections.append("")

        sections.append("### 1. 模型继承")
        sections.append("")
        sections.append(f"所有模型**必须**继承 `{base_class}`：")
        sections.append("")
        sections.append("```python")
        # 动态生成导入
        base_import = self._find_class_import(kb, base_class)
        if base_import:
            sections.append(base_import)
        else:
            sections.append("from django.db import models")
        sections.append("")
        sections.append(f"class MyModel({base_class}):  # ✅ 正确")
        sections.append("    pass")
        sections.append("```")
        sections.append("")

        sections.append("### 2. 主键定义")
        sections.append("")
        if pk_pattern.get('field_type') == 'CharField' and pk_pattern.get('default'):
            sections.append(f"主键**必须**使用 `{pk_pattern['field_type']}` + `{pk_pattern['default']}` 默认值：")
        else:
            sections.append("主键使用项目标准模式：")
        sections.append("")
        sections.append("```python")
        sections.append(f"class MyModel({base_class}):")
        if pk_pattern.get('field_type') == 'CharField' and pk_pattern.get('default'):
            sections.append(f"    id = models.CharField(max_length=32, primary_key=True, default={pk_pattern.get('default')})")
        else:
            sections.append("    # 使用默认主键或项目标准")
        sections.append("```")
        sections.append("")

        if manager_class and manager_class != 'models.Manager()':
            sections.append("### 3. Manager 定义")
            sections.append("")
            sections.append(f"**必须**使用 `{manager_class}` 作为 objects 管理器：")
            sections.append("")
            sections.append("```python")
            sections.append(f"class MyModel({base_class}):")
            sections.append(f"    objects = {manager_class}")
            sections.append("```")
            sections.append("")

        # 项目代码示例 - 从知识库中提取真实示例
        sections.append("## 项目代码示例")
        sections.append("")
        sections.append("以下是项目中的真实 Model 代码，创建新 Model 时参考此风格：")
        sections.append("")

        # 从知识库中提取真实的模型代码
        models = self.patterns._django_models if self.patterns else []
        example_count = 0
        for model in models[:3]:
            source = model.get('source_code', '')
            if source and len(source) > 50:
                name = model.get('name', 'Model')
                location = model.get('location', {})
                file_path = location.get('file_path', '')
                line_start = location.get('line', 1)
                if file_path:
                    rel_path = file_path.split('/')[-2] + '/' + file_path.split('/')[-1] if '/' in file_path else file_path
                sections.append(f"### 示例: `{name}`")
                sections.append("")
                # 添加代码证据引用
                lines = source.strip().split('\n')
                line_end = line_start + len(lines) - 1
                sections.append(f"**来源**: `{rel_path}:{line_start}-{line_end}`")
                sections.append("")
                sections.append("```python")
                if len(lines) > 30:
                    sections.append('\n'.join(lines[:25]))
                    sections.append("    # ... (省略)")
                else:
                    sections.append(source.strip())
                sections.append("```")
                sections.append("")
                example_count += 1
                if example_count >= 2:
                    break

        if example_count == 0:
            sections.append("```python")
            sections.append("# 项目中未找到 Model 示例，请参考 Django 标准写法")
            sections.append("from django.db import models")
            sections.append("")
            sections.append("class MyModel(models.Model):")
            sections.append("    name = models.CharField(max_length=100)")
            sections.append("```")
            sections.append("")

        # 字段类型规范 - 从项目中自动提取
        field_types = self.patterns.field_types if self.patterns else []
        if field_types:
            sections.append("## 常用字段类型")
            sections.append("")
            sections.append("以下是项目中最常用的字段类型：")
            sections.append("")
            sections.append("| 字段类型 | 使用次数 | 示例 |")
            sections.append("|----------|----------|------|")
            for ft in field_types[:8]:
                examples = ft.get('examples', [])
                example_str = examples[0].get('definition', '')[:40] if examples else ''
                sections.append(f"| `models.{ft['type']}` | {ft['count']} | `{example_str}...` |")
            sections.append("")

        # 关系定义 - 从项目中自动提取
        model_patterns = self.patterns.model_patterns if self.patterns else {}
        relationships = model_patterns.get('relationships', [])
        if relationships:
            sections.append("## 关系定义")
            sections.append("")
            sections.append("项目中使用的关系字段：")
            sections.append("")
            # 按关系类型分组
            rel_by_type = {}
            for rel in relationships:
                rel_type = rel.get('type', '')
                if rel_type not in rel_by_type:
                    rel_by_type[rel_type] = []
                rel_by_type[rel_type].append(rel)

            for rel_type, rels in rel_by_type.items():
                sections.append(f"### {rel_type}")
                sections.append("")
                sections.append("```python")
                for rel in rels[:3]:  # 每种类型最多3个示例
                    definition = rel.get('definition', '')
                    if definition:
                        sections.append(definition)
                sections.append("```")
                sections.append("")

        # Meta 配置 - 从项目中自动提取
        meta_options = model_patterns.get('meta_options', [])
        if meta_options:
            sections.append("## Meta 配置")
            sections.append("")
            sections.append("项目中常用的 Meta 配置：")
            sections.append("")
            # 统计常用选项
            option_count = {}
            for opt in meta_options:
                opt_name = opt.get('option', '')
                if opt_name:
                    option_count[opt_name] = option_count.get(opt_name, 0) + 1

            sections.append("| 选项 | 使用次数 | 示例值 |")
            sections.append("|------|----------|--------|")
            for opt_name, count in sorted(option_count.items(), key=lambda x: -x[1])[:5]:
                # 找一个示例值
                example_value = next((o.get('value', '') for o in meta_options if o.get('option') == opt_name), '')
                sections.append(f"| `{opt_name}` | {count} | `{example_value[:30]}` |")
            sections.append("")

            sections.append("```python")
            sections.append("class Meta:")
            for opt_name in list(option_count.keys())[:3]:
                example_value = next((o.get('value', '') for o in meta_options if o.get('option') == opt_name), '')
                sections.append(f"    {opt_name} = {example_value}")
            sections.append("```")
            sections.append("")

        # 检查清单 - 动态生成
        sections.append("## 检查清单")
        sections.append("")
        sections.append(f"- [ ] 继承 `{base_class}`")
        if pk_pattern.get('default'):
            sections.append(f"- [ ] 使用 `{pk_pattern.get('field_type', 'CharField')}` + `{pk_pattern.get('default')}` 作为主键")
        if manager_class and manager_class != 'models.Manager()':
            sections.append(f"- [ ] 使用 `{manager_class}` 作为 objects")
        sections.append("- [ ] 定义 `Meta.db_table`")
        sections.append("")

        return "\n".join(sections)

    def generate_error_skill(self, kb: KnowledgeBase) -> str:
        """生成错误处理规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/error",
            title="错误处理规范",
            description="异常定义、错误码、异常处理模式",
            triggers=["错误", "异常", "Exception", "Error", "raise", "try", "except"],
            dependencies=["project-context/SKILL"],
            priority=2,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# 错误处理规范")
        sections.append("")
        sections.append("本文档定义了错误处理规范，AI 在生成代码时**必须**遵守这些规范。")
        sections.append("")

        # 必须遵守的规范
        sections.append("## 必须遵守的规范")
        sections.append("")

        sections.append("### 1. 禁止裸 except")
        sections.append("")
        sections.append("**必须**指定异常类型：")
        sections.append("")
        sections.append("```python")
        sections.append("# ❌ 错误")
        sections.append("try:")
        sections.append("    do_something()")
        sections.append("except:  # 禁止裸 except")
        sections.append("    pass")
        sections.append("")
        sections.append("# ✅ 正确")
        sections.append("try:")
        sections.append("    do_something()")
        sections.append("except ValueError as e:")
        sections.append("    logger.warning('Invalid value: %s', e)")
        sections.append("except Exception as e:")
        sections.append("    logger.exception('Unexpected error: %s', e)")
        sections.append("```")
        sections.append("")

        sections.append("### 2. 使用 logger 记录异常")
        sections.append("")
        sections.append("**必须**使用 `logger.exception()` 记录异常堆栈：")
        sections.append("")
        sections.append("```python")
        sections.append("import logging")
        sections.append("")
        sections.append("logger = logging.getLogger(__name__)")
        sections.append("")
        sections.append("try:")
        sections.append("    do_something()")
        sections.append("except Exception as e:")
        sections.append("    logger.exception('Error occurred: %s', e)  # ✅ 包含堆栈")
        sections.append("```")
        sections.append("")

        sections.append("### 3. 统一错误响应格式")
        sections.append("")
        sections.append("```python")
        sections.append("# 错误响应格式")
        sections.append("return {'status': 'error', 'message': str(e)}")
        sections.append("```")
        sections.append("")

        # 完整代码模板
        sections.append("## 完整代码模板")
        sections.append("")
        sections.append("```python")
        sections.append("import logging")
        sections.append("")
        sections.append("logger = logging.getLogger(__name__)")
        sections.append("")
        sections.append("")
        sections.append("def handle_request(request):")
        sections.append("    try:")
        sections.append("        # 业务逻辑")
        sections.append("        result = do_something()")
        sections.append("        return {'status': 'success', 'data': result}")
        sections.append("    except ValueError as e:")
        sections.append("        logger.warning('Invalid value: %s', e)")
        sections.append("        return {'status': 'error', 'message': str(e)}")
        sections.append("    except Exception as e:")
        sections.append("        logger.exception('Unexpected error: %s', e)")
        sections.append("        return {'status': 'error', 'message': 'Internal error'}")
        sections.append("```")
        sections.append("")

        # 常见错误
        sections.append("## 常见错误")
        sections.append("")
        sections.append("| 错误做法 | 正确做法 |")
        sections.append("|----------|----------|")
        sections.append("| `except:` | `except Exception as e:` |")
        sections.append("| `print(e)` | `logger.exception(e)` |")
        sections.append("| 忽略异常 | 记录并处理异常 |")
        sections.append("| 暴露敏感信息 | 返回通用错误消息 |")
        sections.append("")

        # 检查清单
        sections.append("## 检查清单")
        sections.append("")
        sections.append("- [ ] 指定异常类型，禁止裸 `except:`")
        sections.append("- [ ] 使用 `logger.exception()` 记录异常")
        sections.append("- [ ] 返回统一的错误响应格式")
        sections.append("- [ ] 不暴露敏感信息给客户端")
        sections.append("")

        return "\n".join(sections)

    def generate_constants_skill(self, kb: KnowledgeBase) -> str:
        """生成常量规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/constants",
            title="常量定义规范",
            description="项目常量、枚举、配置值定义规范",
            triggers=["常量", "枚举", "Enum", "配置", "CONSTANT"],
            dependencies=["project-context/SKILL"],
            priority=3,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# 常量定义规范")
        sections.append("")
        sections.append("本文档定义了常量和枚举的开发规范，AI 在生成代码时**必须**遵守这些规范。")
        sections.append("")

        # 必须遵守的规范
        sections.append("## 必须遵守的规范")
        sections.append("")

        sections.append("### 1. 常量命名")
        sections.append("")
        sections.append("常量**必须**使用全大写 + 下划线命名：")
        sections.append("")
        sections.append("```python")
        sections.append("# ✅ 正确")
        sections.append("DEFAULT_PAGE_SIZE = 20")
        sections.append("MAX_RETRY_COUNT = 3")
        sections.append("")
        sections.append("# ❌ 错误")
        sections.append("defaultPageSize = 20  # 驼峰命名")
        sections.append("max_retry_count = 3   # 小写")
        sections.append("```")
        sections.append("")

        sections.append("### 2. 枚举类继承")
        sections.append("")
        sections.append("枚举类**必须**继承 `Enum` 或项目基类：")
        sections.append("")
        sections.append("```python")
        sections.append("from enum import Enum")
        sections.append("")
        sections.append("class TaskStatus(Enum):  # ✅ 正确")
        sections.append("    PENDING = 0")
        sections.append("    RUNNING = 1")
        sections.append("    SUCCESS = 2")
        sections.append("    FAILED = 3")
        sections.append("```")
        sections.append("")

        # 项目常量示例 - 从知识库中提取
        sections.append("## 项目常量示例")
        sections.append("")
        constants = getattr(kb, 'constants', []) or []
        if constants:
            sections.append("以下是项目中的真实常量：")
            sections.append("")
            sections.append("```python")
            shown = 0
            seen_names = set()  # 去重
            # 需要过滤的动态值模式
            dynamic_patterns = ['os.path', 'sys.', 'parser.get', 'patch(', 'getattr(', 'getenv(']
            for const in constants:
                name = const.get('name', '')
                value = const.get('value', '')
                # 跳过已显示的常量名（去重）
                if name in seen_names:
                    continue
                # 基本过滤：全大写、长度>2、不以_开头
                if not (name and name.isupper() and len(name) > 2 and not name.startswith('_')):
                    continue
                # 过滤动态值（包含函数调用等）
                if any(p in str(value) for p in dynamic_patterns):
                    continue
                # 过滤过长的值
                if len(str(value)) > 50:
                    continue
                # 输出有效常量
                if isinstance(value, str):
                    # 过滤纯布尔字符串（如 'True', 'False'）
                    if value in ('True', 'False'):
                        continue
                    sections.append(f"{name} = {repr(value)}")
                elif isinstance(value, (int, float, bool)):
                    sections.append(f"{name} = {value}")
                else:
                    continue
                seen_names.add(name)
                shown += 1
                if shown >= 8:
                    break
            sections.append("```")
            sections.append("")

        # 检查清单
        sections.append("## 检查清单")
        sections.append("")
        sections.append("- [ ] 常量使用全大写 + 下划线命名")
        sections.append("- [ ] 枚举类继承 `BaseEnum` 或 `Enum`")
        sections.append("")

        return "\n".join(sections)

    def generate_imports_skill(self, kb: KnowledgeBase) -> str:
        """生成导入规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/imports",
            title="导入规范",
            description="模块导入规范和常用导入路径",
            triggers=["导入", "import", "from", "模块", "包"],
            dependencies=["project-context/SKILL"],
            priority=3,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# 导入规范")
        sections.append("")
        sections.append("本文档定义了模块导入规范，AI 在生成代码时**必须**遵守这些规范。")
        sections.append("")

        # 必须遵守的规范
        sections.append("## 必须遵守的规范")
        sections.append("")

        sections.append("### 1. 导入顺序")
        sections.append("")
        sections.append("导入**必须**按以下顺序排列：")
        sections.append("")
        sections.append("1. 标准库")
        sections.append("2. 第三方库")
        sections.append("3. Django")
        sections.append("4. 项目模块")
        sections.append("")

        sections.append("### 2. 禁止 import *")
        sections.append("")
        sections.append("```python")
        sections.append("# ❌ 错误")
        sections.append("from some_module import *")
        sections.append("")
        sections.append("# ✅ 正确")
        sections.append("from some_module import specific_function")
        sections.append("```")
        sections.append("")

        # 项目常用导入 - 从知识库中提取
        sections.append("## 项目常用导入")
        sections.append("")

        imports = getattr(kb, 'imports', []) or []
        if imports:
            # 统计最常用的项目模块导入（排除标准库和第三方库）
            from collections import Counter
            project_imports = []
            for i in imports:
                module = i.get('module', '')
                meta = i.get('metadata', {})
                # 排除标准库和第三方库
                if module and not meta.get('is_standard_lib') and not meta.get('is_third_party'):
                    # 只保留项目相关的模块
                    if module.startswith('Common') or module.startswith('.') or '.' in module:
                        project_imports.append(module)
            top_imports = Counter(project_imports).most_common(10)

            if top_imports:
                sections.append("以下是项目中最常用的导入：")
                sections.append("")
                sections.append("```python")
                for module, count in top_imports:
                    sections.append(f"from {module} import ...  # 使用 {count} 次")
                sections.append("```")
                sections.append("")

        # 检查清单
        sections.append("## 检查清单")
        sections.append("")
        sections.append("- [ ] 导入顺序: 标准库 → 第三方库 → Django → 项目模块")
        sections.append("- [ ] 禁止 `from xxx import *`")
        sections.append("- [ ] 使用绝对导入")
        sections.append("")

        return "\n".join(sections)

    def generate_decorators_skill(self, kb: KnowledgeBase) -> str:
        """生成装饰器规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/decorators",
            title="装饰器规范",
            description="项目中使用的装饰器及其用法",
            triggers=["装饰器", "decorator", "@"],
            dependencies=["project-context/SKILL"],
            priority=3,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# 装饰器规范")
        sections.append("")
        sections.append("本文档定义了装饰器使用规范，AI 在生成代码时**必须**遵守这些规范。")
        sections.append("")

        # 动态获取装饰器
        decorators = self.patterns.view_decorators if self.patterns and self.patterns.view_decorators else []

        # 必须遵守的规范
        sections.append("## 必须遵守的规范")
        sections.append("")

        sections.append("### 1. View 方法必须使用的装饰器")
        sections.append("")
        sections.append("| 装饰器 | 说明 | 必须 |")
        sections.append("|--------|------|------|")
        if decorators:
            for i, dec in enumerate(decorators[:4]):
                required = "✅ 是" if i < 2 else "可选"
                sections.append(f"| `@{dec['name']}()` | 项目常用装饰器 | {required} |")
        else:
            sections.append("| `@login_required` | 登录验证 | 视情况 |")
        sections.append("")

        sections.append("### 2. 装饰器顺序")
        sections.append("")
        sections.append("装饰器**必须**按以下顺序使用：")
        sections.append("")
        sections.append("```python")
        if decorators:
            for i, dec in enumerate(decorators[:2]):
                comment = "# 最外层" if i == 0 else "# 第二层"
                sections.append(f"@{dec['name']}()  {comment}")
        else:
            sections.append("@decorator1()  # 最外层")
            sections.append("@decorator2()  # 第二层")
        sections.append("def get(self, request):")
        sections.append("    pass")
        sections.append("```")
        sections.append("")

        # 项目代码示例 - 从知识库提取
        sections.append("## 项目代码示例")
        sections.append("")
        views = self.patterns._django_views if self.patterns else []
        if views:
            sections.append("以下是项目中使用装饰器的真实代码：")
            sections.append("")
            for view in views[:1]:
                source = view.get('source_code', '')
                if source:
                    sections.append("```python")
                    lines = source.strip().split('\n')
                    sections.append('\n'.join(lines[:15]))
                    if len(lines) > 15:
                        sections.append("    # ...")
                    sections.append("```")
                    sections.append("")

        # 检查清单
        sections.append("## 检查清单")
        sections.append("")
        if decorators:
            for dec in decorators[:2]:
                sections.append(f"- [ ] View 方法使用 `@{dec['name']}()` 装饰器")
        sections.append("- [ ] 装饰器顺序正确")
        sections.append("")

        return "\n".join(sections)

    def generate_index(self, kb: KnowledgeBase, generated_files: Dict[str, str]) -> str:
        """生成索引文件"""
        lines = [
            "# Skill 索引",
            f"# 生成时间: {datetime.now().isoformat()}",
            f"# 项目: {kb.project_name}",
            "",
            "skills:",
        ]

        # Skill 依赖关系定义
        dependency_map = {
            "SKILL.md": [],
            "web.md": ["error.md", "imports.md", "decorators.md"],
            "models.md": ["imports.md"],
            "error.md": ["logging.md"],
            "constants.md": [],
            "imports.md": [],
            "decorators.md": ["imports.md"],
            "middleware.md": ["imports.md"],
            "urls.md": ["web.md"],
            "service.md": ["error.md", "logging.md"],
            "handler.md": ["error.md", "logging.md"],
            "logging.md": [],
            "config.md": [],
        }

        for filename, filepath in sorted(generated_files.items()):
            if filename == 'index.yaml':
                continue

            skill_id = f"project-context/{filename.replace('.md', '')}"
            lines.append(f"  - id: {skill_id}")
            lines.append(f"    file: {filename}")
            # 添加依赖关系
            deps = dependency_map.get(filename, [])
            if deps:
                dep_ids = [f"project-context/{d.replace('.md', '')}" for d in deps if d in generated_files]
                if dep_ids:
                    lines.append(f"    dependencies: {dep_ids}")

        lines.append("")
        lines.append("# 触发词映射")
        lines.append("triggers:")

        trigger_map = {
            "SKILL.md": ["项目", "概述", "结构", "技术栈"],
            "web.md": ["API", "接口", "视图", "View", "HTTP"],
            "models.md": ["模型", "Model", "数据库", "字段"],
            "error.md": ["错误", "异常", "Exception", "Error"],
            "constants.md": ["常量", "枚举", "Enum"],
            "imports.md": ["导入", "import", "模块"],
            "decorators.md": ["装饰器", "decorator"],
            "middleware.md": ["中间件", "middleware", "拦截"],
            "urls.md": ["URL", "路由", "path", "endpoint"],
            "service.md": ["Service", "服务", "Manager", "业务逻辑"],
            "handler.md": ["Handler", "处理器", "Task", "后台任务"],
            "logging.md": ["日志", "logger", "logging", "log"],
            "config.md": ["配置", "config", "settings", "环境变量"],
        }

        for filename, triggers in trigger_map.items():
            if filename in generated_files:
                lines.append(f"  {filename}:")
                for trigger in triggers:
                    lines.append(f"    - {trigger}")

        lines.append("")
        return "\n".join(lines)

    def _write_file(self, path: str, content: str) -> None:
        """写入文件"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _truncate_code(self, code: str) -> str:
        """截断代码"""
        lines = code.split('\n')
        if len(lines) <= self.max_example_lines:
            return code

        # 保留头尾
        head = lines[:self.max_example_lines // 2]
        tail = lines[-(self.max_example_lines // 2):]

        return '\n'.join(head + ['    # ... (省略中间部分)'] + tail)

    def _select_view_examples(self, views: List[Dict]) -> List[Dict]:
        """选择有代表性的视图示例"""
        # 优先选择有装饰器的视图
        with_decorators = [v for v in views if v.get('decorators')]
        if with_decorators:
            return with_decorators[:self.max_examples]
        return views[:self.max_examples]

    def _select_model_examples(self, models: List[Dict]) -> List[Dict]:
        """选择有代表性的模型示例"""
        # 优先选择有关系的模型
        with_relations = [m for m in models if m.get('metadata', {}).get('relation_count', 0) > 0]
        if with_relations:
            return with_relations[:self.max_examples]
        return models[:self.max_examples]

    def _find_decorator_import(self, kb: KnowledgeBase, dec_name: str) -> Optional[str]:
        """从项目导入中查找装饰器的导入语句"""
        for imp in kb.imports:
            # 检查是否导入了这个装饰器
            names = imp.get('names', [])
            if dec_name in names:
                module = imp.get('module', '')
                if module:
                    return f"from {module} import {dec_name}"
        return None

    def _find_class_import(self, kb: KnowledgeBase, class_name: str) -> Optional[str]:
        """从项目导入中查找类的导入语句"""
        # 优先使用 ProjectPatterns 的导入映射
        if self.patterns:
            imp = self.patterns.get_import_for(class_name)
            if imp:
                return imp
        # 回退到知识库搜索
        for imp in kb.imports:
            # 支持新的 imported_names 字段
            names = imp.get('imported_names', []) or imp.get('names', [])
            if class_name in names:
                module = imp.get('module', '')
                if module:
                    return f"from {module} import {class_name}"
        return None

    def _get_decorator_description(self, dec_name: str) -> str:
        """获取装饰器描述"""
        descriptions = {
            'formatting': '格式化响应，统一返回格式',
            'authenticated': '认证检查，验证用户登录状态',
            'connection_release': '数据库连接释放，用于长时间操作',
            'webtasklogger': '任务日志记录，记录操作日志',
            'login_required': '登录验证',
            'permission_required': '权限验证',
            'csrf_exempt': 'CSRF 豁免',
            'require_http_methods': 'HTTP 方法限制',
            'cache_page': '页面缓存',
            'transaction.atomic': '事务处理',
            'retry': '重试机制，失败后自动重试',
            'except2log': '异常日志记录',
        }
        return descriptions.get(dec_name, '')

    def generate_middleware_skill(self, kb: KnowledgeBase) -> str:
        """生成中间件规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/middleware",
            title="中间件规范",
            description="Django 中间件定义和使用规范",
            triggers=["中间件", "middleware", "拦截", "请求处理"],
            dependencies=["project-context/SKILL"],
            priority=3,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# 中间件规范")
        sections.append("")
        sections.append("本文档定义了中间件开发规范，AI 在生成代码时**必须**遵守这些规范。")
        sections.append("")

        # 完整代码模板
        sections.append("## 完整代码模板")
        sections.append("")
        sections.append("```python")
        sections.append("class MyMiddleware:")
        sections.append("    def __init__(self, get_response):")
        sections.append("        self.get_response = get_response")
        sections.append("")
        sections.append("    def __call__(self, request):")
        sections.append("        # 请求前处理")
        sections.append("        response = self.get_response(request)")
        sections.append("        # 响应后处理")
        sections.append("        return response")
        sections.append("")
        sections.append("    def process_view(self, request, view_func, view_args, view_kwargs):")
        sections.append("        # 视图处理前")
        sections.append("        pass")
        sections.append("```")
        sections.append("")

        # 检查清单
        sections.append("## 检查清单")
        sections.append("")
        sections.append("- [ ] 实现 `__init__` 和 `__call__` 方法")
        sections.append("- [ ] 在 settings.py 中注册中间件")
        sections.append("")

        return "\n".join(sections)

    def generate_urls_skill(self, kb: KnowledgeBase) -> str:
        """生成 URL 路由规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/urls",
            title="URL 路由规范",
            description="Django URL 路由定义规范",
            triggers=["URL", "路由", "path", "urlpatterns", "endpoint"],
            dependencies=["project-context/SKILL"],
            priority=3,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# URL 路由规范")
        sections.append("")
        sections.append("本文档定义了 URL 路由规范，AI 在生成代码时**必须**遵守这些规范。")
        sections.append("")

        # 完整代码模板
        sections.append("## 完整代码模板")
        sections.append("")
        sections.append("```python")
        sections.append("from django.conf.urls import url")
        sections.append("from .views import MyView, AnotherView")
        sections.append("")
        sections.append("urlpatterns = [")
        sections.append("    url(r'^api/v1/resource$', MyView.as_view()),")
        sections.append("    url(r'^api/v1/resource/(?P<id>[a-zA-Z0-9]+)$', AnotherView.as_view()),")
        sections.append("]")
        sections.append("```")
        sections.append("")

        # 检查清单
        sections.append("## 检查清单")
        sections.append("")
        sections.append("- [ ] 使用 `url()` 函数定义路由")
        sections.append("- [ ] 视图使用 `.as_view()` 方法")
        sections.append("- [ ] URL 路径使用正则表达式")
        sections.append("")

        return "\n".join(sections)

    def generate_service_skill(self, kb: KnowledgeBase, service_classes: List[Dict]) -> str:
        """生成服务层规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/service",
            title="服务层规范",
            description="Service 和 Manager 类的开发规范",
            triggers=["Service", "服务", "Manager", "业务逻辑"],
            dependencies=["project-context/SKILL"],
            priority=2,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# 服务层规范")
        sections.append("")
        sections.append("本文档定义了服务层开发规范，AI 在生成 Service/Manager 代码时**必须**遵守这些规范。")
        sections.append("")

        # 从 ProjectPatterns 获取 Service 模式
        service_patterns = self.patterns.service_patterns if self.patterns else {}
        detected_services = service_patterns.get('service_classes', [])
        db_operations = service_patterns.get('db_operations', [])
        logging_patterns = service_patterns.get('logging_patterns', [])

        # 必须遵守的规范
        sections.append("## 必须遵守的规范")
        sections.append("")

        # 检测 logger 导入路径
        logger_import = self.patterns.get_import_for('logger') if self.patterns else ''

        sections.append("### 1. 使用 logger 记录日志")
        sections.append("")
        sections.append("**禁止**使用 `print()`，**必须**使用 `logger`：")
        sections.append("")
        sections.append("```python")
        if logger_import:
            sections.append(logger_import)
        else:
            sections.append("from Common.log import logger  # 或项目标准日志模块")
        sections.append("")
        sections.append("class MyService:")
        sections.append("    def do_something(self):")
        sections.append("        logger.info('Starting operation')  # ✅ 正确")
        sections.append("        # print('Starting operation')  # ❌ 禁止")
        sections.append("```")
        sections.append("")

        # 项目代码示例 - 从知识库中自动提取
        sections.append("## 项目代码示例")
        sections.append("")

        if detected_services:
            # 按优先级排序：service 目录下的类优先
            sorted_services = sorted(detected_services, key=lambda x: -x.get('priority', 0))

            sections.append("以下是项目中的真实 Service/Manager 代码：")
            sections.append("")

            example_count = 0
            for svc in sorted_services[:3]:
                name = svc.get('name', '')
                source = svc.get('source', '')
                methods = svc.get('methods', [])

                if source and len(source) > 50:
                    sections.append(f"### 示例: `{name}`")
                    sections.append("")
                    if methods:
                        sections.append(f"**方法**: {', '.join(methods[:5])}")
                        sections.append("")
                    sections.append("```python")
                    lines = source.strip().split('\n')
                    if len(lines) > 25:
                        sections.append('\n'.join(lines[:20]))
                        sections.append("    # ... (省略)")
                    else:
                        sections.append(source.strip())
                    sections.append("```")
                    sections.append("")
                    example_count += 1
                    if example_count >= 2:
                        break

            if example_count == 0:
                # 如果没有找到带源码的示例，显示类名列表
                sections.append("项目中检测到的 Service/Manager 类：")
                sections.append("")
                for svc in detected_services[:5]:
                    name = svc.get('name', '')
                    methods = svc.get('methods', [])
                    sections.append(f"- `{name}`: {', '.join(methods[:3])}...")
                sections.append("")
        else:
            # 通用模板
            sections.append("```python")
            sections.append("from Common.log import logger")
            sections.append("")
            sections.append("class MyService:")
            sections.append("    def __init__(self):")
            sections.append("        pass")
            sections.append("")
            sections.append("    def do_something(self, data):")
            sections.append("        logger.info('Processing data: %s', data)")
            sections.append("        # 业务逻辑")
            sections.append("        return result")
            sections.append("```")
            sections.append("")

        # 数据库操作模式 - 从项目中自动提取
        if db_operations:
            sections.append("## 数据库操作模式")
            sections.append("")
            sections.append("项目中常用的数据库操作：")
            sections.append("")

            # 统计操作类型
            op_count = {}
            for op in db_operations:
                operation = op.get('operation', '')
                if operation:
                    op_count[operation] = op_count.get(operation, 0) + 1

            sections.append("| 操作 | 使用次数 | 示例 |")
            sections.append("|------|----------|------|")
            for operation, count in sorted(op_count.items(), key=lambda x: -x[1])[:8]:
                # 找一个示例
                example = next((o for o in db_operations if o.get('operation') == operation), {})
                model = example.get('model', 'Model')
                sections.append(f"| `{operation}` | {count} | `{model}.objects.{operation}(...)` |")
            sections.append("")

            sections.append("```python")
            sections.append("# 常用数据库操作示例")
            for operation in list(op_count.keys())[:4]:
                example = next((o for o in db_operations if o.get('operation') == operation), {})
                model = example.get('model', 'Model')
                if operation == 'filter':
                    sections.append(f"results = {model}.objects.filter(status=1)")
                elif operation == 'get':
                    sections.append(f"obj = {model}.objects.get(id=obj_id)")
                elif operation == 'create':
                    sections.append(f"obj = {model}.objects.create(name='test')")
                elif operation == 'first':
                    sections.append(f"obj = {model}.objects.first()")
                elif operation == 'all':
                    sections.append(f"objs = {model}.objects.all()")
                elif operation == 'update':
                    sections.append(f"{model}.objects.filter(id=obj_id).update(status=2)")
                elif operation == 'delete':
                    sections.append(f"{model}.objects.filter(id=obj_id).delete()")
            sections.append("```")
            sections.append("")

        # 检查清单
        sections.append("## 检查清单")
        sections.append("")
        sections.append("- [ ] 使用 `logger` 记录日志，禁止 `print()`")
        sections.append("- [ ] 异常使用 `logger.exception()` 记录")
        sections.append("- [ ] 业务逻辑封装在 Service/Manager 类中")
        if db_operations:
            sections.append("- [ ] 数据库操作使用 ORM 方法")
        sections.append("")

        return "\n".join(sections)

    def generate_handler_skill(self, kb: KnowledgeBase, handler_classes: List[Dict]) -> str:
        """生成处理器规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/handler",
            title="处理器规范",
            description="Handler 和 Task 类的开发规范",
            triggers=["Handler", "处理器", "Task", "后台任务", "异步"],
            dependencies=["project-context/SKILL"],
            priority=2,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# 处理器规范")
        sections.append("")
        sections.append("本文档定义了处理器开发规范，AI 在生成 Handler/Task 代码时**必须**遵守这些规范。")
        sections.append("")

        # 完整代码模板
        sections.append("## 完整代码模板")
        sections.append("")
        sections.append("```python")
        sections.append("import logging")
        sections.append("")
        sections.append("logger = logging.getLogger(__name__)")
        sections.append("")
        sections.append("")
        sections.append("class MyHandler:")
        sections.append("    def __init__(self):")
        sections.append("        pass")
        sections.append("")
        sections.append("    def handle(self, data):")
        sections.append("        logger.info('Handling data: %s', data)")
        sections.append("        try:")
        sections.append("            result = self._process(data)")
        sections.append("            return result")
        sections.append("        except Exception as e:")
        sections.append("            logger.exception('Error handling: %s', e)")
        sections.append("            raise")
        sections.append("```")
        sections.append("")

        # 检查清单
        sections.append("## 检查清单")
        sections.append("")
        sections.append("- [ ] 使用 `logger` 记录日志")
        sections.append("- [ ] 异常使用 `logger.exception()` 记录")
        sections.append("- [ ] 实现 `handle()` 方法")
        sections.append("")

        return "\n".join(sections)

    def generate_logging_skill(self, kb: KnowledgeBase) -> str:
        """生成日志规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/logging",
            title="日志规范",
            description="日志记录规范和最佳实践",
            triggers=["日志", "logger", "logging", "log", "记录"],
            dependencies=["project-context/SKILL"],
            priority=3,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# 日志规范")
        sections.append("")
        sections.append("本文档定义了日志记录规范，AI 在生成代码时**必须**遵守这些规范。")
        sections.append("")

        # 必须遵守的规范
        sections.append("## 必须遵守的规范")
        sections.append("")
        sections.append("### 1. 禁止使用 print()")
        sections.append("")
        sections.append("**必须**使用 `logger`，**禁止**使用 `print()`：")
        sections.append("")
        sections.append("```python")
        sections.append("import logging")
        sections.append("")
        sections.append("logger = logging.getLogger(__name__)")
        sections.append("")
        sections.append("# ✅ 正确")
        sections.append("logger.info('Processing data')")
        sections.append("")
        sections.append("# ❌ 禁止")
        sections.append("# print('Processing data')")
        sections.append("```")
        sections.append("")

        sections.append("### 2. 日志级别")
        sections.append("")
        sections.append("| 级别 | 使用场景 |")
        sections.append("|------|----------|")
        sections.append("| `logger.debug()` | 调试信息 |")
        sections.append("| `logger.info()` | 一般信息 |")
        sections.append("| `logger.warning()` | 警告信息 |")
        sections.append("| `logger.error()` | 错误信息 |")
        sections.append("| `logger.exception()` | 异常信息（包含堆栈） |")
        sections.append("")

        # 完整代码模板
        sections.append("## 完整代码模板")
        sections.append("")
        sections.append("```python")
        sections.append("import logging")
        sections.append("")
        sections.append("logger = logging.getLogger(__name__)")
        sections.append("")
        sections.append("")
        sections.append("def my_function(data):")
        sections.append("    logger.info('Processing: %s', data)")
        sections.append("    try:")
        sections.append("        result = process(data)")
        sections.append("        logger.info('Success: %s', result)")
        sections.append("        return result")
        sections.append("    except Exception as e:")
        sections.append("        logger.exception('Error: %s', e)")
        sections.append("        raise")
        sections.append("```")
        sections.append("")

        # 检查清单
        sections.append("## 检查清单")
        sections.append("")
        sections.append("- [ ] 使用 `logger`，禁止 `print()`")
        sections.append("- [ ] 异常使用 `logger.exception()`")
        sections.append("- [ ] 选择正确的日志级别")
        sections.append("")

        return "\n".join(sections)

    def generate_config_skill(self, kb: KnowledgeBase, config_constants: List[Dict]) -> str:
        """生成配置规范 Skill"""
        metadata = SkillMetadata(
            skill_id="project-context/config",
            title="配置规范",
            description="项目配置项和环境变量规范",
            triggers=["配置", "config", "settings", "环境变量", "路径"],
            dependencies=["project-context/SKILL"],
            priority=3,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# 配置规范")
        sections.append("")
        sections.append("本文档定义了配置规范，AI 在生成代码时**必须**遵守这些规范。")
        sections.append("")

        # 必须遵守的规范
        sections.append("## 必须遵守的规范")
        sections.append("")
        sections.append("### 1. 路径配置")
        sections.append("")
        sections.append("路径**必须**使用 `os.path.join()` 拼接：")
        sections.append("")
        sections.append("```python")
        sections.append("import os")
        sections.append("")
        sections.append("# ✅ 正确")
        sections.append("LOG_DIR = os.path.join(INSTALL_DIR, 'logs')")
        sections.append("")
        sections.append("# ❌ 错误")
        sections.append("# LOG_DIR = INSTALL_DIR + '/logs'")
        sections.append("```")
        sections.append("")

        sections.append("### 2. 敏感配置")
        sections.append("")
        sections.append("敏感配置**必须**从环境变量读取：")
        sections.append("")
        sections.append("```python")
        sections.append("import os")
        sections.append("")
        sections.append("DB_HOST = os.environ.get('DB_HOST', 'localhost')")
        sections.append("DB_PASSWORD = os.environ.get('DB_PASSWORD')  # 不设默认值")
        sections.append("```")
        sections.append("")

        # 完整代码模板
        sections.append("## 完整代码模板")
        sections.append("")
        sections.append("```python")
        sections.append("import os")
        sections.append("")
        sections.append("# 路径配置")
        sections.append("INSTALL_DIR = os.path.dirname(os.path.dirname(__file__))")
        sections.append("ETC_PATH = os.path.join(INSTALL_DIR, 'etc')")
        sections.append("LOG_DIR = os.path.join(INSTALL_DIR, 'logs')")
        sections.append("")
        sections.append("# 从环境变量读取敏感配置")
        sections.append("DB_HOST = os.environ.get('DB_HOST', 'localhost')")
        sections.append("DB_PORT = int(os.environ.get('DB_PORT', 3306))")
        sections.append("```")
        sections.append("")

        # 检查清单
        sections.append("## 检查清单")
        sections.append("")
        sections.append("- [ ] 路径使用 `os.path.join()` 拼接")
        sections.append("- [ ] 敏感配置从环境变量读取")
        sections.append("- [ ] 配置常量使用大写命名")
        sections.append("")

        return "\n".join(sections)

    def generate_view_template(self, kb: KnowledgeBase) -> str:
        """生成 View 代码模板"""
        metadata = SkillMetadata(
            skill_id="project-context/templates/view",
            title="View 代码模板",
            description="创建新 View 时使用的代码模板",
            triggers=["新建View", "创建接口", "添加API", "新增视图"],
            dependencies=["project-context/web"],
            priority=4,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# View 代码模板")
        sections.append("")
        sections.append("## 使用场景")
        sections.append("")
        sections.append("当你需要创建新的 API 接口时，参考项目中的真实代码。")
        sections.append("")

        # 从知识库提取真实 View 代码
        sections.append("## 项目代码示例")
        sections.append("")
        views = self.patterns._django_views if self.patterns else []
        if views:
            for view in views[:1]:
                source = view.get('source_code', '')
                name = view.get('name', 'View')
                if source:
                    sections.append(f"以下是 `{name}` 的真实代码：")
                    sections.append("")
                    sections.append("```python")
                    lines = source.strip().split('\n')
                    sections.append('\n'.join(lines[:25]))
                    if len(lines) > 25:
                        sections.append("    # ...")
                    sections.append("```")
                    sections.append("")

        # 动态生成检查清单
        decorators = self.patterns.view_decorators[:2] if self.patterns and self.patterns.view_decorators else []
        sections.append("## 检查清单")
        sections.append("")
        sections.append("- [ ] 继承 `View` 类")
        if decorators:
            dec_str = ' + '.join([f"`@{d['name']}()`" for d in decorators])
            sections.append(f"- [ ] 使用 {dec_str} 装饰器")
        sections.append("- [ ] 返回字典格式响应")
        sections.append("")

        return "\n".join(sections)

    def generate_model_template(self, kb: KnowledgeBase) -> str:
        """生成 Model 代码模板"""
        metadata = SkillMetadata(
            skill_id="project-context/templates/model",
            title="Model 代码模板",
            description="创建新 Model 时使用的代码模板",
            triggers=["新建Model", "创建模型", "添加表", "新增数据模型"],
            dependencies=["project-context/models"],
            priority=4,
            generated_at=datetime.now().isoformat(),
        )

        sections = []
        sections.append(metadata.to_yaml_header())
        sections.append("")
        sections.append("# Model 代码模板")
        sections.append("")
        sections.append("## 使用场景")
        sections.append("")
        sections.append("当你需要创建新的数据模型时，参考项目中的真实代码。")
        sections.append("")

        # 从知识库提取真实 Model 代码
        sections.append("## 项目代码示例")
        sections.append("")
        models = self.patterns._django_models if self.patterns else []
        if models:
            for model in models[:1]:
                source = model.get('source_code', '')
                name = model.get('name', 'Model')
                if source:
                    sections.append(f"以下是 `{name}` 的真实代码：")
                    sections.append("")
                    sections.append("```python")
                    lines = source.strip().split('\n')
                    sections.append('\n'.join(lines[:25]))
                    if len(lines) > 25:
                        sections.append("    # ...")
                    sections.append("```")
                    sections.append("")

        # 动态生成检查清单
        base_class = self.patterns.model_base_class if self.patterns else 'models.Model'
        manager_class = self.patterns.manager_class if self.patterns else ''

        sections.append("## 检查清单")
        sections.append("")
        sections.append(f"- [ ] 继承 `{base_class}`")
        if manager_class and manager_class != 'models.Manager()':
            sections.append(f"- [ ] 使用 `{manager_class}` 作为 objects")
        sections.append("- [ ] 添加 `Meta` 类定义表名")
        sections.append("")

        return "\n".join(sections)
