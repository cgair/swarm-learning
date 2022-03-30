#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0

from jsonrpcclient.clients.http_client import HTTPClient
from jsonrpcclient.requests import Request
from tree_graph.client.jsonrpc_client import *


# jsonrpcclient.client.request_log.propagate = False
# jsonrpcclient.client.response_log.propagate = False


class RpcProxy:
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout
        self.client = HTTPClient(url)

    def __getattr__(self, name):
        return RpcCaller(self.client, name, self.timeout)

    def cfx_epochNumber(self, epoch: str = None) -> str:
        return RpcCaller(self.client, "cfx_epochNumber", self.timeout).__call__(epoch)

    def cfx_getBalance(self, addr: str, epoch: str = None) -> str:
        return RpcCaller(self.client, "cfx_getBalance", self.timeout).__call__(addr, epoch)

    def cfx_gasPrice(self) -> object:
        return RpcCaller(self.client, "cfx_gasPrice", self.timeout).__call__()

    def cfx_getAdmin(self, addr: str, epoch: str = None) -> object:
        return RpcCaller(self.client, "cfx_getAdmin", self.timeout).__call__(addr, epoch)

    def cfx_getNextNonce(self, addr: str, epoch: str = None, block_hash: str = None) -> str:
        if epoch is None and block_hash is None:
            return RpcCaller(self.client, "cfx_getNextNonce", self.timeout).__call__(addr)

    def cfx_sendRawTransaction(self, raw_tx: str) -> str:
        return RpcCaller(self.client, "cfx_sendRawTransaction", self.timeout).__call__(raw_tx)

    def cfx_getBlockByHash(self, block_hash: str, include_txs: bool = False) -> dict:
        return RpcCaller(self.client, "cfx_getBlockByHash", self.timeout).__call__(block_hash, include_txs)

    def cfx_getBlocksByEpoch(self, epoch: str) -> list:
        return RpcCaller(self.client, "cfx_getBlocksByEpoch", self.timeout).__call__(epoch)

    def cfx_getBlocksByEpochNumber(self, epoch: str, include_txs: bool = False) -> dict:
        return RpcCaller(self.client, "cfx_getBlockByEpochNumber", self.timeout).__call__(epoch, include_txs)

    def cfx_getTransactionByHash(self, tx_hash: str) -> dict:
        return RpcCaller(self.client, "cfx_getTransactionByHash", self.timeout).__call__(tx_hash)

    def cfx_getBestBlockHash(self) -> str:
        return RpcCaller(self.client, "cfx_getBestBlockHash", self.timeout).__call__()

    def cfx_getCode(self, addr: str, epoch: str = None) -> str:
        return RpcCaller(self.client, "cfx_getCode", self.timeout).__call__(addr, epoch)

    def get_logs(self, filter: dict) -> list:
        return RpcCaller(self.client, "cfx_getLogs", self.timeout).__call__(filter)

    def cfx_getTransactionReceipt(self, tx_hash: str):
        return RpcCaller(self.client, "cfx_getTransactionReceipt", self.timeout).__call__(tx_hash)
    
    def cfx_call(self, raw_call: str):
        return RpcCaller(self.client, "cfx_call", self.timeout).__call__(raw_call)


def get_rpc_proxy(url, timeout) -> RpcProxy:
    return RpcProxy(url, timeout)


class RpcCaller:
    def __init__(self, client, method, timeout):
        self.client = client
        self.method = method
        self.timeout = timeout

    def __call__(self, *args, **argsn):
        if argsn:
            raise ValueError('json rpc 2 only supports array arguments')
        request = Request(self.method, *args)
        response = self.client.send(request, timeout=self.timeout)
        return response.data.result
