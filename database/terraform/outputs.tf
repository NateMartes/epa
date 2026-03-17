output "mongo_db_cluster_dns_name" {
  value = module.networking.mongo_cluster_dns_name
}

output "mongo_db_cluster_dns_namespace_name" {
  value = module.networking.private_dns_namespace.name
}

output "mongo_db_cluster_dns_discovery_service" {
  value = module.networking.mongo_discovery_service
}

output "mongo_db_cluster_name" {
  value = module.compute.mongo_db_cluster.name
}

output "vpc_id" {
  value = module.networking.vpc.id
}

output "vpc_cidr_block" {
  value = module.networking.vpc.cidr_block
}

output "first_mongodb_service" {
  value = module.compute.first_mongodb_service
}

output "mongo_dns_id" {
  value = module.networking.mongo_dns_id
}

output "mongo_node_dns_id" {
  value = module.networking.private_dns_namespace.hosted_zone
}

output "route_table_id" {
  value = module.networking.route_table_id
}

output "replica_set_name" {
  value = var.replica_set_name
}