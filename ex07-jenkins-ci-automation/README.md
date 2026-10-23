# Exercise 7: Introduction to Continuous Integration (CI) and Jenkins Installation

## 1. Aim
Understand Continuous Integration and install Jenkins using Docker: run the container, unlock Jenkins with the initial admin password, install the suggested plugins and reach the Jenkins dashboard.

## 2. Environment
| Component | Details |
|---|---|
| Operating system | Windows 11 + WSL2 (Ubuntu 24.04) |
| Container platform | Docker Desktop |
| Jenkins | `jenkins/jenkins:lts` (Jenkins 2.580.1) |

## 3. Theory (from the manual)

### What is Continuous Integration?
Developers integrate code changes into a shared repository frequently. Every integration is automatically built and tested, so problems are found early.

**Key features:** frequent code integration, automated builds, automated testing, immediate feedback.

**Benefits:** early bug detection, better collaboration, faster development, higher code quality.

**How CI works:**
1. **Developer workflow** – a developer pushes code to a Git repository.
2. **CI server workflow** – the CI server detects the change and triggers a build.
3. **Automated build** – the code is compiled and its dependencies resolved.
4. **Automated testing** – tests verify the change.
5. **Feedback** – developers get the build and test results.

**Example CI tools:** GitLab CI/CD, CircleCI, Travis CI, Bamboo, TeamCity, Azure DevOps Pipelines, GitHub Actions, Spinnaker, Buildkite, Drone.

### What is Jenkins?
Jenkins is an open-source automation server for building, testing and deploying software, extended through plugins.

**Key Jenkins concepts:**
1. **Job/Project** – a task or process that Jenkins runs.
2. **Build** – one run of a job: compiling and packaging the code.
3. **Pipeline** – a series of stages to build, test and deploy an application.
4. **Plugins** – extend Jenkins' functionality (e.g. Git plugin, Docker plugin).
5. **Nodes** – machines where Jenkins runs jobs (built-in node / agents).

## 4. Steps (in the order of the manual)

### Step 1: Install Jenkins using Docker
**Command:**
```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 jenkins/jenkins:lts
```
**Output:**
```text
Unable to find image 'jenkins/jenkins:lts' locally
lts: Pulling from jenkins/jenkins
408777b27aa9: Pull complete
...
Digest: sha256:a660310e39ade10631f774bacd5219de767dfd08947ea5c32a739b5e5bb382c1
Status: Downloaded newer image for jenkins/jenkins:lts
55bcea5b01236934d3cfbc33d3e25a4ccbc54fb36ceaa0b2de4d736a6ea59d9d
```
Port **8080** is the web UI; port **50000** is for agent connections.

![Jenkins container started](screenshots/01-jenkins-run.png)

### Step 2: Get the Jenkins initial password
**Commands:**
```bash
docker ps -a
docker exec -it jenkins bash
cat /var/jenkins_home/secrets/initialAdminPassword
```
**Output** (Jenkins line; older stopped containers omitted):
```text
CONTAINER ID   IMAGE                 COMMAND                  CREATED         STATUS         PORTS                                              NAMES
55bcea5b0123   jenkins/jenkins:lts   "/usr/bin/tini -- /u…"   2 minutes ago   Up 2 minutes   0.0.0.0:8080->8080/tcp, 0.0.0.0:50000->50000/tcp   jenkins
```
The `jenkins` container is `Up` with ports 8080 and 50000 mapped.

![Container running](screenshots/02-docker-ps.png)

Inside the container, the initial admin password is printed:

![Initial admin password](screenshots/03-initial-password.png)

### Step 3: Access Jenkins on port 8080
Open `http://localhost:8080/`, paste the initial admin password to unlock Jenkins, choose **Install suggested plugins**, create the first admin user, and click **Save and Finish**.

![Installing suggested plugins](screenshots/05-plugins.png)

The Jenkins dashboard is reached:

![Jenkins dashboard](screenshots/06-jenkins-dashboard.png)

## 5. Issue faced and fix
During **Install suggested plugins**, the downloads of `commons-lang3-api` and `ionicons-api` failed (unstable network from the Docker container). Because many plugins depend on them (Git client, Pipeline, SCM API, GitHub, ...), Manage Jenkins showed **"Some plugins could not be loaded due to unsatisfied dependencies"**:

![Plugin dependency errors](screenshots/07-plugin-dependency-errors.png)

Fix: clicking **Correct** (Jenkins downloaded the missing dependencies) and restarting Jenkins:
```bash
docker restart jenkins
```
The error was gone:

![Errors fixed](screenshots/08-plugins-fixed.png)

The Git plugins are installed and healthy (needed for Exercises 8 and 9):

![Git plugin healthy](screenshots/09-git-plugin.png)

## 6. Changes from the manual
None. All commands were run exactly as written (the manual's `docker exec -it <container-id> bash` was run with the container name `jenkins`, which is equivalent). The plugin download problem above was fixed inside Jenkins with its own **Correct** button.

## 7. Result
Jenkins was installed in Docker, unlocked with the initial admin password and set up with the suggested plugins, and the dashboard at `http://localhost:8080` is ready for creating jobs and pipelines (used in Exercises 8 and 9).
