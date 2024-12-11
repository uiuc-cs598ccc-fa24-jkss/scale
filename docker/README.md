# Docker Compose

**Notes**
    - This assumes you are executing the commands from this directory
    - The network name and project name are arbitrary.  The monitoring containers just need to start on the same network as the test cluster.
    - Alternatively, you can if you know the network name of the test-cluster, you can just parameterize the monitoring statck with that network name

1. Start the test cluster

    ```bash
    # start the cash-flow docker-compose on 'testnet' network and project name 'test' 
    NETWORK_NAME=testnet docker-compose -p test-cluster -f ../test-clusters/cash-flow/backend/docker-compose.yaml up --build
    ```

2. Start the monitoring containers on the same network

    ```bash
    NETWORK_NAME=testnet docker-compose up --build
    ```
