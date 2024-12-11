# Helm Charts

## Overview

Helm is a package manager for Kubernetes that simplifies the deployment and management of applications. It allows you to define, install, and upgrade Kubernetes applications through reusable YAML templates. Helm provides the ability to manage application charts, which are collections of pre-configured Kubernetes resources.

### Benefits of Using Helm

- **Simplified Deployment**: Helm charts encapsulate all necessary Kubernetes configurations for your application, making it easy to deploy with a single command.
- **Reusability**: Helm charts can be reused and shared across multiple projects or teams, allowing for consistent application deployment.
- **Version Control**: Helm supports versioned charts, making it easy to roll back to previous versions or update applications.
- **Parameterization**: Helm charts can be customized using values files or command-line parameters, allowing for flexible application deployments in different environments.

---

## Install `helm`

See [Installing Helm](https://helm.sh/docs/intro/install/)

## Basic Helm Commands

See [Helm notebook](../tests/notebooks/helm.ipynb) for demonstration of commands

### 1. Install a Chart

To install a chart into your Kubernetes cluster:

```bash
helm install [release] [chart] [flags]
```

Example:

- Installing the `tlm` chart into a namespace

```bash
helm install tlm ./tlm --namespace cash-flow
```

### 2. Unstall a Release

To uninstall (delete) a release:

```bash
helm uninstall [release] [chart]
```

Example:

- Uninstalling the `tlm` chart

```bash
helm uninstall tlm 
```

### 3. Upgrade a Release

To upgrade an existing release

```bash
helm upgrade tlm
```

### 4. Install or Upgrade a Release (`upgrade --install`)

If you want to ensure the Helm installs the release if it doesn't exist, or upgrade it if it does (very useful)

```bash
helm upgrade --install [release-name] [chart-name]
```

Example:

To ensure `tlm` is either upgrade or installed

```bash
helm upgrade --install tlm ./tlm
```

Or in a namespace

```bash
helm upgrade --install tlm ./tlm --namespace cash-flow
```

### 5. List Installed Releases

To list all installed Helm releases:

```bash
helm list
```

Or for a specific namespace

```bash
helm list --namespace cash-flow
```

### 6. Rollback a Release

If you need to rollback to a previous release version:

```bash
helm rollback [release-name] [revision-number]
```

Example:

```bash
helm rollback tlm 1
```

---

## Install the 'umbrella` chart

To install all of the monitoring tools currently configured in **scale-full**

**Note** - this will create a release called ***scale*** and install the containers into a namespace called ***monitoring***.  It will create the namespace if it doesn't exist.

```bash
helm install scale ./scale-full -n monitoring --create-namespace
```

### Install and set parameters for the `sampler`

This will set the image *version* to use as **latest**, and the *trainSize* to **500**

```bash
helm install scale ./scale-full -n monitoring --create-namespace --set sampler.image.version=latest --set sampler.trainSize=500
```

---

## Updating Dependencies for the full chart

If you modify any of the sub charts, you'll need to update the dependencies for the `scale-full` chart

- Update the dependencies

```bash
helm dependency update ./scale-full
```

- Build the dependencies

```bash
helm dependency build ./scale-full
```
