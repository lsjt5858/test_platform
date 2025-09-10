from setuptools import setup, find_packages

setup(
    name="bears-test-platform",
    version="0.1.0",
    packages=find_packages(),
    install_requires=open("requirements.txt").readlines(),
    entry_points={
        'console_scripts': [
            'bears=cli.bears:cli',  # 👈 关键：命令名改为 bears
        ],
    },
    author="Your Name",
    description="🐻 Unified Test Automation Platform with K6 + Prometheus + Grafana",
)