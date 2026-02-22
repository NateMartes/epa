provider "aws" {
  region = "us-east-1"
}

module networking {
  source = "./networking"
}

module security {
  source = "./security"
  vpc = module.networking.vpc
  mongo_file_system = module.compute.mongo_file_system
  mongodb_secret_password = module.compute.mongodb_secret_password
}

module compute {
  source = "./compute"
  subnet = module.networking.subnet
  mongo_discovery_service = module.networking.mongo_discovery_service
  mongo_tg = module.networking.mongo_tg
  // ec2_sg = module.security.ec2_sg UNCOMMENT ME IF USING DEV EC2 INSTANCE
  efs_sg = module.security.efs_sg
  mongo_ecs_tasks_sg = module.security.mongo_ecs_tasks_sg
  ecs_mongo_task_role = module.security.ecs_mongo_task_role
  ecs_task_execution_role = module.security.ecs_task_execution_role
  mongo_username = var.EPA_MONGODB_USERNAME
  mongo_password = var.EPA_MONGODB_PASSWORD
  node_count = 3
}