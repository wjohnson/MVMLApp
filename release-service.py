import os, json, datetime, sys

from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.image import Image
from azureml.core.webservice import Webservice
from azureml.core.webservice import AksWebservice
from azureml.core.compute import AksCompute, ComputeTarget
from azureml.exceptions import WebserviceException
from loadws import load_workspace
from dotenv import load_dotenv


if __name__ == "__main__":
    ws = load_workspace()

    aks_service_name = sys.argv[1]
    web_service_name = sys.argv[2]
    image_name = sys.argv[3]
    image_version = int(sys.argv[4])
    

    images = Image.list(workspace=ws)
    image, = (m for m in images if m.version==image_version and m.name == image_name)
    print('Image used to deploy webservice on ACI: {}\nImage Version: {}\nImage Location = {}'.format(image.name, image.version, image.image_location))

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
        cpu_cores=1, 
        memory_gb=2, 
        description='Web service to deploy an uploaded model',
        enable_app_insights=True,
        num_replicas=2,
        gpu_cores=None,
        compute_target_name="aks_ml_deployment"
    )

    # Deploy this particular web service to your AKS cluster.
    service = Webservice.deploy_from_image(
        deployment_config=aks_config,
        deployment_target=aks_target,
        image=image,
        name=web_service_name,
        workspace=ws
    )

    print("Attempting to deploy service:")
    service.wait_for_deployment()
    print('Deployed AKS Webservice: {} \nWebservice Uri: {}'.format(service.name, service.scoring_uri))

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