# Exercise 4: Docker Networking with Multiple Containers

## 1. Aim
Understand Docker networking concepts and configure a multi-container application whose containers communicate with each other by name over a user-defined bridge network.

## 2. Scenario (from the manual)
A web application made of three containers:
- a Python **Flask** web server (container 1)
- a **MySQL** database (container 2)
- a **Redis** cache (container 3)

## 3. Environment
| Component | Details |
|---|---|
| Operating system | Windows 11 + WSL2 (Ubuntu 24.04) |
| Container platform | Docker Desktop |
| Images | `python:3.9-slim`, `mysql:latest`, `redis:latest` |

## 4. Files in this folder
| File | Purpose |
|---|---|
| `app.py` | Flask REST API with an `/about` endpoint on port 5001 – identical to the manual |
| `requirements.txt` | `Flask==2.0.1` plus `Werkzeug==2.0.3` (see Section 6) |
| `Dockerfile` | Builds the `flask-api` image – identical to the manual |
| `manual-original/` | The manual's unmodified files, kept to show why they fail |

## 5. Tasks (in the order of the manual)

### Task 1: Create a bridge network
```bash
docker network create --driver bridge my-bridge-net
```

### Task 2: Verify the network
```bash
docker network ls
```
`my-bridge-net` is listed with the `bridge` driver.

### Task 3: Inspect the network
```bash
docker network inspect my-bridge-net
```
The network gets its own subnet; in the ping test below the containers receive the addresses `172.18.0.2` (mysql) and `172.18.0.3` (redis) from it.

### Task 4: Launch the containers
`app.py` (identical to the manual):
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/about', methods=['GET'])
def about():
    return jsonify({
        "name": "Simple REST API",
        "version": "1.0",
        "description": "This is a simple REST API built with Flask."
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Specify the port number here
```
`requirements.txt`:
```text
Flask==2.0.1
Werkzeug==2.0.3
```
`Dockerfile` (identical to the manual):
```dockerfile
# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and app code to the container
COPY requirements.txt .
COPY app.py .

# Install Flask (and any other dependencies you might have)
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5001

# Define the command to run the application
CMD ["python", "app.py"]
```

**Build the Flask image:**
```bash
docker build -t flask-api .
```
(`--network=host` was added on this machine only because pip could not reach PyPI from the default build network.)
```text
[+] Building 2.3s (10/10) FINISHED
 => [5/5] RUN pip install --no-cache-dir -r requirements.txt
 => => naming to docker.io/library/flask-api:latest
```
![Image built](screenshots/01-build.png)

**Launch the containers:**
```bash
docker run -d --name mysql --net=my-bridge-net -e MYSQL_ROOT_PASSWORD=root mysql:latest
docker run -d --name redis --net=my-bridge-net redis:latest
docker run -d --name flask --net=my-bridge-net -p 5001:5001 flask-api
docker ps
```
All three containers are `Up` on the network (the same `docker ps` listing appears at the top of the clean-up screenshot in Task 6):
```text
IMAGE          COMMAND                  STATUS         PORTS                    NAMES
flask-api      "python app.py"          Up 3 minutes   0.0.0.0:5001->5001/tcp   flask
redis:latest   "docker-entrypoint.s…"   Up 3 minutes   6379/tcp                 redis
mysql:latest   "docker-entrypoint.s…"   Up 3 minutes   3306/tcp, 33060/tcp      mysql
```

### Task 5: Test connectivity
Exec into the Flask container:
```bash
docker exec -it flask bash
```
`python:3.9-slim` does not contain `ping`, so it is installed inside the running container first (the Dockerfile stays as in the manual):
```bash
apt-get update && apt-get install -y iputils-ping
```
Ping the MySQL and Redis containers by name:
```bash
ping -c 4 mysql
ping -c 4 redis
```
**Output:**
```text
--- mysql ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3023ms
PING redis (172.18.0.3) 56(84) bytes of data.
64 bytes from redis.my-bridge-net (172.18.0.3): icmp_seq=1 ttl=64 time=0.251 ms
64 bytes from redis.my-bridge-net (172.18.0.3): icmp_seq=2 ttl=64 time=0.309 ms
64 bytes from redis.my-bridge-net (172.18.0.3): icmp_seq=3 ttl=64 time=0.122 ms
64 bytes from redis.my-bridge-net (172.18.0.3): icmp_seq=4 ttl=64 time=0.138 ms
--- redis ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3028ms
```
Both names resolve through Docker's built-in DNS (`mysql.my-bridge-net`, `redis.my-bridge-net`) with **0% packet loss** – the containers communicate by name over the bridge network.

![Ping test](screenshots/02-ping.png)

### Task 6: Clean up
```bash
docker stop mysql redis flask && docker rm mysql redis flask
docker network rm my-bridge-net
```
**Output:**
```text
mysql
redis
flask
my-bridge-net
```
![Cleanup](screenshots/04-cleanup.png)

## 6. Changes from the manual
The manual's files (in `manual-original/`) were first built and run exactly as written:

| Manual | What happened | What was done |
|---|---|---|
| `docker build` with the manual's Dockerfile | Builds successfully | – (Dockerfile kept as in the manual) |
| `docker run -d --name mysql --net=my-bridge-net mysql:latest` | MySQL exits: `Database is uninitialized and password option is not specified` | Added `-e MYSQL_ROOT_PASSWORD=root` |
| Flask container with only `Flask==2.0.1` | Exits: `ImportError: cannot import name 'url_quote' from 'werkzeug.urls'` (newer Werkzeug is incompatible) | Pinned `Werkzeug==2.0.3` in `requirements.txt` |
| `ping mysql` in the Flask image | `exec: "ping": executable file not found in $PATH` | Installed `iputils-ping` inside the running container |

![Manual Dockerfile builds](screenshots/05-manual-build.png)
![MySQL exits without a password](screenshots/06-manual-mysql-exits.png)
![Flask crashes without the Werkzeug pin](screenshots/07-manual-flask-crash.png)
![No ping in the image](screenshots/08-manual-no-ping.png)

## 7. Questions
1. **What is the purpose of the `--net` flag in `docker run`?** It connects the container to a specific Docker network.
2. **How do containers communicate with each other on the same network?** Docker's built-in DNS resolves container names to their IPs on a user-defined network, so containers reach each other by name (here `mysql` → `172.18.0.2`, `redis` → `172.18.0.3`).
3. **What is the difference between a bridge network and a host network?** A bridge network gives containers an isolated private network with their own IPs; a host network shares the host machine's network stack directly, without isolation.
4. **How can you expose a container's port to the host machine?** With `-p host_port:container_port`, e.g. `-p 5001:5001`.

## 8. Result
The Flask, MySQL and Redis containers ran on the user-defined bridge network `my-bridge-net`, and the Flask container reached both other containers by name with 0% packet loss – the manual's expected result.
