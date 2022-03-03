#!/usr/local/bin/python
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

    checkpoint_path = "../../checkpoints/weights.01-100.h5"

    model = get_model()
    # Loads the weights
    model.load_weights(checkpoint_path)

    # # Evaluate the model
    # loss, acc = model.evaluate(x_test, y_test, verbose=2)
    # print("Untrained model, accuracy: {:5.2f}%".format(100 * acc))
    model.summary()
    # print("=================================================================")
    # print("                          Flatten                                ")
    # print("=================================================================")
    # print(model.get_weights()[0])
    # print(f"[+] 第一层的 w's len = {len(model.get_weights()[0])}")
    # print("=================================================================")
    # print("                           Dense                                 ")
    # print("=================================================================")
    # print(model.get_weights()[1])
    # print(f"[+] 第一层的 b's len = {len(model.get_weights()[1])}")
    # print("=================================================================")
    # print("                          Dropout                                ")
    # print("=================================================================")
    # print(model.get_weights()[2])
    # print(f"[+] 第二层的 w's len = {len(model.get_weights()[2])}")
    # print("=================================================================")
    # print("                           Dense                                 ")
    # print("=================================================================")
    # print(model.get_weights()[3])
    # print(f"[+] 第二层的 b's len = {len(model.get_weights()[3])}")

    weights = model.get_weights() #获取整个网络模型的全部参数
    # print(f"[+] len  = {len(weights)}")
    # print(weights [0].shape)  #第一层的w
    # print(weights [1].shape)  #第一层的b
    # print(weights [2].shape)  #第二层的w
    # print(weights [3].shape)  #第二层的b

    # layer1 = model.get_layer(index=1)
    # weights = layer1.get_weights()   #获取该层的参数W和b
    # print(weights)

    # process layer x
    # 
    layerx = model.get_weights()[2]
    print(layerx[0])
    size_outside = layerx.shape[0]
    size_inside = layerx.shape[1]
    print(f"[+] shape: ({size_outside}, {size_inside})")
    # get max len post decimal
    max_len = 0
    r_len = 0
    for i in range(0, size_outside):
        for j in range(0, size_inside):
            r_len = number_of_digits_post_decimal(layerx[i][j])
            if r_len > max_len:
                max_len = r_len

    for i in range(0, size_outside):
        for j in range(0, size_inside):
            layerx[i][j] = layerx[i][j] * (10 ** r_len)
            if layerx[i][j] > 0:
                layerx[i][j] = int(layerx[i][j] + 0.5 )
            elif layerx[i][j] < 0:
                layerx[i][j] = int(layerx[i][j] - 0.5 )
                
    layer0 = layerx[0].tolist()
    layer0 = [int(l) for l in layer0]
    # print(type(layer0[0]))
    print(layer0)
    ret = "["
    count = 0
    for l in layer0:
        ret += str(l)
        if count == len(layer0) - 1:
            break
        ret += ","
        count += 1
    ret += "]"
    print(ret)

def number_of_digits_post_decimal(x):
    return len(str(x).split(".")[1])


if __name__ == '__main__':
    main()