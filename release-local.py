import os, json, datetime, sys

from azureml.core import Workspace, Environment
from azureml.core.model import Model, InferenceConfig
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.webservice import Webservice
from azureml.core.webservice import AksWebservice
from azureml.core.compute import AksCompute, ComputeTarget
from azureml.exceptions import WebserviceException
from loadws import load_workspace
from dotenv import load_dotenv

import importlib  
import numpy as np

if __name__ == "__main__":
    tester = importlib.import_module("test-call")
    data = tester.load_sample_data()

    ws = load_workspace()

    load_dotenv()

    web_service_name = "localservice"
    model_name = sys.argv[1]
    model_version = int(sys.argv[2])
    
    # Grab the requested model
    model_list = Model.list(workspace=ws)
    model = None
    
    # Unpack the generator and look through the list to find your desired model
    model, = (m for m in model_list if m.version==model_version and m.name==model_name)
    print('Model picked: {} \nModel Description: {} \nModel Version: {}'.format(model.name, model.description, model.version))

    from azureml.core.webservice import LocalWebservice, Webservice

    


    os.chdir('./score')
    print("Creating environment")
    local_env = Environment(name=f'{web_service_name}_env')
    local_env.environment_variables = {"STORAGE_CONNECTION": os.getenv("STORAGE_CONNECTION")}
    print(local_env.environment_variables)
    local_env.python.conda_dependencies = CondaDependencies.create(
        pip_packages=[
        'azureml-defaults',
        'azure-storage-blob',
        'pynacl==1.2.1'
        ],
        conda_packages=[
        'numpy',
        'scikit-learn',
        'tensorflow',
        'keras'
        ])
    
    inf_config = InferenceConfig(
        entry_script="score.py",
        environment=local_env,
        #conda_file="dependencies.yml",
        #runtime="python"
    )

    deployment_config = LocalWebservice.deploy_configuration()
    service = Model.deploy(ws, "myservice", [model], inf_config, deployment_config)
    service.wait_for_deployment(show_output = True)
    print(service.state)

    print("Attempting to deploy model to web service")
    # Deploy this particular web service to your Local Web Service
    service = Model.deploy(
        workspace=ws,
        name=web_service_name, 
        models=[model], 
        inference_config=inf_config, 
        deployment_config=deployment_config
    )

    print("Waiting for deployment to complete:")
    try:
        service.wait_for_deployment(show_output=True)
        print('Deployed Local Webservice: {} \nWebservice Uri: {}'.format(service.name, service.scoring_uri))
    except:
        print(service.get_logs())

    print(f"Scoring URI: {service.scoring_uri}")

    

    data = np.array(data)
    print(data.shape)
    test_sample = json.dumps({'data': data.tolist()})
    test_sample = bytes(test_sample,encoding = 'utf8')

    print("Calling via Requests library only")
    try:
        results = tester.call_using_request_only(service.scoring_uri, test_sample, None)
        print(results)
    except Exception as e:
        print(e)
        print(service.get_logs())
