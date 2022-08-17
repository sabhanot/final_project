# Define the security group for the EC2 Instance
resource "aws_security_group" "aws-vm-sg" {
  name        = "vm-sg"
  description = "Allow incoming connections"
  vpc_id      = aws_vpc.vpc.id  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow incoming HTTP connections"
  }
  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow incoming RDP connections (Windows)"
  }  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow incoming SSH connections (Linux)"
  }
#  ingress {
#    from_port   = 0
#    to_port     = 0
#    protocol    = "-1"
#    cidr_blocks = ["0.0.0.0/0"]
#  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }  
  tags = {
    Name = "ztp-sg"
  }
}

#Creating EC2 Instance
resource "aws_instance" "vm-server" {
  ami                    = data.aws_ami.amazon-linux-2.id
  instance_type          = var.vm_instance_type
  subnet_id              = aws_subnet.public-subnet.id
  vpc_security_group_ids = [aws_security_group.aws-vm-sg.id]
  source_dest_check      = false
  key_name               = aws_key_pair.key_pair.key_name
  associate_public_ip_address = var.vm_associate_public_ip_address
  user_data = "${file("template_file.sh")}"
  
  # root disk
  root_block_device {
    volume_size           = var.vm_root_volume_size
    volume_type           = var.vm_root_volume_type
    delete_on_termination = true
    encrypted             = true
  }
  # extra disk
  ebs_block_device {
    device_name           = "/dev/xvda"
    volume_size           = var.vm_data_volume_size
    volume_type           = var.vm_data_volume_type
    encrypted             = true
    delete_on_termination = true
  }
  
  tags = {
    Name = "ztp_instance"
  }
}
