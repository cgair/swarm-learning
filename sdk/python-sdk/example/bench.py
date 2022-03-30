from tree_graph.client.jsonrpc_client import *
import _thread
import sys

# 默认请求参数
default_gas_price = 1
default_gas = 21000
# 定义发送方数据
private_key = ['0x69bf5d8eae905a74439e1116f6c45964eeb05bcfa00b4355492e3ead40f093a5',
               '0x3813799f2699c8797f64d388ea7da8acdc5f5bd6651a7d0aa0597834747e478b',
               '0xa43ba2cda8052a8ae5b53da9bde449657d44b3a5c82f59a7deebd3216ef9e789',
               '0x4ee30319d4a49866393527fe44e26619478f71a68a6e6f5f9d32268fec9f931f',
               '0xc076217579b76f7ed43ff269762015dc2d547acce34b5c66610d5caa940bfb84']

# 定义地址
addresses = ['0x10ba9121d5755a3892deea290c6e51d43ec27b4a', '0x17a51bdc0d150789913ac21fdd1c1904a5cceb8f',
             '0x130a072407b08025779d651374c99251481b8474', '0x1158088194fa8a153675d1b788d53497856093a2',
             '0x1192d56cc52dfe980bea34b0ab348aa9aade540e']

# 定义访问客户端
# clients = [JsonRpcClient("172.22.84.139", "12537"), JsonRpcClient("172.22.84.141", "12537"),
#            JsonRpcClient("172.22.84.140", "12537"), JsonRpcClient("172.22.84.151", "12537")]


# 发送交易接口
def send_tx(cli, addr, sk, static_tx_number):
    tx_count = 0
    epoch_number = cli.epoch_number()
    start = cli.get_nonce(addr)
    print("start epoch number is: ", epoch_number, " start the nonce is: ", start)
    for index in range(start, static_tx_number + 1):
        tx = cli.new_tx(sender=addr, receiver=addr, nonce=index, gas=default_gas, gas_price=default_gas_price,
                        value=0, data=b'', sign=True, priv_key=sk, epoch_height=epoch_number, chain_id=0)
        tx_hash = cli.send_tx(tx)
        tx_count += 1

    # return tx_hash, tx_count


# 定义bench mark函数
def bench(tx_count):
    try:
        for i in range(0, 5):
            _thread.start_new_thread(send_tx, (clients[i % 4], addresses[i], private_key[i], tx_count,))
    except:
        print("threading start and execute error!")


# 统计结果 334 1122
def statistical_results(cli, start_epoch, end_epoch):
    for index in range(start_epoch, end_epoch):
        tx_account = 0
        blocks_hashes = cli.blocks_by_epoch(index)
        for block_hash in blocks_hashes:
            block = cli.block_by_hash(block_hash, True)
            for tx in block["transactions"]:
                if tx["status"] == '0x0':
                    tx_account += 1
    start_timestamp = cli.block_by_hash(cli.blocks_by_epoch(start_epoch))["timestamp"]
    end_timestamp = cli.block_by_hash(cli.blocks_by_epoch(end_epoch))["timestamp"]
    print("打包交易总笔数：", tx_account)
    print("TPS: ", tx_account / (int(end_timestamp, base=16) - int(start_timestamp, base=16)))


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print("请输入参数")
        exit

    send_tx(clients[int(sys.argv)], addresses[int(sys.argv)], private_key[int(sys.argv)], 100000)
    print("结束Epoch: ", clients[int(sys.argv)].epoch_number())

# bench(10000000)
# send_tx(clients[0], addresses[0], private_key[0], 0)
# tx_account = 0
# for epoch in range(6000, 7000):
#     # time.sleep(10 * 60)
#     blocks = clients[0].blocks_by_epoch(hex(epoch))
#     for block_hash in blocks:
#         block = clients[0].block_by_hash(block_hash, True)
#         for tx in block["transactions"]:
#             if tx["status"] == "0x0":
#                 tx_account += 1
#
# print("tx_account = ", tx_account)
# print(hex(6000))
# print(hex(6999))
#
# print(11659 / (int('0x61c1af34', base=16) - int('0x61c1aece', base=16)))


# time.sleep(10 * 60)
# blocks = clients[0].blocks_by_epoch(hex(400))
# print(blocks)
# for block_hash in blocks:
#     block = clients[0].block_by_hash(block_hash, True)
#     for tx in block["transactions"]:
#         print(tx["status"])
