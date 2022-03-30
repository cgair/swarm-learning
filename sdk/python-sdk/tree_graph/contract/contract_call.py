import json
from os import path

from tree_graph.contract.web3 import Web3, HTTPProvider


class ContractHandler(object):
    def __init__(self, url: str, abi_path: str, contract_addr: str):
        self.web3 = Web3(HTTPProvider(url))
        self.contract_addr = contract_addr
        dir_path = path.dirname(path.realpath(__file__))
        with open(str(path.join(dir_path, abi_path)), 'r') as abi_definition:
            self.abi = json.load(abi_definition)

        self.contract = self.web3.eth.contract(address=Web3.toChecksumAddress(self.contract_addr), abi=self.abi)

    # @property
    def get_total(self) -> int:
        print(self.contract.all_functions())
        return self.contract.functions.totalSupply().call()
