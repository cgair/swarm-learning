#!/usr/local/bin/python
from coder_lib import encode_array

def int_encode():
    ret = encode_array("int256", "-2")
    expected = "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe"
    print(ret)
    assert ret == expected

if __name__ == '__main__':
    int_encode()