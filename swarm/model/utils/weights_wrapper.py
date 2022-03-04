from typing import Tuple, List
import copy
from coder_lib import encode, encode_many


class Weights:
    """A sedes object for binary data of certain length.

    :param epoch: the minimal length in bytes or `None` for no lower limit
    :param batch: 
    :param offset: if true, empty strings are considered valid even if
                        a minimum length is required otherwise
    """ 
    TASK_ID = 1
    def __init__(self,
                 epoch: int,
                 batch: int,
                #  model: str,
                 layer : int,
                 w_or_b: int,
                 factor: int,
                 offset: int,
                 task_id=TASK_ID,
                 data=[0]*1024
                 ):
        self._epoch = epoch
        self._batch = batch
        self._layer = layer
        self._w_or_b = w_or_b
        self._factor = factor
        self._task_id = task_id
        self._offset = offset
        self._data = data
        self._data_str = ""
        self._entire_str = ""

    def from_weights(self, weights: List[int]):
        assert isinstance(weights, list), "Input weights must be list"
        self._data = copy.deepcopy(weights)

    def encode(self) -> str:
        self._entire_to_string()
        assert self._entire_str != None, "Entire string is None"
        return self._entire_str
    
    def _entire_to_string(self):
        weight_str = self._data_to_string()
        self._entire_str = encode_many(["uint", str(self._task_id), "int128", str(self._epoch), "int128", str(self._batch), "uint64", str(self._layer), \
                                    "uint64", str(self._w_or_b), "uint128", str(self._factor), "uint128", str(self._offset), "int128[]",weight_str])


    def _data_to_string(self) -> str:
        ret = "["
        count = 0
        for d in self._data:
            ret += str(d)
            count += 1
            if count == len(self._data):
                ret += "]"
                self._data_str = ret
                return ret
            ret += ","
    
            