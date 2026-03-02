output "kafka_file_system" {
  value = aws_efs_file_system.kafka_file_system
}

output kafka_admin_password {
  value = aws_ssm_parameter.kafka_admin_password_ssm
}

output kafka_producer_password {
  value = aws_ssm_parameter.kafka_producer_password_ssm
}

output kafka_consumer_password {
  value = aws_ssm_parameter.kafka_consumer_password_ssm
}

output "kafka_cluster" {
  value = aws_ecs_cluster.epa_kafka_cluster
}

output "first_kafka_service" {
  value = aws_ecs_service.epa_kafka_service[0].name
}