# Grafana usage doc

## Grafana UI

![grafana](/docs/img/grafana-1.png)

### Using the NodePort

If you are able to access the NodePort (30000) from your machine, then you can view grafana using the `<minikube-ip>`:`<nodePort>`.  This would most likely be <http://192.168.49.2:30000>.

### Using Port-Forwarding

If you are unable to access the nodeport (Mac, Windows) You can also just forward the minikube grafana port

```bash
kubectl port-forward -n monitoring svc/grafana 8080:3000
```

You should see the following output:

```bash
Forwarding from 127.0.0.1:8080 -> 3000
Forwarding from [::1]:8080 -> 3000
Handling connection for 8080
Handling connection for 8080
```

You can then open <http://localhost:8080> in your browser.
