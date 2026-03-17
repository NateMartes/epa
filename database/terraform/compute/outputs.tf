output "mongo_file_system" {
  value = aws_efs_file_system.mongo_file_system
}

output "mongodb_secret_password" {
  value = aws_ssm_parameter.mongodb_secret_password
}

output "replica_set_key" {
  value = aws_ssm_parameter.mongodb_secret_keyfile
}

output "mongo_db_cluster" {
  value = aws_ecs_cluster.epa_mongo_db_cluster
}

output "first_mongodb_service" {
  value = aws_ecs_service.epa_mongo_service[0].name
}