# Exercise 6: Real-Time Operations Monitoring and Alerting (Prometheus + Grafana + Jenkins)

## Aim
Simulate delivery metrics of a quick-commerce delivery service (ZAPPTTO) with Python, scrape them with Prometheus, raise alerts on threshold breaches, visualise them in Grafana and automate the setup with a Jenkins pipeline.

## Environment
Windows 11 + WSL2 (Ubuntu 24.04) + Docker Desktop, Python 3.12, prometheus-client 0.19, Prometheus, Grafana, Jenkins 2.580.1

## Files (`delivery_monitoring/`)
- `delivery_metrics.py` – exposes `total_deliveries`, `pending_deliveries`, `on_the_way_deliveries` (Gauges) and `average_delivery_time` (Summary) on port 8000
- `prometheus.yml` – scrape config (prometheus + delivery_service) and rule file
- `alert_rules.yml` – `HighPendingDeliveries` (> 10 for 15s) and `HighAverageDeliveryTime` (> 30)
- `grafana-dashboard.json` – dashboard with the 4 panels required by the manual
- `Jenkinsfile.manual` – the manual's pipeline, unchanged
- `Jenkinsfile` – the adapted pipeline that runs successfully (see below)
- `Dockerfile` – image for `delivery_metrics` (not provided by the manual)

## Steps (as per the manual)
1. `pip3 install prometheus-client`; create and run `delivery_metrics.py`; check `http://localhost:8000/metrics`
2. Create `prometheus.yml` and `alert_rules.yml`; run Prometheus in Docker; check Status → Targets and Alerts
3. Run Grafana (`docker run -d --name grafana -p 3000:3000 grafana/grafana`); log in; add Prometheus data source `http://172.17.0.1:9090` exactly as in the manual (Save & test succeeded). Grafana reaches Prometheus on the bridge IP `172.17.0.1` because Prometheus runs in Docker with port 9090 published; only the scrape target for the Python script, which runs outside Docker, needed `host.docker.internal` (see the table below)
4. Dashboard with Total, Pending, On-the-Way Deliveries and Average Delivery Time panels
5. Jenkins: check the container; create the Jenkinsfile; New Item → Pipeline → Pipeline script; run
6. Simulate alerts: `pending = random.randint(50, 100)`; restart the script and Prometheus; alerts FIRING

## Deviations from the manual (each one was run as written first)
| Step | What happened | Fix |
|---|---|---|
| `pip3 install prometheus-client` | `externally-managed-environment` (Ubuntu 24.04) | `sudo apt install python3-prometheus-client` (the fix suggested by the error) |
| File names | Manual mentions `alerts_rules.yml` and `prometheus.ym` | Used `alert_rules.yml` / `prometheus.yml`, as in the manual's `docker run` command |
| Prometheus `--network=host` | `localhost:9090` not reachable from the browser (Docker Desktop keeps host-network containers inside its VM) | `-p 9090:9090`, as in the manual's own Jenkinsfile |
| Target `172.17.0.1:8000` | `delivery_service` DOWN: `connection refused` | `host.docker.internal:8000`, as the manual's note recommends for Windows |
| Grafana first login | Password was changed instead of skipped | No effect on the exercise |
| Grafana dashboard | Panels created via Dashboard → Import (JSON) | Same 4 panels and queries as the manual |
| Jenkins `Exited` | Manual suggests `docker rm` and a fresh instance | `docker start jenkins`, to keep the Exercise 7–9 setup |

## Jenkins pipeline: the manual Jenkinsfile run unchanged
The manual's Jenkinsfile was run unchanged. It stopped at **Pre-check Docker** with `docker: not found` (exit code 127) and the remaining stages were skipped. The pipeline cannot run as written because:
1. The `jenkins/jenkins:lts` container has no Docker CLI or Docker socket (the pre-check is designed to catch exactly this)
2. `localSourcePath` is a placeholder (`/path/to/your/local/files`)
3. No Dockerfile for `delivery_metrics` is provided, so `docker build` would have nothing to build
4. Containers named `prometheus` and `grafana` already exist, so `docker run --name` would conflict
The same services were therefore first run manually (steps 1–3). The pipeline was then made to run with 4 small changes: see "Pipeline made to run successfully" below (build #3 `Finished: SUCCESS`).

## Screenshots
1. pip blocked: ![](screenshots/01-pip-error.png)
2. prometheus-client via apt: ![](screenshots/02-apt-install.png)
3. Metrics app running: ![](screenshots/03-metrics-running.png)
4. /metrics endpoint: ![](screenshots/04-metrics-page.png)
5. prometheus.yml: ![](screenshots/05-prometheus-yml.png)
6. Prometheus started (--network=host): ![](screenshots/06-prometheus-run.png)
7. Prometheus container Up: ![](screenshots/07-prometheus-up.png)
8. localhost:9090 unreachable with host network: ![](screenshots/08-host-network-fails.png)
9. Prometheus UI with -p 9090:9090: ![](screenshots/09-prometheus-ui.png)
10. delivery_service DOWN at 172.17.0.1: ![](screenshots/10-targets-down.png)
11. Target changed to host.docker.internal: ![](screenshots/11-target-fix.png)
12. Both targets UP: ![](screenshots/12-targets-up.png)
13. Alerts (normal values): ![](screenshots/13-alerts.png)
14. Grafana started: ![](screenshots/14-grafana-run.png)
15. Grafana home: ![](screenshots/15-grafana-home.png)
16. Prometheus data source OK: ![](screenshots/16-datasource-ok.png)
17. Delivery Monitoring dashboard: ![](screenshots/17-grafana-dashboard.png)
19. Alerts FIRING: ![](screenshots/19-alert-firing.png)
20. Jenkins container started: ![](screenshots/21-jenkins-status.png)
21. Jenkinsfile: ![](screenshots/22-jenkinsfile.png)
22. Pipeline stops at Pre-check Docker: ![](screenshots/23-jenkins-precheck-failed.png)

## Result
Delivery metrics were exposed on `/metrics`, scraped by Prometheus, visualised live on a 4-panel Grafana dashboard, and the alert rules fired (`HighPendingDeliveries`, `HighAverageDeliveryTime`) when pending deliveries were raised to 50–100. The manual Jenkinsfile was first run unchanged and its failure point documented; with 4 documented changes the Jenkins pipeline then finished with `SUCCESS` (build #3) and started the whole stack.

## Pipeline made to run successfully (build #3)
The manual's Expected Output 4 is *"Jenkins Logs: Successful pipeline build with logs for Docker commands"*. To achieve it:

**Jenkins setup** (Jenkins data preserved: container committed to an image and the same `jenkins_home` volume re-attached)
- Jenkins re-created with the Docker socket mounted: `-v /var/run/docker.sock:/var/run/docker.sock`
- Docker CLI installed inside Jenkins (`apt-get install docker-cli`), socket made accessible (`chmod 666 /var/run/docker.sock`)
- Source files copied into the Jenkins container at `/delivery_monitoring`

**Jenkinsfile changes** (`Jenkinsfile.manual` → `Jenkinsfile`)
| Stage | Manual | Change | Reason |
|---|---|---|---|
| Setup Workspace | `localSourcePath = '/path/to/your/local/files' // Replace with your actual path` | `'/delivery_monitoring'` | Placeholder the manual asks to replace |
| Setup Workspace | – | Also copy `Dockerfile` | Manual provides no Dockerfile for `delivery_metrics` |
| Build Docker Image | `docker build -t delivery_metrics .` | `--network=host` | pip could not reach PyPI from the default build network |
| Run Prometheus & Grafana | `docker run -v $WORKSPACE/...` | `docker create` + `docker cp` + `docker start` | `$WORKSPACE` paths exist inside the Jenkins container, not on the Docker host, so bind mounts cannot work |

**Result:** build #3 `Finished: SUCCESS`; the pipeline started `delivery_metrics`, Prometheus and Grafana, and both Prometheus targets were UP.

24. Jenkins re-created, all jobs preserved: ![](screenshots/24-jenkins-recreated.png)
25. Jenkins can run Docker: ![](screenshots/25-jenkins-docker-access.png)
26. Adapted Prometheus stage: ![](screenshots/26-jenkinsfile-changes.png)
27. Pipeline build #3 SUCCESS: ![](screenshots/27-pipeline-success.png)
28. Targets UP (stack started by Jenkins): ![](screenshots/28-pipeline-targets-up.png)
