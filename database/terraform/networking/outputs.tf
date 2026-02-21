output "vpc" {
  value = aws_vpc.mongo_vpc
}

output "subnet" {
  value = aws_subnet.mongo_subnet
}

output "mongo_discovery_service" {
  value = aws_service_discovery_service.mongo_discovery_service
}

output "mongodb_cluster_dns_name" {
  value = aws_eip.main[0].public_dns
}