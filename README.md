# EC2 Fleet Automation (Terraform + Ansible + Bash + Python)

## Project summary
This project demonstrates end-to-end infrastructure provisioning and system configuration using a realistic DevOps toolchain:

- Terraform for AWS infrastructure provisioning
- Ansible for configuration management and idempotent system setup
- Bash for operational health checks
- Python for inventory generation and system reporting

The goal of this repository is to showcase practical DevOps skills, not just isolated tools.

---

## Architecture overview
High-level flow:

```
Terraform
  └── provisions AWS VPC + EC2
        ↓
Python (generate_inventory.py)
  └── converts Terraform outputs → Ansible inventory
        ↓
Ansible
  └── configures OS, users, nginx
        ↓
Bash / Python
  └── health checks + JSON operational report
```

---

## Repository structure
```
ec2-fleet-automation/
├── terraform/                # AWS infrastructure (VPC, SG, EC2)
├── ansible/
│   ├── roles/                # common, users, web
│   ├── inventory/            # generated inventory (ignored in git)
│   ├── group_vars/           # host/group configuration
│   └── site.yml              # main playbook
├── scripts/
│   ├── generate_inventory.py # Terraform → Ansible inventory
│   ├── health_check.sh       # Ping / SSH / HTTP checks
│   └── report.py             # JSON system report via SSH
├── reports/                  # Generated reports (example)
└── .github/workflows/        # CI (Terraform, Ansible, Python)
```

---

## What this project demonstrates
- Infrastructure as Code with Terraform
- Secure EC2 access via SSH and security groups
- Dynamic Ansible inventory generated from Terraform outputs
- Idempotent Ansible roles and playbooks
- Linux system configuration and service management
- Bash scripting for operational checks
- Python scripting for automation and reporting
- CI pipeline validating Terraform, Ansible, and Python code

---

## How to use

### 1. Provision infrastructure (Terraform)
```
cd terraform
terraform init

terraform apply \
  -var="ssh_allowed_cidr=<YOUR_IP>/32" \
  -var="key_pair_name=<YOUR_KEYPAIR>"
```
or using environmental variables
```
cd terraform
terraform init

export TF_VAR_ssh_allowed_cidr="<YOUR_IP>/32"
export TF_VAR_key_pair_name="<YOUR_KEYPAIR>"

terraform apply 
```

### 2. Generate Ansible inventory
```
./scripts/generate_inventory.py
```

### 3. Configure EC2 instance (Ansible)
```
ansible-playbook -i ansible/inventory/generated.ini ansible/site.yml
```

Run the playbook again to verify idempotency (should result in changed=1, only changes will be applicable for jinja template which contains Date, it will change after each playbook iteration).

---

## Operational checks

### Bash health check
```
./scripts/health_check.sh
```

Checks:
- Network reachability (ping)
- SSH connectivity
- HTTP service availability

### Python system report
```
./scripts/report.py
```

Generates a JSON report with:
- Uptime
- Disk usage
- OS and kernel version
- Nginx status and version
- HTTP response status

Example output is stored in reports/report.json.

---

## CI pipeline
GitHub Actions runs automatically on push and pull requests:
- terraform fmt and terraform validate
- Python syntax checks
- Ansible playbook syntax validation

This ensures consistent code quality and prevents common errors before changes are merged.

---

## Idempodency and reporting
```
First ansible run:
```
PLAY [Configure EC2 web host] *********************************************************************************************************************************************************

TASK [Gathering Facts] ****************************************************************************************************************************************************************
ok: [web-1]

TASK [common : Update apt cache] ******************************************************************************************************************************************************
changed: [web-1]

TASK [common : Install baseline packages] *********************************************************************************************************************************************
changed: [web-1]

TASK [users : Ensure managed users exist] *********************************************************************************************************************************************
changed: [web-1] => (item={'name': 'devops', 'groups': ['sudo'], 'ssh_public_key': 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMKdSjLd1i1rLWoKSW9EcUDi+mQ+sofQ4+lTaUlJKkqf ec2-fleet-keypair'})

TASK [users : Install authorized_keys for managed users] ******************************************************************************************************************************
changed: [web-1] => (item={'name': 'devops', 'groups': ['sudo'], 'ssh_public_key': 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMKdSjLd1i1rLWoKSW9EcUDi+mQ+sofQ4+lTaUlJKkqf ec2-fleet-keypair'})

TASK [users : Allow passwordless sudo for sudo group] *********************************************************************************************************************************
changed: [web-1]

TASK [web : Install nginx] ************************************************************************************************************************************************************
changed: [web-1]

TASK [web : Ensure nginx is enabled and running] **************************************************************************************************************************************
ok: [web-1]

TASK [web : Deploy index.html] ********************************************************************************************************************************************************
changed: [web-1]

PLAY RECAP ****************************************************************************************************************************************************************************
web-1                      : ok=9    changed=7    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0 
```
Idempodency after second ansible run:
```
PLAY [Configure EC2 web host] *********************************************************************************************************************************************************

TASK [Gathering Facts] ****************************************************************************************************************************************************************
ok: [web-1]

TASK [common : Update apt cache] ******************************************************************************************************************************************************
ok: [web-1]

TASK [common : Install baseline packages] *********************************************************************************************************************************************
ok: [web-1]

TASK [users : Ensure managed users exist] *********************************************************************************************************************************************
ok: [web-1] => (item={'name': 'devops', 'groups': ['sudo'], 'ssh_public_key': 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMKdSjLd1i1rLWoKSW9EcUDi+mQ+sofQ4+lTaUlJKkqf ec2-fleet-keypair'})

TASK [users : Install authorized_keys for managed users] ******************************************************************************************************************************
ok: [web-1] => (item={'name': 'devops', 'groups': ['sudo'], 'ssh_public_key': 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMKdSjLd1i1rLWoKSW9EcUDi+mQ+sofQ4+lTaUlJKkqf ec2-fleet-keypair'})

TASK [users : Allow passwordless sudo for sudo group] *********************************************************************************************************************************
ok: [web-1]

TASK [web : Install nginx] ************************************************************************************************************************************************************
ok: [web-1]

TASK [web : Ensure nginx is enabled and running] **************************************************************************************************************************************
ok: [web-1]

TASK [web : Deploy index.html] ********************************************************************************************************************************************************
changed: [web-1]

PLAY RECAP ****************************************************************************************************************************************************************************
web-1                      : ok=9    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```
```
{
  "timestamp": "2026-01-01T23:08:07.774252+00:00",
  "target": {
    "user": "ubuntu",
    "ip": "51.20.78.23"
  },
  "checks": {
    "uptime": "up 36 minutes",
    "disk_root": "/dev/root       7.6G  2.0G  5.6G  27% /",
    "nginx_active": "active",
    "os_release": "\"Ubuntu 22.04.5 LTS\"",
    "kernel": "6.8.0-1044-aws",
    "nginx_version": "nginx version: nginx/1.18.0 (Ubuntu)",
    "http_status": "200"
  }
}
```

---

## Notes
- Infrastructure is designed to be easy to destroy and recreate
- Intended for learning, demos, and portfolio use
- No long-lived credentials are stored in the repository

---

## Cleanup
When finished, remove AWS resources to avoid costs:
```
cd terraform
terraform destroy
```

---

## Why this project matters
This repository reflects how DevOps tools are commonly combined in real environments:
- Terraform for provisioning
- Ansible for configuration
- Scripts for automation and observability

It focuses on clarity, correctness, and maintainability over unnecessary complexity.
