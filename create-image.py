import os, json, sys

from azureml.core.conda_dependencies import CondaDependencies 
from azureml.core.image import ContainerImage
from azureml.core.model import Model
from azureml.core import Workspace

from loadws import load_workspace


if __name__ == "__main__":
    container_image_name = sys.argv[1]
    model_name = sys.argv[2]
    model_version = int(sys.argv[3])

    ws = load_workspace()

    # Grab the model object from the list of available models
    model_list = Model.list(workspace=ws)
    model = None
    
    # Unpack the generator and look through the list to find your desired model
    model, = (m for m in model_list if m.version==model_version and m.name==model_name)
    print('Model picked: {} \nModel Description: {} \nModel Version: {}'.format(model.name, model.description, model.version))


    dependencies = CondaDependencies()
    dependencies.add_conda_package("numpy")
    dependencies.add_conda_package("matplotlib")
    dependencies.add_conda_package("scikit-learn")
    dependencies.add_conda_package("tensorflow")
    dependencies.add_conda_package("keras")
    dependencies.add_conda_package("scikit-image")
    dependencies.add_pip_package("pynacl==1.2.1")

    os.makedirs("./score/", exist_ok=True)
    with open("./score/dependencies.yml","w") as f:
        f.write(dependencies.serialize_to_string())

    original_dir = os.getcwd()
    # Change directory since the docker container is expecting thing at the TLD
    os.chdir("./score")
    image_config = ContainerImage.image_configuration(
        execution_script = "score.py",
        runtime = "python",
        conda_file = "dependencies.yml",
        description = "Image with Uploaded Model"
    )

    # Image Name can only include alphanumeric or '.' and '-'
    image = ContainerImage.create(
        name = container_image_name,
        models = [model], # this is the registered model object
        image_config = image_config,
        workspace = ws
    )

    image.wait_for_creation(show_output = True)
    print('Image Created: {} \nImage Version: {}'.format(image.name, image.version))
