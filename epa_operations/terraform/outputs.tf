output "vpc_id" {
  value = module.networking.vpc.id
}

output "vpc_cidr_block" {
  value = module.networking.vpc.cidr_block
}

output "subnet_1_id" {
  value = module.networking.subnet_1.id
}

output "subnet_2_id" {
  value = module.networking.subnet_2.id
}

output "route_table_id" {
  value = module.networking.route_table_id
}