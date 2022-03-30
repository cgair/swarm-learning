#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0
import copy

import eth_utils
import rlp
from rlp.sedes import big_endian_int, binary

from .. import utils
from ..utils import TT256, ecsign, normalize_key, encode_hex, address
from ..utils.exceptions import InvalidTransaction


class UnsignedTransaction(rlp.Serializable):
    fields = [
        ('nonce', big_endian_int),
        ('gas_price', big_endian_int),
        ('gas', big_endian_int),
        ('action', address),
        ('value', big_endian_int),
        ('epoch_height', big_endian_int),
        ('chain_id', big_endian_int),
        ('data', binary),
    ]

    def __init__(self, nonce, gas_price, gas, action, value, data, epoch_height, chain_id):
        if gas_price >= TT256 or \
                value >= TT256 or nonce >= TT256:
            raise InvalidTransaction("Values way too high!")

        super(UnsignedTransaction, self).__init__(
            nonce=nonce,
            gas_price=gas_price,
            gas=gas,
            value=value,
            action=action,
            data=data,
            epoch_height=epoch_height,
            chain_id=chain_id
        )

    def sign(self, key):
        rawHash = utils.sha3(
            rlp.encode(self, UnsignedTransaction))

        key = normalize_key(key)

        v, r, s = ecsign(rawHash, key)
        v = v - 27
        ret = Transaction(transaction=copy.deepcopy(self), v=v, r=r, s=s)
        ret._sender = utils.priv_to_addr(key)
        return ret


class Transaction(rlp.Serializable):
    """
    A transaction is stored as:
    [[nonce, gas_price, gas, action, value, storage_limit, epoch_height, chain_id, data], v, r, s]

    nonce is the number of transactions already sent by that account, encoded
    in binary form (eg.  0 -> '', 7 -> '\x07', 1000 -> '\x03\xd8').

    (v,r,s) is the raw Electrum-style signature of the transaction without the
    signature made with the private key corresponding to the sending account,
    with 0 <= v <= 1. From an Electrum-style signature (65 bytes) it is
    possible to extract the public key, and thereby the address, directly.

    A valid transaction is one where:
    (i) the signature is well-formed, and
    (ii) the sending account has enough funds to pay the fee and the value.
    """

    fields = [
        ('transaction', UnsignedTransaction),
        ('v', big_endian_int),
        ('r', big_endian_int),
        ('s', big_endian_int),
    ]

    _sender = None

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, value):
        self._sender = value

    @property
    def hash(self):
        return utils.sha3(rlp.encode(self))

    def hash_hex(self):
        return eth_utils.encode_hex(self.hash)

    def to_dict(self):
        d = {}
        for name, _ in self.__class__._meta.fields:
            d[name] = getattr(self, name)
        d['sender'] = '0x' + encode_hex(self.sender)
        d['hash'] = '0x' + encode_hex(self.hash)
        return d

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.hash == other.hash

    def __lt__(self, other):
        return isinstance(other, self.__class__) and self.hash < other.hash

    def __hash__(self):
        return utils.big_endian_to_int(self.hash)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Transaction(%s)>' % encode_hex(self.hash)[:4]

    def __getattr__(self, item):
        return getattr(self.transaction, item)
