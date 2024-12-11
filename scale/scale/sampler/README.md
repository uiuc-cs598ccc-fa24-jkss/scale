# Sampler Build / Install How-To

## Building and pushing a new sampler image

### Build and Push

```bash
./build.sh
```

### Build and Push a specified image ***version***

```bash
build.sh -v my-version
```

### Build only

```bash
./build.sh build
```

### Build a specific version

```bash
./build.sh -v my-version build
```

### Push only

```bash
./build.sh push 
```

### Push a specified version

```bash
./build.sh -v my-version push
```

---

## Install `scale` with specified version

Assuming you just built and published the container with ***my-version***,
you can install it in the scale stack with helm using the following command:

```bash
helm install scale ./scale-full -n monitoring --create-namespace --set sampler.image.version=my-version
```
