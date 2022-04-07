from tree_graph.client.jsonrpc_client import *
import eth_utils

import logging

DEFAULT_TX_GAS_PRICE = 80 * (10 ** 9) * 100
DEFAULT_TX_GAS = 2100000 * 10

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    # Create an account with Conflux Portal
    client = JsonRpcClient("192.168.1.6", "12537")

    Alice_addr = "0x1f9422c17a85f15473d5e25834d17d48c2356c7c"
    Alice_prik = "0x5bba79b1fbba518c7283750cf6a1175f3180fab586c1b1787539885f3132ef4f"

    Bob_addr = "0x19aeb665dfa6a8445a46cd9a5c666ac6c0d03c54"
    #
    # two_sum = "0x8e7c354d989521408007b3b39797fca33ee1c2a8"
    # admin = client.get_admin(two_sum)
    # print("[+] contract admin is ", admin)
    # assert admin == Alice_addr
    # assert admin == Bob_addr

    nextNonce = client.get_nonce(Alice_addr)
    epoch_number = client.epoch_number()

    # test internal contract
    # internal_contract = "0x0888000000000000000000000000000000000000"    # admin
    internal_contract = "0x0888800000000000000000000000000000000000"    # sl

    # test admin
    # ek = eth_utils.keccak(b"set_admin(address,address)")
    # data_prefix = ek[0:4].hex()
    # data_body = "0000000000000000000000008e7c354d989521408007b3b39797fca33ee1c2a800000000000000000000000019aeb665dfa6a8445a46cd9a5c666ac6c0d03c54"
    # data_hex = data_prefix + data_body
    # print(f"[+] data hex = {data_hex}")
    # b_val = bytes.fromhex(data_hex)

    # test sl
    ek = eth_utils.keccak(b"record(uint8[]")
    data_prefix = ek[0:4].hex()
    data_body = "0101010101010101"
    data_hex = data_prefix + data_body
    print(f"[+] data hex = {data_hex}")
    b_val = bytes.fromhex(data_hex)

    # same code both test
    tx = client.new_tx(
                       sender=Alice_addr,
                       receiver=internal_contract, 
                       nonce=nextNonce,
                       gas_price=DEFAULT_TX_GAS_PRICE,
                       gas=DEFAULT_TX_GAS,
                       value=0, 
                       data=b_val, 
                       sign=True, 
                       priv_key=Alice_prik, 
                       epoch_height=epoch_number, 
                       chain_id=0)
    
    tx_hash = client.send_tx(tx)
    tx_hash = "0xa5f782448de6cae2c8029ce17747ca6ef12eb9cd9ff0f9cf2ca5f82caca2e18e"    # Alice
    # print("[+] the send transaction hash is ", tx_hash)  
    
    # tx_info = client.get_tx(tx_hash)
    # print(f"[+] the tx info of {tx_hash} is ", tx_info)
    
    tx_receipt = client.get_transaction_receipt(tx_hash)
    print(f"[+] the tx receip of {tx_hash} is ", tx_receipt)     # the contract is deployed after sending a transaction with data as bytecode. 
                                                            # The contractCreated field of the transaction receipt is the contract address after deployment.



