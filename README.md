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
| 2 | `minikube start --container-runtime=docker` | Minikube v1.39.0 defaults to containerd, where the manual's `eval $(minikube docker-env)` + `docker build` fails (`404 page not found`); with the Docker runtime every other command runs as written |
| 3 | Dockerfile copies `app.py` instead of `ex3-flash-sale.py`; `minikube start --container-runtime=docker`; image built inside Minikube as `flashsale:1.0` (the manual's `flask-app` tag was also built); `flashsale-rs` used instead of `flask-app-rs` | gunicorn runs `app:app` (`ModuleNotFoundError`); docker-env build needs the Docker runtime (as in Ex 2); the YAML uses `flashsale:1.0` and creates `flashsale-rs` (`NotFound`) |
| 4 | Followed the detailed walkthrough linked from the exercise (Google Doc): `host='0.0.0.0'`, `Werkzeug==2.0.3`, MySQL with `rootpass` and `devopsdb`, `ping` installed inside the container, extra checks (`curl`, `getent`, `redis-cli`, `SHOW DATABASES`) | The short manual page's version fails: MySQL exits without a password, Flask 2.0.1 crashes with newer Werkzeug (`url_quote`), `python:3.9-slim` has no `ping` |
| 5 | AppArmor profile is accepted but not enforced | The WSL2 kernel has AppArmor disabled |
| 6 | `prometheus-client` from apt; Prometheus run with `-p 9090:9090`; target `host.docker.internal:8000`; Jenkins restarted with `docker start` instead of `docker rm` + fresh instance; Jenkinsfile: 3 documented changes | `pip3` gives `externally-managed-environment` on Ubuntu 24.04; host networking does not publish ports on Docker Desktop; `172.17.0.1` is refused on Docker Desktop; keeps the Exercise 7–9 setup; placeholder path, missing Dockerfile and bind mounts in the Jenkinsfile |
| 7 | None | - |
| 8 | Branch `main` (`git branch -M main`) and Branch Specifier `*/main` | The manual pushes to `main`, but Git creates `master` by default |
| 9 | Files added to the existing `devops-sample-code` clone; Branch Specifier `*/main`; apt sources switched to https inside Jenkins; `python3.11-venv` cannot be installed | The repository already has the Exercise 8 commit; the branch is `main`; plain http is blocked on this network; the Jenkins image ships Python 3.13 |
| 10 | `minikube delete -p devops-multinode` added to Step 0; `minikube start ... --container-runtime=docker`; Shopping Cart `namespace: default` | An old cluster blocked the start; `ssh -- docker images` fails on the default containerd runtime; the `devops-exercise` namespace is never created |
