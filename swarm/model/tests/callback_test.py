#!/usr/bin/env python3
import numpy as np
# from swarmCBB import SwarmCallback
from typing import List
from utils import number_of_digits_post_decimal, caclulate_factor, split_list_by_n

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