# Exercise 10: Multi-Node Kubernetes Cluster with Multiple Applications and ReplicaSets

## 1. Storyboard (from the manual)
An e-commerce platform has two services:
1. **Product Catalog** (AppA) – provides information about available products.
2. **Shopping Cart** (AppB) – manages user shopping carts.

For availability and fault tolerance, Product Catalog runs **2 replicas** and Shopping Cart **3 replicas**, and the replicas of each service are distributed across multiple nodes.

## 2. Use Case
An online store needs high availability for product browsing and cart management. Spreading each service's replicas over several nodes means that if one node fails, the services stay available.

## 3. Environment
| Component | Details |
|---|---|
| Operating system | Windows 11 + WSL2 (Ubuntu 24.04) |
| Container platform | Docker Desktop |
| Kubernetes | Minikube v1.39.0, profile `devops-multinode` (3 nodes, docker driver, **Docker runtime**), Kubernetes v1.37.0 |

## 4. Files in this folder
| File | Purpose |
|---|---|
| `product_catalog.py`, `Dockerfile.product` | Product Catalog service (`GET /products`) – identical to the manual |
| `shopping_cart.py`, `Dockerfile.shopping` | Shopping Cart service (`GET /cart`, `POST /cart`) – identical to the manual |
| `product_catalog_deployment.yaml` | 2 replicas with `podAntiAffinity` – identical to the manual |
| `shopping_cart_deployment.yaml` | 3 replicas with `podAntiAffinity` (namespace `default`, see Section 6) |
| `product_catalog_service.yaml`, `shopping_cart_service.yaml` | NodePort Services – identical to the manual |

## 5. Steps (in the order of the manual)

### Step 0: Clean up any existing Minikube
```bash
minikube stop
minikube delete
minikube delete -p devops-multinode
```
The third command is not in the manual: `minikube delete` only removes the default `minikube` profile, and a `devops-multinode` cluster left over from an earlier run blocked the new start.

![Clean up](screenshots/10-cleanup.png)

### Step 1a: Set up Minikube with multiple nodes
```bash
minikube start --nodes 3 -p devops-multinode --force --container-runtime=docker
```
**Output (key lines):**
```text
👍  Starting "devops-multinode" primary control-plane node in "devops-multinode" cluster
🐳  Preparing Kubernetes v1.37.0 on Docker 29.7.2 ...
👍  Starting "devops-multinode-m02" worker node in "devops-multinode" cluster
🐳  Preparing Kubernetes v1.37.0 on Docker 29.7.2 ...
👍  Starting "devops-multinode-m03" worker node in "devops-multinode" cluster
🐳  Preparing Kubernetes v1.37.0 on Docker 29.7.2 ...
🏄  Done! kubectl is now configured to use "devops-multinode" cluster and "default" namespace by default
```
`--container-runtime=docker` was added to the manual's command: Minikube v1.39.0 uses the containerd runtime by default, and then the manual's Step 5 check `minikube -p devops-multinode ssh -- docker images` fails with `Cannot connect to the Docker daemon`. With the Docker runtime it works as written (Step 5).

![3-node cluster with the Docker runtime](screenshots/15-multinode-docker.png)

### Step 1b: Enable the registry add-on
```bash
minikube -p devops-multinode addons enable registry
```
**Output:**
```text
Registry addon with docker driver uses port 57877 please use that instead of default port 5000
    ▪ Using image registry.k8s.io/minikube/kube-registry-proxy:v0.0.11
    ▪ Using image docker.io/registry:3
🔎  Verifying registry addon...
🌟  The 'registry' addon is enabled
```
![Registry addon](screenshots/16-registry-addon.png)

### Step 2: Product Catalog (AppA) – Python code
`product_catalog.py`:
```python
# product_catalog.py
from flask import Flask, jsonify

app = Flask(__name__)

products = [
    {"id": 1, "name": "Laptop", "price": 1200},
    {"id": 2, "name": "Phone", "price": 800},
    {"id": 3, "name": "Headphones", "price": 150},
]

@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
```

### Step 3: Shopping Cart (AppB) – Python code
`shopping_cart.py`:
```python
# shopping_cart.py
from flask import Flask, jsonify, request

app = Flask(__name__)

cart = []

@app.route("/cart", methods=["GET"])
def get_cart():
    return jsonify(cart)

@app.route("/cart", methods=["POST"])
def add_to_cart():
    item = request.json
    cart.append(item)
    return jsonify(cart), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
```

### Step 4: Dockerize the applications
`Dockerfile.product`:
```dockerfile
# Dockerfile for Product Catalog
FROM python:3.9-slim
WORKDIR /app
COPY product_catalog.py /app/
RUN pip install flask
CMD ["python", "product_catalog.py"]
```
`Dockerfile.shopping`:
```dockerfile
# Dockerfile for Shopping Cart
FROM python:3.9-slim
WORKDIR /app
COPY shopping_cart.py /app/
RUN pip install flask
CMD ["python", "shopping_cart.py"]
```
Build both images (commands exactly as in the manual):
```bash
docker build -t product-catalog:latest -f Dockerfile.product .
docker build -t shopping-cart:latest -f Dockerfile.shopping .
docker images
```
```text
 => => naming to docker.io/library/product-catalog:latest
 => => naming to docker.io/library/shopping-cart:latest
product-catalog:latest   ea5eeb7e1ff9   203MB
shopping-cart:latest     6c79bd7fceab   203MB
```
![Images built](screenshots/17-images-built.png)

### Step 5: Load the images into the cluster
```bash
minikube -p devops-multinode image load product-catalog:latest
minikube -p devops-multinode image load shopping-cart:latest
minikube -p devops-multinode ssh -- docker images
```
**Output of the manual's verify command:**
```text
IMAGE                                          ID             DISK USAGE
gcr.io/k8s-minikube/storage-provisioner:v5     6e38f40d628d   31.5MB
kindest/kindnetd:v20260820-69b56db7            4626fe10df5b   97.7MB
product-catalog:latest                         fd821c454452   134MB
registry.k8s.io/coredns/coredns:v1.14.6        520212b8b0fc   77.4MB
registry.k8s.io/etcd:3.7.0-0                   270fbeb69717   60.1MB
registry.k8s.io/kube-apiserver:v1.37.0         bec5f0e1e2ee   103MB
...
shopping-cart:latest                           02f51ac63ec4   134MB
```
`product-catalog` and `shopping-cart` are listed inside the node, as the manual expects.

![ssh -- docker images](screenshots/18-ssh-docker-images.png)

### Step 6: Deploy the applications on Minikube
`product_catalog_deployment.yaml` (identical to the manual):
```yaml
# product_catalog_deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: product-catalog
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: product-catalog
  template:
    metadata:
      labels:
        app: product-catalog
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: product-catalog
            topologyKey: "kubernetes.io/hostname"
      containers:
      - name: product-catalog-container
        image: product-catalog:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 80
```
`shopping_cart_deployment.yaml` is the same with `name: shopping-cart`, `replicas: 3` and `app: shopping-cart`.

The manual's `shopping_cart_deployment.yaml` uses `namespace: devops-exercise`, but this namespace is never created in the exercise (Product Catalog and both Services use `default`). In the first run, applying the manual's file failed:
```text
Error from server (NotFound): error when creating "shopping_cart_deployment.yaml": namespaces "devops-exercise" not found
```
![Manual namespace error](screenshots/06-manual-namespace-error.png)

The namespace was changed to `default`:
```bash
sed -i 's/namespace: devops-exercise/namespace: default/' shopping_cart_deployment.yaml
```
![Namespace fixed](screenshots/07-namespace-fixed.png)

### Step 7: Expose the Services
Deployments (Step 6) and Services (Step 7), applied with the manual's commands:
```bash
kubectl apply -f product_catalog_deployment.yaml
kubectl apply -f shopping_cart_deployment.yaml
kubectl apply -f product_catalog_service.yaml
kubectl apply -f shopping_cart_service.yaml
```
```text
deployment.apps/product-catalog created
deployment.apps/shopping-cart created
service/product-catalog-service created
service/shopping-cart-service created
```
*(The Service list below and the screenshots for Steps 9–10 come from the first complete run of the exercise, so ports and Pod names differ from Step 8.)*
```bash
kubectl get svc
```
```text
NAME                      TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
kubernetes                ClusterIP   10.96.0.1        <none>        443/TCP        25m
product-catalog-service   NodePort    10.111.251.131   <none>        80:31470/TCP   1s
shopping-cart-service     NodePort    10.105.198.59    <none>        80:31985/TCP   1s
```
![NodePort Services](screenshots/09-services.png)

### Step 8: Verify deployment and distribution
```bash
kubectl get pods -o wide
```
**Output:**
```text
NAME                              READY   STATUS    RESTARTS   AGE   IP           NODE
product-catalog-7cb85d4f-j4tvr    1/1     Running   0          38s   10.244.1.3   devops-multinode-m02
product-catalog-7cb85d4f-nbw79    1/1     Running   0          38s   10.244.2.4   devops-multinode-m03
shopping-cart-6858b5f797-dz74j    1/1     Running   0          37s   10.244.0.4   devops-multinode
shopping-cart-6858b5f797-vrprt    1/1     Running   0          37s   10.244.2.5   devops-multinode-m03
shopping-cart-6858b5f797-x5ksb    1/1     Running   0          37s   10.244.1.4   devops-multinode-m02
```
- **Product Catalog** (2 Pods): one on `devops-multinode-m02`, one on `devops-multinode-m03`.
- **Shopping Cart** (3 Pods): one on each node – `devops-multinode`, `-m02` and `-m03`.

The `requiredDuringSchedulingIgnoredDuringExecution` anti-affinity rule with `topologyKey: kubernetes.io/hostname` forces replicas of the same app onto different nodes, so a single node failure cannot take down a whole service.

![Deploy and Pod distribution across nodes](screenshots/19-deploy-pod-distribution.png)

### Step 9: Access the Services
Each `minikube service` command opens a tunnel and must stay open in its own terminal.

**Step 9a – Product Catalog:**
```bash
minikube -p devops-multinode service product-catalog-service
```
![Products in browser](screenshots/12-products-browser.png)

**Step 9b – Shopping Cart:**
```bash
minikube -p devops-multinode service shopping-cart-service
```
```text
| default | shopping-cart-service | 80 | http://192.168.49.2:31985 |
🔗  Starting tunnel for service shopping-cart-service.
| default | shopping-cart-service |    | http://127.0.0.1:37861    |
👉  http://127.0.0.1:37861
```
![Shopping Cart tunnel](screenshots/11-cart-tunnel.png)

### Step 10: Testing with `curl`
Using the tunnel URLs (Product Catalog `127.0.0.1:38745`, Shopping Cart `127.0.0.1:37861`):
```bash
curl http://127.0.0.1:38745/products
curl http://127.0.0.1:37861/cart
curl -X POST http://127.0.0.1:37861/cart -H "Content-Type: application/json" -d '{"id": 1, "name": "Laptop", "quantity": 1}'
```
**Output:**
```text
[{"id":1,"name":"Laptop","price":1200},{"id":2,"name":"Phone","price":800},{"id":3,"name":"Headphones","price":150}]
[]
[{"id":1,"name":"Laptop","quantity":1}]
```
All three responses match the manual's expected responses.

![curl tests](screenshots/13-curl-tests.png)

**Additional observation – cart state is per Pod:** after the POST, three more `GET /cart` requests all returned `[]`. Each Shopping Cart replica keeps its own in-memory `cart` list, and the Service sent the later requests to other replicas. Replicas give availability, but shared state has to live outside the Pods (e.g. a database or Redis).

![Cart not shared between replicas](screenshots/14-cart-not-shared.png)

## 6. Changes from the manual
| Manual | What happened | What was done |
|---|---|---|
| Step 0: `minikube stop`, `minikube delete` | A `devops-multinode` cluster from an earlier run blocked the new start | `minikube delete -p devops-multinode` added |
| Step 1a: `minikube start --nodes 3 -p devops-multinode --force` | With the default containerd runtime, Step 5's `ssh -- docker images` fails (`Cannot connect to the Docker daemon`) | `--container-runtime=docker` added; Step 5 then works as written |
| Step 6: Shopping Cart in `namespace: devops-exercise` | `namespaces "devops-exercise" not found` | Changed to `namespace: default` |

All other commands were run exactly as written in the manual.

## 7. Summary
Two Flask microservices were deployed on a 3-node Minikube cluster with ReplicaSets (2 and 3 replicas). Pod anti-affinity placed every replica of a service on a different node, both services were exposed through NodePort Services, and the `curl` tests returned exactly the manual's expected responses.
