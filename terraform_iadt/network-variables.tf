# AWS NV
variable "aws_nv" {
  type        = string
  description = "AWS NV"
  default     = "us-east-1b"
}
# VPC Variables
variable "vpc_cidr" {
  type        = string
  description = "CIDR for the VPC"
  default     = "10.1.64.0/18"
}
# Subnet Variables
variable "public_subnet_cidr" {
  type        = string
  description = "CIDR for the public subnet"
  default     = "10.1.64.0/24"
}