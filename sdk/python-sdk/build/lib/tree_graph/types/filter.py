#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0


class Filter(object):
    def __init__(self, from_epoch="earliest", to_epoch="latest_state", block_hashes=None, address=None, topics=[],
                 limit=None):
        self.fromEpoch = from_epoch
        self.toEpoch = to_epoch
        self.blockHashes = block_hashes
        self.address = address
        self.topics = topics
        self.limit = limit
