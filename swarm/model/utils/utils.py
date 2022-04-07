#!/usr/bin/env python3
import os
import eth_utils

from time import sleep
from typing import List, Tuple
from utils.weights_wrapper import Weights
from tree_graph.types.filter import Filter
from coder_lib import encode_many, decode_many
from codecs import encode
from utils.load_config import Conf

conf = Conf()
MODEL_DIR = conf.default("model_dir")
SPLIT_SIZE = conf.default("split_size")
# print(f"[+] conf = {SPLIT_SIZE}, type = {type(SPLIT_SIZE)}")

DEFAULT_TX_GAS_PRICE = conf.default("default_tx_gas_price")
DEFAULT_TX_GAS = conf.default("default_tx_gas")

ADDR = conf.address()
PK = conf.private_key()
CONTRACT = conf.contract()
TASK_ID = conf.task_id()

# BOB_ADDR = "0x19aeb665dfa6a8445a46cd9a5c666ac6c0d03c54"
# BOB_PK = "0xb205017cc1b95e12aa37784b3e66eaf099ba6cf0e80cf10f8fc87b44abba53a7"

# ALICE_ADDR = "0x1f9422c17a85f15473d5e25834d17d48c2356c7c"
# ALICE_PK = "0x5bba79b1fbba518c7283750cf6a1175f3180fab586c1b1787539885f3132ef4f"


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
        post_len = len(str(x).split("."))
        if post_len > 1:
            return len(str(x).split(".")[1])
        else:
            return 0


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
    """
    """
    processed = [x/factor for x in slices]
    return processed


def init_task(client, taskid: int, req_num: int):
    data = get_data("taskHandler(uint256,uint256)", ["uint256", str(taskid), "uint256", str(req_num)])
    b_val = bytes.fromhex(data)
    nextNonce = client.get_nonce(ADDR)
    epoch_number = client.epoch_number()

    tx = client.new_tx(sender=ADDR,
                       receiver=CONTRACT, 
                       nonce=nextNonce,
                       gas_price=DEFAULT_TX_GAS_PRICE,
                       gas=DEFAULT_TX_GAS,
                       value=0, 
                       data=b_val, 
                       sign=True, 
                       priv_key=PK, 
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
    w = Weights(epoch, batch, layer, w_or_b, factor, offset, TASK_ID)
    w.from_weights(weight)
    data_body = w.encode()
    data_hex = data_prefix + data_body
    # print(f"[+] data in hex: {data_hex}")
    b_val = bytes.fromhex(data_hex)

    nextNonce = client.get_nonce(ADDR)
    epoch_number = client.epoch_number()

    # contract recorder addr = ''
    tx = client.new_tx(sender=ADDR,
                       receiver=CONTRACT, 
                       nonce=nextNonce,
                       gas_price=DEFAULT_TX_GAS_PRICE,
                       gas=DEFAULT_TX_GAS,
                       value=0, 
                       data=b_val, 
                       sign=True, 
                       priv_key=PK, 
                       epoch_height=epoch_number, 
                       chain_id=0)
    tx_hash = client.send_tx(tx)
    # print(f"[+] tx hash: {tx_hash}")

    while True: 
        receipt = client.get_transaction_receipt(tx_hash)
        if receipt is not None:
            # print(f"[+] tx receipt: {receipt}")
            outcomeStatus = receipt["outcomeStatus"]
            assert int(outcomeStatus) == 0, "Send tx failed"
            # print(f"[+] tx outcomeStatus: {outcomeStatus}")
            return epoch_number

    # When using python to connect to web3, the address needs to be checked first.
    # for contract address we should accept lower case address because ganache, at the moment, print contract address in lower case.
    # for account address we should accept only checksum address.


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
    while True:
        sleep(3)
        logs = client.get_logs(filt)
        if len(logs) > 0:
            return logs
    

def get_merged(client, taskid, layer, w_or_b, offset):
    data = get_data("getGift(uint256,uint64,uint64,uint128)", ["uint256", str(taskid), "uint64", str(layer), "uint64", str(w_or_b), "uint128", str(offset)])
    data = "0x" + data
    resp = cfx_call(data=data)
    return resp    


def parse_logs(logs):
    func_proto = eth_utils.keccak(b"PrepareGiftDone(uint256,uint64,uint64,uint128)")
    prepare_done = "0x" + func_proto.hex()
    for log in logs:
        topics = log['topics']
        if topics:
            if topics[0] == prepare_done:
                taskid = int(topics[1], 16)
                layer = int(topics[2], 16)
                w_or_b = int(topics[3], 16)
                offset = int(log["data"], 16)
                return taskid, layer, w_or_b, offset
    print("[-] DEBUG: PrepareGiftDone event does not omit")
            


def prepare_done(logs) -> bool:
    func_proto = eth_utils.keccak(b"PrepareGiftDone(uint256,uint64,uint64,uint128)")
    prepare_done = "0x" + func_proto.hex()
    for log in logs:
        topics = log['topics']
        if topics:
            if topics[0] == prepare_done:
                return True
    print("[-] Result does not prepared, start another loop...")
    return False


def parse_merged(data, factor):
    merged_weights = []
    # decode_many has depreciated beacause some bug
    # ret = decode_many(["uint256", "uint256", "int128[]"], data)
    # we implement simple decode manually
    assert len(data) % 32 == 0, "Invalid data"



    ret = list(chunkstring(data, 64))
    assert len(ret[4:]) == 128, "Invalid data"
    for r in ret[4:]:
        # value = hex_to_signed(r)
        # if value is not None and factor is not None:
        value = int(r, 16)
        ui = round(value/(2* 10 ** factor), factor)
        merged_weights.append(ui)
    return merged_weights


def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))


# TODO: integrate cfx_call into python sdk
def cfx_call(data: str, contract=CONTRACT):
    import requests
    import json
    headers = {
        'Content-type': 'application/json',
    }
    data = {'method': "cfx_call", 'id': 1, "jsonrpc": "2.0", "params":[{"to":CONTRACT, "data": data}]}
    data = json.dumps(data)
    # print(f"[+] DEBUG: cfx_call request data = {data}")
    response = requests.post('http://192.168.1.6:12537', headers=headers, data=data)
    print(f"[+] response = {response.json()}")
    if response.json().get('result'):
        return response.json().get('result')
    else:
        print(f"[-] Something went wrong with cfx_call.")
        return None


import math # hex string to signed integer 
def hex_to_signed(val): 
    uintval = int(val,16) 
    bits = 4 * ( len(val) - 2) 
    if uintval >= math.pow(2,bits-1): 
        uintval = int(0 - (math.pow(2,bits) - uintval)) 
        return uintval 
