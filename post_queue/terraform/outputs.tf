output "kafka_cluster_name" {
  value = module.compute.kafka_cluster.name
}

output "first_kafka_service" {
  value = module.compute.first_kafka_service
}