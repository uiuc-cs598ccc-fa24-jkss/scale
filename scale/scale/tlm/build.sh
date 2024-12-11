#!/bin/bash

echo "Sourcing .env file"

ENV_FILE="${PWD}/.env.tlm"

if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

# Parse options
while getopts ":v:h" opt; do
  case $opt in
    v)
      TLM_SVC_VERSION="$OPTARG"
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
DEFAULT_TAG="$TLM_SVC_TAG-$TLM_SVC_VERSION"
tag="$DEFAULT_TAG"

# Functions
build_image() {
    local tag=$1
    echo "Building image: $DOCKER_REPO:$tag"
    docker build -t "$DOCKER_REPO:$tag" .
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
