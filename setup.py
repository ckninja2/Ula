import base64
import os
import shutil
import subprocess
import time
import urllib.request

PUB_KEY = base64.b64decode(os.getenv("PUB_KEY")).decode('utf-8')
PRVT_KEY = base64.b64decode(os.getenv("PRVT_KEY")).decode('utf-8')
HOST_PRVT_KEY = base64.b64decode(
    os.getenv("HOST_PRVT_KEY")).decode('utf-8')


def download_file(url, output_path):
    with urllib.request.urlopen(url) as response, open(output_path, 'wb') as out_file:
        out_file.write(response.read())


def setup_win_ssh_server():
    os.makedirs("OpenSSH-Win64\\ssh", exist_ok=True)
    os.makedirs(os.path.expanduser("~\\.ssh"), exist_ok=True)

    ssh_config = """
HostKey ssh/ssh_host_rsa_key
Subsystem sftp sftp-server.exe
LogLevel DEBUG3
PidFile ssh/sshd.pid
"""
    with open("OpenSSH-Win64\\ssh\\sshd_config", "w", encoding="utf-8") as f:
        f.write(ssh_config)

    # Write the SSH keys
    with open(os.path.expanduser("~\\.ssh\\authorized_keys"), "w", encoding="utf-8") as f:
        f.write(PUB_KEY)
    with open(os.path.expanduser("~\\.ssh\\id_rsa"), "w", encoding="utf-8") as f:
        f.write(PRVT_KEY)
    with open("OpenSSH-Win64\\ssh\\ssh_host_rsa_key", "w", encoding="utf-8") as f:
        f.write(HOST_PRVT_KEY)

    # Set permissions on SSH keys
    key_path = os.path.join(
        os.getcwd(), "OpenSSH-Win64\\ssh\\ssh_host_rsa_key")
    subprocess.run(["icacls", key_path, "/c", "/t",
                   "/Inheritance:d"], check=True)
    subprocess.run(["icacls", key_path, "/c", "/t",
                   "/Grant", f"{os.environ['USERNAME']}:F"], check=True)
    subprocess.run(["takeown", "/F", key_path], check=True)
    subprocess.run(["icacls", key_path, "/c", "/t",
                   "/Grant:r", f"{os.environ['USERNAME']}:F"], check=True)
    subprocess.run(["icacls", key_path, "/c", "/t", "/Remove:g",
                   "SYSTEM", "Users", "Administrators"], check=True)

    # Add firewall rule for SSH
    subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", "name=Allow SSH",
                    "dir=in", "action=allow", "protocol=TCP", "localport=22"], check=True)


def start_win_ssh_server():
    # Build absolute paths for sshd.exe and its config file
    sshd_path = os.path.abspath("OpenSSH-Win64\\sshd.exe")
    config_path = os.path.abspath("OpenSSH-Win64\\ssh\\sshd_config")

    # Start SSH server in the foreground for log visibility
    subprocess.Popen(
        [sshd_path, "-f", config_path],
        text=True
    )


cloudflared_url = ''
cloudflared = ''
if os.getenv('RUNNER_OS') == 'Linux':
    cloudflared_url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64'
    cloudflared = 'cloudflared'
    download_file(cloudflared_url, cloudflared)
    os.chmod(cloudflared, 0o755)
    with open(os.path.expanduser("~/.ssh/authorized_keys"), "w", encoding="utf-8") as f:
        f.write(PUB_KEY)
    with open(os.path.expanduser("~/.ssh/id_rsa"), "w", encoding="utf-8") as f:
        f.write(PRVT_KEY)
elif os.getenv('RUNNER_OS') == 'Windows':
    cloudflared_url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe'
    cloudflared = 'cloudflared.exe'
    download_file(cloudflared_url, cloudflared)

    open_ssh_url = 'https://github.com/PowerShell/Win32-OpenSSH/releases/latest/download/OpenSSH-Win64.zip'
    download_file(open_ssh_url, 'OpenSSH-Win64.zip')
    shutil.unpack_archive('OpenSSH-Win64.zip')
    setup_win_ssh_server()
    start_win_ssh_server()


process = subprocess.Popen(
    [cloudflared, "tunnel", "--no-autoupdate",
        "--url", "tcp://localhost:22"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)

link = ''
for line in process.stderr:
    print(line)
    if ".trycloudflare.com" in line:
        link = line.split()[3]
        print(f"found link {link}")
        break

time.sleep(-1)
