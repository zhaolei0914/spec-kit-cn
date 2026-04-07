#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitNexus → Specify 项目上下文 Skill 转换器

结合 GitNexus 知识图谱 + 项目文件扫描，生成完整的项目上下文 Skill，
覆盖五大维度：技术栈、项目结构、技术方案、开发规范、环境配置。

用法:
    python gitnexus_to_skill.py <project_path> [--output <output_dir>]

示例:
    # 先运行 GitNexus 分析
    bash gitnexus.sh analyze --skills /path/to/project

    # 然后生成项目上下文 Skill
    python gitnexus_to_skill.py /path/to/project --output __AGENT_SKILLS_DIR__/project-context
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


# ============================================================
# 一、项目文件扫描器 —— 从实际项目文件提取事实数据
# ============================================================

# 包管理文件 → 语言/框架映射
PACKAGE_FILE_MAP = {
    'package.json': 'JavaScript/TypeScript',
    'package-lock.json': 'JavaScript/TypeScript',
    'yarn.lock': 'JavaScript/TypeScript',
    'pnpm-lock.yaml': 'JavaScript/TypeScript',
    'pyproject.toml': 'Python',
    'setup.py': 'Python',
    'setup.cfg': 'Python',
    'requirements.txt': 'Python',
    'Pipfile': 'Python',
    'poetry.lock': 'Python',
    'go.mod': 'Go',
    'go.sum': 'Go',
    'Cargo.toml': 'Rust',
    'pom.xml': 'Java',
    'build.gradle': 'Java/Kotlin',
    'build.gradle.kts': 'Kotlin',
    'Gemfile': 'Ruby',
    'composer.json': 'PHP',
    'pubspec.yaml': 'Dart/Flutter',
    'mix.exs': 'Elixir',
    'CMakeLists.txt': 'C/C++',
    'Makefile': 'Make',
}

# 文件扩展名 → 语言
EXT_LANG_MAP = {
    '.py': 'Python', '.pyx': 'Python',
    '.js': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript',
    '.ts': 'TypeScript', '.tsx': 'TypeScript',
    '.jsx': 'JavaScript/React',
    '.vue': 'Vue',
    '.svelte': 'Svelte',
    '.java': 'Java',
    '.kt': 'Kotlin', '.kts': 'Kotlin',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.cs': 'C#',
    '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.c': 'C', '.h': 'C/C++',
    '.swift': 'Swift',
    '.dart': 'Dart',
    '.ex': 'Elixir', '.exs': 'Elixir',
    '.sh': 'Shell/Bash',
    '.ps1': 'PowerShell',
    '.sql': 'SQL',
    '.r': 'R',
    '.scala': 'Scala',
    '.lua': 'Lua',
    '.zig': 'Zig',
}

# 配置文件模式 → 技术
CONFIG_TECH_MAP = {
    'Dockerfile': 'Docker',
    'docker-compose.yml': 'Docker Compose',
    'docker-compose.yaml': 'Docker Compose',
    '.dockerignore': 'Docker',
    'Jenkinsfile': 'Jenkins CI',
    '.gitlab-ci.yml': 'GitLab CI',
    '.travis.yml': 'Travis CI',
    'Makefile': 'Make',
    'webpack.config.js': 'Webpack',
    'vite.config.ts': 'Vite',
    'vite.config.js': 'Vite',
    'rollup.config.js': 'Rollup',
    'tsconfig.json': 'TypeScript',
    '.eslintrc.js': 'ESLint',
    '.eslintrc.json': 'ESLint',
    '.prettierrc': 'Prettier',
    'jest.config.js': 'Jest',
    'vitest.config.ts': 'Vitest',
    'pytest.ini': 'pytest',
    'pyproject.toml': 'Python',
    'tox.ini': 'tox',
    '.flake8': 'Flake8',
    'mypy.ini': 'mypy',
    '.mypy.ini': 'mypy',
    'nginx.conf': 'Nginx',
    'k8s': 'Kubernetes',
    'helm': 'Helm',
    '.github/workflows': 'GitHub Actions',
    'serverless.yml': 'Serverless Framework',
    'terraform': 'Terraform',
}

# 常见框架检测模式（从依赖列表中匹配）
FRAMEWORK_PATTERNS = {
    # Python
    'django': 'Django', 'flask': 'Flask', 'fastapi': 'FastAPI',
    'tornado': 'Tornado', 'sanic': 'Sanic', 'starlette': 'Starlette',
    'celery': 'Celery', 'dramatiq': 'Dramatiq',
    'sqlalchemy': 'SQLAlchemy', 'tortoise-orm': 'Tortoise ORM',
    'alembic': 'Alembic', 'pydantic': 'Pydantic',
    # JS/TS
    'react': 'React', 'react-dom': 'React',
    'next': 'Next.js', 'nuxt': 'Nuxt.js',
    'vue': 'Vue.js', '@angular/core': 'Angular',
    'express': 'Express.js', 'koa': 'Koa',
    'nestjs': 'NestJS', '@nestjs/core': 'NestJS',
    'svelte': 'Svelte', 'solid-js': 'Solid.js',
    'prisma': 'Prisma', 'typeorm': 'TypeORM',
    'mongoose': 'Mongoose', 'sequelize': 'Sequelize',
    'tailwindcss': 'Tailwind CSS',
    'antd': 'Ant Design', 'element-plus': 'Element Plus',
    '@mui/material': 'Material UI',
    # Java
    'spring-boot': 'Spring Boot', 'mybatis': 'MyBatis',
    'hibernate': 'Hibernate',
    # Go
    'gin': 'Gin', 'echo': 'Echo', 'fiber': 'Fiber',
    'gorm': 'GORM',
    # 中间件
    'redis': 'Redis', 'ioredis': 'Redis',
    'elasticsearch': 'Elasticsearch',
    'kafka': 'Kafka', 'kafkajs': 'Kafka',
    'rabbitmq': 'RabbitMQ', 'amqplib': 'RabbitMQ',
    'mysql': 'MySQL', 'mysql2': 'MySQL',
    'pg': 'PostgreSQL', 'psycopg2': 'PostgreSQL',
    'pymongo': 'MongoDB', 'mongodb': 'MongoDB',
    'sqlite3': 'SQLite',
}


class CodePatternDetector:
    """通用多语言代码模式检测器 —— 从代码文件中提取命名、风格、反模式等事实"""

    # 各语言扩展名分组
    LANG_EXTENSIONS = {
        'python': {'.py'},
        'javascript': {'.js', '.mjs', '.cjs', '.jsx'},
        'typescript': {'.ts', '.tsx'},
        'go': {'.go'},
        'java': {'.java'},
        'kotlin': {'.kt', '.kts'},
        'rust': {'.rs'},
        'ruby': {'.rb'},
        'php': {'.php'},
        'csharp': {'.cs'},
        'cpp': {'.cpp', '.cc', '.cxx', '.c', '.h', '.hpp'},
        'shell': {'.sh', '.bash'},
        'swift': {'.swift'},
        'dart': {'.dart'},
    }

    SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                 'dist', 'build', '.next', '.nuxt', 'target', 'vendor',
                 '.gitnexus', '.claude', '.specify', '.tox', '.mypy_cache',
                 'migrations', 'Thrift', 'thrift', 'generated', 'proto'}

    def __init__(self, project_path: str, max_files: int = 200, max_lines_per_file: int = 500):
        self.project_path = project_path
        self.max_files = max_files
        self.max_lines_per_file = max_lines_per_file

    def detect_all(self) -> dict:
        """执行所有检测，返回结构化事实"""
        files = self._collect_code_files()
        samples = self._read_samples(files)

        return {
            'naming': self._detect_naming(samples),
            'indentation': self._detect_indentation(samples),
            'docstring_style': self._detect_docstring_style(samples),
            'import_style': self._detect_import_style(samples),
            'anti_patterns': self._detect_anti_patterns(samples),
            'architecture_hints': self._detect_architecture_hints(files),
            'logging_style': self._detect_logging_style(samples),
            'error_handling': self._detect_error_handling(samples),
            'env_vars_in_code': self._detect_env_vars(samples),
            'sample_count': len(samples),
        }

    def _collect_code_files(self) -> list:
        """收集源代码文件路径"""
        code_exts = set()
        for exts in self.LANG_EXTENSIONS.values():
            code_exts.update(exts)

        files = []
        for root, dirs, filenames in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            for f in filenames:
                ext = os.path.splitext(f)[1].lower()
                if ext in code_exts:
                    files.append(os.path.join(root, f))
                    if len(files) >= self.max_files * 3:
                        break
        # 优先选择核心目录的文件
        def _priority(path):
            rel = os.path.relpath(path, self.project_path)
            parts = rel.split(os.sep)
            if parts[0] in ('src', 'lib', 'app', 'core', 'cmd', 'pkg', 'internal'):
                return 0
            if parts[0] in ('test', 'tests', 'spec', 'specs', '__tests__'):
                return 2
            return 1
        files.sort(key=_priority)
        return files[:self.max_files]

    def _read_samples(self, files: list) -> list:
        """读取代码文件内容样本"""
        samples = []
        for fp in files:
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[:self.max_lines_per_file]
                rel = os.path.relpath(fp, self.project_path)
                ext = os.path.splitext(fp)[1].lower()
                lang = 'unknown'
                for lang_name, exts in self.LANG_EXTENSIONS.items():
                    if ext in exts:
                        lang = lang_name
                        break
                samples.append({'path': rel, 'ext': ext, 'lang': lang,
                                'lines': lines, 'content': ''.join(lines)})
            except (IOError, UnicodeDecodeError):
                pass
        return samples

    # ---- 命名规范检测 ----
    def _detect_naming(self, samples: list) -> dict:
        """检测函数、变量、类、文件命名风格"""
        func_names, class_names, var_names, file_names = [], [], [], []
        re_func = {
            'python': re.compile(r'^(?:def|async def)\s+(\w+)\s*\(', re.MULTILINE),
            'javascript': re.compile(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(?)', re.MULTILINE),
            'typescript': re.compile(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*(?:async\s*)?\(?)', re.MULTILINE),
            'go': re.compile(r'^func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(', re.MULTILINE),
            'java': re.compile(r'(?:public|private|protected|static|\s)+\w+\s+(\w+)\s*\(', re.MULTILINE),
            'kotlin': re.compile(r'fun\s+(\w+)\s*\(', re.MULTILINE),
            'rust': re.compile(r'fn\s+(\w+)\s*[<(]', re.MULTILINE),
            'ruby': re.compile(r'def\s+(\w+)', re.MULTILINE),
            'shell': re.compile(r'^(\w+)\s*\(\)\s*\{', re.MULTILINE),
        }
        re_class = re.compile(r'class\s+(\w+)', re.MULTILINE)

        for s in samples:
            # 文件名
            fname = os.path.basename(s['path'])
            if not fname.startswith('.') and not fname.startswith('_'):
                file_names.append(os.path.splitext(fname)[0])
            # 函数名
            pat = re_func.get(s['lang'])
            if pat:
                for m in pat.finditer(s['content']):
                    name = m.group(1) or (m.group(2) if m.lastindex >= 2 else None)
                    if name and not name.startswith('_') and len(name) > 1:
                        func_names.append(name)
            # 类名
            for m in re_class.finditer(s['content']):
                class_names.append(m.group(1))

        return {
            'function_style': self._classify_naming(func_names),
            'class_style': self._classify_naming(class_names),
            'file_style': self._classify_naming(file_names),
            'function_examples': func_names[:10],
            'class_examples': class_names[:10],
        }

    @staticmethod
    def _classify_naming(names: list) -> str:
        """分类命名风格"""
        if not names:
            return 'unknown'
        styles = Counter()
        for n in names:
            if '_' in n and n == n.lower():
                styles['snake_case'] += 1
            elif '_' in n and n == n.upper():
                styles['UPPER_SNAKE_CASE'] += 1
            elif n[0].isupper() and '_' not in n:
                styles['PascalCase'] += 1
            elif n[0].islower() and '_' not in n and any(c.isupper() for c in n):
                styles['camelCase'] += 1
            elif '-' in n:
                styles['kebab-case'] += 1
            else:
                styles['other'] += 1
        if not styles:
            return 'unknown'
        return styles.most_common(1)[0][0]

    # ---- 缩进检测 ----
    def _detect_indentation(self, samples: list) -> dict:
        """检测缩进方式"""
        space2, space4, tabs = 0, 0, 0
        for s in samples:
            for line in s['lines']:
                if line.startswith('\t'):
                    tabs += 1
                elif line.startswith('    '):
                    space4 += 1
                elif line.startswith('  ') and not line.startswith('   '):
                    space2 += 1
        total = space2 + space4 + tabs
        if total == 0:
            return {'style': 'unknown', 'detail': ''}
        if tabs > total * 0.5:
            return {'style': 'tabs', 'detail': 'Tab 缩进'}
        if space2 > space4:
            return {'style': '2-spaces', 'detail': '2 空格缩进'}
        return {'style': '4-spaces', 'detail': '4 空格缩进'}

    # ---- Docstring 风格检测 ----
    def _detect_docstring_style(self, samples: list) -> dict:
        """检测文档字符串风格"""
        styles = Counter()
        for s in samples:
            c = s['content']
            if s['lang'] == 'python':
                if re.search(r'""".*?Args:', c, re.DOTALL):
                    styles['Google'] += 1
                elif re.search(r'""".*?:param\s', c, re.DOTALL):
                    styles['Sphinx'] += 1
                elif re.search(r'""".*?Parameters\s*\n\s*-{3,}', c, re.DOTALL):
                    styles['NumPy'] += 1
                elif '"""' in c:
                    styles['简单 docstring'] += 1
            elif s['lang'] in ('javascript', 'typescript'):
                if '/**' in c:
                    styles['JSDoc'] += 1
            elif s['lang'] == 'go':
                if re.search(r'^// \w+', c, re.MULTILINE):
                    styles['Go 行注释'] += 1
            elif s['lang'] == 'java':
                if '/**' in c:
                    styles['Javadoc'] += 1
            elif s['lang'] == 'rust':
                if '///' in c:
                    styles['Rust doc'] += 1
        if not styles:
            return {'style': 'unknown', 'examples': []}
        primary = styles.most_common(1)[0][0]
        return {'style': primary, 'all_styles': dict(styles)}

    # ---- Import 风格检测 ----
    def _detect_import_style(self, samples: list) -> dict:
        """检测导入风格"""
        result = {'grouped': False, 'absolute': 0, 'relative': 0, 'wildcard': 0}
        for s in samples:
            c = s['content']
            if s['lang'] == 'python':
                result['absolute'] += len(re.findall(r'^import \w+|^from \w+', c, re.MULTILINE))
                result['relative'] += len(re.findall(r'^from \.', c, re.MULTILINE))
                result['wildcard'] += len(re.findall(r'import \*', c, re.MULTILINE))
                # 检测分组（连续 import 之间有空行）
                if re.search(r'^import .+\n\n^from .+', c, re.MULTILINE):
                    result['grouped'] = True
            elif s['lang'] in ('javascript', 'typescript'):
                result['absolute'] += len(re.findall(r"^import .+ from ['\"](?!\.)", c, re.MULTILINE))
                result['relative'] += len(re.findall(r"^import .+ from ['\"]\.+", c, re.MULTILINE))
        style = '绝对导入为主' if result['absolute'] > result['relative'] else '相对导入为主'
        if result['grouped']:
            style += '，分组排列'
        return {'style': style, **result}

    # ---- 反模式检测 ----
    def _detect_anti_patterns(self, samples: list) -> list:
        """检测常见反模式"""
        issues = []
        print_debug, bare_except, hardcoded, wildcard_import = 0, 0, 0, 0
        todo_count, fixme_count = 0, 0

        for s in samples:
            c = s['content']
            lang = s['lang']

            # print 调试
            if lang == 'python':
                print_debug += len(re.findall(r'^\s*print\s*\(', c, re.MULTILINE))
                bare_except += len(re.findall(r'^\s*except\s*:', c, re.MULTILINE))
                wildcard_import += len(re.findall(r'^from \S+ import \*', c, re.MULTILINE))
            elif lang in ('javascript', 'typescript'):
                print_debug += len(re.findall(r'console\.(log|debug|info)\s*\(', c, re.MULTILINE))

            # 硬编码检测（通用）
            hardcoded += len(re.findall(
                r'(?:password|secret|api_key|apikey|token|private_key)\s*=\s*["\'][^"\']{3,}',
                c, re.IGNORECASE))

            # TODO/FIXME
            todo_count += len(re.findall(r'#\s*TODO|//\s*TODO', c, re.IGNORECASE))
            fixme_count += len(re.findall(r'#\s*FIXME|//\s*FIXME', c, re.IGNORECASE))

        if print_debug > 3:
            issues.append({'type': 'print_debug', 'count': print_debug,
                           'desc': f'发现 {print_debug} 处调试打印语句'})
        if bare_except > 0:
            issues.append({'type': 'bare_except', 'count': bare_except,
                           'desc': f'发现 {bare_except} 处裸 except:'})
        if wildcard_import > 0:
            issues.append({'type': 'wildcard_import', 'count': wildcard_import,
                           'desc': f'发现 {wildcard_import} 处 import *'})
        if hardcoded > 0:
            issues.append({'type': 'hardcoded_secret', 'count': hardcoded,
                           'desc': f'发现 {hardcoded} 处疑似硬编码密钥'})
        if todo_count > 5:
            issues.append({'type': 'todo', 'count': todo_count,
                           'desc': f'发现 {todo_count} 处 TODO 注释'})
        return issues

    # ---- 架构线索检测 ----
    def _detect_architecture_hints(self, files: list) -> list:
        """从目录结构和文件模式推断架构类型"""
        hints = []
        rels = [os.path.relpath(f, self.project_path) for f in files]
        dirs = set()
        for r in rels:
            parts = r.split(os.sep)
            if len(parts) > 1:
                dirs.add(parts[0])

        # CLI 工具检测
        root_files = os.listdir(self.project_path)
        if any(f in root_files for f in ('pyproject.toml', 'setup.py', 'Cargo.toml')) and \
           any(d in dirs for d in ('src', 'lib')):
            if os.path.exists(os.path.join(self.project_path, 'src')) and \
               not any(d in dirs for d in ('app', 'web', 'api', 'server')):
                hints.append('CLI 工具 / 库')

        # Web 应用检测
        if any(d in dirs for d in ('app', 'web', 'api', 'server', 'routes', 'controllers', 'views')):
            hints.append('Web 应用')
        if 'pages' in dirs or 'components' in dirs:
            hints.append('前端 SPA')
        if os.path.exists(os.path.join(self.project_path, 'manage.py')):
            hints.append('Django 项目')

        # Monorepo 检测
        if any(d in dirs for d in ('packages', 'apps', 'services', 'modules')):
            hints.append('Monorepo')

        # 微服务检测
        docker_compose = any(f in root_files for f in ('docker-compose.yml', 'docker-compose.yaml'))
        if docker_compose and len([d for d in dirs if d not in ('docs', 'scripts', 'test', 'tests')]) > 3:
            hints.append('微服务 / 多容器')

        # 模板/工具包检测
        if 'templates' in dirs and 'scripts' in dirs:
            hints.append('工具包 / 模板集')

        return hints if hints else ['通用项目']

    # ---- 日志风格检测 ----
    def _detect_logging_style(self, samples: list) -> dict:
        """检测日志使用方式"""
        patterns = Counter()
        for s in samples:
            c = s['content']
            if re.search(r'logger\.\w+\s*\(', c):
                patterns['logger.*()'] += 1
            if re.search(r'logging\.\w+\s*\(', c):
                patterns['logging.*()'] += 1
            if re.search(r'console\.\w+\s*\(', c):
                patterns['console.*()'] += 1
            if re.search(r'log\.\w+\s*\(', c):
                patterns['log.*()'] += 1
            if re.search(r'print\s*\(', c):
                patterns['print()'] += 1
            if re.search(r'fmt\.Print', c):
                patterns['fmt.Print*()'] += 1
        return {'primary': patterns.most_common(1)[0][0] if patterns else 'unknown',
                'all': dict(patterns)}

    # ---- 错误处理风格检测 ----
    def _detect_error_handling(self, samples: list) -> dict:
        """检测错误处理模式"""
        patterns = Counter()
        for s in samples:
            c = s['content']
            if s['lang'] == 'python':
                patterns['try/except'] += len(re.findall(r'^\s*try\s*:', c, re.MULTILINE))
                patterns['raise'] += len(re.findall(r'^\s*raise\s', c, re.MULTILINE))
            elif s['lang'] in ('javascript', 'typescript'):
                patterns['try/catch'] += len(re.findall(r'\btry\s*\{', c))
                patterns['throw'] += len(re.findall(r'\bthrow\s', c))
                patterns['.catch()'] += len(re.findall(r'\.catch\s*\(', c))
            elif s['lang'] == 'go':
                patterns['if err != nil'] += len(re.findall(r'if\s+err\s*!=\s*nil', c))
            elif s['lang'] == 'rust':
                patterns['Result<>'] += len(re.findall(r'Result<', c))
                patterns['?'] += len(re.findall(r'\?\s*;', c))
        return dict(patterns)

    # ---- 环境变量检测 ----
    def _detect_env_vars(self, samples: list) -> list:
        """检测代码中使用的环境变量"""
        env_vars = set()
        for s in samples:
            c = s['content']
            lang = s['lang']
            # Python: os.getenv / os.environ
            for m in re.finditer(r"os\.(?:getenv|environ(?:\.get)?)\s*\(\s*['\"](\w+)", c):
                env_vars.add(m.group(1))
            # JS/TS: process.env
            for m in re.finditer(r'process\.env\.(\w+)', c):
                env_vars.add(m.group(1))
            # Go: os.Getenv
            for m in re.finditer(r'os\.Getenv\s*\(\s*"(\w+)"', c):
                env_vars.add(m.group(1))
            # Shell: only exported vars or vars read from env
            if lang == 'shell':
                for m in re.finditer(r'export\s+(\w+)=', c):
                    env_vars.add(m.group(1))
                for m in re.finditer(r'\$\{(\w+):-', c):  # ${VAR:-default} pattern
                    env_vars.add(m.group(1))
            # .env file patterns in configs (KEY=value)
            elif s['path'].endswith(('.env', '.env.example', '.env.local')):
                for m in re.finditer(r'^(\w+)=', c, re.MULTILINE):
                    env_vars.add(m.group(1))
        # 过滤常见 OS/shell 内置变量和过短的名称
        noise = {'HOME', 'PATH', 'USER', 'SHELL', 'PWD', 'LANG', 'TERM',
                 'HOSTNAME', 'OLDPWD', 'SHLVL', 'TMPDIR', 'LOGNAME',
                 'LC_ALL', 'LC_CTYPE', 'EDITOR', 'VISUAL', 'PAGER',
                 'PS1', 'PS2', 'IFS', 'BASH', 'ZSH', 'RANDOM', 'LINENO',
                 'SECONDS', 'PPID', 'UID', 'EUID', 'GROUPS'}
        return sorted(v for v in env_vars - noise if len(v) > 2)


def scan_project(project_path: str) -> dict:
    """扫描项目文件，提取项目上下文事实数据"""
    result = {
        'languages': Counter(),        # 语言 → 文件数
        'frameworks': [],               # 检测到的框架
        'middleware': [],               # 中间件
        'build_tools': [],              # 构建工具
        'ci_cd': [],                    # CI/CD
        'containerization': [],         # 容器化
        'config_files': [],             # 配置文件列表
        'env_files': [],                # 环境配置文件
        'dir_structure': {},            # 顶层目录结构
        'package_info': {},             # 包管理信息（名称、版本、依赖）
        'python_version': None,
        'node_version': None,
        'java_version': None,
        'total_files': 0,
    }

    skip_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                 '.tox', '.mypy_cache', '.pytest_cache', 'dist', 'build',
                 '.gitnexus', '.claude', '.specify', '.next', '.nuxt',
                 'target', 'vendor', '.idea', '.vscode'}

    # 1. 扫描文件
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        rel_root = os.path.relpath(root, project_path)

        for f in files:
            result['total_files'] += 1
            ext = os.path.splitext(f)[1].lower()
            if ext in EXT_LANG_MAP:
                result['languages'][EXT_LANG_MAP[ext]] += 1

            # 检测配置文件
            if f in CONFIG_TECH_MAP:
                tech = CONFIG_TECH_MAP[f]
                if tech not in [x for x in result['build_tools'] + result['ci_cd'] + result['containerization']]:
                    if 'CI' in tech or 'Actions' in tech:
                        _add_unique(result['ci_cd'], tech)
                    elif 'Docker' in tech or 'Kubernetes' in tech or 'Helm' in tech:
                        _add_unique(result['containerization'], tech)
                    else:
                        _add_unique(result['build_tools'], tech)

            # 环境文件
            if f in ('.env', '.env.example', '.env.local', '.env.production',
                     '.env.development', '.env.test'):
                result['env_files'].append(os.path.join(rel_root, f))

            # 配置文件
            if f.endswith(('.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.json')) and rel_root == '.':
                result['config_files'].append(f)

    # 检查 .github/workflows
    workflows_dir = os.path.join(project_path, '.github', 'workflows')
    if os.path.isdir(workflows_dir):
        _add_unique(result['ci_cd'], 'GitHub Actions')

    # 2. 顶层目录结构
    for entry in sorted(os.listdir(project_path)):
        full = os.path.join(project_path, entry)
        if entry.startswith('.') or entry in skip_dirs:
            continue
        if os.path.isdir(full):
            # 计算子文件数
            count = sum(1 for _, _, fs in os.walk(full) for _ in fs)
            result['dir_structure'][entry] = {'type': 'dir', 'files': count}
        elif os.path.isfile(full):
            result['dir_structure'][entry] = {'type': 'file', 'size': os.path.getsize(full)}

    # 3. 解析包管理文件获取依赖
    _parse_package_json(project_path, result)
    _parse_pyproject_toml(project_path, result)
    _parse_requirements_txt(project_path, result)
    _parse_go_mod(project_path, result)
    _parse_pom_xml(project_path, result)

    return result


def _add_unique(lst: list, item: str):
    if item not in lst:
        lst.append(item)


def _parse_package_json(project_path: str, result: dict):
    """解析 package.json"""
    pj = os.path.join(project_path, 'package.json')
    if not os.path.exists(pj):
        return
    try:
        with open(pj, 'r', encoding='utf-8') as f:
            data = json.load(f)
        result['package_info']['name'] = data.get('name', '')
        result['package_info']['version'] = data.get('version', '')

        # Node 版本
        engines = data.get('engines', {})
        if 'node' in engines:
            result['node_version'] = engines['node']

        # 合并所有依赖
        all_deps = {}
        all_deps.update(data.get('dependencies', {}))
        all_deps.update(data.get('devDependencies', {}))

        _detect_frameworks(all_deps.keys(), result)
        _add_unique(result['build_tools'], 'npm')
    except (json.JSONDecodeError, IOError):
        pass


def _parse_pyproject_toml(project_path: str, result: dict):
    """解析 pyproject.toml（简单解析，不依赖 tomllib）"""
    pt = os.path.join(project_path, 'pyproject.toml')
    if not os.path.exists(pt):
        return
    try:
        with open(pt, 'r', encoding='utf-8') as f:
            content = f.read()

        # 项目名
        m = re.search(r'^name\s*=\s*"(.+?)"', content, re.MULTILINE)
        if m:
            result['package_info']['name'] = m.group(1)
        m = re.search(r'^version\s*=\s*"(.+?)"', content, re.MULTILINE)
        if m:
            result['package_info']['version'] = m.group(1)

        # Python 版本
        m = re.search(r'requires-python\s*=\s*"(.+?)"', content)
        if m:
            result['python_version'] = m.group(1)

        # 依赖
        deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if deps_match:
            deps_str = deps_match.group(1)
            dep_names = re.findall(r'"([a-zA-Z0-9_-]+)', deps_str)
            _detect_frameworks(dep_names, result)

        # 构建工具
        if 'hatchling' in content:
            _add_unique(result['build_tools'], 'Hatch')
        if 'setuptools' in content:
            _add_unique(result['build_tools'], 'setuptools')
        if 'poetry' in content:
            _add_unique(result['build_tools'], 'Poetry')
        if 'flit' in content:
            _add_unique(result['build_tools'], 'Flit')

        _add_unique(result['build_tools'], 'pip')
    except IOError:
        pass


def _parse_requirements_txt(project_path: str, result: dict):
    """解析 requirements.txt"""
    for name in ('requirements.txt', 'requirements-dev.txt', 'requirements/base.txt'):
        rp = os.path.join(project_path, name)
        if os.path.exists(rp):
            try:
                with open(rp, 'r', encoding='utf-8') as f:
                    deps = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('-'):
                            dep = re.split(r'[>=<!\[\];]', line)[0].strip()
                            if dep:
                                deps.append(dep.lower())
                    _detect_frameworks(deps, result)
            except IOError:
                pass


def _parse_go_mod(project_path: str, result: dict):
    """解析 go.mod"""
    gm = os.path.join(project_path, 'go.mod')
    if not os.path.exists(gm):
        return
    try:
        with open(gm, 'r', encoding='utf-8') as f:
            content = f.read()
        m = re.search(r'^go\s+(\S+)', content, re.MULTILINE)
        if m:
            result['package_info']['go_version'] = m.group(1)
        # 检测框架
        deps = re.findall(r'^\s+(\S+)', content, re.MULTILINE)
        for dep in deps:
            dep_short = dep.split('/')[-1].lower()
            _detect_frameworks([dep_short], result)
    except IOError:
        pass


def _parse_pom_xml(project_path: str, result: dict):
    """简单解析 pom.xml"""
    pom = os.path.join(project_path, 'pom.xml')
    if not os.path.exists(pom):
        return
    try:
        with open(pom, 'r', encoding='utf-8') as f:
            content = f.read()
        # Java 版本
        m = re.search(r'<java.version>(.+?)</java.version>', content)
        if m:
            result['java_version'] = m.group(1)
        # Spring Boot
        if 'spring-boot' in content:
            _add_unique(result['frameworks'], 'Spring Boot')
            m = re.search(r'<spring-boot.version>(.+?)</spring-boot.version>', content)
            if not m:
                m = re.search(r'spring-boot-starter-parent.*?<version>(.+?)</version>', content, re.DOTALL)
        if 'mybatis' in content.lower():
            _add_unique(result['frameworks'], 'MyBatis')
        _add_unique(result['build_tools'], 'Maven')
    except IOError:
        pass


def _detect_frameworks(dep_names, result: dict):
    """从依赖名列表中检测框架和中间件"""
    for dep in dep_names:
        dep_lower = dep.lower().replace('_', '-')
        if dep_lower in FRAMEWORK_PATTERNS:
            tech = FRAMEWORK_PATTERNS[dep_lower]
            if tech in ('Redis', 'Elasticsearch', 'Kafka', 'RabbitMQ',
                        'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite'):
                _add_unique(result['middleware'], tech)
            else:
                _add_unique(result['frameworks'], tech)


# ============================================================
# 二、项目事实采集器 —— 整合扫描 + 代码模式 + GitNexus
# ============================================================

def collect_project_facts(project_path: str) -> dict:
    """采集所有项目事实数据，整合为统一结构"""
    # 1. 基础文件扫描
    scan = scan_project(project_path)

    # 2. 代码模式检测
    detector = CodePatternDetector(project_path)
    code_patterns = detector.detect_all()

    # 3. README 摘要
    readme_summary = _read_readme_summary(project_path)

    # 4. GitNexus 数据
    meta = load_gitnexus_meta(project_path)
    skills = load_gitnexus_skills(project_path)

    # 5. 整合为统一结构
    facts = {
        'generated_at': datetime.now().isoformat(),
        'project_name': scan.get('package_info', {}).get('name') or os.path.basename(os.path.abspath(project_path)),
        'project_facts': {
            'languages': dict(scan['languages'].most_common()),
            'frameworks': scan['frameworks'],
            'middleware': scan['middleware'],
            'build_tools': scan['build_tools'],
            'ci_cd': scan['ci_cd'],
            'containerization': scan['containerization'],
            'versions': {
                'python': scan.get('python_version'),
                'node': scan.get('node_version'),
                'java': scan.get('java_version'),
                'go': scan.get('package_info', {}).get('go_version'),
                'project': scan.get('package_info', {}).get('version'),
            },
        },
        'structure_facts': {
            'dir_structure': scan['dir_structure'],
            'total_files': scan['total_files'],
            'config_files': scan['config_files'],
            'env_files': scan['env_files'],
            'architecture_hints': code_patterns.get('architecture_hints', []),
        },
        'code_patterns': code_patterns,
        'code_graph': {
            'meta': meta.get('stats', {}),
            'module_count': len(skills),
            'modules': [
                {
                    'name': s['name'],
                    'stats': s['parsed'].get('stats', ''),
                    'entry_points': s['parsed'].get('entry_points', []),
                    'key_files': s['parsed'].get('key_files', []),
                    'connected_areas': s['parsed'].get('connected_areas', []),
                    'execution_flows': s['parsed'].get('execution_flows', []),
                }
                for s in skills
            ],
        },
        'doc_facts': {
            'readme_summary': readme_summary,
        },
    }
    return facts


def _get_dir_purpose(dirname: str) -> str:
    """根据目录名返回用途说明"""
    purposes = {
        'src': '核心源代码',
        'scripts': '分析/生成脚本',
        'templates': '模板文件',
        'docs': '文档',
        'tests': '测试代码',
        'test': '测试代码',
        'ecc-components': 'ECC组件',
        'media': '媒体资源',
        'memory': '项目记忆',
        'dist': '构建输出',
        'build': '构建输出',
        '.github': 'CI/CD配置',
        '.specify': 'Specify配置',
    }
    return purposes.get(dirname, f'({dirname})')


def _read_readme_summary(project_path: str) -> str:
    for name in ('README.md', 'README.rst', 'README.txt', 'README'):
        readme_path = os.path.join(project_path, name)
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[:30]
                # 提取第一段非标题、非空行的文本
                paragraphs = []
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#') and not stripped.startswith('=') \
                            and not stripped.startswith('-') and not stripped.startswith('[!'):
                        paragraphs.append(stripped)
                    elif paragraphs:
                        break
                return ' '.join(paragraphs)[:300] if paragraphs else ''
            except IOError:
                pass
    return ''


def save_context_facts(facts: dict, output_dir: str):
    """保存事实数据为 JSON 文件"""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, '.context-facts.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(facts, f, ensure_ascii=False, indent=2)
    return path


# ============================================================
# 三、GitNexus 数据加载与解析
# ============================================================

def load_gitnexus_meta(project_path: str) -> dict:
    """加载 .gitnexus/meta.json"""
    meta_path = os.path.join(project_path, '.gitnexus', 'meta.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_gitnexus_skills(project_path: str) -> list:
    """加载所有 GitNexus 生成的 SKILL.md 文件"""
    skills_dir = os.path.join(project_path, '.claude', 'skills', 'generated')
    if not os.path.isdir(skills_dir):
        return []

    skills = []
    for entry in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, entry, 'SKILL.md')
        if os.path.isfile(skill_path):
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
            skills.append({
                'name': entry,
                'path': skill_path,
                'content': content,
                'parsed': parse_skill_md(content),
            })
    return skills


def parse_skill_md(content: str) -> dict:
    """解析 GitNexus SKILL.md 提取结构化数据"""
    result = {
        'title': '', 'stats': '',
        'key_files': [], 'entry_points': [], 'key_symbols': [],
        'execution_flows': [], 'connected_areas': [],
    }

    lines = content.split('\n')
    current_section = ''
    table_rows = []

    for line in lines:
        if line.startswith('# ') and not result['title']:
            result['title'] = line[2:].strip()
            continue
        if re.match(r'^\d+ symbols', line):
            result['stats'] = line.strip()
            continue
        if line.startswith('## '):
            if current_section and table_rows:
                _store_table(result, current_section, table_rows)
                table_rows = []
            current_section = line[3:].strip()
            continue
        if line.startswith('|') and '---' not in line:
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if cells and not all(c.startswith('-') for c in cells):
                table_rows.append(cells)
            continue
        if current_section == 'Entry Points' and line.startswith('- **'):
            match = re.match(r'- \*\*`(.+?)`\*\* \((\w+)\) — `(.+?):(\d+)`', line)
            if match:
                result['entry_points'].append({
                    'name': match.group(1), 'type': match.group(2),
                    'file': match.group(3), 'line': int(match.group(4)),
                })

    if current_section and table_rows:
        _store_table(result, current_section, table_rows)
    return result


def _store_table(result: dict, section: str, rows: list):
    """存储表格数据到对应的结果字段"""
    if section == 'Key Files':
        for row in rows:
            if len(row) >= 2:
                result['key_files'].append({'file': row[0].strip('` '), 'symbols': row[1]})
    elif section == 'Key Symbols':
        for row in rows:
            if len(row) >= 4:
                result['key_symbols'].append({
                    'name': row[0].strip('` '), 'type': row[1],
                    'file': row[2].strip('` '), 'line': row[3],
                })
    elif section == 'Execution Flows':
        for row in rows:
            if len(row) >= 3:
                result['execution_flows'].append({'flow': row[0], 'type': row[1], 'steps': row[2]})
    elif section == 'Connected Areas':
        for row in rows:
            if len(row) >= 2:
                result['connected_areas'].append({'area': row[0], 'connections': row[1]})


# ============================================================
# 三、Skill 文档生成 —— 五大项目上下文维度
# ============================================================

def generate_project_context_skill(scan: dict, meta: dict, skills: list, project_path: str,
                                    facts: dict = None) -> str:
    """生成主 SKILL.md —— 项目全局上下文（facts 参数提供代码模式检测数据）"""
    project_name = scan.get('package_info', {}).get('name') or os.path.basename(os.path.abspath(project_path))
    now = datetime.now().isoformat()
    stats = meta.get('stats', {})
    cp = (facts or {}).get('code_patterns', {})  # code patterns shortcuts
    readme_summary = (facts or {}).get('doc_facts', {}).get('readme_summary', '')
    L = []  # lines collector

    # --- YAML front matter (遵循 Skill 规范) ---
    L.append("---")
    L.append(f"name: {project_name}-context")
    L.append(f"description: {project_name} 项目的技术栈、结构、方案、规范和环境上下文")
    L.append("version: 1.0.0")
    L.append(f"updated: {datetime.now().strftime('%Y-%m-%d')}")
    L.append("---")
    L.append("")

    # --- 标题 ---
    L.append(f"# {project_name} 项目上下文")
    L.append("")
    if readme_summary:
        L.append(f"> {readme_summary}")
    else:
        L.append("> {{LLM_PROJECT_SUMMARY}}")
        L.append("> <!-- 填充指导: 一句话概述项目用途和特点（20-50字） -->")
    L.append("")

    # ========================================
    # 1. 技术栈上下文
    # ========================================
    L.append("---")
    L.append("")
    L.append("## 一、技术栈上下文（用什么技术？）")
    L.append("")

    # 语言
    L.append("### 编程语言")
    L.append("")
    if scan['languages']:
        sorted_langs = scan['languages'].most_common()
        total = sum(c for _, c in sorted_langs)
        L.append("| 语言 | 文件数 | 占比 |")
        L.append("|------|--------|------|")
        for lang, count in sorted_langs:
            pct = f"{count/total*100:.0f}%"
            L.append(f"| **{lang}** | {count} | {pct} |")
        L.append("")
    else:
        L.append("（未检测到源代码文件）")
        L.append("")

    # 框架
    L.append("### 框架")
    L.append("")
    if scan['frameworks']:
        for fw in scan['frameworks']:
            L.append(f"- **{fw}**")
    else:
        L.append("{{LLM_FRAMEWORKS}}")
        L.append("<!-- 填充指导: 阅读代码中的 import 语句和配置文件，识别使用的框架 -->")
    L.append("")

    # 中间件/数据库
    L.append("### 中间件与数据存储")
    L.append("")
    if scan['middleware']:
        for mw in scan['middleware']:
            L.append(f"- **{mw}**")
    else:
        L.append("{{LLM_MIDDLEWARE}}")
        L.append("<!-- 填充指导: 从配置文件和依赖中识别使用的数据库、缓存、消息队列等中间件 -->")
    L.append("")

    # 构建工具
    L.append("### 构建与工具链")
    L.append("")
    items = []
    if scan['build_tools']:
        items += [f"**构建**: {', '.join(scan['build_tools'])}"]
    if scan['ci_cd']:
        items += [f"**CI/CD**: {', '.join(scan['ci_cd'])}"]
    if scan['containerization']:
        items += [f"**容器化**: {', '.join(scan['containerization'])}"]
    if items:
        for item in items:
            L.append(f"- {item}")
    else:
        L.append("（未检测到构建工具）")
    L.append("")

    # 版本
    L.append("### 版本约束")
    L.append("")
    versions = []
    if scan['python_version']:
        versions.append(f"- **Python**: `{scan['python_version']}`")
    if scan['node_version']:
        versions.append(f"- **Node.js**: `{scan['node_version']}`")
    if scan['java_version']:
        versions.append(f"- **JDK**: `{scan['java_version']}`")
    pkg = scan.get('package_info', {})
    if pkg.get('go_version'):
        versions.append(f"- **Go**: `{pkg['go_version']}`")
    if pkg.get('version'):
        versions.append(f"- **项目版本**: `{pkg['version']}`")
    if versions:
        L.extend(versions)
    else:
        L.append("{{LLM_VERSIONS}}")
        L.append("<!-- 填充指导: 从配置文件中识别语言和依赖的版本约束 -->")
    L.append("")

    # ========================================
    # 2. 项目结构上下文
    # ========================================
    L.append("---")
    L.append("")
    L.append("## 二、项目结构上下文（代码怎么组织？）")
    L.append("")

    # 整体架构
    L.append("### 整体架构")
    L.append("")
    arch_hints = cp.get('architecture_hints', [])
    if arch_hints:
        L.append(f"**架构类型**: {' + '.join(arch_hints)}")
        L.append("")
        L.append("{{LLM_ARCHITECTURE_DETAIL}}")
        L.append("<!-- 填充指导: 基于上方自动检测的架构类型，补充 1-2 句描述：")
        L.append("     项目的分层方式、核心模块职责划分、前后端关系等 -->")
    else:
        L.append("{{LLM_ARCHITECTURE}}")
        L.append("<!-- 填充指导: 根据目录结构和模块关系，判断项目架构类型：")
        L.append("     微服务 / 单体 / 前后端分离 / monorepo / CLI 工具 / 库 -->")
    L.append("")

    # 目录结构（带用途说明）
    top_dirs = scan['dir_structure']
    if top_dirs:
        L.append("### 目录结构")
        L.append("")
        L.append("```")
        L.append(f"{project_name}/")
        for name, info in sorted(top_dirs.items(), key=lambda x: (0 if x[1]['type'] == 'file' else 1, x[0])):
            if info['type'] == 'dir':
                # 添加目录用途注释
                purpose = _get_dir_purpose(name)
                L.append(f"├── {name}/{' ' * max(1, 18-len(name))}# {purpose}")
            else:
                L.append(f"├── {name}")
        L.append("```")
        L.append("")

    # 功能模块映射（目录 → 功能）
    if skills:
        L.append("### 功能模块映射")
        L.append("")
        L.append("物理目录与功能职责的对应关系：")
        L.append("")
        L.append("| 目录 | 功能聚类 | 核心职责 | 文件数 |")
        L.append("|------|----------|----------|--------|")

        # 按目录分组聚类
        dir_to_clusters = {}
        for skill in skills:
            parsed = skill['parsed']
            stats_match = re.match(r'(\d+) symbols \| (\d+) files \| Cohesion: (\d+%)', parsed.get('stats', ''))
            files = stats_match.group(2) if stats_match else '?'
            cohesion = stats_match.group(3) if stats_match else '?'
            # 提取目录
            dirs = set()
            for kf in parsed.get('key_files', [])[:3]:
                parts = kf['file'].split('/')
                if len(parts) >= 2:
                    dirs.add(parts[0])
            for d in dirs:
                if d not in dir_to_clusters:
                    dir_to_clusters[d] = []
                dir_to_clusters[d].append({
                    'name': skill['name'],
                    'title': parsed.get('title', skill['name']),
                    'files': files,
                    'cohesion': cohesion,
                })

        # 输出表格（优先显示重要目录）
        priority_dirs = ['src', 'scripts', 'templates', 'ecc-components', 'docs']
        sorted_dirs = sorted(dir_to_clusters.keys(),
                            key=lambda x: (priority_dirs.index(x) if x in priority_dirs else 99, x))

        for d in sorted_dirs:
            clusters = dir_to_clusters[d]
            names = [c['name'] for c in clusters]
            titles = [c['title'] for c in clusters]
            total_files = sum(int(c['files']) for c in clusters if c['files'].isdigit())
            # 核心职责取前2个聚类标题
            purpose = ' / '.join(titles[:2]) if titles else '-'
            L.append(f"| `{d}/` | {', '.join(names[:3])} | {purpose} | {total_files} |")
        L.append("")
        L.append("> 注：聚类名（如 Analyzer, Generator）是 GitNexus 根据代码调用关系自动识别的功能模块，详见各模块详情文件（`analyzer.md`, `generator.md` 等）")
        L.append("")

    # ========================================
    # 3. 技术方案上下文（精简版）
    # ========================================
    L.append("---")
    L.append("")
    L.append("## 三、技术方案上下文（业务怎么实现？）")
    L.append("")
    L.append("技术方案详情见各模块文件（入口点、执行流、关键符号）：")
    L.append("")
    for skill in skills[:5]:  # 只列前5个核心模块
        title = skill['parsed'].get('title', skill['name'])
        eps = skill['parsed'].get('entry_points', [])
        flows = skill['parsed'].get('execution_flows', [])
        L.append(f"- `{skill['name']}.md` — {title} — {len(eps)} 入口点, {len(flows)} 执行流")
    L.append("")

    # 业务流程和设计模式 — 需要 LLM 推理
    L.append("### 核心业务流程")
    L.append("")
    L.append("{{LLM_BUSINESS_FLOWS}}")
    L.append("<!-- 填充指导: 根据上方入口点和执行流，用自然语言描述核心业务流程，例如：")
    L.append("     用户注册 → 参数校验 → 密码加密 → 入库 → 发送通知")
    L.append("     订单创建 → 库存检查 → 支付调用 → 状态更新 → 异步通知 -->")
    L.append("")

    L.append("### 设计模式与架构决策")
    L.append("")
    L.append("{{LLM_DESIGN_PATTERNS}}")
    L.append("<!-- 填充指导: 根据代码结构识别使用的设计模式，例如：")
    L.append("     - 工厂模式: XxxFactory 类")
    L.append("     - 策略模式: 多个 Handler 实现")
    L.append("     - 中间件模式: 请求处理链")
    L.append("     - 观察者模式: 事件发布/订阅 -->")
    L.append("")

    # ========================================
    # 4. 开发规范上下文
    # ========================================
    L.append("---")
    L.append("")
    L.append("## 四、开发规范上下文（代码怎么写才合规？）")
    L.append("")

    # 项目核心原则（吸收 constitution.md 结构）
    L.append("### 项目核心原则")
    L.append("")
    L.append("{{LLM_CORE_PRINCIPLES}}")
    L.append("<!-- 填充指导: 根据项目特点提炼 3-5 条核心原则，参考格式：")
    L.append("     1. **库优先**: 每个功能从独立库开始，自包含、可测试、有明确目的")
    L.append("     2. **CLI 接口**: 通过 CLI 暴露功能，stdin/args → stdout，错误 → stderr")
    L.append("     3. **测试优先**: TDD 强制要求，红-绿-重构循环")
    L.append("     4. **简单性**: 从简单开始，YAGNI 原则，复杂性需被证明")
    L.append("     5. **可观测性**: 文本 I/O 确保可调试，需要结构化日志 -->")
    L.append("")

    L.append("### 命名规范")
    L.append("")
    naming = cp.get('naming', {})
    if naming and naming.get('function_style') != 'unknown':
        func_style = naming.get('function_style', 'unknown')
        class_style = naming.get('class_style', 'unknown')
        file_style = naming.get('file_style', 'unknown')
        func_ex = naming.get('function_examples', [])[:5]
        class_ex = naming.get('class_examples', [])[:5]
        L.append(f"- **函数/方法**: `{func_style}`")
        if func_ex:
            L.append(f"  — 如 {', '.join(f'`{e}`' for e in func_ex)}")
        L.append(f"- **类名**: `{class_style}`")
        if class_ex:
            L.append(f"  — 如 {', '.join(f'`{e}`' for e in class_ex)}")
        L.append(f"- **文件名**: `{file_style}`")
        L.append(f"- **常量**: `UPPER_SNAKE_CASE`")
        L.append("")
        L.append("{{LLM_NAMING_EXTRA}}")
        L.append("<!-- 填充指导: 补充上述自动检测遗漏的命名规范（如接口路径前缀 /api/v1/ 等） -->")
    else:
        L.append("{{LLM_NAMING_CONVENTIONS}}")
        L.append("<!-- 填充指导: 从代码中提炼命名规范：函数/变量/类名/文件名/常量 -->")
    L.append("")

    L.append("### 代码风格")
    L.append("")
    indent = cp.get('indentation', {})
    docstyle = cp.get('docstring_style', {})
    impstyle = cp.get('import_style', {})
    logstyle = cp.get('logging_style', {})
    errhandling = cp.get('error_handling', {})
    has_style_facts = indent.get('style') != 'unknown' or docstyle.get('style') != 'unknown'
    if has_style_facts:
        if indent.get('detail'):
            L.append(f"- **缩进**: {indent['detail']}")
        if docstyle.get('style') and docstyle['style'] != 'unknown':
            L.append(f"- **文档注释**: {docstyle['style']} 风格")
        if impstyle.get('style'):
            L.append(f"- **导入**: {impstyle['style']}")
        if logstyle.get('primary') and logstyle['primary'] != 'unknown':
            L.append(f"- **日志**: `{logstyle['primary']}`")
        if errhandling:
            top_err = sorted(errhandling.items(), key=lambda x: -x[1])[:2]
            if top_err:
                L.append(f"- **错误处理**: {', '.join(f'`{k}` ({v}处)' for k, v in top_err)}")
        L.append("")
        L.append("{{LLM_CODE_STYLE_EXTRA}}")
        L.append("<!-- 填充指导: 补充上述自动检测遗漏的代码风格规范 -->")
    else:
        L.append("{{LLM_CODE_STYLE}}")
        L.append("<!-- 填充指导: 从代码和配置中提炼代码风格：缩进、注释、异常处理、日志、导入顺序 -->")
    L.append("")

    L.append("### 禁止规则")
    L.append("")
    anti = cp.get('anti_patterns', [])
    if anti:
        for ap in anti:
            L.append(f"- ❌ {ap['desc']}")
        L.append("")
        L.append("{{LLM_FORBIDDEN_EXTRA}}")
        L.append("<!-- 填充指导: 补充上述自动检测遗漏的禁止规则 -->")
    else:
        L.append("{{LLM_FORBIDDEN_RULES}}")
        L.append("<!-- 填充指导: 列出禁止的编码行为：print调试、裸except、硬编码密钥、import * 等 -->")
    L.append("")

    L.append("### 错误处理")
    L.append("")
    L.append("{{LLM_ERROR_HANDLING}}")
    L.append("<!-- 填充指导: 从代码中提炼错误处理方式：异常类型、错误码、日志记录、用户提示 -->")
    L.append("")

    # ========================================
    # 4.5 API 规范
    # ========================================
    L.append("---")
    L.append("")
    L.append("## API 规范")
    L.append("")
    L.append("{{LLM_API_SPEC}}")
    L.append("<!-- 填充指导: 从路由和接口定义中提炼：URL风格、请求/响应格式、认证方式、版本控制 -->")
    L.append("")

    # ========================================
    # 4.6 测试规范
    # ========================================
    L.append("## 测试规范")
    L.append("")
    L.append("{{LLM_TEST_SPEC}}")
    L.append("<!-- 填充指导: 从测试代码中提炼：测试框架、覆盖率要求、测试命名、mock策略 -->")
    L.append("")

    # ========================================
    # 5. 环境与配置上下文
    # ========================================
    L.append("---")
    L.append("")
    L.append("## 五、环境与配置上下文（运行依赖什么？）")
    L.append("")

    L.append("### 配置文件")
    L.append("")
    if scan['config_files']:
        for cf in sorted(scan['config_files']):
            L.append(f"- `{cf}`")
    else:
        L.append("（未检测到根目录配置文件）")
    L.append("")

    L.append("### 环境变量")
    L.append("")
    env_vars = cp.get('env_vars_in_code', [])
    if scan['env_files']:
        L.append("**环境文件**:")
        for ef in scan['env_files']:
            L.append(f"- `{ef}`")
        L.append("")
    if env_vars:
        L.append("**代码中使用的环境变量**:")
        L.append("")
        for ev in env_vars[:20]:
            L.append(f"- `{ev}`")
        L.append("")
        if len(env_vars) > 20:
            L.append(f"（共 {len(env_vars)} 个，仅显示前 20 个）")
            L.append("")
    elif not scan['env_files']:
        L.append("{{LLM_ENV_VARIABLES}}")
        L.append("<!-- 填充指导: 识别代码中使用的环境变量（os.getenv / process.env 等） -->")
    L.append("")

    L.append("### 部署方式")
    L.append("")
    deploy_hints = []
    if scan['containerization']:
        deploy_hints.append(f"- **容器化**: {', '.join(scan['containerization'])}")
    if scan['ci_cd']:
        deploy_hints.append(f"- **CI/CD**: {', '.join(scan['ci_cd'])}")
    if deploy_hints:
        L.extend(deploy_hints)
        L.append("")
    L.append("{{LLM_DEPLOYMENT}}")
    L.append("<!-- 填充指导: 描述项目的部署方式、运行命令和启动流程 -->")
    L.append("")

    # ========================================
    # 附录：模块详情导航
    # ========================================
    if skills:
        L.append("---")
        L.append("")
        L.append("## 附录：模块详情导航")
        L.append("")
        L.append(f"GitNexus 已识别出 {len(skills)} 个功能模块（如 {skills[0]['name']}, {skills[1]['name'] if len(skills) > 1 else ''}...），")
        L.append("详见 `index.yaml` 或各模块 `.md` 文件（入口点、执行流、关键符号等详情）。")
        L.append("")

    return "\n".join(L)


def translate_to_chinese(content: str) -> str:
    """将 GitNexus 英文 SKILL.md 内容翻译为中文"""
    section_map = {
        '## When to Use': '## 使用场景',
        '## Key Files': '## 关键文件',
        '## Entry Points': '## 入口点',
        '## Key Symbols': '## 关键符号',
        '## Execution Flows': '## 执行流',
        '## Connected Areas': '## 关联模块',
        '## How to Explore': '## 探索方式',
    }
    for en, zh in section_map.items():
        content = content.replace(en, zh)

    table_header_map = {
        '| File | Symbols |': '| 文件 | 符号 |',
        '| Symbol | Type | File | Line |': '| 符号 | 类型 | 文件 | 行号 |',
        '| Flow | Type | Steps |': '| 执行流 | 类型 | 步骤数 |',
        '| Area | Connections |': '| 模块 | 连接数 |',
    }
    for en, zh in table_header_map.items():
        content = content.replace(en, zh)

    content = re.sub(r'(\d+) symbols \| (\d+) files \| Cohesion: (\d+%)',
                     r'\1 个符号 | \2 个文件 | 内聚度: \3', content)
    content = re.sub(r'- Working with code in ', '- 处理 ', content)
    content = re.sub(r'- Understanding how (.+?) work', r'- 理解 \1 的工作原理', content)
    content = re.sub(r'- Modifying (.+?)-related functionality', r'- 修改 \1 相关功能', content)
    content = content.replace('Start here when exploring this area:', '探索该模块的起点：')
    content = content.replace('cross_community', '跨模块')
    content = content.replace('intra_community', '模块内')

    type_map = {' Class ': ' 类 ', ' Function ': ' 函数 ', ' Method ': ' 方法 ',
                ' Variable ': ' 变量 ', ' Constant ': ' 常量 ', ' Module ': ' 模块 '}
    lines = content.split('\n')
    translated = []
    for line in lines:
        if line.startswith('|'):
            for en, zh in type_map.items():
                line = line.replace(en, zh)
        translated.append(line)
    content = '\n'.join(translated)

    content = re.sub(r'\(Function\)', '(函数)', content)
    content = re.sub(r'\(Class\)', '(类)', content)
    content = re.sub(r'\(Method\)', '(方法)', content)
    content = re.sub(r'(\d+) calls', r'\1 次调用', content)

    return content


def generate_module_skill(skill: dict) -> str:
    """将单个 GitNexus SKILL.md 转换为 Specify 模块 Skill 格式（中文）"""
    parsed = skill['parsed']
    name = skill['name']
    now = datetime.now().isoformat()

    sections = []
    sections.append("---")
    sections.append(f"name: {name}")
    sections.append(f"description: {parsed.get('title', name)} 模块的文件、符号、入口点和执行流详情")
    sections.append("version: 1.0.0")
    sections.append(f"updated: {datetime.now().strftime('%Y-%m-%d')}")
    sections.append("---")
    sections.append("")

    content = skill['content']
    if content.startswith('---'):
        end_idx = content.find('---', 3)
        if end_idx != -1:
            content = content[end_idx + 3:].strip()
    explore_idx = content.find('## How to Explore')
    if explore_idx != -1:
        content = content[:explore_idx].rstrip()

    content = translate_to_chinese(content)
    sections.append(content)
    sections.append("")

    return "\n".join(sections)


def generate_index_yaml(scan: dict, skills: list, meta: dict) -> str:
    """生成 index.yaml 索引文件"""
    now = datetime.now().isoformat()
    project_name = scan.get('package_info', {}).get('name', 'project')

    lines = [
        "# 项目上下文 Skill 索引",
        f"# 项目: {project_name}",
        f"# 生成时间: {now}",
        f"# 生成器: GitNexus 知识图谱 + 项目扫描器",
        "",
        "skills:",
        "  - id: project-context/SKILL",
        "    file: SKILL.md",
        "    description: 项目全局上下文（技术栈、结构、方案、规范、环境）",
    ]

    for skill in skills:
        sid = f"project-context/{skill['name']}"
        lines.append(f"  - id: {sid}")
        lines.append(f"    file: {skill['name']}.md")
        lines.append(f"    description: {skill['name'].title()} 模块详情")
        connected = skill['parsed'].get('connected_areas', [])
        if connected:
            dep_ids = [f"project-context/{c['area'].lower()}" for c in connected
                       if any(s['name'] == c['area'].lower() for s in skills)]
            if dep_ids:
                lines.append(f"    dependencies: {dep_ids}")

    lines.append("")
    lines.append("# 上下文维度映射")
    lines.append("context_dimensions:")
    lines.append("  技术栈: SKILL.md#一技术栈上下文用什么技术")
    lines.append("  项目结构: SKILL.md#二项目结构上下文代码怎么组织")
    lines.append("  技术方案: SKILL.md#三技术方案上下文业务怎么实现")
    lines.append("  开发规范: SKILL.md#四开发规范上下文代码怎么写才合规")
    lines.append("  环境配置: SKILL.md#五环境与配置上下文运行依赖什么")
    lines.append("")

    lines.append("# 触发词映射")
    lines.append("triggers:")
    lines.append("  SKILL.md:")
    for t in ['项目', '概述', '结构', '技术栈', '规范', '上下文']:
        lines.append(f"    - {t}")

    for skill in skills:
        lines.append(f"  {skill['name']}.md:")
        lines.append(f"    - {skill['name']}")
        lines.append(f"    - {skill['parsed'].get('title', skill['name'])}")

    lines.append("")
    return "\n".join(lines)


# ============================================================
# 四、主流程
# ============================================================

def convert(project_path: str, output_dir: str):
    """执行转换：项目扫描 + 代码模式检测 + GitNexus 数据 → 项目上下文 Skill"""

    # ---- 阶段 1：采集事实 ----
    print(f"[INFO] 扫描项目文件: {project_path}")
    scan = scan_project(project_path)
    print(f"[INFO] 检测到语言: {', '.join(f'{l}({c})' for l, c in scan['languages'].most_common(5))}")
    if scan['frameworks']:
        print(f"[INFO] 检测到框架: {', '.join(scan['frameworks'])}")
    if scan['middleware']:
        print(f"[INFO] 检测到中间件: {', '.join(scan['middleware'])}")

    print(f"[INFO] 代码模式检测中...")
    detector = CodePatternDetector(project_path)
    code_patterns = detector.detect_all()
    naming = code_patterns.get('naming', {})
    if naming.get('function_style') != 'unknown':
        print(f"[INFO] 命名风格: 函数={naming.get('function_style')}, "
              f"类={naming.get('class_style')}, 文件={naming.get('file_style')}")
    indent = code_patterns.get('indentation', {})
    if indent.get('detail'):
        print(f"[INFO] 缩进: {indent['detail']}")
    anti = code_patterns.get('anti_patterns', [])
    if anti:
        print(f"[INFO] 反模式: {len(anti)} 项 ({', '.join(a['type'] for a in anti)})")
    env_vars = code_patterns.get('env_vars_in_code', [])
    if env_vars:
        print(f"[INFO] 环境变量: {len(env_vars)} 个 ({', '.join(env_vars[:5])}{'...' if len(env_vars) > 5 else ''})")
    arch = code_patterns.get('architecture_hints', [])
    if arch:
        print(f"[INFO] 架构类型: {', '.join(arch)}")

    meta = load_gitnexus_meta(project_path)
    skills = load_gitnexus_skills(project_path)
    if meta:
        print(f"[INFO] GitNexus 知识图谱: {meta.get('stats', {}).get('nodes', 0)} 节点, "
              f"{meta.get('stats', {}).get('edges', 0)} 边, "
              f"{meta.get('stats', {}).get('communities', 0)} 聚类")
    else:
        print("[WARN] 未找到 .gitnexus/meta.json，仅使用项目扫描+代码模式检测")
    if skills:
        print(f"[INFO] GitNexus 模块: {len(skills)} 个功能聚类")
    else:
        print("[WARN] 未找到 .claude/skills/generated/，仅使用项目扫描+代码模式检测")

    readme_summary = _read_readme_summary(project_path)

    # 构建事实数据
    facts = {
        'generated_at': datetime.now().isoformat(),
        'project_name': scan.get('package_info', {}).get('name') or os.path.basename(os.path.abspath(project_path)),
        'code_patterns': code_patterns,
        'doc_facts': {'readme_summary': readme_summary},
    }

    # ---- 阶段 2：生成 Skill 文件 ----
    os.makedirs(output_dir, exist_ok=True)
    generated = {}

    # 1. 主 SKILL.md — 五大维度项目上下文（使用事实数据自动填充）
    content = generate_project_context_skill(scan, meta, skills, project_path, facts=facts)
    path = os.path.join(output_dir, 'SKILL.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    generated['SKILL.md'] = path
    print(f"  ✓ SKILL.md (项目全局上下文 — 技术栈/结构/方案/规范/环境)")

    # 2. 模块详情 Skill（来自 GitNexus）
    for skill in skills:
        mc = generate_module_skill(skill)
        mp = os.path.join(output_dir, f"{skill['name']}.md")
        with open(mp, 'w', encoding='utf-8') as f:
            f.write(mc)
        generated[f"{skill['name']}.md"] = mp
        print(f"  ✓ {skill['name']}.md (模块详情)")

    # 3. index.yaml
    ic = generate_index_yaml(scan, skills, meta)
    ip = os.path.join(output_dir, 'index.yaml')
    with open(ip, 'w', encoding='utf-8') as f:
        f.write(ic)
    generated['index.yaml'] = ip
    print(f"  ✓ index.yaml (索引)")

    # 4. 保存事实数据（供增量更新和漂移检测使用）
    full_facts = collect_project_facts(project_path)
    facts_path = save_context_facts(full_facts, output_dir)
    generated['.context-facts.json'] = facts_path
    print(f"  ✓ .context-facts.json (采集事实数据)")

    # 统计占位符数量
    with open(os.path.join(output_dir, 'SKILL.md'), 'r', encoding='utf-8') as f:
        skill_content = f.read()
    placeholder_count = len(re.findall(r'\{\{LLM_\w+\}\}', skill_content))

    print(f"\n[INFO] 共生成 {len(generated)} 个文件 → {output_dir}")
    if placeholder_count > 0:
        print(f"[INFO] SKILL.md 含 {placeholder_count} 个 {{{{LLM_*}}}} 占位符，需由 LLM 在后续流程中填充")
    else:
        print(f"[INFO] SKILL.md 已全部自动填充，无需 LLM 额外处理")
    return generated


def main():
    parser = argparse.ArgumentParser(
        description='GitNexus → Specify 项目上下文 Skill 转换器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('project_path', help='项目路径（需先运行 GitNexus 分析）')
    parser.add_argument('--output', '-o',
                        help='Skill 输出目录（默认: <project>/.specify/skills/project-context）')

    args = parser.parse_args()

    project_path = os.path.abspath(args.project_path)
    output_dir = args.output or os.path.join(project_path, '.specify', 'skills', 'project-context')
    output_dir = os.path.abspath(output_dir)

    convert(project_path, output_dir)


if __name__ == '__main__':
    main()
