#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0
from .. import utils

BLANK_NODE = b''
BLANK_ROOT = utils.sha3rlp(b'')
NULL_ROOT = utils.sha3(b'')


def state_root(
        snapshot_root=NULL_ROOT,
        intermediate_delta_root=NULL_ROOT,
        delta_root=NULL_ROOT):
    return [snapshot_root, intermediate_delta_root, delta_root]


UNINITIALIZED_STATE_ROOT = state_root()
