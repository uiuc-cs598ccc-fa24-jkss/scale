
# generate apis
./deploy.sh deploy

# build and publish containers
./build.sh

# build kubernetes templates (config and secrets)
pushd k8s
python build.py
popd




