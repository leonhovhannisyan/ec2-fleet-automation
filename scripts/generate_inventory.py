#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TF_DIR = ROOT / "terraform"
OUT_FILE = ROOT / "ansible" / "inventory" / "generated.ini"

def tf_output_json() -> dict:
    res = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=str(TF_DIR),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(res.stdout)

def main():
    data = tf_output_json()

    public_ip = data["instance_public_ip"]["value"]
    ssh_user = data["ssh_user"]["value"]

    content = f"""[web]
web-1 ansible_host={public_ip}

[all:vars]
ansible_user={ssh_user}
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
"""

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(content)
    print(f"Wrote inventory: {OUT_FILE}")
    print(content)

if __name__ == "__main__":
    main()
