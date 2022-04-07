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

    nextNonce = client.get_nonce(Alice_addr)
    epoch_number = client.epoch_number()

    # test internal contract
    precompiled_contract = "0x0000000000000000000000000000000000000002"    # 

    # test 
    data = "01" * 400000
    b_val = bytes.fromhex(data)

    # same code both test
    tx = client.new_tx(
                       sender=Alice_addr,
                       receiver=precompiled_contract, 
                       nonce=nextNonce,
                       gas_price=DEFAULT_TX_GAS_PRICE,
                       gas=DEFAULT_TX_GAS,
                       value=0, 
                       data=b_val, 
                       sign=True, 
                       priv_key=Alice_prik, 
                       epoch_height=epoch_number, 
                       chain_id=0)
    
    # tx_hash = client.send_tx(tx)
    # short data success
    # tx_hash = "0x29eff1215b8ef2f97d6f93f0cfca547e6e0689cc4892b42d97ef8a0ac5181d5c"    # Alice
    # larger data
    tx_hash = "0xa595b860f92c0a0b5d70b5af4d90170963804a7a15804816bd80ec35923f72fc"    # Alice
    # print("[+] the send transaction hash is ", tx_hash)  
    
    # tx_info = client.get_tx(tx_hash)
    # print(f"[+] the tx info of {tx_hash} is ", tx_info)
    
    tx_receipt = client.get_transaction_receipt(tx_hash)
    print(f"[+] the tx receip of {tx_hash} is ", tx_receipt)     # the contract is deployed after sending a transaction with data as bytecode. 
                                                            # The contractCreated field of the transaction receipt is the contract address after deployment.


    import hashlib
    data = "00000001010101"     # 0xd320665ee40e9320e3c59b0cc2b3c279dcb4459938283a6140b42973b4e66664
    b_val = bytes.fromhex(data)
    m = hashlib.sha256()
    m.update(b_val)
    dh = "0x" + (m.digest()).hex()  
    print(f"[+] digest in hex: {dh}")

    # res = "0x27ecd0a598e76f8a2fd264d427df0a119903e8eae384e478902541756f089dd1"
    # 0x27ecd0a598e76f8a2fd264d427df0a119903e8eae384e478902541756f089dd1
