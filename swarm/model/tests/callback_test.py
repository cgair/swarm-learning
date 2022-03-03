#!/usr/bin/env python3
import pytest
import numpy as np
# from swarmCBB import SwarmCallback
from utils import number_of_digits_post_decimal, caclulate_factor, contruct_result_string, faltten

def test_number_of_digits_post_decimal():
    assert number_of_digits_post_decimal(-0.1234567) == 7
    assert number_of_digits_post_decimal(2.123456789) == 9


def test_caclulate_factor():
    weight = np.array([-0.00725056, 0.0168993, 0.00075373, -0.00990144, 0.00284106, 0.01322524, -0.00417293, 0.00808944, -0.02160874, 0.00079403])
    assert caclulate_factor(weight, (10,)) == 8


def test_contruct_result_string():
    weight = np.array([ 0.09356794, 0.02917077, 0.06075062, 0.00063394])
    assert contruct_result_string(weight, 8) == "9356794,2917077,6075062,63394"
