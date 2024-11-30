# Example of an insecure AWS security group configuration

provider "aws" {
  region = "us-east-1"
}

# Insecure Security Group
resource "aws_security_group" "insecure_sg" {
  name        = "insecure-sg"
  description = "This is an insecure security group"

  # Allowing unrestricted inbound access on port 22 (SSH) and 80 (HTTP)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # This opens SSH to the entire internet
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # This opens HTTP to the entire internet
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # Allowing all outbound traffic
  }
}

# Insecure EC2 instance using an insecure SSH key
resource "aws_instance" "insecure_instance" {
  ami           = "ami-12345678"  # Replace with a valid AMI ID
  instance_type = "t2.micro"

  key_name = "insecure-ssh-key"  # This could be an insecure SSH key

  # Instance with no security hardening (No IAM roles or security groups)
  security_groups = [aws_security_group.insecure_sg.name]
}

# Insecure S3 Bucket
resource "aws_s3_bucket" "insecure_bucket" {
  bucket = "insecure-bucket-example"

  acl = "public-read"  # This makes the S3 bucket publicly accessible
}

# EC2 instance without encryption enabled
resource "aws_ebs_volume" "insecure_ebs" {
  availability_zone = "us-east-1a"
  size              = 8
  encrypted         = false  # EBS should be encrypted for better security
}
