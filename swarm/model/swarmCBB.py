# Most of the code is written according to site: https://github.com/keras-team/keras/blob/v2.7.0/keras/callbacks.py#L1160-L1583
import tensorflow as tf
import numpy as np

from utils.utils import MODEL_DIR, TASKID, \
                        file_prepared, send_file, get_merge_file

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
        self._client = "JsonRpcClient(192.168.1.21, 12537)"

    def on_epoch_begin(self, epoch, logs=None):
        print("[+] Start epoch {}.".format(epoch))
        self._current_epoch = epoch

    def on_train_begin(self, logs=None):
        print("[+] Starting training.")

    def on_train_end(self, logs=None):
        print("[+] Training ended.")
            
    def on_train_batch_end(self, batch, logs=None):
        if self._should_sync_merge_on_batch(batch):
            self._sync_model(epoch=self._current_epoch, batch=batch, logs=logs)
            self._merge_model(epoch=self._current_epoch, batch=batch, logs=logs)

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
                    if send_file(TASKID, file):
                        return
                else: 
                    print(f"[-] File does not prepared, retry {i}")

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

    def _merge_model(self, epoch, batch, logs=None):
        """Merge the model.
        Args:
            epoch: the epoch this iteration is in.
            batch: the batch this iteration is in. 
            logs: the `logs` dict passed in to `on_batch_end` or `on_epoch_end`.
        """
        if isinstance(self.merge_freq, int):
            # Block only when merging interval is reached.
            # prepare containers
            curr_model = self._get_model()
            peer_model = self._get_model()
            peer_model_path = get_merge_file(TASKID, epoch, batch)
            peer_model.load_weights(peer_model_path)

            peer_weights = peer_model.get_weights()
            curr_weights = curr_model.get_weights()
            size = len(curr_weights)
            assert len(peer_weights) == size, "Invalid Model"
            merged_weights = (np.array(peer_weights) + np.array(curr_weights)) / 2.0

            merged_weights = np.array(merged_weights)
            self.model.set_weights(merged_weights)