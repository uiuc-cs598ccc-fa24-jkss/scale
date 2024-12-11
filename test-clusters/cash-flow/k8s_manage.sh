#!/bin/bash

NAMESPACE="cash-flow"
ACTION=$1

# get python executable
if command -v python3 &>/dev/null; then
    PYTHON_EXEC=python3
elif command -v python &>/dev/null; then
    PYTHON_EXEC=python
else
    echo "Python is not installed." >&2
    exit 1
fi

PYTHON_HOME=$($PYTHON_EXEC -c "import sysconfig; print(sysconfig.get_config_var('prefix'))")

echo "Python Home: $PYTHON_HOME"

if [ "$ACTION" == "start" ]; then
    echo "Building config maps and secrets..."
    pushd k8s
    # python build.py
    $PYTHON_EXEC build.py

    echo "Starting the application..."..

    kubectl apply -f namespace.yaml

    # create the configmap and apply specs for the otel collector

    kubectl apply -f user-db/user-db-config.yaml
    kubectl apply -f user-db/user-db-secret.yaml
    kubectl apply -f user-db/user-db-pv.yaml
    kubectl apply -f user-db/user-db-pvc.yaml
    kubectl apply -f user-db/user-db-dep.yaml
    kubectl apply -f user-db/user-db-service.yaml

    kubectl apply -f tx-db/tx-db-config.yaml
    kubectl apply -f tx-db/tx-db-secret.yaml
    kubectl apply -f tx-db/tx-db-pv.yaml
    kubectl apply -f tx-db/tx-db-pvc.yaml
    kubectl apply -f tx-db/tx-db-dep.yaml
    kubectl apply -f tx-db/tx-db-service.yaml

    # nginx
    # kubectl create configmap nginx-config --from-file=conf/nginx/nginx.conf -n cash-flow
    # kubectl apply -f conf/nginx/nginx-dep.yml 
    # kubectl apply -f conf/nginx/nginx-service.yml 

    # celery 
    kubectl apply -f celery/celery-config.yaml
    kubectl apply -f celery/celery-dep.yaml
   
    # redis
    kubectl apply -f redis/redis-dep.yaml
    kubectl apply -f redis/redis-service.yaml
 
    kubectl apply -f auth/auth-config.yaml
    kubectl apply -f auth/auth-secret.yaml
    kubectl apply -f auth/auth-dep.yaml
    kubectl apply -f auth/auth-service.yaml

    kubectl apply -f dms/dms-config.yaml
    kubectl apply -f dms/dms-secret.yaml
    kubectl apply -f dms/dms-dep.yaml
    kubectl apply -f dms/dms-service.yaml
  
    kubectl apply -f registration/registration-config.yaml
    kubectl apply -f registration/registration-dep.yaml
    kubectl apply -f registration/registration-service.yaml

    kubectl apply -f tasking/tasking-config.yaml
    kubectl apply -f tasking/tasking-dep.yaml
    kubectl apply -f tasking/tasking-service.yaml

    kubectl apply -f transaction/transaction-config.yaml
    kubectl apply -f transaction/transaction-dep.yaml
    kubectl apply -f transaction/transaction-service.yaml

    kubectl apply -f notification/notification-dep.yaml
    kubectl apply -f notification/notification-service.yaml

    kubectl apply -f cli/cli-deployment.yaml

    popd
    echo "Application started."

elif [ "$ACTION" == "stop" ]; then
    echo "Stopping the application..."
    pushd k8s

    kubectl delete -f cli/cli-deployment.yaml

    kubectl delete -f auth/auth-config.yaml
    kubectl delete -f auth/auth-secret.yaml
    kubectl delete -f auth/auth-dep.yaml
    kubectl delete -f auth/auth-service.yaml

    kubectl delete -f registration/registration-config.yaml
    kubectl delete -f registration/registration-dep.yaml
    kubectl delete -f registration/registration-service.yaml

    kubectl delete -f tasking/tasking-config.yaml
    kubectl delete -f tasking/tasking-dep.yaml
    kubectl delete -f tasking/tasking-service.yaml

    kubectl delete -f notification/notification-dep.yaml
    kubectl delete -f notification/notification-service.yaml

    kubectl delete -f transaction/transaction-config.yaml
    kubectl delete -f transaction/transaction-dep.yaml
    kubectl delete -f transaction/transaction-service.yaml

    kubectl delete -f dms/dms-config.yaml
    kubectl delete -f dms/dms-secret.yaml
    kubectl delete -f dms/dms-dep.yaml
    kubectl delete -f dms/dms-service.yaml    

    # celery 
    kubectl delete -f celery/celery-dep.yaml

    kubectl delete -f user-db/user-db-config.yaml
    kubectl delete -f user-db/user-db-secret.yaml
    kubectl delete -f user-db/user-db-dep.yaml
    kubectl delete -f user-db/user-db-service.yaml
    kubectl delete -f user-db/user-db-pv.yaml
    kubectl delete -f user-db/user-db-pvc.yaml

    kubectl delete -f tx-db/tx-db-config.yaml
    kubectl delete -f tx-db/tx-db-secret.yaml
    kubectl delete -f tx-db/tx-db-dep.yaml
    kubectl delete -f tx-db/tx-db-service.yaml
    kubectl delete -f tx-db/tx-db-pv.yaml
    kubectl delete -f tx-db/tx-db-pvc.yaml

    # nginx
    # kubectl create configmap nginx-config --from-file=conf/nginx/nginx.conf -n cash-flow
    # kubectl delete -f conf/nginx/nginx-dep.yml 
    # kubectl delete -f conf/nginx/nginx-service.yml 

    # redis
    kubectl delete -f redis/redis-dep.yaml
    kubectl delete -f redis/redis-service.yaml
   
    # kubectl delete -f namespace.yaml

    popd

    echo "Application stopped."
else
    echo "Usage: $0 {start|stop}"
fi
