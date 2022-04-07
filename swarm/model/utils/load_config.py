import json
import toml


class Account:
    def __init__(self, name, config_path=str("../../config/Account.json")):
        self.name = str(name)
        self.path = str(config_path)
        with open(self.path, 'r') as (f):
            self.data = json.load(f)

    def address(self):
        return self.data[self.name]['address']


# Example:  print(Account('Alice').address())

class Conf:
    def __init__(self, path="../../config/config.toml"):
        self._conf = toml.load(path)

    def address(self):
        return self._conf["account"]["address"]

    def private_key(self):
        return self._conf["account"]["private_key"]
    
    def contract(self):
        return self._conf["contract"]["address"]

    def default(self, which: str):
        return self._conf["default_conf"][which]