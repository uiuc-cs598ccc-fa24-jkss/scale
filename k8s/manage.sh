#!/bin/bash

# check if a namespace exists 
check_namespace_exists() {
    local NAMESPACE=$1
    if [ ! -z "$NAMESPACE" ]; then
        if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
            echo "Error: Namespace $NAMESPACE doesn't exist. Exiting."
            exit 1
        else
            echo "Using existing namespace: $NAMESPACE"
        fi
    fi
}

# start deployments
start_deployments() {
    local NAMESPACE_ARG=$1

    echo "Starting deployments..."


    kubectl apply -f tlm/tlm-service.yaml $NAMESPACE_ARG

    # Apply ConfigMaps
    kubectl apply -f otel-collector/otel-collector-config.yaml $NAMESPACE_ARG
    kubectl apply -f tempo/tempo-config.yaml $NAMESPACE_ARG
    kubectl apply -f grafana/grafana-config.yaml $NAMESPACE_ARG

    # Apply Deployments and Services
    kubectl apply -f tempo/tempo.yaml $NAMESPACE_ARG
    kubectl apply -f grafana/grafana.yaml $NAMESPACE_ARG
    kubectl apply -f otel-collector/otel-collector.yaml $NAMESPACE_ARG
    kubectl apply -f sampler/sampler.yaml $NAMESPACE_ARG

    # Check the status of the pods
    echo "Waiting for pods to be ready..."
    kubectl wait --for=condition=Ready pods --all --timeout=300s -n $NAMESPACE
}

# stop deployments
stop_deployments() {
    local NAMESPACE_ARG=$1

    echo "Stopping deployments..."

    # Delete Deployments and Services
    kubectl delete -f grafana/grafana.yaml $NAMESPACE_ARG
    kubectl delete -f tempo/tempo.yaml $NAMESPACE_ARG
    kubectl delete -f otel-collector/otel-collector.yaml $NAMESPACE_ARG
    kubectl delete -f sampler/sampler.yaml $NAMESPACE_ARG

    # Delete ConfigMaps
    kubectl delete -f otel-collector/otel-collector-config.yaml $NAMESPACE_ARG
    kubectl delete -f grafana/grafana-config.yaml $NAMESPACE_ARG
    kubectl delete -f tempo/tempo-config.yaml $NAMESPACE_ARG

    kubectl delete -f tlm/tlm-service.yaml $NAMESPACE_ARG

    # Check if any resources are still running
    echo "Checking remaining resources..."
    kubectl get all $NAMESPACE_ARG
}

# Main logic to parse the action (start/stop) and the optional -n argument for namespace
ACTION=$1
shift 1  # Shift the positional parameters so we can parse the -n argument

# Parse the -n argument if present
NAMESPACE=""
NAMESPACE_ARG=""
while getopts ":n:" opt; do
  case ${opt} in
    n )
      NAMESPACE=$OPTARG
      NAMESPACE_ARG="-n $NAMESPACE"
      ;;
    \? )
      echo "Invalid option: $OPTARG" 1>&2
      exit 1
      ;;
  esac
done

# Create the namespace if provided
check_namespace_exists "$NAMESPACE"

# Check if a valid action (start/stop) was provided
if [ -z "$ACTION" ]; then
    echo "No action provided. Use 'start' or 'stop'."
    exit 1
fi

# Execute the correct function based on the ACTION
if [ "$ACTION" == "start" ]; then
    start_deployments "$NAMESPACE_ARG"
elif [ "$ACTION" == "stop" ]; then
    stop_deployments "$NAMESPACE_ARG"
else
    echo "Invalid action: Use 'start' or 'stop'."
    exit 1
fi