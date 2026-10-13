import docker

client = docker.from_env()

container = client.containers.run(
    "flask-apparmor",
    ports={'5000/tcp': 5000},
    security_opt=["apparmor=my-apparmor-profile"],
    detach=True
)
print(f"Container started: {container.short_id}")

exit_code, output = container.exec_run("cat /etc/passwd")
print(f"Attempt to read /etc/passwd: Exit Code {exit_code}")
print(f"First line of output: {output.decode().splitlines()[0] if output else ''}")

exit_code, output = container.exec_run("/bin/bash -c 'echo bash executed'")
print(f"Attempt to execute /bin/bash: Exit Code {exit_code}, Output: {output.decode().strip()}")

container.stop()
container.remove()
print("Container stopped and removed")
