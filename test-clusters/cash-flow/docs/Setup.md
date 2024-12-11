# Setup
## Prerequisite
* **wget**

The `deploy.sh` script will download the `openapi-generator-cli.jar` and use that to generate the server and client apis.  `wget` is a used to installing the jar. 

* **Linux** distributions should come with `wget`.  If not, you should be able to get it from your package manager. 

* **Mac** users are on their own :)

* **Windows** download:
  
  `winget install wget`
    * In addition, you may want to install `Git Bash` and/or `cygwin`.

## To run the full setup

execute:
`./setup.sh`

This script will:
1. Call [deploy.sh](./cash-flow/deploy.sh) to generate the server and client APIs
2. Call [build.sh](./cash-flow/build.sh) to build and publish the docker containers to [a dockerhub repo](https://hub.docker.com/repository/docker/johndurkin/cash-flow/general)
3. Call [build.py](./cash-flow/k8s/build.py) to generate kubernetes `config` and `secret` templates
   
If this script completes successfully, the application will be ready to run. 

