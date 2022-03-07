from conflux import (
    Conflux,
    HTTPProvider,
)
from hexbytes import HexBytes


class event_filter():
    def __init__(self, rpc_addr, contract_addr, task_id, layer, w_or_b, offset, timeout):
        self.c = Conflux(HTTPProvider(str(rpc_addr)))
        self.contract_addr = contract_addr
        self.task_id = task_id
        self.layer = layer
        self.w_or_b = w_or_b
        self.offset = offset
        self.timeout = timeout

    def update_watching_info(self, task_id, layer, w_or_b, offset):
        self.task_id = task_id
        self.layer = layer
        self.w_or_b = w_or_b
        self.offset = offset

    def __perpare_gift_event(self, contract_logs):
        for i in contract_logs:
            if (
                    i['address'] == self.contract_addr and
                    int(HexBytes(i["topics"][1]).hex(), 16) == self.task_id and
                    int(HexBytes(i["topics"][2]).hex(), 16) == self.layer and
                    int(HexBytes(i["topics"][3]).hex(), 16) == self.w_or_b and
                    int(HexBytes(i["data"]).hex(), 16) == self.offset
            ):
                return True
            else:
                return False

    def report(self):
        counter = 0
        pervious_epoch = self.c.cfx.epochNumber("latest_confirmed") - 1
        while counter < self.timeout:
            lasted_epoch = self.c.cfx.epochNumber("latest_confirmed")
            if pervious_epoch >= lasted_epoch:
                continue
            else:
                contract_logs = self.c.cfx.getLogs({"fromEpoch": 66617355, "toEpoch": 66617356})
                if (len(contract_logs) > 0):
                    print(contract_logs)
                    if self.__perpare_gift_event(contract_logs):
                        return
                    else:
                        counter += 1
            counter += 1
        return False

#spy = event_filter('https://test.confluxrpc.com', "cfxtest:xxxxx",
# 1, 1, 1, 1, 10)

#print(spy.report())
