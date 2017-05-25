# _*_ coding: utf_8 _*_
"""
Created on 9/1/2016

@author: Eddie
"""
import os, unittest
from setuptools import setup, find_packages

def pysh_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyshgp",
    version = "0.1.0",
    author = "Eddie Pantridge",
    author_email = "erp12@hampshire.edu",
    description = "Push Genetic Programming in Python",
    license = "LGPL",
    keywords = ["push gp", "genetic programming", "pushgp", "gp", "push"],
    url = "https://github.com/erp12/Pysh",
    packages=find_packages(exclude=['examples', 'docs', 'tests*']),
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)"],
    install_requires=[
        'numpy>=1.12.0',
        'scipy>=0.18.0',
        'scikit-learn>=0.18.0',
        'pathos>=0.2.0',
        'PrettyTable>=0.7.2'
    ],
    test_suite='setup.pysh_test_suite'
)
