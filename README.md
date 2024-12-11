# SCALE

## Description

A software system which analyzes various system and application generated observability data in order to perform dynamic scaling of application work loads in cloud hosted and/or on-premises environments. We envision a monitor that can make use of open technologies to probe distributed tracing and metric data.  This system would wire up to client APIs of a diverse set of process orchestration software. This can include container orchestrators, serverless function controllers or VM provisioning frameworks amongst others.  Based on processing of the observability data, a processor will make vertical or horizontal scaling decisions.  These decisions will then be communicated to the orchestration systems via their client API to carry out the scaling action.

We are proposing a more customizable solution than the current state of the art.  One that works well with multiple open source technologies as well as proprietary cloud APIs, thus making it more portable across different cloud providers or on-premises orchestration platforms.  Most development teams today instrument their applications in some form for distributed tracing, metrics collection or both.  In addition, orchestration platforms, web and network proxies and virtualization systems expose a myriad of system level metrics. These all amount to data points which can be used for real time monitoring, trend research and performance analysis.
However, these same da:w
ta points could in turn be analyzed, and when combined with a rich set of thresholds and rules provided by development or operational teams, or by automation and machine learning, be the driver behind dynamic resource scaling.

## Architecture

![](/docs/img/scale-architecture-1.png)

## Installation

The application is deployed to a kubernetes cluster.

### Install using `helm`

The simplest and preferred method if installation is `helm`.  

* See [helm installation](/charts/README.md#updating-dependencies-for-the-full-chart)

### Install with `kubectl`

Another option is to install kubernetes manifests with `kubectl`.

* See [Managing the kubernets cluster with kubectl](/k8s/README.md#manage-minikube-cluster)

## Building and Pushing new container images

* [sampler](/scale/scale/sampler/README.md#sampler-build--install-how-to)

* [modeler](/scale/scale/modeler/README.md#modeler-build--install-how-to)

## How-Tos

There are several docs and jupyter notebooks that walk through some common processes

* [helm](/tests/notebooks/helm.ipynb)
* [Grafana](/docs/how-tos/grafana.md#grafana-usage-doc)
* [Tempo Client Usage](/tests/notebooks/tempo_client.ipynb)
* [kubernetes scaling](/tests/notebooks/k8s_scaling.ipynb)
* [build and deploy](/tests/notebooks/build-deploy.ipynb)
* [trace modeling with pandas](/tests/notebooks/trace_modeling.ipynb)
* [running the otel-demo cluster](/tests/notebooks/otel-demo.ipynb)
* [managing the cash-flow test cluster](/tests/notebooks/minikube.ipynb)
* [running the cash-flow test cluster](/tests/notebooks/cash-flow-test.ipynb)

## Roadmap

1. Preliminary testing to gather gather results for Milestone 3
2. Incorporate metrics into model processing for fine-tuning autoscaling decisions

## Authors and acknowledgment

* John Durkin
* Kevin Mooney
* Samson Koshy
* Sushil Khadka
