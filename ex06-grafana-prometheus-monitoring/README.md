# Exercise 6: Real-Time Operations Monitoring and Alerting (Prometheus + Grafana + Jenkins)

## 1. Objective (from the manual)
As a DevOps engineer at ZAPPTTO, a fast-paced delivery service, build a monitoring application that gives real-time insight into delivery performance: simulate delivery metrics with Python, scrape them with Prometheus, raise automated alerts, visualise them on a Grafana dashboard, and automate the setup with a Jenkins pipeline.

## 2. Environment
| Component | Details |
|---|---|
| Operating system | Windows 11 + WSL2 (Ubuntu 24.04) |
| Container platform | Docker Desktop |
| Python | 3.12, `prometheus-client` |
| Monitoring | Prometheus (`prom/prometheus`), Grafana (`grafana/grafana`) |
| CI | Jenkins 2.580.1 (`jenkins/jenkins:lts`) |

## 3. Code directory structure (`delivery_monitoring/`)
Created as in the manual (`mkdir delivery_monitoring`, `cd delivery_monitoring`):

| File | Purpose |
|---|---|
| `delivery_metrics.py` | Exposes `total_deliveries`, `pending_deliveries`, `on_the_way_deliveries` (Gauges) and `average_delivery_time` (Summary) on port 8000 – identical to the manual |
| `prometheus.yml` | Scrape config (`prometheus` + `delivery_service`) and rule file |
| `alert_rules.yml` | `HighPendingDeliveries` (> 10 for 15s) and `HighAverageDeliveryTime` (> 30) – identical to the manual |
| `Jenkinsfile.manual` | The manual's pipeline, unchanged |
| `Jenkinsfile` | The pipeline with the 4 changes needed to run (Step 5) |
| `Dockerfile` | Image for `delivery_metrics`, needed by the pipeline (not provided by the manual) |
| `grafana-dashboard.json` | Export of the 4-panel dashboard from Step 4 |

## 4. Steps (in the order of the manual)

### 2a. Install packages
```bash
pip3 install prometheus-client
```
On Ubuntu 24.04 this is blocked:
```text
error: externally-managed-environment
× This environment is externally managed
╰─> To install Python packages system-wide, try apt install python3-xyz ...
```
![pip blocked](screenshots/01-pip-error.png)

The package was installed the way the error message suggests:
```bash
sudo apt install python3-prometheus-client
```
![prometheus-client installed with apt](screenshots/02-apt-install.png)

### Step 1: Write and run the Python application
`delivery_metrics.py` (identical to the manual) defines the four metrics and updates them every second:
```python
from prometheus_client import start_http_server, Summary, Gauge
import random
import time

# Metrics
total_deliveries = Gauge("total_deliveries", "Total number of deliveries")
pending_deliveries = Gauge("pending_deliveries", "Number of pending deliveries")
on_the_way_deliveries = Gauge("on_the_way_deliveries", "Number of deliveries on the way")
average_delivery_time = Summary("average_delivery_time", "Average delivery time in seconds")
...
```
```bash
python3 delivery_metrics.py
```
**Output:**
```text
[INFO] Starting the HTTP server on port 8000...
[INFO] HTTP server started. Simulating deliveries...
[DEBUG] Total deliveries: 97
[DEBUG] Pending deliveries: 20
[DEBUG] On-the-way deliveries: 12
[DEBUG] Average delivery time: 22.67 seconds
[INFO] Sleeping for 1 seconds...
```
![Metrics app running](screenshots/03-metrics-running.png)

**Expected output 1 – metrics endpoint** `http://localhost:8000/metrics` (opened in the browser; the manual's `curl http://localhost:8000/metrics` returns the same text):
```text
# TYPE total_deliveries gauge
total_deliveries 83.0
# TYPE pending_deliveries gauge
pending_deliveries 11.0
# TYPE on_the_way_deliveries gauge
on_the_way_deliveries 6.0
# TYPE average_delivery_time summary
average_delivery_time_count 93.0
average_delivery_time_sum 2726.354273546113
```
![/metrics endpoint](screenshots/04-metrics-page.png)

### Step 2a: Configure Prometheus
`prometheus.yml`:
```yaml
scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "delivery_service"
    static_configs:
      - targets: ["host.docker.internal:8000"]

rule_files:
  - /etc/prometheus/alert_rules.yml
```
![prometheus.yml](screenshots/05-prometheus-yml.png)

### Step 2a: Configure alerts
`alert_rules.yml` (identical to the manual):
```yaml
groups:
  - name: delivery_alerts
    rules:
      - alert: HighPendingDeliveries
        expr: pending_deliveries > 10
        for: 15s
        labels:
          severity: warning
        annotations:
          summary: "High pending deliveries"
          description: "Pending deliveries are above 10 for the last 15 second."

      - alert: HighAverageDeliveryTime
        expr:  (average_delivery_time_sum / average_delivery_time_count) > 30
        labels:
          severity: critical
        annotations:
          summary: "High average delivery time"
          description: "Average delivery time is above 30 seconds for the last 15 seconds."
```

### Run Prometheus
**Manual command, run exactly as written:**
```bash
docker run -d --name prometheus --network=host -v ./prometheus.yml:/etc/prometheus/prometheus.yml -v ./alert_rules.yml:/etc/prometheus/alert_rules.yml prom/prometheus
docker ps -a | grep prom
```
The container starts and is `Up`:

![Prometheus started with --network=host](screenshots/06-prometheus-run.png)
![Prometheus container Up](screenshots/07-prometheus-up.png)

But `http://localhost:9090` cannot be opened, because Docker Desktop keeps host-network containers inside its own VM:

![localhost:9090 unreachable](screenshots/08-host-network-fails.png)

Prometheus was therefore restarted with `-p 9090:9090` instead of `--network=host` (the same port mapping the manual's own Jenkinsfile uses), and the UI opens:

![Prometheus UI](screenshots/09-prometheus-ui.png)

**Verify targets (Status → Targets).** With the manual's Linux/WSL target `172.17.0.1:8000`, the `delivery_service` target is DOWN:
```text
delivery_service   http://172.17.0.1:8000/metrics   DOWN
Error scraping target: Get "http://172.17.0.1:8000/metrics": dial tcp 172.17.0.1:8000: connect: connection refused
```
![delivery_service DOWN](screenshots/10-targets-down.png)

The manual's note says `host.docker.internal` reaches the host machine from a container on Docker Desktop, so the target was changed to `host.docker.internal:8000`:
```bash
sed -i 's/172.17.0.1:8000/host.docker.internal:8000/' prometheus.yml
grep targets prometheus.yml
```

![Target changed](screenshots/11-target-fix.png)

Both targets are now **UP**:

![Both targets UP](screenshots/12-targets-up.png)

**Alerts page with normal values (Step 3d: verify targets and alerts):** `HighPendingDeliveries` (`pending_deliveries > 10`, `for: 15s`) is already PENDING with value 11, and `HighAverageDeliveryTime` is inactive:

![Alerts with normal values](screenshots/13-alerts.png)

### Step 3: Set up Grafana
```bash
docker run -d --name grafana -p 3000:3000 grafana/grafana
```
![Grafana started](screenshots/14-grafana-run.png)

**Step 3a/3b:** open `http://localhost:3000` and log in with `admin` / `admin` (the new password was set instead of skipped – no effect on the exercise):

![Grafana home](screenshots/15-grafana-home.png)

**Step 3c: Add Prometheus as a data source** – Connections → Data sources → Prometheus, URL `http://172.17.0.1:9090` exactly as in the manual, **Save & test** succeeded. Grafana reaches Prometheus on the bridge IP `172.17.0.1` because Prometheus runs in Docker with port 9090 published; only the scrape target for the Python script, which runs outside Docker, needed `host.docker.internal`.

![Data source OK](screenshots/16-datasource-ok.png)

### Step 4: Create the dashboard
A dashboard **Delivery Monitoring** with the four panels of the manual (created by importing `grafana-dashboard.json`, which contains exactly these queries):

| Panel | Query |
|---|---|
| Total Deliveries | `total_deliveries` |
| Pending Deliveries | `pending_deliveries` |
| On-the-Way Deliveries | `on_the_way_deliveries` |
| Average Delivery Time | `average_delivery_time_sum / average_delivery_time_count` |

**Expected output 3 – Grafana dashboard:**

![Delivery Monitoring dashboard](screenshots/17-grafana-dashboard.png)

### Step 5: Create the Jenkins pipeline
**Step 5a – check the Jenkins container:** Jenkins from Exercises 7–9 had exited. Instead of `docker rm` and a fresh instance (which the manual allows), it was started again so that the Exercise 7–9 jobs stay intact:

![Jenkins container started](screenshots/21-jenkins-status.png)

**Step 5b – create the `Jenkinsfile`** (the manual's file, saved as `Jenkinsfile.manual`) and run it as a Pipeline job (New Item → Pipeline → Pipeline script):

![Jenkinsfile](screenshots/22-jenkinsfile.png)

**Build #2 – the manual's Jenkinsfile, unchanged:** it stops at the **Pre-check Docker** stage and the remaining stages are skipped:
```text
+ docker --version
.../script.sh.copy: 1: docker: not found
Stage "Setup Workspace" skipped due to earlier failure(s)
Stage "Build Docker Image" skipped due to earlier failure(s)
Stage "Run Application" skipped due to earlier failure(s)
Stage "Run Prometheus & Grafana" skipped due to earlier failure(s)
ERROR: Pre-check failed: script returned exit code 127
Finished: FAILURE
```
![Pipeline stops at Pre-check Docker](screenshots/23-jenkins-precheck-failed.png)

The manual's pipeline cannot run as written because:
1. The `jenkins/jenkins:lts` container has no Docker CLI and no access to the Docker socket (the pre-check exists to catch exactly this).
2. `localSourcePath` is a placeholder (`/path/to/your/local/files`).
3. No Dockerfile for `delivery_metrics` is provided, so `docker build` has nothing to build.
4. `-v $WORKSPACE/...` bind mounts do not work: the paths exist inside the Jenkins container, not on the Docker host.

**Making the pipeline run (Expected output 4: "Successful pipeline build with logs for Docker commands").**

Jenkins setup (data preserved: the container was committed to an image and the same `jenkins_home` volume re-attached):
- Jenkins re-created with the Docker socket mounted: `-v /var/run/docker.sock:/var/run/docker.sock`
- Docker CLI installed inside Jenkins (`apt-get install docker-cli`), socket made accessible (`chmod 666 /var/run/docker.sock`)
- Source files copied into the Jenkins container at `/delivery_monitoring`

![Jenkins re-created, jobs preserved](screenshots/24-jenkins-recreated.png)
![Jenkins can run Docker](screenshots/25-jenkins-docker-access.png)

Jenkinsfile changes (`Jenkinsfile.manual` → `Jenkinsfile`):

| Stage | Manual | Change | Reason |
|---|---|---|---|
| Setup Workspace | `localSourcePath = '/path/to/your/local/files' // Replace with your actual path` | `'/delivery_monitoring'` | Placeholder the manual asks to replace |
| Setup Workspace | – | Also copy `Dockerfile` | The manual provides no Dockerfile for `delivery_metrics` |
| Build Docker Image | `docker build -t delivery_metrics .` | `--network=host` | pip could not reach PyPI from the default build network |
| Run Prometheus & Grafana | `docker run -v $WORKSPACE/...` | `docker create` + `docker cp` + `docker start` | `$WORKSPACE` paths exist inside the Jenkins container, not on the Docker host |

![Adapted Prometheus stage](screenshots/26-jenkinsfile-changes.png)

**Build #3 – `Finished: SUCCESS`:**
```text
+ docker run -d -p 8000:8000 --name delivery_metrics delivery_metrics
+ docker create --name prometheus -p 9090:9090 prom/prometheus
+ docker cp /var/jenkins_home/workspace/Delivery-Monitoring-Pipeline/prometheus.yml prometheus:/etc/prometheus/prometheus.yml
+ docker cp /var/jenkins_home/workspace/Delivery-Monitoring-Pipeline/alert_rules.yml prometheus:/etc/prometheus/alert_rules.yml
+ docker start prometheus
+ docker run -d --name grafana -p 3000:3000 grafana/grafana
[Pipeline] End of Pipeline
Finished: SUCCESS
```
![Pipeline build #3 SUCCESS](screenshots/27-pipeline-success.png)

The stack started by Jenkins is scraped successfully – both targets UP:

![Targets UP (stack started by Jenkins)](screenshots/28-pipeline-targets-up.png)

### Step 6: Simulate alerts
`delivery_metrics.py` was changed as the manual says:
```python
pending = random.randint(50, 100)  # Increase range to exceed alert threshold
```
After restarting the script and Prometheus, **Expected output 5 – Prometheus alerts:** both rules of `delivery_alerts` are **FIRING**:
```text
delivery_alerts   /etc/prometheus/alert_rules.yml   FIRING (2)
  HighPendingDeliveries     FIRING (1)
  HighAverageDeliveryTime   FIRING (1)
```
![Alerts FIRING](screenshots/19-alert-firing.png)

The file in this repo was set back to `randint(10, 20)` afterwards, to match Step 1.

## 5. Changes from the manual
| Manual | What happened | What was done |
|---|---|---|
| `pip3 install prometheus-client` | `externally-managed-environment` (Ubuntu 24.04) | `sudo apt install python3-prometheus-client` (the fix the error suggests) |
| File names `alerts_rules.yml`, `prometheus.ym` in the text | – | `alert_rules.yml` / `prometheus.yml`, as in the manual's `docker run` command |
| Prometheus `--network=host` | `localhost:9090` not reachable (Docker Desktop VM) | `-p 9090:9090`, as in the manual's own Jenkinsfile |
| Target `172.17.0.1:8000` | `delivery_service` DOWN: `connection refused` | `host.docker.internal:8000`, as the manual's note recommends |
| Grafana: skip password update | Password was changed instead | No effect on the exercise |
| Grafana panels | Created by importing a JSON dashboard | Same 4 panels and queries as the manual |
| Jenkins exited: `docker rm` + fresh instance | – | `docker start jenkins`, to keep the Exercise 7–9 setup |
| Jenkinsfile | Build #2 fails at Pre-check Docker | 4 documented changes → build #3 `SUCCESS` |

## 6. Expected outputs (from the manual)
| # | Expected output | Achieved |
|---|---|---|
| 1 | Metrics endpoint `http://localhost:8000/metrics` | ✅ Step 1 |
| 2 | Prometheus query: graphs for `total_deliveries`, `pending_deliveries` and `average_delivery_time` | Partly: both targets UP and the metrics are graphed in Grafana (Step 4); no Prometheus Graph-tab screenshot |
| 3 | Grafana dashboard with delivery metrics | ✅ Step 4 |
| 4 | Jenkins: successful pipeline build with logs for Docker commands | ✅ Build #3 `Finished: SUCCESS` |
| 5 | Prometheus alerts for high pending deliveries | ✅ Step 6 (`HighPendingDeliveries` FIRING) |

## 7. Result
Delivery metrics were exposed on `/metrics`, scraped by Prometheus, visualised live on a 4-panel Grafana dashboard, and the alert rules fired when pending deliveries were raised to 50–100. The manual's Jenkinsfile was first run unchanged and its failure point documented; with 4 documented changes the Jenkins pipeline then finished with `SUCCESS` (build #3) and started the whole stack.
