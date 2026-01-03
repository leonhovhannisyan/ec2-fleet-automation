output "instance_public_ip" {
  value       = aws_instance.web.public_ip
  description = "Public IP of the EC2 instance"
}

output "instance_private_ip" {
  value       = aws_instance.web.private_ip
  description = "Private IP of the EC2 instance"
}

output "ssh_user" {
  value       = "ubuntu"
  description = "Default SSH user for the AMI"
}

output "http_url" {
  value       = "http://${aws_instance.web.public_ip}"
  description = "HTTP URL (after nginx is installed)"
}
