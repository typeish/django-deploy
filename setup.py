#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os


rel_file = lambda *args: os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)

def read_from(filename):
    fp = open(filename)
    try:
        return fp.read()
    finally:
        fp.close()

def get_requirements():
    data = read_from(rel_file('requirements.txt'))
    lines = map(lambda s: s.strip(), data.splitlines())
    return filter(None, lines)

setup(
    name='django-deploy',
    version='0.1.0',
    description='Django deployment utility',
    author='John Debs',
    author_email='johnthedebs@gmail.com',
    url='http://github.com/johnthedebs/django-deploy',
    packages=find_packages(),
    install_requires=get_requirements(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ),
)
