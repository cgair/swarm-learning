#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0

import inspect
import json
import os
import random
import time
from decimal import Decimal

import coincurve
import rlp
import sha3 as _sha3
from eth_utils import decode_hex, int_to_big_endian, big_endian_to_int
from eth_utils import encode_hex as encode_hex_0x
from py_ecc.secp256k1 import privtopub, ecdsa_raw_sign, ecdsa_raw_recover
from rlp.sedes import big_endian_int, BigEndianInt, Binary
from rlp.utils import ALL_BYTES


def sha3_256(x):
    return _sha3.keccak_256(x).digest()


def check_json_precision():
    """Make sure json library being used does not lose precision converting BTC values"""
    n = Decimal("20000000.00000003")
    satoshis = int(json.loads(json.dumps(float(n))) * 1.0e8)
    if satoshis != 2000000000000003:
        raise RuntimeError("JSON encode/decode loses precision")


def wait_until(predicate,
               *,
               attempts=float('inf'),
               timeout=float('inf'),
               lock=None):
    if attempts == float('inf') and timeout == float('inf'):
        timeout = 60
    attempt = 0
    time_end = time.time() + timeout

    while attempt < attempts and time.time() < time_end:
        if lock:
            with lock:
                if predicate():
                    return
        else:
            if predicate():
                return
        attempt += 1
        time.sleep(0.5)

    # Print the cause of the timeout
    predicate_source = inspect.getsourcelines(predicate)
    logger.error("wait_until() failed. Predicate: {}".format(predicate_source))
    if attempt >= attempts:
        raise AssertionError("Predicate {} not true after {} attempts".format(
            predicate_source, attempts))
    elif time.time() >= time_end:
        raise AssertionError("Predicate {} not true after {} seconds".format(
            predicate_source, timeout))
    raise RuntimeError('Unreachable')


class Memoize:
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}

    def __call__(self, *args):
        if args not in self.memo:
            self.memo[args] = self.fn(*args)
        return self.memo[args]


TT256 = 2 ** 256
TT256M1 = 2 ** 256 - 1
TT255 = 2 ** 255
SECP256K1P = 2 ** 256 - 4294968273


def is_numeric(x):
    return isinstance(x, int)


def is_string(x):
    return isinstance(x, bytes)


def to_string(value):
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return bytes(value, 'utf-8')
    if isinstance(value, int):
        return bytes(str(value), 'utf-8')


def int_to_bytes(value):
    if isinstance(value, bytes):
        return value
    return int_to_big_endian(value)


def to_string_for_regexp(value):
    return str(to_string(value), 'utf-8')


unicode = str


def bytearray_to_bytestr(value):
    return bytes(value)


def encode_int32(v):
    return v.to_bytes(32, byteorder='big')


def bytes_to_int(value):
    return int.from_bytes(value, byteorder='big')


def str_to_bytes(value):
    if isinstance(value, bytearray):
        value = bytes(value)
    if isinstance(value, bytes):
        return value
    return bytes(value, 'utf-8')


def ascii_chr(n):
    return ALL_BYTES[n]


def encode_hex(n):
    if isinstance(n, str):
        return encode_hex(n.encode('ascii'))
    return encode_hex_0x(n)[2:]


def ecrecover_to_pub(rawhash, v, r, s):
    if coincurve and hasattr(coincurve, "PublicKey"):
        try:
            pk = coincurve.PublicKey.from_signature_and_message(
                zpad(bytearray_to_bytestr(int_to_32bytearray(r)), 32) + zpad(
                    bytearray_to_bytestr(int_to_32bytearray(s)), 32) + ascii_chr(v - 27),
                rawhash,
                hasher=None,
            )
            pub = pk.format(compressed=False)[1:]
            x, y = pk.point()
        except BaseException:
            x, y = 0, 0
            pub = b"\x00" * 64
    else:
        result = ecdsa_raw_recover(rawhash, (v, r, s))
        if result:
            x, y = result
            pub = encode_int32(x) + encode_int32(y)
        else:
            raise ValueError('Invalid VRS')
    assert len(pub) == 64
    return pub, x, y


def ecsign(rawhash, key):
    if coincurve and hasattr(coincurve, 'PrivateKey'):
        pk = coincurve.PrivateKey(key)
        signature = pk.sign_recoverable(rawhash, hasher=None)
        v = safe_ord(signature[64]) + 27
        r = big_endian_to_int(signature[0:32])
        s = big_endian_to_int(signature[32:64])
    else:
        v, r, s = ecdsa_raw_sign(rawhash, key)
    return v, r, s


def ec_random_keys():
    priv_key = random.randint(0, 2 ** 256).to_bytes(32, "big")
    pub_key = privtopub(priv_key)
    return priv_key, pub_key


def convert_to_nodeid(signature, challenge):
    r = big_endian_to_int(signature[:32])
    s = big_endian_to_int(signature[32:64])
    v = big_endian_to_int(signature[64:]) + 27
    signed = int_to_bytes(challenge)
    h_signed = sha3_256(signed)
    return ecrecover_to_pub(h_signed, v, r, s)


def get_nodeid(node):
    challenge = random.randint(0, 2 ** 32 - 1)
    signature = node.getnodeid(list(int_to_bytes(challenge)))
    return convert_to_nodeid(signature, challenge)


def safe_ord(value):
    if isinstance(value, int):
        return value
    else:
        return ord(value)


# decorator


def debug(label):
    def deb(f):
        def inner(*args, **kwargs):
            i = random.randrange(1000000)
            print(label, i, 'start', args)
            x = f(*args, **kwargs)
            print(label, i, 'end', x)
            return x

        return inner

    return deb


def flatten(li):
    o = []
    for x in li:
        o.extend(x)
    return o


def bytearray_to_int(arr):
    o = 0
    for a in arr:
        o = (o << 8) + a
    return o


def int_to_32bytearray(i):
    o = [0] * 32
    for x in range(32):
        o[31 - x] = i & 0xff
        i >>= 8
    return o


# sha3_count = [0]


def sha3(seed):
    return sha3_256(to_string(seed))


assert encode_hex(sha3(b'')) == 'c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'
assert encode_hex(sha3(b'\x00' * 256)) == 'd397b3b043d87fcd6fad1291ff0bfd16401c274896d8c63a923727f077b8e0b5'


@Memoize
def priv_to_addr(k):
    k = normalize_key(k)
    x, y = privtopub(k)
    addr = bytearray(sha3(encode_int32(x) + encode_int32(y))[12:])
    addr[0] &= 0x0f
    addr[0] |= 0x10
    return bytes(addr)


def priv_to_pub(k):
    k = normalize_key(k)
    x, y = privtopub(k)
    return bytes(encode_int32(x) + encode_int32(y))


def pub_to_addr(k):
    x = big_endian_to_int(decode_hex(k[2:34]))
    y = big_endian_to_int(decode_hex(k[34:66]))
    addr = bytearray(sha3(encode_int32(x) + encode_int32(y))[12:])
    addr[0] &= 0x0f
    addr[0] |= 0x10
    return bytes(addr)


def checksum_encode(addr):  # Takes a 20-byte binary address as input
    addr = normalize_address(addr)
    o = ''
    v = big_endian_to_int(sha3(encode_hex(addr)))
    for i, c in enumerate(encode_hex(addr)):
        if c in '0123456789':
            o += c
        else:
            o += c.upper() if (v & (2 ** (255 - 4 * i))) else c.lower()
    return '0x' + o


def check_checksum(addr):
    return checksum_encode(normalize_address(addr)) == addr


def normalize_address(x, allow_blank=False):
    if is_numeric(x):
        return int_to_addr(x)
    if allow_blank and x in {'', b''}:
        return b''
    if len(x) in (42, 50) and x[:2] in {'0x', b'0x'}:
        x = x[2:]
    if len(x) in (40, 48):
        x = decode_hex(x)
    if len(x) == 24:
        assert len(x) == 24 and sha3(x[:20])[:4] == x[-4:]
        x = x[:20]
    if len(x) != 20:
        raise Exception("Invalid address format: %r" % x)
    return x


def normalize_key(key):
    if is_numeric(key):
        o = encode_int32(key)
    elif len(key) == 32:
        o = key
    elif len(key) == 64:
        o = decode_hex(key)
    elif len(key) == 66 and key[:2] == '0x':
        o = decode_hex(key[2:])
    else:
        raise Exception("Invalid key format: %r" % key)
    if o == b'\x00' * 32:
        raise Exception("Zero privkey invalid")
    return o


def zpad(x, num_zeros):
    """ Left zero pad value `x` at least to length `l`.

    >>> zpad('', 1)
    '\x00'
    >>> zpad('\xca\xfe', 4)
    '\x00\x00\xca\xfe'
    >>> zpad('\xff', 1)
    '\xff'
    >>> zpad('\xca\xfe', 2)
    '\xca\xfe'
    """
    return b'\x00' * max(0, num_zeros - len(x)) + x


def rzpad(value, total_length):
    """ Right zero pad value `x` at least to length `l`.

    >>> zpad('', 1)
    '\x00'
    >>> zpad('\xca\xfe', 4)
    '\xca\xfe\x00\x00'
    >>> zpad('\xff', 1)
    '\xff'
    >>> zpad('\xca\xfe', 2)
    '\xca\xfe'
    """
    return value + b'\x00' * max(0, total_length - len(value))


def int_to_addr(x):
    o = [b''] * 20
    for i in range(20):
        o[19 - i] = ascii_chr(x & 0xff)
        x >>= 8
    return b''.join(o)


def coerce_addr_to_bin(x):
    if is_numeric(x):
        return encode_hex(zpad(big_endian_int.serialize(x), 20))
    elif len(x) == 40 or len(x) == 0:
        return decode_hex(x)
    else:
        return zpad(x, 20)[-20:]


def coerce_addr_to_hex(x):
    if is_numeric(x):
        return encode_hex(zpad(big_endian_int.serialize(x), 20))
    elif len(x) == 40 or len(x) == 0:
        return x
    else:
        return encode_hex(zpad(x, 20)[-20:])


def coerce_to_int(x):
    if is_numeric(x):
        return x
    elif len(x) == 40:
        return big_endian_to_int(decode_hex(x))
    else:
        return big_endian_to_int(x)


def coerce_to_bytes(x):
    if is_numeric(x):
        return big_endian_int.serialize(x)
    elif len(x) == 40:
        return decode_hex(x)
    else:
        return x


def parse_int_or_hex(s):
    if is_numeric(s):
        return s
    elif s[:2] in (b'0x', '0x'):
        s = to_string(s)
        tail = (b'0' if len(s) % 2 else b'') + s[2:]
        return big_endian_to_int(decode_hex(tail))
    else:
        return int(s)


def ceil32(x):
    return x if x % 32 == 0 else x + 32 - (x % 32)


def to_signed(i):
    return i if i < TT255 else i - TT256


def sha3rlp(x):
    return sha3(rlp.encode(x))


def print_func_call(ignore_first_arg=False, max_call_number=100):
    """ utility function to facilitate debug, it will print input args before
    function call, and print return value after function call

    usage:

        @print_func_call
        def some_func_to_be_debu():
            pass

    :param ignore_first_arg: whether print the first arg or not.
    useful when ignore the `self` parameter of an object method call
    """
    from functools import wraps

    def display(x):
        x = to_string(x)
        try:
            x.decode('ascii')
        except BaseException:
            return 'NON_PRINTABLE'
        return x

    local = {'call_number': 0}

    def inner(f):

        @wraps(f)
        def wrapper(*args, **kwargs):
            local['call_number'] += 1
            tmp_args = args[1:] if ignore_first_arg and len(args) else args
            this_call_number = local['call_number']
            print(('{0}#{1} args: {2}, {3}'.format(
                f.__name__,
                this_call_number,
                ', '.join([display(x) for x in tmp_args]),
                ', '.join(display(key) + '=' + to_string(value)
                          for key, value in kwargs.items())
            )))
            res = f(*args, **kwargs)
            print(('{0}#{1} return: {2}'.format(
                f.__name__,
                this_call_number,
                display(res))))

            if local['call_number'] > 100:
                raise Exception("Touch max call number!")
            return res

        return wrapper

    return inner


def dump_state(trie):
    res = ''
    for k, v in list(trie.to_dict().items()):
        res += '%r:%r\n' % (encode_hex(k), encode_hex(v))
    return res


def checktx(node, tx_hash):
    return node.cfx_getTransactionReceipt(tx_hash) is not None


def wait_for_block_count(node, count, timeout=10):
    wait_until(lambda: node.getblockcount() >= count, timeout=timeout)


def sync_blocks(rpc_connections, *, sync_count=True, wait=1, timeout=60):
    """
    Wait until everybody has the same tip.

    sync_blocks needs to be called with an rpc_connections set that has least
    one node already synced to the latest, stable tip, otherwise there's a
    chance it might return before all nodes are stably synced.
    """
    stop_time = time.time() + timeout
    while time.time() <= stop_time:
        best_hash = [x.best_block_hash() for x in rpc_connections]
        block_count = [x.getblockcount() for x in rpc_connections]
        if best_hash.count(best_hash[0]) == len(rpc_connections) and (
                not sync_count or block_count.count(block_count[0]) == len(rpc_connections)):
            return
        time.sleep(wait)
    raise AssertionError("Block sync timed out:{}".format("".join(
        "\n  {!r}".format(b) for b in best_hash + block_count)))


def get_datadir_path(dirname, n):
    return os.path.join(dirname, "node" + str(n))


class WaitHandler:
    def __init__(self, node, msgid, func=None):
        self.keep_wait = True
        self.node = node
        self.msgid = msgid

        def on_message(obj, msg):
            if func is not None:
                func(obj, msg)
            self.keep_wait = False

        node.set_callback(msgid, on_message)

    def wait(self, timeout=10):
        wait_until(lambda: not self.keep_wait, timeout=timeout)
        self.node.reset_callback(self.msgid)


address = Binary.fixed_length(20, allow_empty=True)
int20 = BigEndianInt(20)
int32 = BigEndianInt(32)
int256 = BigEndianInt(256)
hash32 = Binary.fixed_length(32)
hash20 = Binary.fixed_length(20)
trie_root = Binary.fixed_length(32, allow_empty=True)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[91m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
