from web3 import HTTPProvider, Web3
import json
import time


def log_loop(event_filter, poll_interval, features, flags):
    count = 0
    result = True
    while count <= 10:  #TODO: 等待时长上限 如果需要外部控制的话 请把这里改成True
        for event in event_filter.get_new_entries():
            for i in range(len(features)):
                print(json.loads(Web3.toJSON(event))["args"][features[i]])
                print(type(json.loads(Web3.toJSON(event))["args"][features[i]]))
                print(flags[i])
                print(type(flags[i]))
                if json.loads(Web3.toJSON(event))["args"][features[i]] == flags[i]:

                    result = True
                else:
                    result = False
            if result:
                print("hello")
                return result
        count += 1
        time.sleep(poll_interval)
    return False


class Listener:
    def __init__(self, rpc_addr, contract_addr, contract_raw_abi):
        self.web3 = Web3(HTTPProvider(rpc_addr))
        self.contract_addr = contract_addr
        self.contract_abi = json.loads(contract_raw_abi)
        self.contract = self.web3.eth.contract(
            address=self.contract_addr, abi=self.contract_abi)

    def init_task_event(self, task_id, who):
        features = ['taskID', 'who']
        flags = [task_id, who]
        log_loop(self.contract.events.InitTaskDone.createFilter(fromBlock='latest'),
                 2, features, flags)

    def update_task_event(self, task_id, who):
        features = ['taskID', 'who']
        flags = [task_id, who]
        log_loop(self.contract.events.UpdateTaskDone.createFilter(fromBlock='latest'),
                 2, features, flags)

    def record_event(self, task_id, who, layer, w_or_b, offset):
        features = ['taskID', 'who', 'layer', 'w_or_b', 'offset']
        flags = [task_id, who, layer, w_or_b, offset]
        log_loop(self.contract.events.RecordDone.createFilter(fromBlock='latest'),
                 2, features, flags)

    def prepare_event(self, task_id, layer, w_or_b, offset):
        features = ['taskID', 'layer', 'w_or_b', 'offset']
        flags = [task_id, layer, w_or_b, offset]
        log_loop(self.contract.events.PrepareGiftDone.createFilter(fromBlock='latest'),
                 2, features, flags)
