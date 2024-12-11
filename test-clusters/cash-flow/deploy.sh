#!/bin/bash

export GENERATE_CMD="java -jar openapi-generator-cli.jar generate"

# Generate FastAPI code from OpenAPI
export TEMPLATE_DIR=${PWD}/templates
export SPEC_DIR=${PWD}/specs
export API_V1_SERVICES=${SPEC_DIR}/api/v1/services
export BACKEND=${PWD}/backend
export BACKEND_SERVICES=${BACKEND}/services
export BACKEND_INTERFACES=${BACKEND}/interfaces
export BACKEND_INTERFACES_INTERNAL=${BACKEND_INTERFACES}/internal

export AUTH_SERVICE_DIR=${BACKEND_SERVICES}/auth
export AUTH_SERVICE_DEPLOY_DIR=${AUTH_SERVICE_DIR}/openapi
export AUTH_SERVICE_GENERATOR=python-fastapi
export AUTH_SERVICE_SPEC_FILE=${API_V1_SERVICES}/auth/auth.yaml
export AUTH_SERVICE_DEPLOYED_DIR=${BACKEND_SERVICES}/auth/openapi
export AUTH_SERVICE_TEMPLATE_DIR=${TEMPLATE_DIR}/services/auth

export AUTH_CLIENT_GENERATOR=python
export AUTH_CLIENT_DEPLOY_DIR=${BACKEND_INTERFACES}/internal/auth
export AUTH_CLIENT_DEPLOYMENT_DIR=${PWD}${BACKEND_INTERFACES_INTERNAL}/auth

export TRANSACTION_SERVICE_DIR=${BACKEND_SERVICES}/transaction
export TRANSACTION_SERVICE_DEPLOY_DIR=${TRANSACTION_SERVICE_DIR}/openapi
export TRANSACTION_SERVICE_GENERATOR=python-fastapi
export TRANSACTION_SERVICE_SPEC_FILE=${API_V1_SERVICES}/transaction/transaction.yaml
export TRANSACTION_SERVICE_DEPLOYED_DIR=${BACKEND_SERVICES}/transaction/openapi
export TRANSACTION_SERVICE_TEMPLATE_DIR=${TEMPLATE_DIR}/services/transactions

export REGISTRATION_SERVICE_DIR=${BACKEND_SERVICES}/registration
export REGISTRATION_SERVICE_DEPLOY_DIR=${REGISTRATION_SERVICE_DIR}/openapi
export REGISTRATION_SERVICE_GENERATOR=python-fastapi
export REGISTRATION_SERVICE_SPEC_FILE=${API_V1_SERVICES}/registration/registration.yaml
export REGISTRATION_SERVICE_DEPLOYED_DIR=${BACKENDD_SERVICES}/registration/openapi
export REGISTRATION_SERVICE_TEMPLATE_DIR=${TEMPLATE_DIR}/services/registration

export REGISTRATION_CLIENT_GENERATOR=python
export REGISTRATION_CLIENT_DEPLOY_DIR=${BACKEND_INTERFACES}/internal/registration
export REGISTRATION_CLIENT_DEPLOYMENT_DIR=${PWD}${BACKEND_INTERFACES_INTERNAL}/registration

export DMS_SERVICE_DIR=${BACKEND_SERVICES}/dms
export DMS_SERVICE_DEPLOY_DIR=${DMS_SERVICE_DIR}/openapi
export DMS_SERVICE_GENERATOR=python-fastapi
export DMS_CLIENT_GENERATOR=python
export DMS_CLIENT_DEPLOY_DIR=${BACKEND_INTERFACES}/internal/dms
export DMS_SPEC_FILE=${SPEC_DIR}/internal/services/dms/v1/dms.yaml
export DMS_TEMPLATE_DIR=${SPEC_DIR}/internal/services/dms/v1/templates
export DMS_SERVICE_DEPLOYED_DIR=${BACKEND_SERVICES}/dms/openapi
export DMS_CLIENT_DEPLOYMENT_DIR=${PWD}${BACKEND_INTERFACES_INTERNAL}/dms

export NOTIF_SERVICE_DIR=${BACKEND_SERVICES}/notification
export NOTIF_SERVICE_DEPLOY_DIR=${NOTIF_SERVICE_DIR}/openapi
export NOTIF_SERVICE_GENERATOR=python-fastapi
export NOTIF_CLIENT_GENERATOR=python
export NOTIF_CLIENT_DEPLOY_DIR=${BACKEND_INTERFACES}/internal/notification
export NOTIF_SPEC_FILE=${SPEC_DIR}/internal/services/notification/v1/notification.yaml
# export NOTIF_TEMPLATE_DIR=${SPEC_DIR}/internal/services/notification/v1/templates
export NOTIF_SERVICE_DEPLOYED_DIR=${BACKEND_SERVICES}/notification/openapi
export NOTIF_CLIENT_DEPLOYMENT_DIR=${PWD}${BACKEND_INTERFACES_INTERNAL}/notification

export TASKING_SERVICE_DIR=${BACKEND_SERVICES}/tasking
export TASKING_SERVICE_DEPLOY_DIR=${TASKING_SERVICE_DIR}/openapi
export TASKING_SERVICE_GENERATOR=python-fastapi
export TASKING_CLIENT_GENERATOR=python
export TASKING_CLIENT_DEPLOY_DIR=${BACKEND_INTERFACES}/internal/tasking
export TASKING_SPEC_FILE=${SPEC_DIR}/internal/services/tasking/v1/tasking.yaml
export TASKING_SERVICE_DEPLOYED_DIR=${BACKEND_SERVICES}/tasking/openapi
export TASKING_CLIENT_DEPLOYMENT_DIR=${PWD}${BACKEND_INTERFACES_INTERNAL}/tasking

export OTEL_TEMPLATE_DIR=${TEMPLATE_DIR}/otel



# Function to clean the deployment directories
clean() {
    echo "Cleaning deployment directories."
    directories=(
    "${AUTH_SERVICE_DEPLOYED_DIR}"
    "${TRANSACTION_SERVICE_DEPLOYED_DIR}"
    "${REGISTRATION_SERVICE_DEPLOYED_DIR}"
    "${REGISTRATION_CLIENT_DEPLOYMENT_DIR}"
    "${DMS_SERVICE_DEPLOYED_DIR}"
    "${TASKING_SERVICE_DEPLOYED_DIR}"
    "${DMS_CLIENT_DEPLOYMENT_DIR}"
    "${TASKING_CLIENT_DEPLOYMENT_DIR}"
    )

    # Loop through each directory and clean it
    for dir in "${directories[@]}"; do
        echo "Cleaning ${dir}"
        chmod -R 777 "${dir}"
        rm -rf "${dir}"
    done
}



# Function to deploy the services
deploy() {
  # Deploy DMS
  echo "Generating DMS APIs from OpenAPI"
  
  # Copy the OTel template to the Auth and Transaction service template directories
  cp -r ${OTEL_TEMPLATE_DIR}/* ${AUTH_SERVICE_TEMPLATE_DIR}
  cp -r ${OTEL_TEMPLATE_DIR}.* ${TRANSACTION_SERVICE_TEMPLATE_DIR}

  echo "Generating internal DMS server"
  ${GENERATE_CMD} \
      -i ${DMS_SPEC_FILE} \
      -g ${DMS_SERVICE_GENERATOR} \
      -o ${DMS_SERVICE_DEPLOY_DIR} \
      --template-dir ${OTEL_TEMPLATE_DIR} \
      --package-name server \
      --reserved-words-mappings date=date 

  echo "Generating internal DMS client"
  ${GENERATE_CMD} \
      -i ${DMS_SPEC_FILE} \
      -g ${DMS_CLIENT_GENERATOR} \
      -o ${DMS_CLIENT_DEPLOY_DIR} \
      --package-name dms_client \
      --reserved-words-mappings date=date

  echo "Generating internal Notification server"
  ${GENERATE_CMD} \
      -i ${NOTIF_SPEC_FILE} \
      -g ${NOTIF_SERVICE_GENERATOR} \
      -o ${NOTIF_SERVICE_DEPLOY_DIR} \
      --template-dir ${OTEL_TEMPLATE_DIR} \
      --package-name server \
      --reserved-words-mappings date=date 

  echo "Generating internal Notification client"
  ${GENERATE_CMD} \
      -i ${NOTIF_SPEC_FILE} \
      -g ${NOTIF_CLIENT_GENERATOR} \
      -o ${NOTIF_CLIENT_DEPLOY_DIR} \
      --package-name notification_client \
      --reserved-words-mappings date=date

  # # Deploy Tasking Service
  echo "Generating Tasking APIs from OpenAPI"
  echo "Generating internal Tasking server"
  ${GENERATE_CMD} \
      -i ${TASKING_SPEC_FILE} \
      -g ${TASKING_SERVICE_GENERATOR} \
      -o ${TASKING_SERVICE_DEPLOY_DIR} \
      --template-dir ${OTEL_TEMPLATE_DIR} \
      --package-name server \
      --reserved-words-mappings date=date 

  # # Deploy the Tasking client
  echo "Generating internal Tasking client"
  ${GENERATE_CMD} \
      -i ${TASKING_SPEC_FILE} \
      -g ${TASKING_CLIENT_GENERATOR} \
      -o ${TASKING_CLIENT_DEPLOY_DIR} \
      --template-dir ${OTEL_TEMPLATE_DIR} \
      --package-name tasking_client \
      --reserved-words-mappings date=date

  # Deploy Auth Service   
  echo "Generating Auth Service APIs from OpenAPI"
  ${GENERATE_CMD} \
      -i ${AUTH_SERVICE_SPEC_FILE} \
      -g ${AUTH_SERVICE_GENERATOR} \
      -o ${AUTH_SERVICE_DEPLOY_DIR} \
      --template-dir ${AUTH_SERVICE_TEMPLATE_DIR} \
      --package-name server \
      --reserved-words-mappings date=date 

  # Deploy Auth Client
  echo "Generating Auth Client APIs from OpenAPI"
  ${GENERATE_CMD} \
      -i ${AUTH_SERVICE_SPEC_FILE} \
      -g ${AUTH_CLIENT_GENERATOR} \
      -o ${AUTH_CLIENT_DEPLOY_DIR} \
      --package-name auth_client \
      --reserved-words-mappings date=date

  # Deploy Transaction Service   
  echo "Generating Transaction Service APIs from OpenAPI"
  ${GENERATE_CMD} \
      -i ${TRANSACTION_SERVICE_SPEC_FILE} \
      -g ${TRANSACTION_SERVICE_GENERATOR} \
      -o ${TRANSACTION_SERVICE_DEPLOY_DIR} \
      --template-dir ${TRANSACTION_SERVICE_TEMPLATE_DIR} \
      --package-name server \
      --reserved-words-mappings date=date


  # Deploy Registration Service   
  echo "Generating Registration Service APIs from OpenAPI"
  ${GENERATE_CMD} \
      -i ${REGISTRATION_SERVICE_SPEC_FILE} \
      -g ${REGISTRATION_SERVICE_GENERATOR} \
      -o ${REGISTRATION_SERVICE_DEPLOY_DIR} \
      --template-dir ${OTEL_TEMPLATE_DIR} \
      --package-name server \
      --reserved-words-mappings date=date 

  # Deploy Auth Client
  echo "Generating Registration Client APIs from OpenAPI"
  ${GENERATE_CMD} \
      -i ${REGISTRATION_SERVICE_SPEC_FILE} \
      -g ${REGISTRATION_CLIENT_GENERATOR} \
      -o ${REGISTRATION_CLIENT_DEPLOY_DIR} \
      --package-name registration_client \
      --reserved-words-mappings date=date      

  echo "Deployment complete."
}

# Check the argument and call the appropriate function
if [ "$1" == "deploy" ]; then
  if [ ! -f openapi-generator-cli.jar ]; then
    echo "Downloading openapi-generator-cli.jar"
    wget wget https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/7.8.0/openapi-generator-cli-7.8.0.jar -O openapi-generator-cli.jar  
  fi  
  deploy
  rm -f openapi-generator-cli.jar
elif [ "$1" == "clean" ]; then
  clean
else
  echo "Usage: $0 {deploy|clean}"
  exit 1
fi
