# Installing the otel-demo (Online Boutique) with `helm`

## Prerequisites

1. `helm` is installed.  **See** [helm install](../../tests/notebooks/helm.ipynb)

2. Add the **open-telemetry** repo.

```bash
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts

# update the repo
helm repo update
```

---

## Installing the demo chart

1. This create a helm ***release*** called `otel-demo`, and will install the cluster into a namespace called `demo`

2. The following command assumes you are running from this directory **/test-clusters/otel-demo/**, but you can run it from anywhere given you provide the correct path to the [overrides.yaml](overrides.yaml)  

Note: you may want to start the observiability tools prior to starting this cluster.  See [Installing the full monitoring stack](../../charts/README.md#install-the-umbrella-chart)

```bash
helm install otel-demo open-telemetry/opentelemetry-demo -f otel-demo/overrides.yaml --namespace demo --create-namespace
```

---

## Note about the `overrides.yaml`

This is really all that it is:

```yaml
default:
  envOverrides:
    - name: OTEL_COLLECTOR_NAME
      value: "otel-collector.monitoring.svc.cluster.local"
```

The key part here is specifying the FQDN.  In this case, I deployed the ovservability tools to a namespace called `monitoring`, and the otel-demo cluster to a namespace called `demo`.  So the full DNS is required to reach the collector.  

## Viewing `otel-demo` chart details

### Chart details

```bash
helm show chart open-telemetry/opentelemetry-demo
```

### View the defuault vlaues

```bash
helm show values open-telemetry/opentelemetry-demo
```

### View the full content

```bash
helm template scale-otel-demo open-telemetry/opentelemetry-demo
```

### Output to configuration file (with overrides)

```bash
helm template scale-otel-demo open-telemetry/opentelemetry-demo -f overrides.yaml > opentelemetry-demo.yaml
```

## Running the static manifest

```bash
kubectl apply -f opentelemetry-demo.yaml
```

## Accessing the Locust dashboard

1. Forward the port for the frontend proxy
  
```bash
kubectl --namespace default port-forward svc/scale-otel-demo-frontendproxy 8080:8080
```

2. Access <http://localhost:8080> in your browser
