"""
Copyright (C) Microsoft Corporation. All rights reserved.​
 ​
Microsoft Corporation (“Microsoft”) grants you a nonexclusive, perpetual,
royalty-free right to use, copy, and modify the software code provided by us
("Software Code"). You may not sublicense the Software Code or any use of it
(except to your affiliates and to vendors to perform work on your behalf)
through distribution, network access, service agreement, lease, rental, or
otherwise. This license does not purport to express any claim of ownership over
data you may have shared with Microsoft in the creation of the Software Code.
Unless applicable law gives you more rights, Microsoft reserves all other
rights not expressly granted herein, whether by implication, estoppel or
otherwise. ​
 ​
THE SOFTWARE CODE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
MICROSOFT OR ITS LICENSORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THE SOFTWARE CODE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
from azureml.core import Workspace
import os, json, sys
import azureml.core
from azureml.core.authentication import AzureCliAuthentication
from azureml.core import Workspace
import azureml.core

print("SDK Version:", azureml.core.VERSION)
# print('current dir is ' +os.curdir)
with open("tests/AzureDevOpsConfig/config.json") as f:
    config = json.load(f)
'''
workspace_name = config["workspace_name"]
resource_group = config["resource_group"]
subscription_id = config["subscription_id"]
location = config["location"]
'''

workspace_name = "RecoWS"
resource_group = "recommender"
subscription_id = "15ae9cb6-95c1-483d-a0e3-b1a1a3b06324"

cli_auth = AzureCliAuthentication()

try:
    print("Trying to get ws")
    ws = Workspace.get(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        auth=cli_auth,
    )

except:
    # this call might take a minute or two.
    print("Creating new workspace")
    ws = Workspace.create(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        # create_resource_group=True,
        location=location,
        auth=cli_auth,
    )

# print Workspace details
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep="\n")


from azureml.core import Experiment
experiment_name = 'train-on-amlcompute'
experiment = Experiment(workspace = ws, name = 'Reco Experiment')


from azureml.core.compute import ComputeTarget, AmlCompute

AmlCompute.supported_vmsizes(workspace = ws)
#AmlCompute.supported_vmsizes(workspace = ws, location='southcentralus')

from azureml.core.runconfig import RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import DEFAULT_CPU_IMAGE

# create a new runconfig object
run_config = RunConfiguration()

# signal that you want to use AmlCompute to execute script.
run_config.target = "amlcompute"

# AmlCompute will be created in the same region as workspace
# Set vm size for AmlCompute
run_config.amlcompute.vm_size = 'STANDARD_NC6'

# enable Docker 
run_config.environment.docker.enabled = True

# set Docker base image to the default CPU-based image
run_config.environment.docker.base_image = DEFAULT_CPU_IMAGE

# use conda_dependencies.yml to create a conda environment in the Docker image for execution
run_config.environment.python.user_managed_dependencies = False

# auto-prepare the Docker image when used for execution (if it is not already prepared)
run_config.auto_prepare_environment = True

# specify CondaDependencies obj
run_config.environment.python.conda_dependencies = CondaDependencies.create(conda_packages=['scikit-learn'])

# Now submit a run on AmlCompute
from azureml.core.script_run_config import ScriptRunConfig

script_run_config = ScriptRunConfig(source_directory=project_folder,
                                    script='train.py',
                                    run_config=run_config)

run = experiment.submit(script_run_config)

# Show run details
run