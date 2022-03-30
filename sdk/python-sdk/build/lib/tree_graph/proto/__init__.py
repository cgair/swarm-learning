#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0
# Auto generate modules from .proto files if modified
from pathlib import Path
import subprocess
import sys


SRC_DIR = Path(__file__).parent / "../proto"
DEST_DIR = Path(__file__).parent

assert SRC_DIR.is_dir(), 'Path changed'


def regenerate():
    def content_mtime(path):
        stat = path.stat()
        return max(stat.st_mtime, stat.st_ctime)

    names = []
    for src in SRC_DIR.glob("*.proto"):
        names.append(src.stem)
        dest = DEST_DIR / (src.stem + "_pb2.py")
        if not dest.exists() or content_mtime(dest) <= content_mtime(src):
            print("proto: regenerating", src.name)
            subprocess.check_call([
                sys.executable, # Path to python interpreter.
                "-m", "grpc_tools.protoc",
                "-I", SRC_DIR,
                "--python_out", DEST_DIR,
                "--grpc_python_out", DEST_DIR,
                src
            ])
    return names


regenerate()

# Workaround for https://github.com/protocolbuffers/protobuf/issues/1491
sys.path.append(str(Path(__file__).parent))
