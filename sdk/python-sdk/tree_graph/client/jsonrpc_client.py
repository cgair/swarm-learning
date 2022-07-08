#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0

from tkinter.messagebox import NO
import eth_utils
import rlp
import random
import time

from rlp.sedes import Binary
from ..types.filter import Filter
from ..types.transaction import Transaction, UnsignedTransaction
from ..utils.asserts import assert_is_hash_string, assert_is_hex_string
from ..utils import priv_to_addr, priv_to_pub
from tree_graph.client.rpc_proxy import *

import logging

CONFLUX_RPC_WAIT_TIMEOUT = 60


class JsonRpcClient(object):
    # epoch definitions
    EPOCH_EARLIEST = "earliest"
    EPOCH_LATEST_STATE = "latest_state"
    EPOCH_LATEST_CHECKPOINT = "latest_checkpoint"
    EPOCH_LATEST_CANDIDATE = "latest_candidate"

    def __init__(self, host, port, rpc_timeout=None):
        self.host = host
        self.port = port
        self._rpc_timeout = rpc_timeout or CONFLUX_RPC_WAIT_TIMEOUT
        self._rpc = get_rpc_proxy(
            "http://{}:{}".format(self.host, self.port),
            timeout=self._rpc_timeout)

        # # hash/address definitions
        # self.ZERO_HASH = eth_utils.encode_hex(b'\x00' * 32)
        
        # default tx values
        self.DEFAULT_TX_GAS_PRICE = 1
        self.DEFAULT_TX_GAS = 21000
        self.DEFAULT_TX_FEE = self.DEFAULT_TX_GAS_PRICE * self.DEFAULT_TX_GAS
        # self.DEFAULT_BALANCE = 10000 * 365 * 10 ** 18
        self.DEFAULT_BALANCE = 10000 * 10 ** 18
        self.genesis_pri_key = eth_utils.decode_hex("0x46b9e861b63d3509c88b7817275a30d22d62c8cd8fa6486ddee35ef0d8e0495f")
        self.genesis_pub_key = eth_utils.encode_hex(priv_to_pub(self.genesis_pri_key))
        self.genesis_addr = eth_utils.encode_hex(priv_to_addr(self.genesis_pri_key))
        self.coinbase_addr = eth_utils.encode_hex(b'\x10' * 20)
        # self.sender_list = []
        
        # self._initialize_rpc_and_account()

    @staticmethod
    def rand_account() -> (str, bytes):
        priv_key = eth_utils.encode_hex(bytes([random.randint(0, 255) for i in range(32)]))
        addr = eth_utils.encode_hex(priv_to_addr(priv_key))
        return addr, priv_key

    # added by cgair for test
    # 
    def gen_account(file_path=None) -> (str, bytes):
        priv_key = eth_utils.encode_hex(bytes([random.randint(0, 255) for i in range(32)]))
        addr = eth_utils.encode_hex(priv_to_addr(priv_key))
        return addr, priv_key

    # added by cgair for test
    # 
    def top_up(self, 
               addr, 
               times=1):
        nonce = self.get_nonce(self.genesis_addr)
        for i in range(times):
            tx = self.new_tx(
                sender=self.genesis_addr,
                priv_key=self.genesis_pri_key,
                receiver=addr,
                gas_price=self.DEFAULT_TX_GAS_PRICE,
                gas=self.DEFAULT_TX_GAS,
                value=self.DEFAULT_BALANCE,
                nonce=nonce)
            self.send_tx(tx)
            nonce += 1

    def _initialize_rpc_and_account(self):
        random.seed(self.genesis_pri_key)
        self._rpc = get_rpc_proxy(
            "http://{}:{}".format(self.host, self.port),
            timeout=self._rpc_timeout)
        logging.debug(f"[+] the epoch number is {epoch_number}")
        passed_check = False
        for i in range(100):
            nonce = self.get_nonce(self.genesis_addr)
            epoch_number = self.epoch_number()
            addr, priv_key = self.rand_account()
            self.sender_list.append((addr, priv_key))
            if passed_check:
                continue
            if self.get_balance(addr) == 0:
                tx = self.new_tx(
                    sender=self.genesis_addr,
                    priv_key=self.genesis_pri_key,
                    receiver=addr,
                    gas_price=self.DEFAULT_TX_GAS_PRICE,
                    gas=self.DEFAULT_TX_GAS,
                    value=self.DEFAULT_BALANCE,
                    epoch_height=epoch_number, 
                    nonce=nonce)
                self.send_tx(tx)
            else:
                passed_check = True

    @staticmethod
    def EPOCH_NUM(num: int) -> str:
        return hex(num)

    def get_logs(self, filter: Filter) -> list:
        logs = self._rpc.cfx_getLogs(filter.__dict__)
        return logs

    def get_storage_at(self, addr: str, pos: str, epoch: str = None) -> str:
        assert_is_hash_string(addr, length=40)
        assert_is_hash_string(pos)

        if epoch is None:
            res = self._rpc.cfx_getStorageAt(addr, pos)
        else:
            res = self._rpc.cfx_getStorageAt(addr, pos, epoch)

        return res

    def get_code(self, address: str, epoch: str = None) -> str:
        if epoch is None:
            code = self._rpc.cfx_getCode(address)
        else:
            code = self._rpc.cfx_getCode(address, epoch)
        assert_is_hex_string(code)
        return code

    def gas_price(self) -> int:
        return int(self._rpc.cfx_gasPrice(), 0)

    def epoch_number(self, epoch: str = None) -> int:
        if epoch is None:
            return int(self._rpc.cfx_epochNumber(), 0)
        else:
            return int(self._rpc.cfx_epochNumber(epoch), 0)

    def get_balance(self, addr: str, epoch: str = None) -> int:
        if epoch is None:
            return int(self._rpc.cfx_getBalance(addr), 0)
        else:
            return int(self._rpc.cfx_getBalance(addr, epoch), 0)

    def get_admin(self, addr: str, epoch: str = None) -> str:
        if epoch is None:
            return self._rpc.cfx_getAdmin(addr)
        else:
            return self._rpc.cfx_getAdmin(addr, epoch)

    def get_nonce(self, addr: str, epoch: str = None, block_hash: str = None) -> int:
        if epoch is None and block_hash is None:
            return int(self._rpc.cfx_getNextNonce(addr), 0)
        elif epoch is None:
            return int(self._rpc.cfx_getNextNonce(addr, "hash:" + block_hash), 0)
        else:
            return int(self._rpc.cfx_getNextNonce(addr, epoch), 0)

    def send_raw_tx(self, raw_tx: str) -> str:
        tx_hash = self._rpc.cfx_sendRawTransaction(raw_tx)
        assert_is_hash_string(tx_hash)
        return tx_hash

    def send_tx(self, tx: Transaction) -> str:
        encoded = eth_utils.encode_hex(rlp.encode(tx))
        tx_hash = self.send_raw_tx(encoded)
        return tx_hash

    def block_by_hash(self, block_hash: str, include_txs: bool = False) -> dict:
        return self._rpc.cfx_getBlockByHash(block_hash, include_txs)

    def blocks_by_epoch(self, epoch: str) -> list:
        return self._rpc.cfx_getBlocksByEpoch(epoch)

    def block_by_epoch(self, epoch:str, include_txs: bool = False) -> dict:
        return self._rpc.cfx_getBlocksByEpochNumber(epoch, include_txs)

    def best_block_hash(self) -> str:
        return self._rpc.cfx_getBestBlockHash()

    def get_tx(self, tx_hash: str) -> dict:
        return self._rpc.cfx_getTransactionByHash(tx_hash)

    def new_tx(self, sender=None, receiver=None, nonce=None, gas_price=1, gas=10 ** 6, value=0, data=b'', sign=True,
               priv_key=None, epoch_height=0, chain_id=0):
        if sender is None:
            sender = self.genesis_addr
            if priv_key is None:
                priv_key = self.genesis_pri_key

        if receiver is None:
            receiver = "0x"
        if nonce is None:
            nonce = self.get_nonce(sender)

        action = eth_utils.decode_hex(receiver)
        tx = UnsignedTransaction(nonce, gas_price, gas, action, value, data, epoch_height, chain_id)

        if sign:
            return tx.sign(priv_key)
        else:
            return tx

    def send_data(self, data: bytes=b'', gas=10 ** 6, retries=2):
        random.seed(time.time())
        for _ in range(retries):
            try:
                index = random.randint(0, len(self.sender_list) - 1)
                addr, priv_key = self.sender_list[index]
                tx = self.new_tx(
                    sender=addr,
                    priv_key=priv_key,
                    data=data,
                    gas=gas)
                return self.send_tx(tx)
            except Exception as e:
                print("catch exception[{}], retrying..".format(repr(e)))
        return None

    def block_hashes_by_epoch(self, epoch: str) -> list:
        blocks = self._rpc.cfx_getBlocksByEpoch(epoch)
        for b in blocks:
            assert_is_hash_string(b)
        return blocks

    def chain(self) -> list:
        return self._rpc.cfx_getChain()

    def get_transaction_receipt(self, tx_hash: str) -> dict:
        assert_is_hash_string(tx_hash)
        return self._rpc.cfx_getTransactionReceipt(tx_hash)

    def txpool_status(self) -> (int, int):
        status = self._rpc.txpool_status()
        return status["deferred"], status["ready"]

    def get_validator_set(self) -> list:
        return self._rpc.cfx_getValidatorSet()

    def get_bft_membership_id(self) -> int:
        return self._rpc.cfx_getBFTMembershipId()