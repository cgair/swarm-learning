#!/usr/bin/env python3
import numpy as np
import tensorflow as tf
import math
from utils.utils import number_of_digits_post_decimal, caclulate_factor, expand_with_factor, \
                    should_split, split_list_by_n, processed, SPLIT_SIZE, parse_logs
def test_parse_logs():
    logs = [{'address': '0x8c7d67a81a7148dff4aafbba94b06e3c1fa86cd6', 'blockHash': '0xf52e55311921408d706dcf875b3574ef568d64dbb52d80022b4968b48d5e463c', 'data': '0x', 'epochNumber': '0x1944', 'logIndex': '0x0', 'topics': ['0x37bb154f4af11c2ad09fcb84fcfa4c6b5d8e1a9cf9f7fc6dedf09d9b9cac0af8', '0x0000000000000000000000000000000000000000000000000000000000000004', '0x00000000000000000000000019aeb665dfa6a8445a46cd9a5c666ac6c0d03c54'], 'transactionHash': '0xe464ed58cdc80b9e5329ffa85d3d91ef8319ae73acf7a9e06e2e28ef5e3f45ca', 'transactionIndex': '0x0', 'transactionLogIndex': '0x0'}, {'address': '0x8c7d67a81a7148dff4aafbba94b06e3c1fa86cd6', 'blockHash': '0x149fd239d91bca22e7fe034d4065c589089637b9e0dedba84e08ee47634b0157', 'data': '0x00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000', 'epochNumber': '0x1947', 'logIndex': '0x0', 'topics': ['0x5213845946959a8b4c3e89b8a2f5000fd33f91e39c10c86df18ae57605c2cd35', '0x0000000000000000000000000000000000000000000000000000000000000004', '0x00000000000000000000000019aeb665dfa6a8445a46cd9a5c666ac6c0d03c54', '0x0000000000000000000000000000000000000000000000000000000000000000'], 'transactionHash': '0x4777572d2590606929019574788ab890fcb98fac8e8f6cad95b857b76cc8249e', 'transactionIndex': '0x0', 'transactionLogIndex': '0x0'}, {'address': '0x8c7d67a81a7148dff4aafbba94b06e3c1fa86cd6', 'blockHash': '0xe36c68572f95fcad67c18710eb432e305c94bb0e95161e16e72a12d4176de7a4', 'data': '0x0000000000000000000000000000000000000000000000000000000000000002', 'epochNumber': '0x1956', 'logIndex': '0x0', 'topics': ['0xc1fe5bc39b930588ec2115239681b70237f5cd8e637e5ec2acf68ae33e879126', '0x0000000000000000000000000000000000000000000000000000000000000004', '0x0000000000000000000000001f9422c17a85f15473d5e25834d17d48c2356c7c'], 'transactionHash': '0x6545f1016c4806ab2ec61ab696760c2fa74ef101c729bd9291cd9c9fb5f3204e', 'transactionIndex': '0x0', 'transactionLogIndex': '0x0'}, {'address': '0x8c7d67a81a7148dff4aafbba94b06e3c1fa86cd6', 'blockHash': '0x56c39d225714b53ce240b3e969ee435355dd90b694a3ff1f9e2d74ff93b049e5', 'data': '0x0000000000000000000000000000000000000000000000000000000000000000', 'epochNumber': '0x195a', 'logIndex': '0x0', 'topics': ['0x5572b3f2f4cc6c154ee555ce79315632da4659523f9ae1d8dbebf71e6fcf58ef', '0x0000000000000000000000000000000000000000000000000000000000000004', '0x0000000000000000000000000000000000000000000000000000000000000000', '0x0000000000000000000000000000000000000000000000000000000000000001'], 'transactionHash': '0x83ce1c4a048bef5c4702e23588fd31c58ef767db66f987d60c445c342e924ce7', 'transactionIndex': '0x0', 'transactionLogIndex': '0x0'}]
    taskid, layer, w_or_b, offset = parse_logs(logs)
    assert taskid == 4
    assert layer == 0
    assert w_or_b == 1
    assert offset == 0

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


def test_full_steps():
    # take epoch 1 batch 100 as an example
    # on batch end 
    print('\n')
    print("=================================================================")
    print("                        Sync model                               ")
    print("=================================================================")
    checkpoint_path = "/swarm/model/checkpoints/weights.01-100.h5"
    model = _get_model()
    # Loads the weights
    model.load_weights(checkpoint_path)
    weights = model.get_weights() 
    size = len(weights)

    super_big_list = []
    for x in range(0, size):
        shape = weights [x].shape
        print(f"[+] weights[{x}]'s shape = {shape}")
        flattend = list(weights [x].flatten())
        # print(f"[+] after flatten: weights[{x}] = {flattend}")
        # Calculate the factor that should be expanded, cause solidity only has int256 and uint256
        factor = caclulate_factor(flattend)
        flattend = expand_with_factor(flattend, factor)
        # print(f"[+] after expand with factor: weights[{x}] = {flattend}")
        # type = 0 means `w` while 1 means `b`
        wb = 0 if x % 2 == 0 else 1
        if should_split(shape):
            assert len(flattend) == shape[0] * shape[1]
            to_transfer = list(split_list_by_n(flattend, SPLIT_SIZE))
            print(f"[+] after split, we will transfer {len(to_transfer)} items (vec[weights_after_expand])")
            assert len(to_transfer) == math.ceil(shape[0] * shape[1] / SPLIT_SIZE)
            # print(f"[+] after split: transfer = {to_transfer}")
            offset = 0
            # print(f"[+] offset: ", end=' ')
            for tt in to_transfer:
                packed = []
                packed.append(x)
                packed.append(factor)
                packed.append(wb)
                packed.append(offset)
                packed.append(tt)
                # print(offset, end=' ')
                offset += SPLIT_SIZE
                super_big_list.append(packed)
            # print('\n')
            
        else:
            print(f"[+] donnot need split just flatten")
            packed = []
            packed.append(x)
            packed.append(factor)
            packed.append(wb)
            packed.append(0)
            packed.append(flattend)
            super_big_list.append(packed)
        print(f"[+] there are {len(super_big_list)} elements in super big list")
    
    print("=================================================================")
    print("                      Reconstitution                             ")
    print("=================================================================")
    # prepare containers
    prepare_list = locals()
    for i in range(0, size):
        shape = weights[i].shape
        prepare_list['layer_' + str(i)] = []

    for sbl in super_big_list:
        layer = sbl[0]
        factor = sbl[1]
        offset = sbl[3]
        merged_weights = sbl[4]
        pd = processed(10**factor, merged_weights)
        prepare_list['layer_' + str(layer)].extend(pd)
    # print(f"[+] prepare_list['layer_3'] = {prepare_list['layer_3']}")
    for i in range(0, size):
        print(f"[+] the {i}^th container layer_{i}'s length is {len(prepare_list['layer_' + str(i)])}")

    
    ret_l = []
    for i in range(0, size):
        before = np.array(prepare_list['layer_' + str(i)])
        # shape = weights[i].shape
        ret = before.reshape(weights[i].shape)
        # print(f"[+] after reshape: {ret}")
        print(f"[+] after reshape shape: {ret.shape}")
        ret_l.append(ret)
    merged_weights = np.array(ret_l)
    print(f"[+] a random result weight is: {merged_weights[0][0][0]}")
    model.set_weights(merged_weights)
    model.summary()

def _get_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        # tf.keras.layers.Dense(512, activation=tf.nn.relu),
        tf.keras.layers.Dense(128, activation=tf.nn.relu),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation=tf.nn.softmax)
    ])

    model.compile(optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy'])

    return model
