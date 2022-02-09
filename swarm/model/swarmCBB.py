# Most of the code is written according to site: https://github.com/keras-team/keras/blob/v2.7.0/keras/callbacks.py#L1160-L1583
from asyncio import tasks
import tensorflow as tf
import subprocess
from utils import MODEL_DIR, TASK_ID, file_prepared, get_merge_file, send_file


class SwarmCallback(tf.keras.callbacks.Callback):
    def __init__(self,
                #  filepath,
                 merge_freq=100,
                 sync_interval=100):
        super().__init__()
        self.merge_freq = merge_freq
        # self.filepath = path_to_string(filepath)
        self.sync_interval = sync_interval
        self._current_epoch = 0
        self._batches_seen_since_last_merging = 0
        self._batches_seen_since_last_syncing = 0
        self._last_batch_seen = 0   

    def on_epoch_begin(self, epoch, logs=None):
        print("[+] Start epoch {}.".format(epoch))
        self._current_epoch = epoch

    def on_train_begin(self, logs=None):
        print("[+] Starting training.")

    def on_train_end(self, logs=None):
        print("[+] Training ended.")

    # def on_train_batch_begin(self, batch, logs=None):
        # if self._should_merge_on_batch(batch):
        #     self._merge_model(epoch=self._current_epoch, batch=batch, logs=logs)
            
    def on_train_batch_end(self, batch, logs=None):
        if self._should_sync_merge_on_batch(batch):
            self._sync_model(epoch=self._current_epoch, batch=batch, logs=logs)
            self._merge_model(epoch=self._current_epoch, batch=batch, logs=logs)

    def _merge_model(self, epoch, batch, logs=None):
        """Merge the model.
        Args:
            epoch: the epoch this iteration is in.
            batch: the batch this iteration is in. 
            logs: the `logs` dict passed in to `on_batch_end` or `on_epoch_end`.
        """
        if isinstance(self.merge_freq, int):
            # Block only when merging interval is reached.
            print("\n")
            print(f"[+] Merging at epoch: {epoch}, batch: {batch}...")
            peer_model = self._get_model()
            task_id = "uuid-001"
            weights_path = get_merge_file(task_id, epoch, batch)

            # Loads the weights
            peer_model.load_weights(weights_path)
            # current_weights to store the current weights.
            current_weights = self.model.get_weights()
            peer_weights = peer_model.get_weights()

            size = len(peer_model.get_weights())
            merge_weights = [0] * size
            for i in range(0, size):
                merge_weights[i] = (current_weights[i] + peer_weights[i]) / 2

            self.model.set_weights(merge_weights)

    def _should_sync_merge_on_batch(self, batch):
        """
        Handles batch-level syncing logic.
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
                    for i in range(0, 10):      # We send the file for 10 times if not success.
                        if send_file(TASK_ID, file):
                            break
                    break
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



