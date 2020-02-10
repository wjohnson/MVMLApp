import os
from azureml.core import Workspace
from dotenv import load_dotenv

def load_workspace():
    load_dotenv()
    
    try:
        ws = Workspace.get(
            subscription_id=os.getenv("subscription_id"),
            resource_group=os.getenv("resource_group"),
            name=os.getenv("workspace_name")
        )
    except:
        ws = Workspace.create(
            subscription_id=os.getenv("subscription_id"),
            resource_group=os.getenv("resource_group"),
            name=os.getenv("workspace_name"),
            location=os.getenv("location")
        )
    
    return ws