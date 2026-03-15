provider "aws" {
  region = "us-west-2"
}

variable node_count {default = 3}

module networking {
  source = "./networking"
  node_count = var.node_count
}

module security {
  source = "./security"
  vpc = module.networking.vpc
  kafka_file_system = module.compute.kafka_file_system
  kafka_admin_password = module.compute.kafka_admin_password
  kafka_producer_password = module.compute.kafka_producer_password
  kafka_consumer_password = module.compute.kafka_consumer_password
}

module compute {
  source = "./compute"
  subnet = module.networking.subnet
  kafka_discovery_service = module.networking.kafka_discovery_service
  kafka_dns_namespace = module.networking.private_dns_namespace
  kafka_tg = module.networking.kafka_tg
  kafka_lb_name = module.networking.kafka_lb_name
  // ec2_sg = module.security.ec2_sg UNCOMMENT ME IF USING DEV EC2 INSTANCE
  efs_sg = module.security.efs_sg
  kafka_ecs_tasks_sg = module.security.kafka_ecs_tasks_sg
  ecs_kafka_task_role = module.security.ecs_kafka_task_role
  ecs_task_execution_role = module.security.ecs_task_execution_role
  ec2_instance_profile = module.security.ec2_instance_profile
  node_count = var.node_count
  kafka_admin_password = var.EPA_KAFKA_ADMIN_PASSWORD
  kafka_producer_password = var.EPA_KAFKA_PRODUCER_PASSWORD
  kafka_consumer_password = var.EPA_KAFKA_CONSUMER_PASSWORD
}
