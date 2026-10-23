# DevOps Lab - Mridani R Achar (1BM23IS145)

B.M.S. College of Engineering, Information Science and Engineering - DevOps Lab coursework.
All exercises follow the DevOps Lab Manual (SunagP/DevOps-Lab). Each folder contains the code, screenshots and a README with steps, results and any deviations from the manual (each change is explained, with a screenshot of the manual version failing where it fails; see the summary table at the bottom).

**Environment:** Windows 11 + WSL2 (Ubuntu 24.04) + Docker Desktop, Minikube v1.39.0, Kubernetes v1.37.0, Jenkins 2.580.1

| # | Exercise | Folder |
|---|---|---|
| 1 | Kubernetes Getting Started (nginx Pod + NodePort Service) | [ex01-kubernetes-getting-started](ex01-kubernetes-getting-started/) |
| 2 | Deploy a Flask app on Minikube using kubectl and YAML | [ex02-minikube-kubectl-flask](ex02-minikube-kubectl-flask/) |
| 3 | Scaling a Flask app with ReplicaSets | [ex03-minikube-scaling-replicasets](ex03-minikube-scaling-replicasets/) |
| 4 | Docker Networking with multiple containers | [ex04-docker-networking](ex04-docker-networking/) |
| 5 | Docker Security with AppArmor and Python | [ex05-docker-security-apparmor](ex05-docker-security-apparmor/) |
| 6 | Real-time monitoring with Prometheus, Grafana and Jenkins | [ex06-grafana-prometheus-monitoring](ex06-grafana-prometheus-monitoring/) |
| 7 | CI and Jenkins installation | [ex07-jenkins-ci-automation](ex07-jenkins-ci-automation/) |
| 8 | Jenkins "Hello World" job | [ex08-jenkins-hello-world-job](ex08-jenkins-hello-world-job/) |
| 9 | Jenkins multi-stage pipeline | [ex09-jenkins-multistage-pipeline](ex09-jenkins-multistage-pipeline/) |
| 10 | Multi-node Minikube with multiple apps | [ex10-minikube-multinode-multiapp](ex10-minikube-multinode-multiapp/) |

## Second repository (Exercises 8 and 9)
As instructed in the manual (Exercise 8, Step 1a: *"Repository Name: devops-sample-code"*), the code that Jenkins pulls is in a separate repository: https://github.com/mridanirachar/devops-sample-code
Copies of those files are also included in the `ex08` and `ex09` folders here.

## Changes from the manual (summary)
Each change is explained in the README of that exercise, with a screenshot of the manual version failing where it fails.

| Ex | Change from the manual | Reason |
|---|---|---|
| 1 | None | - |
| 2 | Image copied into Minikube with `minikube image load` instead of building after `eval $(minikube docker-env)` | This cluster uses the containerd runtime, so the docker-env build fails (`404 page not found`). Starting Minikube with `--container-runtime=docker` would allow the manual step. |
| 3 | Dockerfile copies `app.py` instead of `ex3-flash-sale.py`; `flashsale-rs` used instead of `flask-app-rs`; image loaded with `minikube image load` | gunicorn runs `app:app` (`ModuleNotFoundError`); the YAML creates `flashsale-rs` (`NotFound`); containerd as in Ex 2 |
| 4 | Followed the detailed walkthrough linked from the exercise (Google Doc): `host='0.0.0.0'`, `Werkzeug==2.0.3`, MySQL with `rootpass` and `devopsdb`, `ping` installed inside the container, extra checks (`curl`, `getent`, `redis-cli`, `SHOW DATABASES`) | The short manual page's version fails: MySQL exits without a password, Flask 2.0.1 crashes with newer Werkzeug (`url_quote`), `python:3.9-slim` has no `ping` |
| 5 | AppArmor profile is accepted but not enforced | The WSL2 kernel has AppArmor disabled |
| 6 | `prometheus-client` from apt; Prometheus target `host.docker.internal:8000`; Prometheus run with `-p 9090:9090`; Jenkinsfile: 4 documented changes | `pip3` gives `externally-managed-environment` on Ubuntu 24.04; `172.17.0.1` is refused on Docker Desktop; host networking does not publish ports on Docker Desktop; placeholder path, missing Dockerfile, network and bind mounts in the Jenkinsfile |
| 7 | None | - |
| 8 | Branch `main` (`git branch -M main`) and Branch Specifier `*/main` | The manual pushes to `main`, but Git creates `master` by default |
| 9 | apt sources switched to https inside Jenkins; `python3.11-venv` cannot be installed | Plain http is blocked on this network; the Jenkins image ships Python 3.13 |
| 10 | Shopping Cart `namespace: default`; images checked with `minikube image ls`; `docker build --network=host` | The `devops-exercise` namespace is never created; `ssh -- docker images` fails on containerd; pip timed out during the build |
