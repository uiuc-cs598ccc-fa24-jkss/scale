# Manage minikube cluster

## Starting cluster

Using the `manage.sh` script, you can start `otel-collector`, `tempo`, and `grafana` pods either

- In the `default` namespace

```bash
./manage.sh start
```

- Or in a provided namespace.  This can be used to deploy the pods to an existing cluster.

```bash
./manage.sh start -n cash-flow
```

## Stopping the cluster

Use the same script to stop the pods:

- Stop the pods if they were started in the `default` namespace:

```bash
./manage.sh stop
```

- Stop the pods in a provided namespace

```bash
./manage.sh stop -n cash-flow
```

# Viewing Grafana UI

## Port Forwarding

**In separate terminal window**

```bash
kubectl port-forward service/grafana 3000:3000 -n cash-flow 
```

In browser, go to <http://localhost:3000>

# Using the NodePort

Get the minikube ip

```
minikube ip

192.168.49.2
```

Get the NodePort

e.g. if running in the cash-flow cluster

```
kubectl get svc -n cash-flow | grep grafana

grafana          NodePort    10.98.44.51      <none>        3000:30894/TCP      22m
```

Navigate to http://<minikube-ip>:<nodeport> in your browser

In this case it would be **<http://192.168.49.2:30894>**

Alternatively, if you're using the cash-cli / k8s command line tool.  You can run ```

```
k8s service-ip grafana

http://192.168.49.2:30894
```

# Getting a shell to a service

# get shell
```bash
kubectl exec --stdin --tty -n cash-flow services/tempo -- /bin/bash
```


# Testing sampler with otelgen

1. Deploy cluster with manage.sh as described above
2. Download otelgen utility from [here](https://github.com/krzko/otelgen/releases)
3. Setup port forwarding for otel-collector
```bash
kubectl port-forward service/otel-collector 24317:4317 -n cash-flow
```
4. Setup port forwarding for the sampler
```bash
kubectl port-forward service/sampler 34317:4317 -n cash-flow
```
5. Use otelgen to push traces into otel-collector to the forwarded otel-collector port
```
otelgen --otel-exporter-otlp-endpoint localhost:24317 --i traces m -t 150 -w 20 -s microservices
```
6. You can tail the log of the sampler to see when it has sampled
```bash
kubectl logs --follow -n cash-flow services/sampler
```
You should see output like the below when enough traces have passed to sample
```
Number of clusters:  5                               
Number of p_micro_clusters is 5                      
Size of p_micro_clusters is [36, 1, 1, 1, 1]         
Number of o_micro_clusters is 0                      
Size of o_micro_clusters is [] 
```
7. You can now run the test client @ `<project_root>/scale/sampler/test_client.py` which connect to the forwarded sampler port
```bash
# Assuming at project root
cd scale/sampler
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/test_client.py
```
You will need to run the otelgen command again if it has stopped to produce traces.  
The command will then start to output trace IDs, like so
```
0c4d24bf97894bf211001a617d581506
3b54416bde507bbfaef08de3ec711cae
8632bbacca69e30d1d384043e07faeef
db693d3973baddc65c97ee9cb3447d41
fa82279b94fb76790addf6cc843e927b
1b4005eb6d50d9c450580c4ebe5b9641
```