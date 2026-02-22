output "vpc" {
  value = aws_vpc.mongo_vpc
}

output "subnet" {
  value = aws_subnet.private_mongo_subnet
}

output "mongo_discovery_service" {
  value = aws_service_discovery_service.mongo_discovery_service
}

output "mongo_tg" {
  value = aws_lb_target_group.mongo_tg
}

output "mongo_lb" {
  value = aws_lb.mongo_lb
}