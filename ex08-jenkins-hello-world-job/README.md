# Exercise 8: Creating a "Hello World" Jenkins Job

## Aim
Store a shell script in a GitHub repository and create a Jenkins Freestyle job that pulls the script from GitHub and runs it.

## Environment
Windows 11 + WSL2 (Ubuntu 24.04), Jenkins 2.580.1 in Docker (from Exercise 7), Git 2.43

## Files
- `hello-world.sh` – copy of the script; source repository: https://github.com/mridanirachar/devops-sample-code

## Steps (as per the manual)
1. Create a public GitHub repository `devops-sample-code`
2. Create `hello-world.sh` (`echo "Hello, Jenkins!"`) and `chmod +x hello-world.sh`
3. `git init`, `git add hello-world.sh`, `git commit -m "Add hello-world.sh"`
4. `git remote add origin https://github.com/mridanirachar/devops-sample-code.git`, `git push -u origin main`
5. In Jenkins: New Item → `HelloWorld` → Freestyle project
6. Git repository URL; Build Steps → Execute shell → `sh hello-world.sh`
7. Save → Build Now → Console Output

## Deviations from the manual (each run as written first)
| Step | What happened | Fix |
|---|---|---|
| Push | `git init` created branch `master`, so `git push -u origin main` failed: `src refspec main does not match any` | `git branch -M main`, then push |
| Build #1 | Jenkins' default Branch Specifier `*/master` → `Couldn't find any revision to build` → FAILURE | Branch Specifier changed to `*/main` |
| Token | Manual suggests a fine-grained PAT | Used the existing classic PAT (repo scope) |

## Screenshots
1. Empty GitHub repository: ![](screenshots/01-github-repo.png)
2. Script created: ![](screenshots/02-script.png)
3. git status (branch master): ![](screenshots/03-git-status.png)
4. Manual's push fails: ![](screenshots/04-push-error.png)
5. Script on GitHub: ![](screenshots/06-github-file.png)
6. HelloWorld job created: ![](screenshots/08-job-created.png)
7. Build #1 fails: ![](screenshots/09-build-1-failed.png)
8. Branch changed to */main: ![](screenshots/10-branch-fix.png)
9. Build #2 succeeds (Hello, Jenkins!): ![](screenshots/11-build-2-success.png)

## Result
Jenkins cloned the script from GitHub and ran it, printing `Hello, Jenkins!` with `Finished: SUCCESS`.
