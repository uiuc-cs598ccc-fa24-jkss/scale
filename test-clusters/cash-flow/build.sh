# Source the .env file
echo "Sourcing .env file"
pushd backend
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
popd

# docker compose build

# docker push $DOCKER_REPO:$CELERY_DOCKER_TAG
# docker push $DOCKER_REPO:$AUTH_DOCKER_TAG
# docker push $DOCKER_REPO:$TASKING_DOCKER_TAG
# docker push $DOCKER_REPO:$TRANSACTION_DOCKER_TAG
# docker push $DOCKER_REPO:$DMS_DOCKER_TAG
# docker push $DOCKER_REPO:$REGISTRATION_DOCKER_TAG

build_celery() {
    pushd backend 
    echo "Building celery image"
    docker compose build celery-worker
    popd
}

build_auth() {
    pushd backend 
    echo "Building Auth image"
    docker compose build auth
    popd
}

build_tasking() {
    pushd backend 
    echo "Building Tasking image"
    docker compose build tasking
    popd
}

build_transaction() {
    pushd backend 
    echo "Building Transaction image"
    docker compose build transaction
    popd
}

build_dms() {
    pushd backend 
    echo "Building DMS image"
    docker compose build dms
    popd
}

build_registration() {
    pushd backend 
    echo "Building Registration image"
    docker compose build registration
    popd
}

build_notification() {
    pushd backend 
    echo "Building Notification image"
    docker compose build notification
    popd
}

build_cli() {
    echo "Building CLI image"
    docker build -f ./Dockerfile.cli -t $DOCKER_REPO:$CLI_DOCKER_TAG-$CLI_VERSION .
}

push_celery() {
    docker push $DOCKER_REPO:$CELERY_DOCKER_TAG-$CELERY_VERSION
}

push_auth() {
    docker push $DOCKER_REPO:$AUTH_DOCKER_TAG-$AUTH_VERSION
}

push_tasking() {
    docker push $DOCKER_REPO:$TASKING_DOCKER_TAG-$TASKING_VERSION
}

push_transaction() {
    docker push $DOCKER_REPO:$TRANSACTION_DOCKER_TAG-$TRANSACTION_VERSION
}

push_dms() {
    docker push $DOCKER_REPO:$DMS_DOCKER_TAG-$DMS_VERSION
}

push_registration() {
    docker push $DOCKER_REPO:$REGISTRATION_DOCKER_TAG-$REGISTRATION_VERSION
}

push_notification() {
    docker push $DOCKER_REPO:$NOTIF_DOCKER_TAG-$NOTIF_VERSION
}

push_cli() {

    docker push $DOCKER_REPO:$CLI_DOCKER_TAG-$CLI_VERSION
}


if [ "$1" == "celery" ]; then
    build_celery
    push_celery
elif [ "$1" == "auth" ]; then
    build_auth
    push_auth
elif [ "$1" == "tasking" ]; then
    build_tasking
    push_tasking
elif [ "$1" == "transaction" ]; then
    build_transaction
    push_transaction
elif [ "$1" == "dms" ]; then
    build_dms
    push_dms
elif [ "$1" == "registration" ]; then
    build_registration
    push_registration
elif [ "$1" == "notification" ]; then
    build_notification
    push_notification
elif [ "$1" == "cli" ]; then
    ENV_FILE="${PWD}/cli/.env.cli"

    if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
    fi
    build_cli
    push_cli    
else
    build_celery
    build_auth
    build_tasking
    build_transaction
    build_dms
    build_registration
    build_notification
    push_celery
    push_auth
    push_tasking
    push_transaction
    push_dms
    push_registration
    push_notification
fi