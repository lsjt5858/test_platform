#!/usr/bin/env python
"""
Test Platform - 四层架构测试框架
统一的前后端自动化测试引擎，支持 API、UI、业务校验、数据层校验等一体化自动化测试
"""

from setuptools import setup, find_packages

setup(
    name="test-platform",
    version="1.0.0",
    description="Four-Layer Test Automation Platform (Core-App-Biz-Test)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Test Platform Team",
    author_email="test@example.com",
    url="https://github.com/your-org/test-platform",
    
    # 这是一个元包，依赖各个子包
    install_requires=[
        "nut-core>=1.0.0",
        "nut-app>=1.0.0", 
        "nut-biz>=1.0.0",
        "easyui>=1.0.0",
    ],
    
    python_requires=">=3.9",
    
    # 包含性能测试和监控工具
    extras_require={
        "full": [
            # 性能测试
            "k6",
            # 监控
            "prometheus_client>=0.17.0",
            # 报告
            "allure-pytest>=2.13.0",
            "pytest-html>=3.1.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    
    # 命令行工具
    entry_points={
        "console_scripts": [
            "test-platform=nut_core.cli.main:main",
            "hamster=nut_core.cli.hammer:main",
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Framework :: Pytest",
    ],
    
    keywords="testing, automation, api, ui, performance, framework, four-layer-architecture",
)