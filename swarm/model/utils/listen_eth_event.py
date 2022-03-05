from web3 import HTTPProvider, Web3
import json
import time


#  TODO: __all__ = ['Listener.init_task_event', 'update_task_event', 'record_event', 'prepare_event']
#  当合约更新时更新此字段
contract_recorder_abi = '[{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"taskID","type":"uint256"},{"indexed":false,"internalType":"address","name":"who","type":"address"}],"name":"InitTaskDone","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"taskID","type":"uint256"},{"indexed":false,"internalType":"uint64","name":"layer","type":"uint64"},{"indexed":false,"internalType":"uint64","name":"w_or_b","type":"uint64"},{"indexed":false,"internalType":"uint128","name":"offset","type":"uint128"}],"name":"PrepareGiftDone","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"taskID","type":"uint256"},{"indexed":false,"internalType":"address","name":"who","type":"address"},{"indexed":false,"internalType":"uint64","name":"layer","type":"uint64"},{"indexed":false,"internalType":"uint64","name":"w_or_b","type":"uint64"},{"indexed":false,"internalType":"uint128","name":"offset","type":"uint128"}],"name":"RecordDone","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"taskID","type":"uint256"},{"indexed":false,"internalType":"address","name":"who","type":"address"},{"indexed":false,"internalType":"uint256","name":"enrollCount","type":"uint256"}],"name":"UpdateTaskDone","type":"event"},{"constant":false,"inputs":[],"name":"clean","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"taskID","type":"uint256"},{"internalType":"uint64","name":"layer","type":"uint64"},{"internalType":"uint64","name":"w_or_b","type":"uint64"},{"internalType":"uint128","name":"offset","type":"uint128"}],"name":"getGift","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"int128[]","name":"","type":"int128[]"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"taskID","type":"uint256"},{"internalType":"uint64","name":"layer","type":"uint64"},{"internalType":"uint64","name":"w_or_b","type":"uint64"},{"internalType":"uint128","name":"offset","type":"uint128"}],"name":"getTest1","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"int128[]","name":"","type":"int128[]"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getTest2","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"taskID","type":"uint256"},{"internalType":"uint128","name":"epoch","type":"uint128"},{"internalType":"uint128","name":"batch","type":"uint128"},{"internalType":"uint64","name":"layer","type":"uint64"},{"internalType":"uint64","name":"w_or_b","type":"uint64"},{"internalType":"uint128","name":"factor","type":"uint128"},{"internalType":"uint128","name":"offset","type":"uint128"},{"internalType":"int128[]","name":"para","type":"int128[]"}],"name":"recordPara","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"uint256","name":"reqNum","type":"uint256"}],"name":"taskHandler","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'


class Listener:
    """
    本类被用于创建监听事件的方法, 初始化时需要如下参数 \n
    rpc地址, 实例化的Recorder.sol地址, 监听次数(默认 10), 监听间隔(默认2 单位 sec) \n
    由此确保通过thread调用时可以安全退出
    """
    def __init__(self, rpc_addr, contract_addr, max_req_times=10, interval=2):
        self.web3 = Web3(HTTPProvider(rpc_addr))
        self.contract_addr = contract_addr
        self.contract_abi = json.loads(contract_recorder_abi)
        self.contract = self.web3.eth.contract(
            address=self.contract_addr, abi=self.contract_abi)
        self.max_req_times = max_req_times
        self.interval = interval

    def __log_loop(self, event_filter, features, flags):
        count = 0
        result = True
        while count < self.max_req_times:  # count <= 10:
            for event in event_filter.get_new_entries():
                count_pre_event = 0
                for i in range(len(features)):
                    ''' 测试函数
                    print(json.loads(Web3.toJSON(event))["args"][features[i]])
                    print(type(json.loads(Web3.toJSON(event))["args"][features[i]]))
                    print(flags[i])
                    print(type(flags[i]))
                    '''
                    if json.loads(Web3.toJSON(event))["args"][features[i]] == flags[i]:
                        count_pre_event += 1
                    else:
                        result = False
                        count_pre_event = 0
                if count_pre_event == len(features):  # 在上面的for循环遍历掉所有feature且都为True时则返回
                    return result
            count += 1
            time.sleep(self.interval)
        return False

    def init_task_event(self, task_id, who):
        """
        Return true when task init succ \n
        task_id: uint256 \n
        who: string, who INITED this task, string of eth account address such like '0x0123456789abcdef0123456789abcdef01234567'
        """
        features = ['taskID', 'who']
        flags = [task_id, who]
        return self.__log_loop(self.contract.events.InitTaskDone.createFilter(fromBlock='latest'),
                               features, flags)

    def update_task_event(self, task_id, who):
        """
        Return true when new partner join exist task succ \n
        task_id: uint256 \n
        who: string, who UPDATED this task, eth account address
        """
        features = ['taskID', 'who']
        flags = [task_id, who]
        return self.__log_loop(self.contract.events.UpdateTaskDone.createFilter(fromBlock='latest'),
                               features, flags)

    def record_event(self, task_id, who, layer, w_or_b, offset):
        """
        Return true when upload parameters to the block_chain_network succ \n
        task_id: uint256 \n
        who: string, who UPLOADED parameters, eth account address \n
        layer: uint the index of ml model layer \n
        w_or_b: uint, the type(weight or bias) of parameters \n
        offset: uint the offset in the matrix
        """
        features = ['taskID', 'who', 'layer', 'w_or_b', 'offset']
        flags = [task_id, who, layer, w_or_b, offset]
        return self.__log_loop(self.contract.events.RecordDone.createFilter(fromBlock='latest'),
                               features, flags)

    def gift_prepare_event(self, task_id, layer, w_or_b, offset):
        """
        Return true when parameters merged successfully by the block_chain_network node \n
        task_id: uint256 \n
        layer: uint the index of ml model layer \n
        w_or_b: uint, the type(weight or bias) of parameters \n
        offset: uint the offset in the matrix
        """
        features = ['taskID', 'layer', 'w_or_b', 'offset']
        flags = [task_id, layer, w_or_b, offset]
        return self.__log_loop(self.contract.events.PrepareGiftDone.createFilter(fromBlock='latest'),
                               features, flags)
