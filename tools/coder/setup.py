#!/usr/bin/env python3
from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup(
    name="coder_lib",
    version="1.0",
    rust_extensions=[RustExtension("coder.coder_lib", binding=Binding.PyO3)],
    # classifiers=[
    #     "License :: ,
    #     "Development Status :: ,
    #     "Intended Audience :: Developers",
    #     "Programming Language :: Python",
    #     "Programming Language :: Rust",
    # ],
    packages=["coder_lib"],
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False,
)