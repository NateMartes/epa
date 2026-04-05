output "vpc" {
  value = aws_vpc.mongo_vpc
}

output "subnet" {
  value = aws_subnet.private_mongo_subnet
}

output "private_dns_namespace" {
  value = aws_service_discovery_private_dns_namespace.mongo_monitoring
}

output "mongo_discovery_service" {
  value = aws_service_discovery_service.mongo_discovery_service
}

output "mongo_dns_id" {
  value = aws_route53_zone.mongo_cluster.zone_id
}

output "route_table_id" {
  value = aws_route_table.private_rt.id
}

output "mongo_cluster_dns_name" {
  value = aws_route53_record.mongo_txt.name
}