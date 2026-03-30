# -*- coding: utf-8 -*-
"""
提取器单元测试
"""
import sys
import os
import unittest

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor.libcst import (
    ClassExtractor,
    FunctionExtractor,
    ConstantExtractor,
    ImportExtractor,
    CommentExtractor,
    ExceptionExtractor,
    DecoratorExtractor,
    DjangoModelExtractor,
    DjangoViewExtractor,
    DjangoURLExtractor,
    DjangoMiddlewareExtractor,
)


class TestClassExtractor(unittest.TestCase):
    """测试类提取器"""

    def setUp(self):
        self.extractor = ClassExtractor({})

    def test_simple_class(self):
        """测试简单类提取"""
        code = '''
class MyClass:
    """这是一个测试类"""

    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}"
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertEqual(len(result.units), 1)
        self.assertEqual(result.units[0].name, "MyClass")
        self.assertEqual(result.units[0].unit_type, "class")
        self.assertIn("这是一个测试类", result.units[0].docstring or "")

    def test_inherited_class(self):
        """测试继承类提取"""
        code = '''
class ChildClass(ParentClass, Mixin):
    pass
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertEqual(len(result.units), 1)
        self.assertIn("ParentClass", result.units[0].metadata.get("bases", []))
        self.assertIn("Mixin", result.units[0].metadata.get("bases", []))

    def test_decorated_class(self):
        """测试装饰器类提取"""
        code = '''
@dataclass
@register
class DataModel:
    name: str
    value: int
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertEqual(len(result.units), 1)
        decorators = result.units[0].metadata.get("decorators", [])
        self.assertIn("@dataclass", decorators)
        self.assertIn("@register", decorators)


class TestFunctionExtractor(unittest.TestCase):
    """测试函数提取器"""

    def setUp(self):
        self.extractor = FunctionExtractor({})

    def test_simple_function(self):
        """测试简单函数提取"""
        code = '''
def hello(name: str) -> str:
    """Say hello"""
    return f"Hello, {name}"
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertEqual(len(result.units), 1)
        self.assertEqual(result.units[0].name, "hello")
        self.assertEqual(result.units[0].unit_type, "function")

    def test_function_with_decorators(self):
        """测试带装饰器的函数"""
        code = '''
@staticmethod
def static_method():
    pass

@classmethod
def class_method(cls):
    pass
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertEqual(len(result.units), 2)

    def test_async_function(self):
        """测试异步函数"""
        code = '''
async def fetch_data(url: str) -> dict:
    """Fetch data from URL"""
    pass
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertEqual(len(result.units), 1)
        self.assertTrue(result.units[0].metadata.get("is_async", False))


class TestConstantExtractor(unittest.TestCase):
    """测试常量提取器"""

    def setUp(self):
        self.extractor = ConstantExtractor({})

    def test_simple_constants(self):
        """测试简单常量提取"""
        code = '''
MAX_SIZE = 100
DEFAULT_NAME = "test"
PI = 3.14159
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertGreaterEqual(len(result.units), 3)
        names = [u.name for u in result.units]
        self.assertIn("MAX_SIZE", names)
        self.assertIn("DEFAULT_NAME", names)
        self.assertIn("PI", names)

    def test_enum_extraction(self):
        """测试枚举提取"""
        code = '''
from enum import Enum

class Status(Enum):
    PENDING = 1
    ACTIVE = 2
    COMPLETED = 3
'''
        result = self.extractor.extract_from_source(code, "test.py")
        # 应该提取到枚举成员
        self.assertGreaterEqual(len(result.units), 1)


class TestImportExtractor(unittest.TestCase):
    """测试导入提取器"""

    def setUp(self):
        self.extractor = ImportExtractor({})

    def test_simple_import(self):
        """测试简单导入"""
        code = '''
import os
import sys
from typing import List, Dict
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertGreaterEqual(len(result.units), 3)

    def test_from_import(self):
        """测试 from 导入"""
        code = '''
from django.db import models
from django.views import View
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertGreaterEqual(len(result.units), 2)


class TestCommentExtractor(unittest.TestCase):
    """测试注释提取器"""

    def setUp(self):
        self.extractor = CommentExtractor({})

    def test_todo_comments(self):
        """测试 TODO 注释提取"""
        code = '''
# TODO: 实现这个功能
# FIXME: 修复这个 bug
# NOTE: 这是一个重要说明
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertGreaterEqual(len(result.units), 3)
        tags = [u.metadata.get("tag") for u in result.units]
        self.assertIn("TODO", tags)
        self.assertIn("FIXME", tags)
        self.assertIn("NOTE", tags)


class TestExceptionExtractor(unittest.TestCase):
    """测试异常提取器"""

    def setUp(self):
        self.extractor = ExceptionExtractor({})

    def test_custom_exception(self):
        """测试自定义异常提取"""
        code = '''
class CustomError(Exception):
    """自定义异常"""
    pass

class ValidationError(ValueError):
    """验证错误"""
    pass
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertGreaterEqual(len(result.units), 2)
        names = [u.name for u in result.units]
        self.assertIn("CustomError", names)
        self.assertIn("ValidationError", names)


class TestDecoratorExtractor(unittest.TestCase):
    """测试装饰器提取器"""

    def setUp(self):
        self.extractor = DecoratorExtractor({})

    def test_decorator_usage(self):
        """测试装饰器使用提取"""
        code = '''
@login_required
@permission_required("admin")
def admin_view(request):
    pass

@cache_result(timeout=300)
def cached_function():
    pass
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertGreaterEqual(len(result.units), 3)


class TestDjangoModelExtractor(unittest.TestCase):
    """测试 Django 模型提取器"""

    def setUp(self):
        self.extractor = DjangoModelExtractor({})

    def test_simple_model(self):
        """测试简单模型提取"""
        code = '''
from django.db import models

class User(models.Model):
    """用户模型"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertEqual(len(result.units), 1)
        self.assertEqual(result.units[0].name, "User")
        self.assertEqual(result.units[0].unit_type, "django_model")

        fields = result.units[0].metadata.get("fields", [])
        field_names = [f.get("name") for f in fields]
        self.assertIn("name", field_names)
        self.assertIn("email", field_names)


class TestDjangoViewExtractor(unittest.TestCase):
    """测试 Django 视图提取器"""

    def setUp(self):
        self.extractor = DjangoViewExtractor({})

    def test_class_based_view(self):
        """测试类视图提取"""
        code = '''
from django.views import View

class UserListView(View):
    """用户列表视图"""

    def get(self, request):
        return HttpResponse("User list")

    def post(self, request):
        return HttpResponse("Create user")
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertEqual(len(result.units), 1)
        self.assertEqual(result.units[0].name, "UserListView")

        http_methods = result.units[0].metadata.get("http_methods", [])
        self.assertIn("get", http_methods)
        self.assertIn("post", http_methods)


class TestDjangoURLExtractor(unittest.TestCase):
    """测试 Django URL 提取器"""

    def setUp(self):
        self.extractor = DjangoURLExtractor({})

    def test_url_patterns(self):
        """测试 URL 模式提取"""
        code = '''
from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.user_list, name="user-list"),
    path("users/<int:pk>/", views.user_detail, name="user-detail"),
]
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertGreaterEqual(len(result.units), 2)


class TestDjangoMiddlewareExtractor(unittest.TestCase):
    """测试 Django 中间件提取器"""

    def setUp(self):
        self.extractor = DjangoMiddlewareExtractor({})

    def test_middleware_class(self):
        """测试中间件类提取"""
        code = '''
class AuthMiddleware:
    """认证中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 前置处理
        response = self.get_response(request)
        # 后置处理
        return response

    def process_request(self, request):
        pass
'''
        result = self.extractor.extract_from_source(code, "test.py")
        self.assertEqual(len(result.units), 1)
        self.assertEqual(result.units[0].name, "AuthMiddleware")


if __name__ == "__main__":
    unittest.main(verbosity=2)
