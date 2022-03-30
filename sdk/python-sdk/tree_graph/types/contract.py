#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0
import json

import solcx
import web3

solcx.set_solc_version('v0.5.17')


def get_contract_instance(contract_dict=None,
                          source=None,
                          contract_name=None,
                          address=None,
                          abi_file=None,
                          bytecode_file=None):
    w3 = web3.Web3()
    contract = None
    if source and contract_name:
        output = solcx.compile_files([source])
        contract_dict = output[f"{source}:{contract_name}"]
        if "bin" in contract_dict:
            contract_dict["bytecode"] = contract_dict.pop("bin")
        elif "code" in contract_dict:
            contract_dict["bytecode"] = contract_dict.pop("code")
    if contract_dict:
        contract = w3.eth.contract(
            abi=contract_dict['abi'], bytecode=contract_dict['bytecode'], address=address)
    elif abi_file:
        with open(abi_file, 'r') as abi_file:
            abi = json.loads(abi_file.read())
        if address:
            contract = w3.eth.contract(abi=abi, address=address)
        elif bytecode_file:
            if bytecode_file:
                with open(bytecode_file, 'r') as bytecode_file:
                    bytecode = bytecode_file.read()
                contract = w3.eth.contract(abi=abi, bytecode=bytecode)
            else:
                raise ValueError("The bytecode or the address must be provided")
    return contract
