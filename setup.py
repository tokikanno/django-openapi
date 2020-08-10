# -*- coding:utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name='openapi-router',
    version='0.1',
    author='toki kanno',
    author_email='toki.kanno@gmail.com',
    description='A minimal FastAPI implementation in python2 + Django/Flask without pydantic',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tokikanno/openapi-router',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=2.7',
)
