import logging
import json
import os
import uuid
try:
    from azure.storage.blob import BlobServiceClient, BlobClient
    import keras
    from keras.models import load_model
    import numpy as np
except ModuleNotFoundError as e:
    import sys
    print(sys.modules)
    raise e

from azureml.core.model import Model


import keras
from keras.datasets import mnist
from keras import backend as K

def init():
    global model
    # retreive the path to the model file using the model name
    # get_model_path should be updated to referene the correct registered model name
    model_path = Model.get_model_path('uploadedmodel')
    model=load_model(model_path)

def run(raw_data):
    print("Running")
    data = np.array(json.loads(raw_data)['data'])
    print(data.shape)
    # make prediction
    y_hat = model.predict(data).tolist()
    #y_hat = np.argmax(y_hat, axis=1)
    connect_str = os.getenv('STORAGE_CONNECTION')
    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    blob_name = f"{uuid.uuid4()}.json"

    # Create a unique name for the container
    blob_client = blob_service_client.get_blob_client(container="modeloutput", blob=blob_name)

    results = blob_client.upload_blob(json.dumps(y_hat))

    return json.dumps({"blob_name":blob_name})

# For debugging purposes
# if __name__ == "__main__":
#     init()
#     results = run(None)
#     print(results)
