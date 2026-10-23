# Exercise 2: Deploy a Flask App on Minikube using kubectl and YAML

## 1. Aim
Set up a single-node Kubernetes cluster with Minikube and deploy a Python Flask application on it using a Deployment defined in YAML, then expose it with a NodePort Service.

## 2. Environment
| Component | Details |
|---|---|
| Operating system | Windows 11 + WSL2 (Ubuntu 24.04) |
| Container platform | Docker Desktop |
| Kubernetes | Minikube v1.39.0 (docker driver, containerd runtime), Kubernetes v1.37.0 |
| CLI | kubectl |

## 3. Files in this folder
| File | Purpose |
|---|---|
| `app.py` | Flask app listening on port 15000 (identical to the manual) |
| `Dockerfile` | Builds the `flask-app` image (identical to the manual) |
| `flask-deployment.yaml` | Deployment + NodePort Service, final version from Step 13 (identical to the manual) |

## 4. Steps (in the order of the manual)

### Step 1: Start Minikube
```bash
minikube start
```

### Step 2: Create a Flask application
`app.py`:
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Flask on Kubernetes!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15000)
```

### Step 3: Create a Dockerfile for the Flask application
`Dockerfile`:
```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install flask
CMD ["python", "app.py"]
```

### Step 4: Build the Docker image with Minikube's Docker daemon
**Manual commands, run exactly as written:**
```bash
minikube docker-env
eval $(minikube docker-env)
docker build -t flask-app .
```
`minikube docker-env` runs, but warns: *"Using the docker-env command with the containerd runtime is a highly experimental feature"*.

![minikube docker-env](screenshots/09-manual-docker-env.png)

The build inside Minikube then fails:
```text
ERROR: failed to build: Error response from daemon: 404 page not found
```
![Build inside Minikube fails](screenshots/10-manual-build-in-minikube.png)

**Why:** this Minikube cluster uses the **containerd** runtime, and building through `docker-env` only works with the Docker runtime.

**What was done instead:** the same Dockerfile was built with the host Docker and the image was copied into the cluster:
```bash
docker build -t flask-app .
minikube image load flask-app:latest
minikube image ls | grep flask
```
**Output:**
```text
docker.io/library/flask-app:latest
```
![Image loaded into Minikube](screenshots/01-image-loaded.png)

Rebuilding with the manual's Dockerfile (`COPY . /app`) and loading it gives the same image:

![Rebuild with the manual Dockerfile](screenshots/11-rebuild-copy-dot.png)

Because the YAML uses `imagePullPolicy: Never` (Step 5), Kubernetes uses this local image instead of pulling from Docker Hub. *(Starting Minikube with `--container-runtime=docker` would let the manual's `docker-env` build run as written.)*

### Step 5: Create the Kubernetes Deployment YAML file
`flask-deployment.yaml` (Deployment part, as in the manual):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask-app
  template:
    metadata:
      labels:
        app: flask-app
    spec:
      containers:
      - name: flask-app
        image: flask-app:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 15000
```

### Step 6: Deploy the application
### Step 7: Check deployment status
### Step 8: Verify Pods created by the Deployment
**Commands:**
```bash
kubectl apply -f flask-deployment.yaml
kubectl get deployments
kubectl get pods -l app=flask-app
```
**Output:**
```text
deployment.apps/flask-app created
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
flask-app   1/1     1            1           10s
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-59f7cdccb4-8cttm   1/1     Running   0          11s
```
![Deployment and Pod running](screenshots/02-deployment.png)

### Step 9: Describe the Deployment
**Command:**
```bash
kubectl describe deployment flask-app
```
**Key output:**
```text
Name:                   flask-app
Namespace:              default
Selector:               app=flask-app
Replicas:               1 desired | 1 updated | 1 total | 1 available | 0 unavailable
StrategyType:           RollingUpdate
  Containers:
   flask-app:
    Image:         flask-app:latest
    Port:          15000/TCP
Conditions:
  Available      True    MinimumReplicasAvailable
  Progressing    True    NewReplicaSetAvailable
NewReplicaSet:   flask-app-59f7cdccb4 (1/1 replicas created)
Events:
  Normal  ScalingReplicaSet  34s  deployment-controller  Scaled up replica set flask-app-59f7cdccb4 from 0 to 1
```
![Deployment description](screenshots/03-describe.png)

### Step 10: View deployment logs
**Command** (the manual uses `kubectl logs <pod-name>`; selecting the Pod by its label gives the same logs):
```bash
kubectl logs -l app=flask-app
```
**Output:**
```text
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:15000
 * Running on http://10.244.0.4:15000
Press CTRL+C to quit
```
![Flask logs](screenshots/04-logs.png)

### Step 11: Check Services
### Step 12: Try to access the Flask service on port 15000
**Commands:**
```bash
kubectl get services
curl http://127.0.0.1:15000
```
**Output:**
```text
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   21h
curl: (7) Failed to connect to 127.0.0.1 port 15000 after 0 ms: Couldn't connect to server
```
As the manual explains, the connection fails because the app exposes port 15000 only inside the cluster and no Service exists yet.

![Access fails without a Service](screenshots/05-curl-before-service.png)

### Step 13: Update the deployment file with a Service section
The Service section is added to `flask-deployment.yaml`:
```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: flask-app-service
spec:
  selector:
    app: flask-app
  ports:
  - port: 15000
    targetPort: 15000
  type: NodePort
```
**Commands:**
```bash
kubectl apply -f flask-deployment.yaml
kubectl get services
```
**Output:**
```text
deployment.apps/flask-app unchanged
service/flask-app-service created
NAME                TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)           AGE
flask-app-service   NodePort    10.106.245.196   <none>        15000:31968/TCP   0s
kubernetes          ClusterIP   10.96.0.1        <none>        443/TCP           21h
```
![Service created](screenshots/06a-service-created.png)

Get the URL of the Service:
```bash
minikube service flask-app-service --url
```
**Output:**
```text
http://127.0.0.1:46775
❗  Because you are using a Docker driver on linux, the terminal needs to be open to run it.
```
![Service URL](screenshots/06-service.png)

In a second terminal:
```bash
curl http://127.0.0.1:46775
```
**Output:**
```text
Hello from Flask on Kubernetes!
```
![curl succeeds](screenshots/07-curl-success.png)

The app also opens in the browser:

![App in browser](screenshots/08-browser.png)

The full flow also works with the image built from the manual's Dockerfile:

![Works with the manual Dockerfile](screenshots/12-works-with-manual-dockerfile.png)

### Clean up
```bash
kubectl delete -f flask-deployment.yaml
```

## 5. Changes from the manual
| Manual | What happened | What was done |
|---|---|---|
| Step 4: `eval $(minikube docker-env)` + `docker build -t flask-app .` | `ERROR: failed to build: ... 404 page not found` (this cluster uses the containerd runtime) | Built with the host Docker, then `minikube image load flask-app:latest` |
| Step 10: `kubectl logs <pod-name>` | – | `kubectl logs -l app=flask-app` (same logs, Pod selected by label) |

All files in this folder (`app.py`, `Dockerfile`, `flask-deployment.yaml`) are identical to the manual.

## 6. Q&A
1. **What is the purpose of `minikube service flask-app-service --url`?** It gives a URL to reach the Service running inside Minikube.
2. **What happens when it runs?** Minikube checks that the Service exists and is exposed, starts a tunnel (Docker driver) and prints the URL.
3. **Why is `targetPort` used?** It is the port the container actually listens on (15000).
4. **`port` vs `targetPort`?** `port` is the Service's own port; `targetPort` is the container port the Service forwards to.
5. **How do you access a Flask app running in Minikube?** Expose it with a Service and use `minikube service <name> --url`.
6. **Why must the terminal stay open with the Docker driver?** The tunnel runs in that terminal; closing it closes the tunnel.
7. **Benefit of `--url`?** It prints the URL instead of opening a browser, so it can be used with curl.
8. **Command to expose a Service?** `kubectl expose ...` or `kubectl apply -f <yaml with a Service>`.
9. **How does Minikube help?** It runs a single-node Kubernetes cluster locally for testing.
10. **Role of kubectl?** The CLI to talk to the Kubernetes API: deploy, inspect, scale and delete resources.

## 7. Result
The Flask app was deployed on Minikube with a YAML Deployment, was unreachable until a NodePort Service was added (Step 12), and then responded with `Hello from Flask on Kubernetes!` – the manual's expected result.
