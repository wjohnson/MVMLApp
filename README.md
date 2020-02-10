# MVMLApp
A Minimum Viable Machine Learning Application through Azure ML

## Contents and Parameters

    train.py: 
        A sample deep learning model that uses MNIST.
    upload-model.py MODEL_NAME MODEL_PATH: 
        Upload a given file or folder and register it as a model in Azure ML.
    score/score.py: 
        The way to initialize and run your model in a container.
    score/dependencies.yml: 
        The dependencies for the given score.py.
    create-image.py CONTAINER_NAME MODEL_NAME MODEL_VERSION: 
        Creates a container based off of the score/score.py and registered model you pass in as args.
    release-service.py AKS_SERVICE_NAME WEB_SERVICE_NAME CONTAINER_NAME CONTAINER_VERSION:
        Creates a web service on the give AKS compute target for the given container version.
    loadws.py: 
        A utility module to centralize loading the workspace
    test-call.py --uri AKS_URI --key AKS_KEY
        A utility module to test calling the AKS web service.



## Instructions

* Create an Azure Machine Learning Workspace in the Azure Portal
* Look up the following and save the contents in a .env file in the root of your directory:

      workspace_name=YOUR_WORKSPACE_NAME
      experiment_name=YOUR_PROJECT_NAME
      subscription_id=YOUR_SUBSCRIPTION_ID
      resource_group=YOUR_RESOURCEGROUP_NAME
      location=YOUR_LOCATION

* Train a Machine Learning Model locally:
  * Serialize the model object and store it and supporting objects in one folder.
* Upload the model to the Azure ML Service by running `python upload-model.py MODEL_NAME MODEL_PATH`
  * Where MODEL_PATH is the path to either the single serialized object or a folder of files needed to run the model.
  * NOTE: This command is not idempotent.  Re-running this step will result in creating a new version of the registered model.
* Create a container image by running `python create-image.py CONTAINER_NAME MODEL_NAME MODEL_VERSION`
  * Before running the command, you may want to change...
  * `./score/score.py` to reflect the steps necessary to initialize and run your model.  Make sure **your model loading is referencing the correct model name**.
  * `./create-image.py` Conda Dependencies.
  * NOTE: This command is not idempotent.  Re-running this step will result in creating a new version of the container image.
* Deploy to the Azure Kubernetes Service by running `python release-service.py AKS_SERVICE_NAME WEB_SERVICE_NAME CONTAINER_NAME CONTAINER_VERSION`
  * If the AKS_SERVICE_NAME does not match an existing inference compute target, a default AKS cluster will be created.
  * If there is an existing web service with the name of WEB_SERVICE_NAME, the deployment will fail.
  * Creates `service_details.json` with URI and key for newly deployed web service