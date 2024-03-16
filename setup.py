#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='xunfei-spark-python',
    version='0.0.1',
    author='Stanley Sun',
    author_email='stanley.java@gmail.com',
    url='https://github.com/sunmh207/xunfei-spark',
    description=u'科大讯飞星火大模型SDK',
    packages=['xunfei'],
    install_requires=['websocket-client==1.7.0']
)