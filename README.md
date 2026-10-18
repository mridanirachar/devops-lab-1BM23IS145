# DevOps Lab - Mridani R Achar (1BM23IS145)

B.M.S. College of Engineering, Information Science and Engineering - DevOps Lab coursework.
All exercises follow the DevOps Lab Manual (SunagP/DevOps-Lab). Each folder contains the code, screenshots and a README with steps, results and any deviations from the manual (each deviation was first run as written, and the failure is shown as evidence).

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

## Known environment limitations (documented with evidence in each README)
- **Exercise 5:** the WSL2 kernel has AppArmor disabled, so the profile is accepted but not enforced.
- **Exercise 6:** the manual's Jenkins pipeline stops at "Pre-check Docker" because the Jenkins container has no Docker; the services were run manually instead.
