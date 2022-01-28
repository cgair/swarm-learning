import os
import subprocess
import socket

CLUSTER = ["localhost:50051", "localhost:23456"]
MODEL_DIR = "./checkpoints/"
CHECKPOINTS_DIR = ""
UFS_CLI = "/home/chenge/workplace/ufs/target/debug/ufs"
TASK_ID = "uuid-001"

def file_prepared(epoch, batch):
    model_name = 'weights.{:0>2}-{:0>2}.hdf5'.format(epoch, batch)
    model_path = MODEL_DIR + model_name
    print(f"model path = {model_path}")
    if os.path.exists(model_path):
        return True, model_path
    return False, ""


def send_file(task_id, filename):
    # Here we simply use a loop to send insights to other workers in the cluster
    for socket in CLUSTER:
        ss = socket.split(":")
        ip = ss[0]
        port = ss[-1]
        cmd = f"{UFS_CLI} upload --ip-address=\"{ip}\" -p {port} -f \"{filename}\" -t \"{task_id}\""
        # Create a child process that does not wait
        child = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={'UFS_LOG': 'info'})    #将标准输出定向输出到subprocess.PIPE
        # child.wait() # 等待子进程结束
        # print(child.stdout.read())
        print(child.stderr.read())


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

