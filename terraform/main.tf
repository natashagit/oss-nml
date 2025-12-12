terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    local = {
      source = "hashicorp/local"
    }
    tls = {
      source = "hashicorp/tls"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# --- 1. KEYS ---
resource "tls_private_key" "pk" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = "hw3-key-free-tier" # New name for Free Tier attempt
  public_key = tls_private_key.pk.public_key_openssh
}

resource "local_file" "ssh_key" {
  content         = tls_private_key.pk.private_key_pem
  filename        = "${path.module}/hw3-key-free-tier.pem"
  file_permission = "0400"
}

# --- 2. NETWORK ---
data "aws_vpc" "default" {
  default = true
}

resource "aws_subnet" "lab_subnet" {
  vpc_id                  = data.aws_vpc.default.id
  cidr_block              = "172.31.200.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
}

resource "aws_security_group" "sg" {
  name        = "oss-nml-monitoring-sg-free"
  description = "Allow SSH, App, and Grafana"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- 3. SERVER ---
resource "aws_instance" "server" {
  ami           = "ami-0c7217cdde317cfec" # Ubuntu 22.04 (us-east-1)
  
  # CRITICAL CHANGE: Downgrade to Free Tier eligible instance
  instance_type = "t3.micro" 
  
  key_name      = aws_key_pair.generated_key.key_name
  subnet_id     = aws_subnet.lab_subnet.id
  vpc_security_group_ids = [aws_security_group.sg.id]

  # CRITICAL ADDITION: Create 2GB Swap file so t3.micro doesn't crash
  user_data = <<-EOF
              #!/bin/bash
              set -e
              
              # 1. Create Swap (Fake RAM)
              fallocate -l 2G /swapfile
              chmod 600 /swapfile
              mkswap /swapfile
              swapon /swapfile
              echo '/swapfile none swap sw 0 0' >> /etc/fstab

              # 2. Install Docker
              apt-get update
              apt-get install -y docker.io docker-compose-v2 git

              # 3. Clone Repo
              cd /home/ubuntu
              git clone --branch hw3_add_telemetry https://github.com/natashagit/oss-nml.git app

              # 4. Permissions
              chown -R ubuntu:ubuntu /home/ubuntu/app
              usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "OSS-NML-Monitor"
  }
}

# --- 4. OUTPUTS ---
output "grafana_url" {
  value = "http://${aws_instance.server.public_ip}:3000"
}

output "ssh_command" {
  value = "ssh -i hw3-key-free-tier.pem ubuntu@${aws_instance.server.public_ip}"
}