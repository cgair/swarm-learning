#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0
# -*- coding: utf-8 -*-
from setuptools import (
    find_packages,
    setup,
)

setup(
    name="light sealer",
    version="1.0",
    description="Light Sealer Python SDK",
    author="Conflux Foundation",
    url="http://www.0-1universe.com",
    install_requires=[
        "eth-utils",
        "rlp",
        "py_ecc",
        "coincurve",
        "pysha3",
        "web3",
        "grpcio-tools",
        "grpcio",
        "jsonrpcclient"
    ],
    python_requires='>=3.6,<4',
    license="Apache License 2.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
)
