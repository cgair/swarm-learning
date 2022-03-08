# Most of the code is written according to site: https://github.com/keras-team/keras/blob/v2.7.0/keras/callbacks.py#L1160-L1583
import tensorflow as tf
import numpy as np
import sys
from hexbytes import HexBytes

from utils.utils import MODEL_DIR, SPLIT_SIZE, \
                        file_prepared, caclulate_factor, send_msg, split_list_by_n, should_split, expand_with_factor, processed, init_task, get_status
from tree_graph.client.jsonrpc_client import *

class SwarmCallback(tf.keras.callbacks.Callback):
    def __init__(self,
                 taskid: int,
                 req_peer: int,    
                 merge_freq=100,
                 sync_interval=100):
        super().__init__()
        self.merge_freq = merge_freq
        self.sync_interval = sync_interval
        self.taskid = taskid
        self.req_peer = req_peer
        self._current_epoch = 0
        self._batches_seen_since_last_merging = 0
        self._batches_seen_since_last_syncing = 0
        self._last_batch_seen = 0
        self._client = JsonRpcClient("192.168.1.21", "12537")

    def on_epoch_begin(self, epoch, logs=None):
        print("[+] Start epoch {}.".format(epoch))
        self._current_epoch = epoch

    def on_train_begin(self, logs=None):
        print("[+] Init task...")
        epoch_num = self._init_task(self._client, self.taskid, self.req_peer)
        print("[+] Starting training.")
        # sys.exit(f"[+] End on train begin") 

    def on_train_end(self, logs=None):
        print("[+] Training ended.")
            
    def on_train_batch_end(self, batch, logs=None):
        if self._should_sync_merge_on_batch(batch):
            self._sync_model(epoch=self._current_epoch, batch=batch, logs=logs)
            self._merge_model(epoch=self._current_epoch, batch=batch, logs=logs)

    def _init_task(self, client, taskid: int, req_peer: int):
        return init_task(client, taskid, req_peer)

    def _merge_model(self, epoch, batch, logs=None):
        """Merge the model.
        Args:
            epoch: the epoch this iteration is in.
            batch: the batch this iteration is in. 
            logs: the `logs` dict passed in to `on_batch_end` or `on_epoch_end`.
        """
        if isinstance(self.merge_freq, int):
            # Block only when merging interval is reached.
            print(f"[+] Reconstitution at epoch: {epoch}, batch: {batch}...")
            # prepare containers
            prepare_list = locals()
            weights = self.model.get_weights() 
            size = len(weights)
            for i in range(0, size):
                shape = weights[i].shape
                prepare_list['layer_' + str(i)] = [0.0] * shape[0]

            merged_weights = []
            layer = 0
            offset = 0
            factor = 10

            start = int(offset)
            end = int(start + SPLIT_SIZE)
            prepare_list['layer_' + str(layer)][start: end] = processed(factor, merged_weights)

            ret_l = []
            for i in range(0, size):
                before = np.array(prepare_list['layer_' + str(i)])
                ret = before.rehsape(before, weights[i].shape)
                ret_l.append(ret)
            
            merged_weights = np.array(ret_l)
            self.model.set_weights(merged_weights)

    def _should_sync_merge_on_batch(self, batch):
        """Handles batch-level syncing logic.
        """
        if batch <= self._last_batch_seen:  # New epoch.
            add_batches = batch + 1  # batches are zero-indexed.
        else:
            add_batches = batch - self._last_batch_seen
        self._batches_seen_since_last_syncing += add_batches
        self._last_batch_seen = batch

        if self._batches_seen_since_last_syncing >= self.sync_interval:
            self._batches_seen_since_last_syncing = 0
            return True
        return False

    def _sync_model(self, epoch, batch, logs=None):
        """Sync the model.
        Args:
            epoch: the epoch this iteration is in.
            batch: the batch this iteration is in. 
            logs: the `logs` dict passed in to `on_batch_end` or `on_epoch_end`.
        """
        if isinstance(self.sync_interval, int):
            # Block only when sync interval is reached.
            for i in range(0, 10):      # We check if the file is prepared for 10 times.
                e = epoch + 1
                b = batch + 1
                flag, path = file_prepared(e, b)
                if flag:
                    print(f"[+] Syncing at epoch: {e}, batch: {b}...")
                    model_name = 'weights.{:0>2}-{:0>2}.h5'.format(e, b)
                    file = f"{MODEL_DIR}{model_name}"
                    print(f"[+] Merging ...")
                    self._process_weights(e, b, file)
                else: 
                    print(f"[-] File does not prepared, retry {i}")

    def _process_weights(self, epoch, batch, file):
        model = self._get_model()
        # Loads the weights
        model.load_weights(file)
        weights = model.get_weights() # 获取整个网络模型的全部参数
        # model.summary() 

        size = len(weights)
        for x in range(0, size):
            shape = weights [x].shape
            flattend = list(weights [x].flatten())
            # Calculate the factor that should be expanded, cause solidity only has int256 and uint256
            factor = caclulate_factor(flattend)
            flattend = expand_with_factor(flattend, factor)
            # type = 0 means `w` while 1 means `b`
            wb = 0 if x % 2 == 0 else 1

            if should_split(shape):
                to_transfer = list(split_list_by_n(flattend, SPLIT_SIZE))
                for i in range(0, len(to_transfer)):
                    send_msg(self._client,
                             epoch, 
                             batch, 
                             x, 
                             wb, 
                             factor,
                             i * SPLIT_SIZE,
                             to_transfer[i]
                            )
                
            else:
                send_msg(self._client,
                         epoch,
                         batch,
                         x,
                         wb,
                         factor,
                         0,
                         flattend
                        )

    
    def _get_model(self):
        model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(512, activation=tf.nn.relu),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10, activation=tf.nn.softmax)
        ])

        model.compile(optimizer='adam',
                        loss='sparse_categorical_crossentropy',
                        metrics=['accuracy'])

        return model