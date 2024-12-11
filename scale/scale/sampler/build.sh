#!/bin/bash

echo "Sourcing .env.sampler file"

ENV_FILE="${PWD}/.env.sampler"

if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

# Parse options
while getopts ":v:h" opt; do
  case $opt in
    v)
      SAMPLER_VERSION="$OPTARG"
      echo "parsing version: $SAMPLER_VERSION"
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
DEFAULT_TAG="$SAMPLER_TAG-$SAMPLER_VERSION"
tag="$DEFAULT_TAG"

# Functions
build_image() {
    pushd ..
    local tag=$1
    echo "Building image: $DOCKER_REPO:$tag"
    docker build -f sampler/Dockerfile -t "$DOCKER_REPO:$tag" .
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
