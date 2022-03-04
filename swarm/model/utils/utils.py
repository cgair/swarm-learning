#!/usr/bin/env python3
import os
import subprocess
import socket
from time import sleep
from typing import List, Tuple
from utils.weights_wrapper import Weights

# MODEL_DIR = "/swarm/model/checkpoints/"
MODEL_DIR = "/swarm/swarm/model/checkpoints/"
SPLIT_SIZE = 1024

# The following item has been depreciated
CLUSTER = ["61.129.70.134:50051", "61.129.70.134:50052"]
UFS_CLI = "ufs"
FS_ROOT_DIR = "/ufs/SMLNODE/fs/"


def file_prepared(epoch, batch):
    model_name = 'weights.{:0>2}-{:0>2}.h5'.format(epoch, batch)
    model_path = MODEL_DIR + model_name
    if os.path.exists(model_path):
        return True, model_path
    return False, ""


def send_file(task_id, filename):
    # Here we simply use a loop to send insights to other workers in the cluster
    for socket in CLUSTER:
        ss = socket.split(":")
        ip = ss[0]
        port = int(ss[-1])
        cmd = f"{UFS_CLI} upload --ip-address=\"{ip}\" -p {port} -f \"{filename}\" -t \"{task_id}\""
        # Create a child process that does not wait
        child = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={'UFS_LOG': 'info'})    #将标准输出定向输出到subprocess.PIPE
        child.wait() # 等待子进程结束
        # print(child.stdout.read())
        # print(child.stderr.read())
        ret_bytes = child.stderr.read()
        ret_string = str(ret_bytes, 'UTF-8')
        print(ret_string)
        if "OK" in ret_string:
            return True
        else:
            return False


def get_host_ip():
    """
    Query the local ip address
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def get_merge_file(task_id, epoch, batch):
    model_name = 'weights.{:0>2}-{:0>2}.h5'.format(epoch + 1, batch + 1)
    peer_model_path = FS_ROOT_DIR + task_id + "/" + model_name
    while True:
        print("Searching file...")
        sleep(5)
        if os.path.exists(peer_model_path):
            return peer_model_path


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


def send_msg(func: str, epoch: int, batch: int, layer: int, w_or_b: int, factor: int, offset: int, weight: List[int]):
    """
    """
    w = Weights(epoch, batch, layer, w_or_b, factor, offset)
    w.from_weights(weight)
    data_body = w.encode()
    return data_body


def expand_with_factor(weights, factor: int) -> List[int]:
    for i in range(0, len(weights)):
        weights[i] = weights[i] * (10 ** factor)
        if weights[i] >= 0:
            weights[i] = int(weights[i] + 0.5 )
        elif weights[i] < 0:
            weights[i] = int(weights[i] - 0.5 )
    return weights




        

