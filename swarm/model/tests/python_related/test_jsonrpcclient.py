#!/usr/bin/env python3

from jsonrpcclient.clients.http_client import HTTPClient
from jsonrpcclient.requests import Request, Notification


client = HTTPClient("http://localhost:12537")
response = client.send([Request("cfx_epochNumber", "latest_state"), Request("cfx_getNextNonce")])

for data in response.data:
    if data.ok:
        print("{}: {}".format(data.id, data.result))
        # base 存在时，视 x 为 base 类型数字，并将其转换为 10 进制数字。
        # base = 0 就是按照数字字面来解释转换
        print(f"epoch number = {int(data.result, 0)}")  # 相当于 int(data.result, 16)}
    else:
        print("{}: {}".format(data.id, data.message))