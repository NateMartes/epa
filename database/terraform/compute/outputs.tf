output "mongo_file_system" {
  value = aws_efs_file_system.mongo_file_system
}

output "mongodb_secret_password" {
  value = aws_ssm_parameter.mongodb_secret_password
}

output "replica_set_key" {
  value = aws_ssm_parameter.mongodb_secret_keyfile
}