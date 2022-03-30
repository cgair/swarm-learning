#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0


class UnknownParentException(Exception):
    pass


class VerificationFailed(Exception):
    pass


class InvalidTransaction(Exception):
    pass


class UnsignedTransaction(InvalidTransaction):
    pass


class InvalidNonce(InvalidTransaction):
    pass


class InsufficientBalance(InvalidTransaction):
    pass


class InsufficientStartGas(InvalidTransaction):
    pass


class BlockGasLimitReached(InvalidTransaction):
    pass


class GasPriceTooLow(InvalidTransaction):
    pass


class SkipTest(Exception):
    """This exception is raised to skip a test"""

    def __init__(self, message):
        self.message = message
