# Get latest Amazon Linux 2 AMI
data "aws_ami" "amazon-linux-2" {
  most_recent = true
  owners      = ["amazon"]  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm*"]
  }
}
