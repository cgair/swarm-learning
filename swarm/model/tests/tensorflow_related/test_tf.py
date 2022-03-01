import tensorflow as tf
import os
import numpy as np

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

def get_model():
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

def main():
    dataDir = os.getenv('DATA_DIR', '../../../data')

    (x_train, y_train),(x_test, y_test) = load_data(dataDir)
    x_train, x_test = x_train / 255.0, x_test / 255.0

    # checkpoint_path = "/ufs/SMLNODE/fs/uuid-001/weights.01-100.h5"
    checkpoint_path = "../../checkpoints/weights.01-100.h5"
    checkpoint_path2 = "../../checkpoints/weights.01-200.h5"

    model = get_model()
    # Loads the weights
    model.load_weights(checkpoint_path)

    # model2 = get_model()
    # model2.load_weights(checkpoint_path2)

    # # Evaluate the model
    # loss, acc = model.evaluate(x_test, y_test, verbose=2)
    # print("Untrained model, accuracy: {:5.2f}%".format(100 * acc))
    model.summary()
    print("===================Flatten============================")
    print(model.get_weights()[0])
    print(f"len = {len(model.get_weights()[0])}")
    print("====================Dense===========================")
    print(model.get_weights()[1])
    print(f"len = {len(model.get_weights()[1])}")
    print("===================Dropout============================")
    print(model.get_weights()[2])
    print(f"len = {len(model.get_weights()[2])}")
    print("====================Dense===========================")
    print(model.get_weights()[3])
    print(f"len = {len(model.get_weights()[3])}")

    weights = model.get_weights() #获取整个网络模型的全部参数
    # weights2 = model2.get_weights() #获取整个网络模型的全部参数

    # print(f"len  = {len(weights)}")
    # print(weights [0].shape)  #第一层的w
    # print(weights [1].shape)  #第一层的b
    # print(weights [2].shape)  #第二层的w
    # print(weights [3].shape)  #第二层的b

    # layer1 = model.get_layer(index=1)
    # weights = layer1.get_weights()   #获取该层的参数W和b
    # print(weights)
    # print("===============================================================")
    # size = len(weights)
    # end_data= [0]*size
    # for i in range(0, size):
    #     end_data[i] = (weights[i]+weights2[i])/2

    # print(end_data)

    # model.set_weights(end_data)
    # model.summary()



if __name__ == '__main__':
    main()
    # some tests
    # s = b'[2022-02-09T02:32:43Z INFO  ufs] Status: 200 OK\n'
    # ss = str(s, 'UTF-8')
    # print(ss)
    # if "OK" in ss:
    #     print("yes")