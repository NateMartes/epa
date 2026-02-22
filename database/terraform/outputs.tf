output "mongo_db_cluster_dns_name" {
  value = module.networking.mongo_lb.dns_name
}

output "mongo_db_cluster_dns_namespace" {
  value = module.networking.private_dns_namespace
}

output "mongo_db_cluster_dns_discovery_service" {
  value = module.networking.mongo_discovery_service
}

output "replica_set_name" {
  value = var.replica_set_name
}