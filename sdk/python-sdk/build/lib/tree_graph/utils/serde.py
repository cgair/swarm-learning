#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0

from . import is_string, decode_hex, encode_hex, big_endian_to_int, is_numeric, TT256, int_to_big_endian, to_string, \
    zpad


def decode_bin(v):
    """decodes a bytearray from serialization"""
    if not is_string(v):
        raise Exception("Value must be binary, not RLP array")
    return v


def decode_addr(v):
    """decodes an address from serialization"""
    if len(v) not in [0, 20]:
        raise Exception("Serialized addresses must be empty or 20 bytes long!")
    return encode_hex(v)


def decode_int(v):
    """decodes and integer from serialization"""
    if len(v) > 0 and (v[0] == b'\x00' or v[0] == 0):
        raise Exception("No leading zero bytes allowed for integers")
    return big_endian_to_int(v)


def decode_int256(v):
    return big_endian_to_int(v)


def encode_bin(v):
    """encodes a bytearray into serialization"""
    return v


def encode_root(v):
    """encodes a trie root into serialization"""
    return v


def encode_int(v):
    """encodes an integer into serialization"""
    if not is_numeric(v) or v < 0 or v >= TT256:
        raise Exception("Integer invalid or out of range: %r" % v)
    return int_to_big_endian(v)


def encode_int256(v):
    return zpad(int_to_big_endian(v), 256)


def scan_bin(v):
    if v[:2] in ('0x', b'0x'):
        return decode_hex(v[2:])
    else:
        return decode_hex(v)


def scan_int(v):
    if v[:2] in ('0x', b'0x'):
        return big_endian_to_int(decode_hex(v[2:]))
    else:
        return int(v)


# Decoding from RLP serialization
decoders = {
    "bin": decode_bin,
    "addr": decode_addr,
    "int": decode_int,
    "int256b": decode_int256,
}

# Encoding to RLP serialization
encoders = {
    "bin": encode_bin,
    "int": encode_int,
    "trie_root": encode_root,
    "int256b": encode_int256,
}

# Encoding to printable format
printers = {
    "bin": lambda v: '0x' + encode_hex(v),
    "addr": lambda v: v,
    "int": lambda v: to_string(v),
    "trie_root": lambda v: encode_hex(v),
    "int256b": lambda x: encode_hex(zpad(encode_int256(x), 256))
}

# Decoding from printable format
scanners = {
    "bin": scan_bin,
    "addr": lambda x: x[2:] if x[:2] in (b'0x', '0x') else x,
    "int": scan_int,
    "trie_root": lambda x: scan_bin,
    "int256b": lambda x: big_endian_to_int(decode_hex(x))
}


def int_to_hex(x):
    o = encode_hex(encode_int(x))
    return '0x' + (o[1:] if (len(o) > 0 and o[0] == b'0') else o)


def remove_0x_head(s):
    return s[2:] if s[:2] in (b'0x', '0x') else s


def parse_as_bin(s):
    return decode_hex(s[2:] if s[:2] == '0x' else s)


def parse_as_int(s):
    return s if is_numeric(s) else int(
        '0' + s[2:], 16) if s[:2] == '0x' else int(s)
