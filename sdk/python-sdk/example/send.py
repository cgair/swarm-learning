from tree_graph.client.jsonrpc_client import *

Default_GasPrice = 80 * (10 ** 9)
Default_Gas = 2100000
Private_Key = '0xce368dbb90c1db5686121ab0a908f67e53b3e4593ae867f30bcc9173ba3d0de5'

if __name__ == '__main__':
    client = JsonRpcClient("localhost", "12537")

    #
    epoch_number = client.epoch_number()
    print("epoch number is ", epoch_number)

    # 
    # balance = client.get_balance('0x1a5882850cc8f38b12c929138ee3fec952a507a1')
    # print("the balance is ", balance / 10 ** 18)

    #
    nextNonce = client.get_nonce('0x1e19b9df8827c1915964a333d2a12ba9bd0e95a5')
    print("the next nonce is ", nextNonce)

    # 
    best_hash = client.best_block_hash()
    print("the best block hash is ", best_hash)

    # if nextNonce == 19844:
    #     nextNonce = 19843
        # block = client.block_by_hash('0x74d5d314f1f31f78ea71b8c17ba077c97fd225e8f7e79ea1254f402224fcf7f3', True)
    # print("the block is ", block)

    # blocks = client.blocks_by_epoch('0x2')
    # print("the blocks is ", blocks)
    #
    # block = client.block_by_epoch('0x2')
    # print("the block is ", block)

    # tx_info = client.get_tx('0x3673ad5bd406909090de6001f640e64da1ccfc6b1ea0f07d87b2c3c36f887e81')
    # print("the tx info is ", tx_info)

    # for i in range(12701, 12717):

    # create the transaction
    # tx = client.new_tx(sender='0x1e19b9df8827c1915964a333d2a12ba9bd0e95a5',
    #                    receiver='0x1e19b9df8827c1915964a333d2a12ba9bd0e95a5', nonce=nextNonce,
    #                    gas_price=Default_GasPrice,
    #                    gas=Default_Gas,
    #                    value=0, data=b'', sign=True, priv_key=Private_Key, epoch_height=epoch_number, chain_id=0)
    # #
    # tx_hash = client.send_tx(tx)
    # print("the send transaction hash is ", tx_hash)

# tx = client.new_tx(sender='0x14ea5d12a23441edf328f5959cb2bb51de47ed30',
#                    receiver='0x14ea5d12a23441edf328f5959cb2bb51de47ed30', nonce=346, gas_price=Default_GasPrice,
#                    gas=Default_Gas,
#                    value=0, data=b'', sign=True, priv_key=Private_Key, epoch_height=epoch_number, chain_id=0)
#
# tx_hash = client.send_tx(tx)
# print("the send transaction hash is ", tx_hash)
