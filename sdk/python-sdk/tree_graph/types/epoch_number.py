#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0
import enum


class EpochNumberKind(enum.Enum):
    Num = 0
    LatestState = 1
    Earliest = 2
    LatestCheckpoint = 3
    LatestCandidate = 4
