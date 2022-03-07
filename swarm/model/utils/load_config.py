import json


class Account:
    def __init__(self, name, config_path=str("../../config/Account.json")):
        self.name = str(name)
        self.path = str(config_path)
        with open(self.path, 'r') as (f):
            self.data = json.load(f)

    def address(self):
        return self.data[self.name]['address']


# Example:  print(Account('Alice').address())
