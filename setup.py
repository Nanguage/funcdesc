#!/usr/bin/env python

"""The setup script."""

import re
from setuptools import setup, find_packages


def get_long_description():
    return "See https://github.com/Nanguage/funcdesc"


def get_version():
    with open("funcdesc/__init__.py") as f:
        for line in f.readlines():
            m = re.match("__version__ = '([^']+)'", line)
            if m:
                return m.group(1)
        raise IOError("Version information can not found.")


def get_install_requirements():
    requirements = [
    ]
    return requirements


requires_dev = [
    "pip", "setuptools", "wheel", "twine", "ipdb",
    'pytest', 'pytest-cov', 'flake8', 'mypy'
]


setup(
    author="Weize Xu",
    author_email='vet.xwz@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description=(
        "Establish a general function description protocol, "
        "which can realize a comprehensive description of the input, "
        "output and side effects of an target function through "
        "an Python object. Provide a unified abstraction for parameter "
        "checking, interface generation and other functions "
        "in applications such as oneFace."
    ),
    install_requires=get_install_requirements(),
    license="MIT license",
    long_description=get_long_description(),
    include_package_data=True,
    keywords='funcdesc',
    name='funcdesc',
    packages=find_packages(include=['funcdesc', 'funcdesc.*']),
    url='https://github.com/Nanguage/funcdesc',
    version=get_version(),
    zip_safe=False,
    extras_require={
        'dev': requires_dev
    }
)
