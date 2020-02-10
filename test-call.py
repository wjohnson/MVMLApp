# Sample Call:
# python3 simplecall.py --uri http://127.0.0.1:5001/score
import numpy as np
import requests
import argparse
import os, json, datetime, sys

import os, json, datetime, sys


import keras
from keras.datasets import mnist
from keras import backend as K

# Just loading some MNIST data
def load_sample_data():
    img_rows, img_cols = 28, 28
    num_classes = 10
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    if K.image_data_format() == 'channels_first':
        x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
        x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
        input_shape = (1, img_rows, img_cols)
    else:
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    print('x_train shape:', x_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')

    # convert class vectors to binary class matrices
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    return x_train, x_test, y_train, y_test

def call_using_request_only(scoring_uri, input_data, key):
    headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {key}"}

    resp = requests.post(scoring_uri, headers=headers, data=input_data)

    if resp.status_code == 200:
        print(resp.json())
        return resp.json()
    else:
        raise Exception('Received bad response from service:\n'
                                    'Response Code: {}\n'
                                    'Headers: {}\n'
                                    'Content: {}'.format(resp.status_code, resp.headers, resp.content))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri",help="The scoring URI to call")
    parser.add_argument("--key",help="The scoring URI's Key")
    args = parser.parse_args()

    x_train, x_test, y_train, y_test = load_sample_data()
    print(x_test.shape)

    data = np.array(x_test[0:10,:])
    print(data.shape)
    test_sample = json.dumps({'data': data.tolist()})
    test_sample = bytes(test_sample,encoding = 'utf8')

    print("Calling via Requests library only")
    _ = call_using_request_only(args.uri, test_sample, args.key)