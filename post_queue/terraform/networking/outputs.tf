output "vpc" {
  value = aws_vpc.kafka_vpc
}

output "subnet" {
  value = aws_subnet.private_kafka_subnet
}

output "private_dns_namespace" {
  value = aws_service_discovery_private_dns_namespace.kafka_monitoring
}

output "kafka_discovery_service" {
  value = aws_service_discovery_service.kafka_discovery_service
}