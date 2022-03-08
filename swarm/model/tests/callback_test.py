#!/usr/bin/env python3
import numpy as np
# import tensorflow as tf
import math
from utils.utils import number_of_digits_post_decimal, caclulate_factor, get_data, \
                    get_status, split_list_by_n, processed, get_status, SPLIT_SIZE
from tree_graph.client.jsonrpc_client import *
from coder_lib import encode_many
from hexbytes import HexBytes

CLIENT = JsonRpcClient("192.168.1.31", "12537")

def test_number_of_digits_post_decimal():
    assert number_of_digits_post_decimal(-0.1234567) == 7
    assert number_of_digits_post_decimal(2.123456789) == 9


def test_caclulate_factor():
    weights = np.array([-0.00725056, 0.0168993, 0.00075373, -0.00990144, 0.00284106, 0.01322524, -0.00417293, 0.00808944, -0.02160874, 0.00079403])
    assert caclulate_factor(weights) == 8


def test_split_list_by_n():
    list_tmp = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    tmp = split_list_by_n(list_tmp, 4)
    assert list(tmp) == [[1, 2, 3, 4], [5, 6, 7, 8], [9]]


def test_processed():
    expected = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    factor = 10
    splited = [[10, 20, 30, 40], [50, 60, 70, 80], [90]]
    ret = [0.0] * 9
    offset = 0
    for s in splited:
        start = int(offset)
        end = int(offset + 4)
        ret[start: end] = processed(factor, s)
        offset += 4
    assert ret == expected


# def test_get_data():
#     func = "taskHandler(uint256,uint256)"
#     data = ["uint256", "1", "uint256", "2"]
#     ret = get_data(func, data)
#     expected = "3b18f64500000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002"
#     assert ret == expected


def test_get_status():
    epoch_num = "119f"    # epoch number or 'latest_state', or 'earliest'
    epoch_num = int(epoch_num, 16)
    print(f"[+] epoch number = {epoch_num}")
    ret = get_status(CLIENT, int(epoch_num))
    print(f"[+] logs[] from epoch {epoch_num} is {ret}")
    topics = ret[0]["topics"]
    print(f"[+] topices: {topics}")
    # print(f"[+] address: {HexBytes(topics[2])}")
    # assert HexBytes(topics[2]) == "0x19aeb665dfa6a8445a46cd9a5c666ac6c0d03c54"


# def test_full_steps():
#     # take epoch 1 batch 100 as an example
#     # on batch end 
#     print('\n')
#     print("=================================================================")
#     print("                        Sync model                               ")
#     print("=================================================================")
#     checkpoint_path = "/swarm/model/checkpoints/weights.01-100.h5"
#     model = _get_model()
#     # Loads the weights
#     model.load_weights(checkpoint_path)
#     weights = model.get_weights() 
#     size = len(weights)

#     super_big_list = []
#     for x in range(0, size):
#         shape = weights [x].shape
#         print(f"[+] weights[{x}]'s shape = {shape}")
#         flattend = list(weights [x].flatten())
#         # print(f"[+] after flatten: weights[{x}] = {flattend}")
#         # Calculate the factor that should be expanded, cause solidity only has int256 and uint256
#         factor = caclulate_factor(flattend)
#         flattend = expand_with_factor(flattend, factor)
#         # print(f"[+] after expand with factor: weights[{x}] = {flattend}")
#         # type = 0 means `w` while 1 means `b`
#         wb = 0 if x % 2 == 0 else 1
#         if should_split(shape):
#             assert len(flattend) == shape[0] * shape[1]
#             to_transfer = list(split_list_by_n(flattend, SPLIT_SIZE))
#             print(f"[+] after split, we will transfer {len(to_transfer)} items (vec[weights_after_expand])")
#             assert len(to_transfer) == math.ceil(shape[0] * shape[1] / SPLIT_SIZE)
#             # print(f"[+] after split: transfer = {to_transfer}")
#             offset = 0
#             # print(f"[+] offset: ", end=' ')
#             for tt in to_transfer:
#                 packed = []
#                 packed.append(x)
#                 packed.append(factor)
#                 packed.append(wb)
#                 packed.append(offset)
#                 packed.append(tt)
#                 # print(offset, end=' ')
#                 offset += SPLIT_SIZE
#                 super_big_list.append(packed)
#             # print('\n')
            
#         else:
#             print(f"[+] donnot need split just flatten")
#             packed = []
#             packed.append(x)
#             packed.append(factor)
#             packed.append(wb)
#             packed.append(0)
#             packed.append(flattend)
#             super_big_list.append(packed)
#         print(f"[+] there are {len(super_big_list)} elements in super big list")
    
#     print("=================================================================")
#     print("                      Reconstitution                             ")
#     print("=================================================================")
#     # prepare containers
#     prepare_list = locals()
#     for i in range(0, size):
#         shape = weights[i].shape
#         prepare_list['layer_' + str(i)] = []

#     for sbl in super_big_list:
#         layer = sbl[0]
#         factor = sbl[1]
#         offset = sbl[3]
#         merged_weights = sbl[4]
#         pd = processed(10**factor, merged_weights)
#         prepare_list['layer_' + str(layer)].extend(pd)
#     # print(f"[+] prepare_list['layer_3'] = {prepare_list['layer_3']}")
#     for i in range(0, size):
#         print(f"[+] the {i}^th container layer_{i}'s length is {len(prepare_list['layer_' + str(i)])}")

    
#     ret_l = []
#     for i in range(0, size):
#         before = np.array(prepare_list['layer_' + str(i)])
#         # shape = weights[i].shape
#         ret = before.reshape(weights[i].shape)
#         # print(f"[+] after reshape: {ret}")
#         print(f"[+] after reshape shape: {ret.shape}")
#         ret_l.append(ret)
#     merged_weights = np.array(ret_l)
#     print(f"[+] a random result weight is: {merged_weights[0][0][0]}")
#     model.set_weights(merged_weights)
#     model.summary()

# def _get_model():
#     model = tf.keras.models.Sequential([
#         tf.keras.layers.Flatten(input_shape=(28, 28)),
#         tf.keras.layers.Dense(512, activation=tf.nn.relu),
#         tf.keras.layers.Dropout(0.2),
#         tf.keras.layers.Dense(10, activation=tf.nn.softmax)
#     ])

#     model.compile(optimizer='adam',
#                     loss='sparse_categorical_crossentropy',
#                     metrics=['accuracy'])

#     return model
