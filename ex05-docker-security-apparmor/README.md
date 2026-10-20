# Exercise 5: Docker Security with AppArmor and Python

## Aim
Secure a containerized Flask application using an AppArmor profile, apply the profile with both the Docker CLI and the Docker SDK for Python, and test whether restricted actions are blocked.

## Files
- `app.py` – Flask application
- `Dockerfile` – builds the `flask-apparmor` image
- `my-apparmor-profile` – AppArmor profile (denies reading `/etc`, executing `/bin` and `/usr/bin`, and `sys_admin`)
- `apply_apparmor.py` – Docker SDK script to run the container with the profile and verify it
- `test_restricted_actions.py` – Docker SDK script to test restricted actions

## Environment
Windows 11 + WSL2 (Ubuntu 24.04) + Docker Desktop

## Steps
1. Build and run the app: `docker build -t flask-apparmor .`, `docker run -d --name flask-secure -p 5000:5000 flask-apparmor`
2. Verify at `http://localhost:5000`
3. Install tools: `sudo apt install -y apparmor apparmor-utils`
4. Copy the profile to `/etc/apparmor.d/my-apparmor-profile` and load it: `sudo apparmor_parser -r /etc/apparmor.d/my-apparmor-profile`
5. Run with the profile: `docker run -d --name flask-secure --security-opt="apparmor=my-apparmor-profile" -p 5000:5000 flask-apparmor`
6. Verify: `docker inspect flask-secure --format 'SecurityOpt={{.HostConfig.SecurityOpt}} AppArmorProfile={{.AppArmorProfile}}'`
7. Test restriction: `docker exec flask-secure cat /etc/passwd`
8. Docker SDK (in a virtual environment): `python3 -m venv venv`, `source venv/bin/activate`, `pip install docker`, then `python apply_apparmor.py` and `python test_restricted_actions.py`

## Screenshots
1. Container running: ![](screenshots/01-container-running.png)
2. App in browser: ![](screenshots/02-browser.png)
3. Loading the profile fails: ![](screenshots/03-apparmor-parser-error.png)
4. Profile requested but not enforced: ![](screenshots/04-profile-not-enforced.png)
5. `apply_apparmor_extended.py` output: ![](screenshots/05-apply-script.png)
6. `test_restricted_actions_extended.py` output: ![](screenshots/06-test-script.png)

## Observations
| Check | Expected (manual) | Observed |
|---|---|---|
| `apparmor_parser -r` | Profile loads | Fails: "Kernel needs AppArmor 2.4 compatibility patch" |
| `docker inspect` | `AppArmorProfile=my-apparmor-profile` | `SecurityOpt=[apparmor=my-apparmor-profile]`, `AppArmorProfile=` (empty) |
| Read `/etc/passwd` | Exit code 1 (blocked) | Exit code 0, file printed |
| Execute `/bin/bash` | Exit code 126 (blocked) | Exit code 0, command ran |

## Why the profile was not enforced
- `docker info` lists only `seccomp` and `cgroupns` under Security Options — **no `apparmor`**.
- `/sys/module/apparmor/parameters/enabled` returns `N`: the WSL2 kernel ships with AppArmor disabled.
- Docker therefore **accepts `--security-opt apparmor=...` without error but silently does not apply it**. This is an important security lesson: a requested security option is not proof of enforcement — it must be verified (here, with `docker inspect` and an actual test of the restricted action).

## Other fixes and notes
- `pip install docker` fails on Ubuntu 24.04 (externally-managed-environment), so a Python virtual environment was used.
- The SDK scripts were extended to print the *enforced* profile (`AppArmorProfile`) and to remove containers after use.
- The manual's profile targets `/usr/bin/python3`, but `python:3.8-slim` runs `/usr/local/bin/python`. On a host with AppArmor enabled, the profile should be attached to the container via `--security-opt` (as done here) rather than relying on the executable path.
- On a native Linux host with AppArmor enabled (e.g. Ubuntu on bare metal), the same steps should show the profile enforced and the restricted actions blocked.

## Questions
1. **Purpose of AppArmor with Docker?** Enforces mandatory access control, confining a container to a limited set of files, capabilities and network access, adding a security layer beyond default isolation.
2. **How do profiles secure a container?** They define what the containerized process can read, write, execute and which capabilities it can use; anything denied is blocked by the kernel.
3. **Why restrict `/etc` and `/var`?** They hold configuration, user account data and logs; restricting them prevents reading sensitive data or tampering with the system.
4. **Other restrictions possible?** Network access, binding to ports, executing binaries, writing to directories, mounting filesystems, and Linux capabilities such as `sys_admin`.
5. **How to verify a profile is applied?** `docker inspect` (`AppArmorProfile` field, not just `HostConfig.SecurityOpt`), `docker info` (check `apparmor` under Security Options), and testing a denied action.

## Result
The Flask app was containerized and the AppArmor profile was created and applied via both the Docker CLI and the Docker SDK. On WSL2 the kernel has AppArmor disabled, so the profile was accepted but not enforced; this was verified and documented with evidence.

## Evidence: the manual's original files (run exactly as written)
`Dockerfile`, `apply_apparmor.py` and `test_restricted_actions.py` are now the manual's unmodified versions. The extended scripts used on Oct 13 are kept as `apply_apparmor_extended.py` and `test_restricted_actions_extended.py` (they additionally print the *enforced* profile from `AppArmorProfile`).

| Manual step | Result | Screenshot |
|---|---|---|
| `docker build -t flask-apparmor .` with the manual's Dockerfile | Builds successfully (`--network=host` used only because of a slow network) | ![](screenshots/07-manual-dockerfile-build.png) |
| `python apply_apparmor.py` | Runs as written: `Container started: 4f469c9fd463`, `AppArmor profile applied: ['apparmor=my-apparmor-profile']` (Docker records the profile; WSL2 does not enforce it) | ![](screenshots/08-manual-apply-script.png) |
| `python test_restricted_actions.py` | `/etc/passwd`: **Exit Code 0** (manual expects 1); `/bin/bash`: **Exit Code 0** (manual expects 126) – confirms the profile is not enforced on WSL2 | ![](screenshots/09-manual-test-script.png) |
