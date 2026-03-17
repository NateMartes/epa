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

output "kafka_dns_id" {
  value = aws_route53_zone.kafka_cluster.id
}

output "route_table_id" {
  value = aws_route_table.kafka_route_table.id
}

output "kafka_tg" {
  value = aws_lb_target_group.kafka_tg
}

output "kafka_lb_name" {
  value = aws_route53_record.kafka_cluster_record.name
}