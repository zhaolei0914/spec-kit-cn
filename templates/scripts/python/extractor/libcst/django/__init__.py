# -*- coding: utf-8 -*-
"""
Django 特定提取器模块

提取 Django 项目特有的代码模式和结构
"""
from .model_extractor import DjangoModelExtractor
from .view_extractor import DjangoViewExtractor
from .url_extractor import DjangoURLExtractor
from .middleware_extractor import DjangoMiddlewareExtractor

__all__ = [
    'DjangoModelExtractor',
    'DjangoViewExtractor',
    'DjangoURLExtractor',
    'DjangoMiddlewareExtractor',
]
