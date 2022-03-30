import rlp
from rlp.sedes import binary
import eth_utils
import sha3
import web3


class UnsignedTransaction(rlp.Serializable):
    fields = [
        ('data', binary),
    ]

    def __init__(self, data):
        super(UnsignedTransaction, self).__init__(
            data=data
        )


if __name__ == '__main__':
    # 
    # hex_val = '4120717569636b2062726f776e20666f78'
    # hex_val = "1003e2d20000000000000000000000000000000000000000000000000000000000000002"
    # b_val = bytes.fromhex(hex_val)
    # print(f"hex to bytes: {b_val}")

    # data = b'0x1003e2d20000000000000000000000000000000000000000000000000000000000000002'
    # print(f"data len = {len(data)}")
    # data = b"me"
    
    # tx = UnsignedTransaction(b_val)
    # print(f"tx data = {tx.data}")

    # encoded = eth_utils.encode_hex(rlp.encode(tx))
    # print(encoded)

    # # use sha3.keccak_256
    # k = sha3.keccak_256()
    # mystring = "add(uint256)"
    # b = bytes(mystring, 'utf-8')
    # k.update(b)
    # print(k.hexdigest())
    
    # use eth_utils.keccak
    ek = eth_utils.keccak(b"add(uint256)")
    # print(ek.hex())
    # assert(k.hexdigest(), ek)

    # use web3.sha3
    ws = web3.Web3.sha3(text='add(uint256)')
    ws4 = ws[0:4]
    print(ws4.hex())
    assert(ws, ek)
