import subprocess
from utils import send_file
import socket

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

if __name__ == '__main__':
    # s1 = 'weights.{:0>2}-{:0>2}.hdf5'.format(1, 100)
    # s2 = 'weights.{:0>2}-{:0>2}.hdf5'.format(10, 600)
    # print(s1, s2)

    # res = subprocess.Popen("lm -l",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    # # 标准输出为空
    # print(res.stdout.read())
    # #标准错误中有错误信息
    # print(res.stderr.read())

    send_file("uuid-004", "/home/chenge/workplace/ufs/config/default.toml")
    print(get_host_ip())