# Execution Procedures

## Start SCALE with hot-reload configuration

1. Start minikube and mount the location of the tests/configs directory

    ```bash
    minikube start --mount --mount-string="/<path-to-project>/cs598-project/tests/configs:/mnt/config"
    ```

2. Place configs in appropriate subdirectory if necessary (i.e. copy files into, or edit current files in the `/tests/configs/<cluster>` subdirectory)

3. start or restart the scale tools

    ```bash
    helm install scale ./scale-full -n monitoring --create-namespace --set sampler.trainSize=150 --set modeler.targetNamespace=demo 
    ```
