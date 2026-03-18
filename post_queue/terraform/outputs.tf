output "kafka_cluster_name" {
  value = module.compute.kafka_cluster.name
}

output "first_kafka_service" {
  value = module.compute.first_kafka_service
}

output "vpc_id" {
  value = module.networking.vpc.id
}

output "vpc_cidr_block" {
  value = module.networking.vpc.cidr_block
}

output "kafka_dns_id" { 
  value = module.networking.kafka_dns_id
}

output "kafka_node_dns_id" {
  value = module.networking.private_dns_namespace.hosted_zone
}

output "route_table_id" {
  value = module.networking.route_table_id
}