output "kafka_file_system" {
  value = aws_efs_file_system.kafka_file_system
}

output "kafka_cluster" {
  value = aws_ecs_cluster.epa_kafka_cluster
}

output "first_mongodb_service" {
  value = aws_ecs_service.epa_kafka_service[0].name
}