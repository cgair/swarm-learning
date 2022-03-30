#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0
import logging
from enum import Enum

import eth_utils
import rlp
from rlp.sedes import binary, big_endian_int, CountableList

from . import state_root
from .transaction import Transaction
from ..config import default_config
from ..utils import hash32, sha3

"""
Conflux P2P network half-a-node.

`P2PConnection: A low-level connection object to a node's P2P interface
P2PInterface: A high-level interface object for communicating to a node over P2P
"""

logger = logging.getLogger("TestFramework.mininode")


class MessageID(Enum):
    PacketHello = 0x80
    PacketDisconnect = 0x01
    PacketProtocol = 0x10
    Status = 0x00

    NewBlockHashes = 0x01
    Transactions = 0x02

    GetBlockHashes = 0x03
    GetBlockHashesResponse = 0x04
    GetBlockHeaders = 0x05
    GetBlockHeadersResponse = 0x06
    GetBlockBodies = 0x07
    GetBlockBodiesResponse = 0x08
    NewBlock = 0x09
    GetTerminalBlockHashesResponse = 0x0a
    GetTerminalBlockHashes = 0x0b
    GetBlocks = 0x0c
    GetBlocksResponse = 0x0d
    GetBlocksWithPublicResponse = 0x0e
    GetCompactBlocks = 0x0f
    GetCompactBlocksResponse = 0x10
    GetBlockTxn = 0x11
    GetBlockTxnResponse = 0x12

    GetBlockHashesByEpoch = 0x17
    GetBlockHeaderChain = 0x18


from rlp.exceptions import (
    DeserializationError,
    SerializationError,
)


# Copied from rlp.sedes.Boolean, but encode False to 0x00, not empty.
class Boolean:
    """A sedes for booleans
    """

    def serialize(self, obj):
        if not isinstance(obj, bool):
            raise SerializationError('Can only serialize bool', obj)

        if obj is False:
            return b'\x00'
        elif obj is True:
            return b'\x01'
        else:
            raise Exception("Invariant: no other options for boolean values")

    def deserialize(self, serial):
        if serial == b'\x00':
            return False
        elif serial == b'\x01':
            return True
        else:
            raise DeserializationError(
                'Invalid serialized boolean.  Must be either 0x01 or 0x00',
                serial
            )


class Capability(rlp.Serializable):
    fields = [
        ("protocol", binary),
        ("version", big_endian_int)
    ]


class NodeEndpoint(rlp.Serializable):
    fields = [
        ("address", binary),
        ("udp_port", big_endian_int),
        ("port", big_endian_int)
    ]


class Hello(rlp.Serializable):
    fields = [
        ("network_id", big_endian_int),
        ("capabilities", CountableList(Capability)),
        ("node_endpoint", NodeEndpoint)
    ]


class Disconnect(rlp.Serializable):
    def __init__(self, code: int, msg: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code
        self.msg = msg

    @classmethod
    def deserialize(cls, serial):
        return cls(int(serial[0]), str(serial[1:]))


class Status(rlp.Serializable):
    fields = [
        ("protocol_version", big_endian_int),
        ("genesis_hash", hash32),
        ("best_epoch", big_endian_int),
        ("terminal_block_hashes", CountableList(hash32)),
    ]


class NewBlockHashes(rlp.Serializable):
    def __init__(self, block_hashes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        block_hashes = block_hashes or []
        assert is_sequence(block_hashes)
        self.block_hashes = block_hashes

    @classmethod
    def serializable(cls, obj):
        if is_sequence(obj.block_hashes):
            return True
        else:
            return False

    @classmethod
    def serialize(cls, obj):
        return CountableList(hash32).serialize(obj.block_hashes)

    @classmethod
    def deserialize(cls, serial):
        return cls(block_hashes=CountableList(hash32).deserialize(serial))


class Transactions:
    def __init__(self, transactions=None):
        transactions = transactions or []
        assert is_sequence(transactions)
        self.transactions = transactions

    @classmethod
    def serializable(cls, obj):
        if is_sequence(obj.transactions):
            return True
        else:
            return False

    @classmethod
    def serialize(cls, obj):
        return CountableList(Transaction).serialize(obj.transactions)

    @classmethod
    def deserialize(cls, serial):
        return cls(transactions=CountableList(Transaction).deserialize(serial))


class GetBlockHashes(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("hash", hash32),
        ("max_blocks", big_endian_int)
    ]

    def __init__(self, hash, max_blocks, reqid=0):
        super().__init__(
            reqid=reqid,
            hash=hash,
            max_blocks=max_blocks,
        )


class GetBlockHashesByEpoch(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("epochs", CountableList(big_endian_int)),
    ]

    def __init__(self, epochs, reqid=0):
        super().__init__(
            reqid=reqid,
            epochs=epochs
        )


class BlockHashes(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("hashes", CountableList(hash32)),
    ]


class GetBlockHeaders(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("hashes", CountableList(hash32)),
    ]

    def __init__(self, hashes, reqid=0):
        super().__init__(
            reqid=reqid,
            hashes=hashes,
        )


class BlockHeader(rlp.Serializable):
    fields = [
        ("parent_hash", binary),
        ("height", big_endian_int),
        ("timestamp", big_endian_int),
        ("author", binary),
        ("transactions_root", binary),
        ("deferred_state_root", binary),
        ("deferred_receipts_root", binary),
        ("deferred_logs_bloom_hash", binary),
        ("gas_limit", big_endian_int),
        ("referee_hashes", CountableList(binary)),
        ("nonce", big_endian_int),
    ]

    def __init__(self,
                 parent_hash=default_config['GENESIS_PREVHASH'],
                 height=0,
                 timestamp=0,
                 author=default_config['GENESIS_COINBASE'],
                 transactions_root=state_root.BLANK_ROOT,
                 deferred_state_root=sha3(rlp.encode(state_root.state_root())),
                 deferred_receipts_root=state_root.BLANK_ROOT,
                 deferred_logs_bloom_hash=default_config['GENESIS_LOGS_BLOOM_HASH'],
                 blame=0,
                 difficulty=default_config['GENESIS_DIFFICULTY'],
                 gas_limit=0,
                 referee_hashes=None,
                 adaptive=0,
                 nonce=0):
        # at the beginning of a method, locals() is a dict of all arguments
        referee_hashes = referee_hashes or []
        fields = {k: v for k, v in locals().items() if
                  k not in ['self', '__class__']}
        self.block = None
        super(BlockHeader, self).__init__(**fields)

    @property
    def hash(self):
        return sha3(rlp.encode(self.rlp_part()))

    def get_hex_hash(self):
        return eth_utils.encode_hex(self.hash)

    def without_nonce(self):
        fields = {field: getattr(self, field) for field in BlockHeaderWithoutNonce._meta.field_names}
        return BlockHeaderWithoutNonce(**fields)

    def rlp_part(self):
        fields = {field: getattr(self, field) for field in BlockHeaderRlpPart._meta.field_names}
        return BlockHeaderRlpPart(**fields)


class BlockHeaderRlpPart(rlp.Serializable):
    fields = [
        (field, sedes) for field, sedes in BlockHeader._meta.fields
    ]


class BlockHeaderWithoutNonce(rlp.Serializable):
    fields = [
        (field, sedes) for field, sedes in BlockHeader._meta.fields if
        field not in ["nonce"]

    ]


class BlockHeaders(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("headers", CountableList(BlockHeader)),
    ]


class GetBlockBodies(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("hashes", CountableList(hash32)),
    ]

    def __init__(self, reqid=0, hashes=None):
        super().__init__(
            reqid=reqid,
            hashes=hashes or [],
        )


class Block(rlp.Serializable):
    fields = [
        ("block_header", BlockHeader),
        ("transactions", CountableList(Transaction))
    ]

    def __init__(self, block_header, transactions=None):
        super(Block, self).__init__(
            block_header=block_header,
            transactions=transactions or [],
        )

    @property
    def hash(self):
        return self.block_header.hash

    def hash_hex(self):
        return eth_utils.encode_hex(self.hash)


class BlockBodies(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("bodies", CountableList(Block)),
    ]


class NewBlock(rlp.Serializable):
    def __init__(self, block, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.block = block

    @classmethod
    def serializable(cls, obj):
        return True

    @classmethod
    def serialize(cls, obj):
        return Block.serialize(obj.block)

    @classmethod
    def deserialize(cls, serial):
        return cls(block=Block.deserialize(serial))


class TerminalBlockHashes(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("hashes", CountableList(hash32)),
    ]


class GetTerminalBlockHashes(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
    ]

    def __init__(self, reqid=0):
        super().__init__(reqid)


class GetBlocks(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("with_public", Boolean()),
        ("hashes", CountableList(hash32)),
    ]

    def __init__(self, reqid=0, with_public=False, hashes=None):
        super().__init__(
            reqid=reqid,
            with_public=with_public,
            hashes=hashes or [],
        )


class Blocks(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("blocks", CountableList(Block)),
    ]


class GetCompactBlocks(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("hashes", CountableList(hash32)),
    ]


class CompactBlock(rlp.Serializable):
    fields = [
        ("block_header", BlockHeader),
        ("nonce", big_endian_int),
        ("tx_short_ids", CountableList(big_endian_int)),
    ]


class GetCompactBlocksResponse(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("compact_blocks", CountableList(CompactBlock)),
        ("blocks", CountableList(Block))
    ]


class GetBlockTxn(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("block_hash", hash32),
        ("indexes", CountableList(big_endian_int)),
    ]


class GetBlockTxnResponse(rlp.Serializable):
    fields = [
        ("reqid", big_endian_int),
        ("block_hash", hash32),
        ("block_txn", CountableList(Transaction))
    ]


class Account(rlp.Serializable):
    fields = [
        ("balance", big_endian_int),
        ("nonce", big_endian_int),
        ("storage_root", hash32),
        ("code_hash", hash32),
    ]


msg_id_dict = {
    Status: MessageID.Status,
    NewBlockHashes: MessageID.NewBlockHashes,
    Transactions: MessageID.Transactions,
    GetBlockHashes: MessageID.GetBlockHashes,
    BlockHashes: MessageID.GetBlockHashesResponse,
    GetBlockHeaders: MessageID.GetBlockHashes,
    BlockHeaders: MessageID.GetBlockHeadersResponse,
    GetBlockBodies: MessageID.GetBlockBodies,
    BlockBodies: MessageID.GetBlockBodiesResponse,
    NewBlock: MessageID.NewBlock,
    TerminalBlockHashes: MessageID.GetTerminalBlockHashesResponse,
    GetTerminalBlockHashes: MessageID.GetTerminalBlockHashes,
    GetBlocks: MessageID.GetBlocks,
    Blocks: MessageID.GetBlocksResponse,
    GetCompactBlocks: MessageID.GetCompactBlocks,
    GetCompactBlocksResponse: MessageID.GetCompactBlocksResponse,
    GetBlockTxn: MessageID.GetBlockTxn,
    GetBlockTxnResponse: MessageID.GetBlockTxnResponse,
    GetBlockHashesByEpoch: MessageID.GetBlockHashesByEpoch,
}

msg_class_dict = {}
for c in msg_id_dict:
    msg_class_dict[msg_id_dict[c]] = c


def get_msg_id(msg):
    c = msg.__class__
    if c in msg_id_dict:
        return msg_id_dict[c]
    else:
        return None


def get_msg_class(msg):
    if msg in msg_class_dict:
        return msg_class_dict[msg]
    else:
        return None


def is_sequence(s):
    return isinstance(s, list) or isinstance(s, tuple)
