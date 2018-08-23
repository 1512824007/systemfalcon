#-*- encoding: UTF-8 -*-
import os
from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = "systemfalcon",
    version = "0.1",
    packages = find_packages(),
    include_package_data = True,
    zip_safe = True,

    install_requires = [
    'Django',
    'django-crontab',
    'django-celery',
    'bootstrap_admin',
    'MySQL-python',
    'requests',
    'itsdangerous',
    'pandas',
    'IPy',
    ],

    # 设置程序的入口为hello
    # 安装后，命令行执行hello相当于调用hello.py中的main方法
    entry_points={
        'console_scripts':[
            'hello = project_file.hello:main'
        ]
    },
)
