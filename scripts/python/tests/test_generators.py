# -*- coding: utf-8 -*-
"""
生成器测试
"""
import sys
import os
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor.libcst import KnowledgeBase, KnowledgeBaseFusion
from generator.skill_generator import SkillGenerator
from generator.windsurf_generator import WindsurfGenerator


class TestSkillGenerator(unittest.TestCase):
    """测试 Skill 生成器"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        self.create_test_files()
        
        # 分析项目
        fusion = KnowledgeBaseFusion({})
        self.kb = fusion.analyze_project(self.test_dir)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.output_dir)
    
    def create_test_files(self):
        """创建测试文件"""
        code = '''
from django.db import models
from django.views import View

MAX_SIZE = 100

class User(models.Model):
    """用户模型"""
    name = models.CharField(max_length=100)

class UserView(View):
    """用户视图"""
    def get(self, request):
        pass

def helper_function():
    """辅助函数"""
    pass

class CustomError(Exception):
    """自定义异常"""
    pass
'''
        with open(os.path.join(self.test_dir, "app.py"), "w") as f:
            f.write(code)
    
    def test_generate_all(self):
        """测试生成所有 Skill"""
        generator = SkillGenerator({})
        files = generator.generate_all(self.kb, self.output_dir)
        
        self.assertIn("SKILL.md", files)
        self.assertIn("index.yaml", files)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "SKILL.md")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "index.yaml")))
    
    def test_skill_content(self):
        """测试 Skill 内容"""
        generator = SkillGenerator({})
        generator.generate_all(self.kb, self.output_dir)
        
        with open(os.path.join(self.output_dir, "SKILL.md")) as f:
            content = f.read()
        
        # 验证 YAML 头部
        self.assertIn("---", content)
        self.assertIn("skill_id:", content)
        self.assertIn("title:", content)
        
        # 验证统计信息
        self.assertIn("项目统计", content)
    
    def test_models_skill(self):
        """测试模型 Skill 生成"""
        generator = SkillGenerator({})
        files = generator.generate_all(self.kb, self.output_dir)
        
        if "models.md" in files:
            with open(os.path.join(self.output_dir, "models.md")) as f:
                content = f.read()
            self.assertIn("User", content)


class TestWindsurfGenerator(unittest.TestCase):
    """测试 Windsurf 生成器"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.create_test_files()
        
        fusion = KnowledgeBaseFusion({})
        self.kb = fusion.analyze_project(self.test_dir)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """创建测试文件"""
        code = '''
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
'''
        with open(os.path.join(self.test_dir, "models.py"), "w") as f:
            f.write(code)
    
    def test_generate_windsurfrules(self):
        """测试生成 .windsurfrules"""
        generator = WindsurfGenerator({"project_root": self.test_dir})
        content = generator.generate_windsurfrules(self.kb, ".specify/skills")
        
        self.assertIn("项目规则", content)
        self.assertIn("开发前置", content)
        self.assertIn("SKILL.md", content)
    
    def test_generate_all(self):
        """测试生成所有 Windsurf 文件"""
        generator = WindsurfGenerator({"project_root": self.test_dir})
        files = generator.generate_all(self.kb, ".specify/skills", self.test_dir)
        
        self.assertIn(".windsurfrules", files)
        self.assertIn("windsurf_rules.md", files)
        self.assertIn("constitution.md", files)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, ".windsurfrules")))


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.create_project_structure()
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir)
    
    def create_project_structure(self):
        """创建完整项目结构"""
        # models.py
        with open(os.path.join(self.test_dir, "models.py"), "w") as f:
            f.write('''
from django.db import models

class Article(models.Model):
    """文章模型"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey("User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
''')
        
        # views.py
        with open(os.path.join(self.test_dir, "views.py"), "w") as f:
            f.write('''
from django.views import View
from django.http import JsonResponse

class ArticleListView(View):
    """文章列表视图"""
    
    def get(self, request):
        return JsonResponse({"articles": []})
''')
        
        # urls.py
        with open(os.path.join(self.test_dir, "urls.py"), "w") as f:
            f.write('''
from django.urls import path
from . import views

urlpatterns = [
    path("articles/", views.ArticleListView.as_view(), name="article-list"),
]
''')
        
        # constants.py
        with open(os.path.join(self.test_dir, "constants.py"), "w") as f:
            f.write('''
MAX_ARTICLES_PER_PAGE = 20
DEFAULT_SORT_ORDER = "-created_at"
''')
        
        # exceptions.py
        with open(os.path.join(self.test_dir, "exceptions.py"), "w") as f:
            f.write('''
class ArticleNotFoundError(Exception):
    """文章未找到异常"""
    pass

class PermissionDeniedError(Exception):
    """权限拒绝异常"""
    pass
''')
    
    def test_full_pipeline(self):
        """测试完整流程"""
        # 1. 分析项目
        fusion = KnowledgeBaseFusion({})
        kb = fusion.analyze_project(self.test_dir)
        
        self.assertGreater(kb.statistics.get("file_count", 0), 0)
        
        # 2. 生成 Skill
        skill_output = os.path.join(self.test_dir, ".specify", "skills")
        skill_generator = SkillGenerator({})
        skill_files = skill_generator.generate_all(kb, skill_output)
        
        self.assertIn("SKILL.md", skill_files)
        
        # 3. 生成 Windsurf 集成
        windsurf_generator = WindsurfGenerator({"project_root": self.test_dir})
        windsurf_files = windsurf_generator.generate_all(
            kb, ".specify/skills", self.test_dir
        )
        
        self.assertIn(".windsurfrules", windsurf_files)
        
        # 4. 验证生成的文件
        self.assertTrue(os.path.exists(os.path.join(skill_output, "SKILL.md")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, ".windsurfrules")))
    
    def test_django_detection(self):
        """测试 Django 组件检测"""
        fusion = KnowledgeBaseFusion({})
        kb = fusion.analyze_project(self.test_dir)
        
        django_stats = kb.statistics.get("django", {})
        
        # 应该检测到 Django 模型和视图
        self.assertGreater(django_stats.get("model_count", 0), 0)
        self.assertGreater(django_stats.get("view_count", 0), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
