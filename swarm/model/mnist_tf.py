import tensorflow as tf
import numpy as np
from swarmCBB import SwarmCallback
import os

max_epochs = 2

def load_data(dataDir):
    """Loads the MNIST dataset.
    # Arguments
        dataDir: path where to find the mnist.npz file
    # Returns
        Tuple of Numpy arrays: `(x_train, y_train), (x_test, y_test)`.
    """
    path = os.path.join(dataDir,'mnist.npz') 

    with np.load(path, allow_pickle=True) as f:
        x_train, y_train = f['x_train'], f['y_train']
        x_test, y_test = f['x_test'], f['y_test']
    return (x_train, y_train), (x_test, y_test)


def main():
    dataDir = os.getenv('DATA_DIR', '../data')
    modelDir = os.getenv('MODEL_DIR', '../model')
    model_name = 'mnist_tf'

    (x_train, y_train),(x_test, y_test) = load_data(dataDir)
    x_train, x_test = x_train / 255.0, x_test / 255.0

    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(512, activation=tf.nn.relu),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation=tf.nn.softmax)
    ])

    model.compile(optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy'])

    save_model_callback = tf.keras.callbacks.ModelCheckpoint(
        # filepath='./checkpoints/sl1/weights.{epoch:02d}-{batch:02d}.h5', 
        # filepath='./checkpoints/sl2/weights.{epoch:02d}-{batch:02d}.h5', 
        filepath='./checkpoints/weights.{epoch:02d}-{batch:02d}.h5', 
        save_weights_only=True, 
        verbose=1,
        monitor='val_loss', 
        mode='min', 
        save_best_only=False,
        save_freq=100)     # when using integer, the callback saves the model at end of this many batches. 

    # Create Swarm callback
    swarmCallback = SwarmCallback(taskid=1, req_peer=2, sync_interval=100)

    model.fit(x_train, y_train, 
                batch_size = 100,
                epochs=max_epochs,
                verbose=1, 
                validation_data=(x_test, y_test),           
                callbacks=[save_model_callback, swarmCallback])

    # Save model and weights
    # model_path = os.path.join(modelDir, model_name)
    # model.save(model_path)
    # print('Saved the trained model!')

if __name__ == '__main__':
  main()