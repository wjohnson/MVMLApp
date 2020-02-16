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


if __name__ == "__main__":
    load_dotenv()

    ws = load_workspace()

    aks_service_name = sys.argv[1]
    web_service_name = sys.argv[2]
    model_name = sys.argv[3]
    model_version = int(sys.argv[4])
    
    # Grab the requested model
    model_list = Model.list(workspace=ws)
    model = None
    
    # Unpack the generator and look through the list to find your desired model
    model, = (m for m in model_list if m.version==model_version and m.name==model_name)
    print('Model picked: {} \nModel Description: {} \nModel Version: {}'.format(model.name, model.description, model.version))

    # Set up Compute Target
    try:
        computeTargets = ComputeTarget.list(ws)
        aks_target, = (t for t in computeTargets if t.name == aks_service_name)
        if aks_target is None:
            raise Exception("Compute Target {} not found.  Attempting to create".format(aks_service_name))
    except:
        prov_config = AksCompute.provisioning_configuration(location='eastus')

        # Create the cluster
        aks_target = ComputeTarget.create(
            workspace = ws, 
            name = aks_service_name, 
            provisioning_configuration = prov_config
        )
        print("Provisioning an AKS Cluster")
        aks_target.wait_for_completion()

    # Configure this particular web service's resources on your AKS Cluster
    aks_config = AksWebservice.deploy_configuration(
        autoscale_enabled=False,
        auth_enabled=True,
        cpu_cores=0.5, 
        memory_gb=1, 
        description='Web service to deploy an uploaded model',
        enable_app_insights=True,
        num_replicas=2,
        gpu_cores=None,
        compute_target_name=aks_service_name
    )

    os.chdir('./score')
    print("Creating environment")
    aks_env = Environment(name=f'{web_service_name}_env')
    aks_env.environment_variables = {"STORAGE_CONNECTION": os.getenv("STORAGE_CONNECTION")}
    aks_env.python.conda_dependencies = CondaDependencies.create(
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
        environment=aks_env
    )

    print("Attempting to deploy model to web service")
    # Deploy this particular web service to your AKS cluster.
    service = Model.deploy(
        workspace=ws,
        name=web_service_name, 
        models=[model], 
        inference_config=inf_config, 
        deployment_config=aks_config, 
        deployment_target=aks_target,
        overwrite=True
    )

    print("Waiting for deployment to complete:")
    try:
        service.wait_for_deployment()
        print('Deployed AKS Webservice: {} \nWebservice Uri: {}'.format(service.name, service.scoring_uri))
    except:
        print(service.get_logs())

    try:
        service_key = service.get_keys()[0]
    except WebserviceException as e:
        raise WebserviceException(
            'Error attempting to retrieve service keys for use with scoring:\n{}'.format(e.message)
        )


    web_service_details = {}
    web_service_details['service_name'] = service.name
    web_service_details['service_url'] = service.scoring_uri
    web_service_details["key"] = service_key
    with open('./service_details.json', 'w') as outfile:
        json.dump(
            obj = web_service_details,
            fp = outfile
        )