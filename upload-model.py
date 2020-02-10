import os, json,sys

from azureml.core import Workspace
from azureml.core.model import Model
from dotenv import load_dotenv
from loadws import load_workspace

if __name__ == "__main__":
    model_name = sys.argv[1]
    model_path = sys.argv[2] 

    load_dotenv()

    ws = load_workspace()
    
    model = Model.register(model_path = model_path, # this points to a local file or folder
                        model_name = model_name, # this is the name the model is registered as
                        description="An uploaded model",
                        workspace = ws)

    print('Model registered: {} \nModel Description: {} \nModel Version: {}'.format(model.name, model.description, model.version))
