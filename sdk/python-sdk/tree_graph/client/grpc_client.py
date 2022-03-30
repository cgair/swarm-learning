#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0
import eth_utils
import grpc
import enum

import rlp

from ..proto.cfx_pb2_grpc import CfxStub
from ..proto import cfx_pb2 as cfx
from ..proto.cfx_pb2 import message__pb2 as cfx_msg
from ..types import UnsignedTransaction, Transaction, EpochNumberKind
from ..utils import encode_hex
from ..utils.serde import remove_0x_head


class GrpcClient(object):
    def __init__(self, node, *, server_root_cert: bytes = None, private_key: bytes = None, cert_chain: bytes = None):
        """
        Initialize a grpc client.

        If `private_key` is not provided, insecure connection will be used.
        Certificates and keys are PEM-encoded.

        :param server_root_cert The root cert for verification of server certificate.
        :param private_key      Client private key.
        :param cert_chain       Client cert chain.
        """
        url = node.grpc_url
        if private_key is None:
            self._channel = grpc.insecure_channel(url)
        else:
            credential = grpc.ssl_channel_credentials(server_root_cert, private_key, cert_chain)
            self._channel = grpc.secure_channel(url, credential)
        self._stub = CfxStub(self._channel)

    # See: https://grpc.io/docs/languages/python/basics/#simple-rpc-1

    @staticmethod
    def _epoch_number(kind: EpochNumberKind, epoch_number: int=None):
        if kind == EpochNumberKind.Num:
            assert epoch_number is not None
        return cfx_msg.EpochNumber(kind=kind.value, number=epoch_number)

    def get_bft_membership_id(self):
        args = cfx.GetBftMembershipIdRequestGrpc()
        return self._stub.get_bft_membership_id(args).result

    def get_next_nonce(self, addr: str) -> int:
        addr_hex = bytes.fromhex(remove_0x_head(addr))
        args = cfx.NextNonceRequestGrpc()
        args.epoch_number.epoch_number.CopyFrom(self._epoch_number(EpochNumberKind.LatestState))
        args.addr.bytes = addr_hex
        return int.from_bytes(self._stub.next_nonce(args).result.bytes, byteorder='big')

    def get_balance(self, addr: str) -> int:
        addr_hex = bytes.fromhex(remove_0x_head(addr))
        args = cfx.BalanceRequestGrpc()
        args.epoch_number.CopyFrom(self._epoch_number(EpochNumberKind.LatestState))
        args.addr.bytes = addr_hex
        return int.from_bytes(self._stub.balance(args).result.bytes, byteorder='big')

    def send_raw_transaction(self, raw: bytes):
        args = cfx.SendRawTransactionRequestGrpc()
        args.raw_tx.byes = raw
        return encode_hex(self._stub.send_raw_transaction(args).result.bytes)

    def new_tx(self, sender, priv_key, receiver, nonce=None, gas_price=1, gas=21000, value=0, data=b'', sign=True,
               epoch_height=0, chain_id=0):
        if nonce is None:
            nonce = self.get_next_nonce(sender)

        action = eth_utils.decode_hex(receiver)
        tx = UnsignedTransaction(nonce, gas_price, gas, action, value, data, epoch_height, chain_id)

        if sign:
            return tx.sign(priv_key)
        else:
            return tx

    def send_tx(self, tx: Transaction) -> str:
        tx_hash = self.send_raw_transaction(rlp.encode(tx))
        return tx_hash
