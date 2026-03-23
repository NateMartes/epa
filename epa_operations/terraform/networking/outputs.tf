output "vpc" {
  value = aws_vpc.operations_vpc
}

output "subnet_1" {
  value = aws_subnet.private_operations_subnet[0]
}

output "subnet_2" {
  value = aws_subnet.private_operations_subnet[1]
}

output "route_table_id" {
  value = aws_route_table.operations_route_table.id
}