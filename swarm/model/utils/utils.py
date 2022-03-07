#!/usr/bin/env python3
import os
import sys
import eth_utils
from typing import List, Tuple
from utils.weights_wrapper import Weights
from utils.listen_eth_event import Listener
from web3 import Web3


MODEL_DIR = "/swarm/model/checkpoints/"
SPLIT_SIZE = 4096

DEFAULT_TX_GAS_PRICE = 80 * (10 ** 9)
DEFAULT_TX_GAS = 2100000


def file_prepared(epoch, batch):
    model_name = 'weights.{:0>2}-{:0>2}.h5'.format(epoch, batch)
    model_path = MODEL_DIR + model_name
    if os.path.exists(model_path):
        return True, model_path
    return False, ""


def caclulate_factor(weights):
    max_len = 0
    curr_len = 0
    # get max len post decimal
    for weight in weights:
        curr_len = number_of_digits_post_decimal(weight)
        if curr_len > max_len:
                max_len = curr_len
    return max_len


def number_of_digits_post_decimal(x):
    return len(str(x).split(".")[1])


def should_split(shape: Tuple[int, int]) -> bool:
    if len(shape) == 1 and shape[0] >= SPLIT_SIZE:
        return True
    elif len(shape) == 2 and shape[0] * shape[1] >= SPLIT_SIZE:
        return True
    return False


def split_list_by_n(list_collection: List[int], n=SPLIT_SIZE):
    """Divide the list equally, each with n elements.
        
    :param list_collection: the original list
    :param n: split size
    :return: the returned result is each iterable object after dividing
    """
    for i in range(0, len(list_collection), n):
        yield list_collection[i: i + n]


def processed(factor: int, slices) -> List[float]:
    processed = [x/factor for x in slices]
    return processed


def send_msg(client, epoch: int, batch: int, layer: int, w_or_b: int, factor: int, offset: int, weight: List[int]):
    """
    """
    addr = "0x19aeb665dfa6a8445a46cd9a5c666ac6c0d03c54"
    priv_key = "0xb205017cc1b95e12aa37784b3e66eaf099ba6cf0e80cf10f8fc87b44abba53a7"

    func_proto = eth_utils.keccak(b"recordPara(uint256,uint128,uint128,uint64,uint64,uint128,uint128,int128[])")
    data_prefix = func_proto[0:4].hex()
    w = Weights(epoch, batch, layer, w_or_b, factor, offset)
    w.from_weights(weight)
    data_body = w.encode()
    data_hex = data_prefix + data_body
    b_val = bytes.fromhex(data_hex)

    nextNonce = client.get_nonce(addr)
    print(f"[+] the next nonce of account {addr} is ", nextNonce)
    epoch_number = client.epoch_number()
    print("[+] epoch number is ", epoch_number)

    # contract recorder addr = '0x8ad3bed567559a70d9c8d0dce08e0477b730f0d8'
    tx = client.new_tx(sender=addr,
                       receiver='0x8ad3bed567559a70d9c8d0dce08e0477b730f0d8', 
                       nonce=nextNonce,
                       gas_price=DEFAULT_TX_GAS_PRICE,
                       gas=DEFAULT_TX_GAS,
                       value=0, 
                       data=b_val, 
                       sign=True, 
                       priv_key=priv_key, 
                       epoch_height=epoch_number, 
                       chain_id=0)
    tx_hash = client.send_tx(tx)
    sys.exit(f"[+] the send transaction hash is {tx_hash}") 

    rpcAddr = 'http://192.168.1.21:12537'
    contractAddr = '0x8723756d8b4cab11ffa39e316200513e32c8ef7c'
    who = "0x19aeb665dfa6a8445a46cd9a5c666ac6c0d03c54" # account_address
    max_req_times = 60  # After max_req_times, instance will give up on listen percific taskID and return false
    interval = 2  # interval between req_time
    taskID = 1
    # When using python to connect to web3, the address needs to be checked first.
    # for contract address we should accept lower case address because ganache, at the moment, print contract address in lower case.
    # for account address we should accept only checksum address.
    # ll = Listener(rpcAddr, Web3.toChecksumAddress(contractAddr), max_req_times, interval)
    # # It will return true if init_task_event generated successfully
    # print(ll.record_event(taskID, Web3.toChecksumAddress(who), layer, w_or_b, offset))
    # while True:
    #     if ll.record_event(taskID, Web3.toChecksumAddress(who), layer, w_or_b, offset):
    #         return tx_hash


def expand_with_factor(weights, factor: int) -> List[int]:
    for i in range(0, len(weights)):
        weights[i] = weights[i] * (10 ** factor)
        if weights[i] >= 0:
            weights[i] = int(weights[i] + 0.5 )
        elif weights[i] < 0:
            weights[i] = int(weights[i] - 0.5 )
    return weights




        

