output "kafka_cluster_dns_namespace_name" {
  value = module.networking.private_dns_namespace.name
}

output "kafka_cluster_dns_discovery_service" {
  value = module.networking.kafka_discovery_service
}

output "kafka_cluster_name" {
  value = module.compute.kafka_cluster.name
}

output "first_mongodb_service" {
  value = module.compute.first_mongodb_service
}