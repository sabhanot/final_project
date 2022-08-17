output "vm_server_instance_id" {
  value = aws_instance.vm-server.id
}
output "vm_server_instance_public_dns" {
  value = aws_instance.vm-server.public_dns
}
output "vm_server_instance_public_ip" {
  value = aws_instance.vm-server.public_ip
}
output "vm_server_instance_private_ip" {
  value = aws_instance.vm-server.private_ip
}