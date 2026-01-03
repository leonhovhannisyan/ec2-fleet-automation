#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "ansible" / "inventory" / "generated.ini"
OUT = ROOT / "reports" / "report.json"

def parse_inventory(path: Path) -> tuple[str, str]:
    ip = None
    user = None
    for line in path.read_text().splitlines():
        line = line.strip()
        if "ansible_host=" in line and not line.startswith("["):
            parts = line.split()
            for p in parts:
                if p.startswith("ansible_host="):
                    ip = p.split("=", 1)[1]
        if line.startswith("ansible_user="):
            user = line.split("=", 1)[1]
    if not ip or not user:
        raise SystemExit("Could not parse IP/user from inventory")
    return user, ip

def ssh(user: str, ip: str, cmd: str) -> str:
    res = subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking=no", f"{user}@{ip}", cmd],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or "SSH command failed")
    return res.stdout.strip()

def main():
    if not INV.exists():
        raise SystemExit(f"Missing inventory: {INV} (run generate_inventory.py)")

    user, ip = parse_inventory(INV)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": {"user": user, "ip": ip},
        "checks": {}
    }

    report["checks"]["uptime"] = ssh(user, ip, "uptime -p || true")
    report["checks"]["disk_root"] = ssh(user, ip, "df -h / | tail -n1 || true")
    report["checks"]["nginx_active"] = ssh(user, ip, "systemctl is-active nginx || true")
    report["checks"]["os_release"] = ssh(user, ip, "cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2- || true")
    report["checks"]["kernel"] = ssh(user, ip, "uname -r || true")
    report["checks"]["nginx_version"] = ssh(user, ip, "nginx -v 2>&1 || true")
    report["checks"]["http_status"] = ssh(user, ip, "curl -s -o /dev/null -w '%{http_code}\n' http://localhost || true")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))
    print(f"Wrote {OUT}")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
