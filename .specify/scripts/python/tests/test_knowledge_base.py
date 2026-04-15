# -*- coding: utf-8 -*-
"""
知识库和融合器测试
"""
import sys
import os
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor.libcst import KnowledgeBase, KnowledgeBaseFusion


class TestKnowledgeBase(unittest.TestCase):
    """测试知识库"""

    def test_create_empty_knowledge_base(self):
        """测试创建空知识库"""
        kb = KnowledgeBase(project_name="test_project")
        self.assertEqual(kb.project_name, "test_project")
        self.assertEqual(len(kb.code_units), 0)

    def test_save_and_load(self):
        """测试保存和加载"""
        kb = KnowledgeBase(project_name="test_project")
        kb.statistics = {
            "file_count": 10,
            "class_count": 5,
            "function_count": 20,
        }

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            kb.save(temp_path)
            loaded_kb = KnowledgeBase.load(temp_path)

            self.assertEqual(loaded_kb.project_name, "test_project")
            self.assertEqual(loaded_kb.statistics["file_count"], 10)
            self.assertEqual(loaded_kb.statistics["class_count"], 5)
        finally:
            os.unlink(temp_path)


class TestKnowledgeBaseFusion(unittest.TestCase):
    """测试知识库融合器"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()

        # 创建测试 Python 文件
        self.create_test_files()

    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir)

    def create_test_files(self):
        """创建测试文件"""
        # models.py
        models_code = '''
from django.db import models

class User(models.Model):
    """用户模型"""
    name = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        db_table = "users"
'''
        with open(os.path.join(self.test_dir, "models.py"), "w") as f:
            f.write(models_code)

        # views.py
        views_code = '''
from django.views import View
from django.http import JsonResponse

class UserListView(View):
    """用户列表视图"""

    def get(self, request):
        return JsonResponse({"users": []})

    def post(self, request):
        return JsonResponse({"created": True})
'''
        with open(os.path.join(self.test_dir, "views.py"), "w") as f:
            f.write(views_code)

        # utils.py
        utils_code = '''
MAX_RETRY = 3
DEFAULT_TIMEOUT = 30

def retry_request(func):
    """重试装饰器"""
    def wrapper(*args, **kwargs):
        for i in range(MAX_RETRY):
            try:
                return func(*args, **kwargs)
            except Exception:
                pass
        raise Exception("Max retry exceeded")
    return wrapper

class CustomError(Exception):
    """自定义异常"""
    pass
'''
        with open(os.path.join(self.test_dir, "utils.py"), "w") as f:
            f.write(utils_code)

    def test_analyze_project(self):
        """测试项目分析"""
        fusion = KnowledgeBaseFusion({})
        kb = fusion.analyze_project(self.test_dir)

        self.assertEqual(kb.project_name, os.path.basename(self.test_dir))
        self.assertGreater(kb.statistics.get("file_count", 0), 0)
        self.assertGreater(len(kb.code_units), 0)

    def test_extract_classes(self):
        """测试类提取"""
        fusion = KnowledgeBaseFusion({})
        kb = fusion.analyze_project(self.test_dir)

        class_units = [u for u in kb.code_units if u.get("unit_type") == "class"]
        class_names = [u.get("name") for u in class_units]

        self.assertIn("User", class_names)
        self.assertIn("UserListView", class_names)
        self.assertIn("CustomError", class_names)

    def test_extract_functions(self):
        """测试函数提取"""
        fusion = KnowledgeBaseFusion({})
        kb = fusion.analyze_project(self.test_dir)

        func_units = [u for u in kb.code_units if u.get("unit_type") == "function"]
        func_names = [u.get("name") for u in func_units]

        self.assertIn("retry_request", func_names)

    def test_extract_constants(self):
        """测试常量提取"""
        fusion = KnowledgeBaseFusion({})
        kb = fusion.analyze_project(self.test_dir)

        const_units = [u for u in kb.code_units if u.get("unit_type") == "constant"]
        const_names = [u.get("name") for u in const_units]

        self.assertIn("MAX_RETRY", const_names)
        self.assertIn("DEFAULT_TIMEOUT", const_names)

    def test_django_model_extraction(self):
        """测试 Django 模型提取"""
        fusion = KnowledgeBaseFusion({})
        kb = fusion.analyze_project(self.test_dir)

        model_units = [u for u in kb.code_units if u.get("unit_type") == "django_model"]

        self.assertGreaterEqual(len(model_units), 1)
        user_model = next((u for u in model_units if u.get("name") == "User"), None)
        self.assertIsNotNone(user_model)

    def test_django_view_extraction(self):
        """测试 Django 视图提取"""
        fusion = KnowledgeBaseFusion({})
        kb = fusion.analyze_project(self.test_dir)

        view_units = [u for u in kb.code_units if u.get("unit_type") == "django_view"]

        self.assertGreaterEqual(len(view_units), 1)
        user_view = next((u for u in view_units if u.get("name") == "UserListView"), None)
        self.assertIsNotNone(user_view)


if __name__ == "__main__":
    unittest.main(verbosity=2)
