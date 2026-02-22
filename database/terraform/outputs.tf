output "mongo_db_cluster_dns_name" {
  value = module.networking.mongo_lb.dns_name
}