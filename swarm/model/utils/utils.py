#!/usr/bin/env python3
import os
import sys
import eth_utils
from typing import List, Tuple
from utils.weights_wrapper import Weights
from tree_graph.types.filter import Filter
from coder_lib import encode_many
from codecs import encode

MODEL_DIR = "/swarm/model/checkpoints/"
SPLIT_SIZE = 2048

DEFAULT_TX_GAS_PRICE = 80 * (10 ** 9) * 10 + 4
DEFAULT_TX_GAS = 2100000

BOB_ADDR = "0x19aeb665dfa6a8445a46cd9a5c666ac6c0d03c54"
BOB_PK = "0xb205017cc1b95e12aa37784b3e66eaf099ba6cf0e80cf10f8fc87b44abba53a7"

ALICE_ADDR = "0x1f9422c17a85f15473d5e25834d17d48c2356c7c"
ALICE_PK = "0x5bba79b1fbba518c7283750cf6a1175f3180fab586c1b1787539885f3132ef4f"

CONTRACT = "0x82b92834bfba83f55f80faca6d5094338911ca9c"


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


def init_task(client, taskid: int, req_num: int):
    data = get_data("taskHandler(uint256,uint256)", ["uint256", str(taskid), "uint256", str(req_num)])
    b_val = bytes.fromhex(data)
    nextNonce = client.get_nonce(ALICE_ADDR)
    epoch_number = client.epoch_number()

    tx = client.new_tx(sender=ALICE_ADDR,
                       receiver=CONTRACT, 
                       nonce=nextNonce,
                       gas_price=DEFAULT_TX_GAS_PRICE,
                       gas=DEFAULT_TX_GAS,
                       value=0, 
                       data=b_val, 
                       sign=True, 
                       priv_key=ALICE_PK, 
                       epoch_height=epoch_number, 
                       chain_id=0)
    tx_hash = client.send_tx(tx)
    print(f"[+] tx hash: {tx_hash}")
    while True: 
        receipt = client.get_transaction_receipt(tx_hash)
        if receipt is not None:
            # print(f"[+] tx receipt: {receipt}")
            outcomeStatus = receipt["outcomeStatus"]
            assert int(outcomeStatus) == 0, "Init task failed"
            # print(f"[+] tx outcomeStatus: {outcomeStatus}")
            return epoch_number

    


def send_msg(client, epoch: int, batch: int, layer: int, w_or_b: int, factor: int, offset: int, weight: List[int]):
    """
    """
    func_proto = eth_utils.keccak(b"recordPara(uint256,uint128,uint128,uint64,uint64,uint128,uint128,int128[])")
    data_prefix = func_proto[0:4].hex()
    w = Weights(epoch, batch, layer, w_or_b, factor, offset)
    w.from_weights(weight)
    data_body = w.encode()
    data_hex = data_prefix + data_body
    b_val = bytes.fromhex(data_hex)

    nextNonce = client.get_nonce(ALICE_ADDR)
    epoch_number = client.epoch_number()

    # contract recorder addr = ''
    tx = client.new_tx(sender=ALICE_ADDR,
                       receiver=CONTRACT, 
                       nonce=nextNonce,
                       gas_price=DEFAULT_TX_GAS_PRICE,
                       gas=DEFAULT_TX_GAS,
                       value=0, 
                       data=b_val, 
                       sign=True, 
                       priv_key=ALICE_PK, 
                       epoch_height=epoch_number, 
                       chain_id=0)
    tx_hash = client.send_tx(tx)
    print(f"[+] tx hash: {tx_hash}")
    while True: 
        receipt = client.get_transaction_receipt(tx_hash)
        if receipt is not None:
            # print(f"[+] tx receipt: {receipt}")
            outcomeStatus = receipt["outcomeStatus"]
            assert int(outcomeStatus) == 0, "Send tx failed"
            # print(f"[+] tx outcomeStatus: {outcomeStatus}")
            return 

    # When using python to connect to web3, the address needs to be checked first.
    # for contract address we should accept lower case address because ganache, at the moment, print contract address in lower case.
    # for account address we should accept only checksum address.

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


def get_data(func_proto: str, data: List[str]):
    func_proto = encode(func_proto, "ascii")
    # func_proto = bytes(func_proto, "ascii")
    func_proto = eth_utils.keccak(func_proto)
    data_prefix = func_proto[0:4].hex()
    data_body = encode_many(data)
    data = data_prefix + data_body
    return data


# TODO: use rust decode log
def get_status(client, epoch_number: int, address=[CONTRACT]):
    filt = Filter(from_epoch=hex(epoch_number), to_epoch="latest_state", address=address)
    print(f"[+] epoch_number = {epoch_number}")
    while True:
        logs = client.get_logs(filt)
        print(f"[+] logs[] = {logs}")
        if len(logs) > 0:
            return logs
    
