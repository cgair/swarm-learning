#!/usr/bin/env python3
import os
import subprocess
from time import sleep

MODEL_DIR = "/swarm/model/checkpoints/" # sl2
# CLUSTER = ["172.17.0.3:50051"] # sl2
CLUSTER = ["172.17.0.4:50051"] # sl1
UFS_CLI = "ufs"
FS_ROOT_DIR = "/ufs/SMLNODE/fs/"
TASKID = "uuid-000"

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


def get_merge_file(task_id, epoch, batch):
    model_name = 'weights.{:0>2}-{:0>2}.h5'.format(epoch + 1, batch + 1)
    peer_model_path = FS_ROOT_DIR + task_id + "/" + model_name
    while True:
        print(f"[+] Search file {peer_model_path}...")
        sleep(5)
        if os.path.exists(peer_model_path):
            return peer_model_path