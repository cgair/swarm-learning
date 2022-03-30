from tree_graph.contract import *

if __name__ == '__main__':
    contract = contract_call.ContractHandler("http://47.100.118.83:12537", "erc_721.json", "0x89422c54c466357a662411e9f94a326e0fb2d2a3")
    total = contract.get_total()
    print(total)
