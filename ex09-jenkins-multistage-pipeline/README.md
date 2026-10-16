# Exercise 9: Jenkins Multi-Stage Pipeline (Python Flask App)

## Aim
Create a Jenkins Pipeline that checks out a Python Flask app from GitHub and runs the stages Build, Test, Deploy, Run Application and Test Application, defined in a Jenkinsfile.

## Environment
Jenkins 2.580.1 in Docker (Debian trixie), Python 3.13.5, Flask 3.1.1

## Files
- `app.py` – Flask app returning "Hello, Jenkins Multi-Stage Pipeline!"
- `test_app.py` – unittest for the `/` route
- `requirements.txt` – `flask==2.1.2`
- `Jenkinsfile` – declarative pipeline with 5 stages and post actions
- Source repository used by Jenkins: https://github.com/mridanirachar/devops-sample-code

## Steps (as per the manual)
1. Create `app.py`, `requirements.txt`, `test_app.py`; push to `devops-sample-code`
2. Create the `Jenkinsfile`; push it
3. Jenkins: New Item → `Python-MultiStage-Pipeline` → Pipeline
4. Pipeline → Definition: Pipeline script from SCM → Git → repository URL
5. Build Now → build #1 fails: `python3: not found`
6. Install Python inside the Jenkins container as root: `docker exec -it -u root jenkins bash`, `apt-get update`, `apt-get install -y python3 python3-pip python3-flask`
7. Build Now → build #2: all stages pass, `Finished: SUCCESS`

## Deviations from the manual
| Manual | What happened | Fix |
|---|---|---|
| New folder + `git init`, push to `devops-sample-code` | Would be rejected: repo already contains the Exercise 8 commit | Added the files to the existing local clone of `devops-sample-code` |
| Default Branch Specifier | `*/master` does not exist (see Exercise 8) | `*/main` |
| `apt-get update` | `Connection refused` to `deb.debian.org:80` from inside the container | Switched apt sources to https: `sed -i 's\|http://deb.debian.org\|https://deb.debian.org\|g' /etc/apt/sources.list.d/debian.sources` |
| `apt install python3.11-venv` | Not needed: the pipeline does not use a venv, and the image ships Python 3.13 | Skipped |

## Screenshots
1. App files: ![](screenshots/01-app-files.png)
2. Pushed to GitHub: ![](screenshots/02-push-app.png)
3. Jenkinsfile (5 stages): ![](screenshots/03-jenkinsfile.png)
4. Pipeline from SCM config: ![](screenshots/04-pipeline-config.png)
5. Build #1 fails (python3 not found): ![](screenshots/05-build-1-failed.png)
6. apt over https works: ![](screenshots/06-apt-https-fix.png)
7. Python and Flask installed: ![](screenshots/07-python-installed.png)
8. Build #2 succeeds: ![](screenshots/08-build-2-success.png)
9. Build history (#1 failed, #2 passed): ![](screenshots/09-build-history.png)

## Result
After installing Python in the Jenkins container, all five stages passed: the unit test ran OK, the app was copied to `python-app-deploy`, started in the background and tested again, ending with `Hello, Jenkins Multi-Stage Pipeline!` and `Finished: SUCCESS`.
