provider "aws" {
  region = "us-east-1"
}

variable node_count {default = 3}
variable replica_set_name {default = "prodReplicaSet"}

module networking {
  source = "./networking"
  epa_mongo_db_cluster_name = module.compute.mongo_db_cluster.name
  node_count = var.node_count
  replica_set_name = var.replica_set_name
}

module security {
  source = "./security"
  vpc = module.networking.vpc
  mongo_file_system = module.compute.mongo_file_system
  mongodb_secret_password = module.compute.mongodb_secret_password
  replica_set_key = module.compute.replica_set_key
}

module compute {
  source = "./compute"
  subnet = module.networking.subnet
  mongo_discovery_service = module.networking.mongo_discovery_service
  mongo_dns_namespace = module.networking.private_dns_namespace
  replica_set_name = var.replica_set_name
  mongo_tg = module.networking.mongo_tg
  // ec2_sg = module.security.ec2_sg UNCOMMENT ME IF USING DEV EC2 INSTANCE
  efs_sg = module.security.efs_sg
  mongo_ecs_tasks_sg = module.security.mongo_ecs_tasks_sg
  ecs_mongo_task_role = module.security.ecs_mongo_task_role
  ecs_task_execution_role = module.security.ecs_task_execution_role
  ec2_instance_profile = module.security.ec2_instance_profile
  mongo_username = var.EPA_MONGODB_USERNAME
  mongo_password = var.EPA_MONGODB_PASSWORD
  node_count = var.node_count
}