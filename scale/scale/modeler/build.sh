#!/bin/bash

echo "Sourcing .env.modeler file"

ENV_FILE="${PWD}/.env.modeler"
if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
  echo "Environment variables after sourcing .env.modeler:"
  env | grep -E 'TRACE_SAMPLER_CHANNEL|DOCKER_REPO|MODELER_TAG' # Add your relevant environment variables here
else
  echo "Environment file not found at: $ENV_FILE"
fi
# Parse options
while getopts ":v:h" opt; do
  case $opt in
    v)
      MODELER_VERSION="$OPTARG"
      echo "parsing version: $MODELER_VERSION"
      ;;
    h)
      echo "Usage: $0 [build|push] [-v version]"
      exit 0
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      echo "Usage: $0 [build|push] [-v version]"
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      echo "Usage: $0 [build|push] [-v version]"
      exit 1
      ;;
  esac
done

# Remove parsed options 
shift $((OPTIND -1))

# Reset the tag if overridden 
DEFAULT_TAG="$MODELER_TAG-$MODELER_VERSION"
tag="$DEFAULT_TAG"

# Functions
build_image() {
    pushd ..
    local tag=$1
    echo "Building image: $DOCKER_REPO:$tag"
    docker build -f modeler/Dockerfile -t "$DOCKER_REPO:$tag" .
    popd
}

push_image() {
    local tag=$1
    echo "Pushing image: $DOCKER_REPO:$tag"
    docker push "$DOCKER_REPO:$tag"
}

# Get action if provided
action=""
if [ $# -gt 0 ]; then
  action="$1"
fi

# Main logic
if [ -z "$action" ]; then
    build_image "$tag"
    push_image "$tag"
elif [ "$action" == "build" ]; then
    build_image "$tag"
elif [ "$action" == "push" ]; then
    push_image "$tag"
else
    echo "Usage: $0 [build|push] [-v version]"
    exit 1
fi
