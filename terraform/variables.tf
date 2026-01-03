variable "region" {
  type        = string
  description = "AWS region"
  default     = "eu-north-1"
}

variable "project_name" {
  type        = string
  description = "Project name prefix"
  default     = "ec2-fleet"
}

variable "ssh_allowed_cidr" {
  type        = string
  description = "Your public IP in CIDR form for SSH access (e.g. 1.2.3.4/32)"
}

variable "key_pair_name" {
  type        = string
  description = "Existing AWS EC2 Key Pair name to use for SSH"
  default = "ec2-fleet-keypair"
}
