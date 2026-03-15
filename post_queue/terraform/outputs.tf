output "kafka_cluster_name" {
  value = module.compute.kafka_cluster.name
}

output "first_kafka_service" {
  value = module.compute.first_kafka_service
}

output "vpc_id" {
  value = module.networking.vpc.id
}

output "kafka_dns_id" { 
  value = module.networking.kafka_dns_id
}

output "route_table_id" {
  value = module.networking.route_table_id
}