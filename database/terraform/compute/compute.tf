# --- EFS File System for MongoDB ---
resource "aws_efs_file_system" "mongo_file_system" {
 creation_token = "mongoefs"
 encrypted = true
  tags = {
    Name = "mongoefs"
  }
}

# --- Tell EFS where to mount the File System
variable subnet {}
variable efs_sg {}
resource "aws_efs_mount_target" "efs_mount_target" {
  count           = length(var.subnet.*.id)
  file_system_id  = aws_efs_file_system.mongo_file_system.id
  subnet_id       = var.subnet[count.index].id
  security_groups = [var.efs_sg.id]
}

# --- ECS Cluster ---
resource "aws_ecs_cluster" "epa_mongo_db_cluster" {
  name = "epa-mongo-db-cluster"
}

# --- ECS Task Definition (Bascially, what should fargate do for the EC2 nodes) ---
variable ecs_task_execution_role {}
variable ecs_mongo_task_role {}
variable mongo_username { sensitive = true }
variable mongo_password { sensitive = true }
resource "aws_ssm_parameter" "mongodb_secret_password" {
  name  = "/mongodb/MONGO_INITDB_ROOT_PASSWORD"
  type  = "SecureString"
  value = var.mongo_password
  overwrite = true

  lifecycle {
    ignore_changes = [value]
  }
}
resource "aws_ecs_task_definition" "mongo_task_definition" {
  
  family                   = "mongolab-mongodb"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.ecs_task_execution_role.arn
  task_role_arn            = var.ecs_mongo_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "mongo",
      image     = "mongo:7",
      cpu       = 256,
      memory    = 512,
      essential = true,
      portMappings = [
        {
          protocol      = "tcp"
          containerPort = 27017
          hostPort      = 27017
        }
      ]
      mountPoints = [
        {
          sourceVolume  = "mongoEfsVolume"
          containerPath = "/data/db"
          readOnly      = false
        },
      ],
      environment = [
        {
          name  = "MONGO_INITDB_ROOT_USERNAME"
          value = var.mongo_username
        }
      ],
      secrets = [
        {
          name      = "MONGO_INITDB_ROOT_PASSWORD"
          valueFrom = aws_ssm_parameter.mongodb_secret_password.name
        }
      ],
      healthcheck = {
        command     = ["CMD-SHELL", "echo 'db.runCommand(\\\"ping\\\").ok' | mongosh mongodb://localhost:27017/test"]
        interval    = 30
        timeout     = 15
        retries     = 3
        startPeriod = 15
      }
    }
  ])
  volume {
      name = "mongoEfsVolume"
  
      efs_volume_configuration {
        file_system_id     = aws_efs_file_system.mongo_file_system.id
        transit_encryption = "ENABLED"
        authorization_config {
          iam = "ENABLED"
        }
      }
    }
}

# --- The Actual ECS service running MongoDB ---
variable "mongo_discovery_service" {}
variable "mongo_ecs_tasks_sg" {}
variable "mongo_tg" {}
resource "aws_ecs_service" "epa_mongo_service" {
  name            = "epa-ecs-mongodb-service"
  cluster         = aws_ecs_cluster.epa_mongo_db_cluster.id
  task_definition = aws_ecs_task_definition.mongo_task_definition.id
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet[*].id
    security_groups  = [var.mongo_ecs_tasks_sg.id]
  }
  
  load_balancer {
    target_group_arn = var.mongo_tg.arn
    container_name = "mongo"
    container_port = 27017
  }

  service_registries {
    registry_arn = var.mongo_discovery_service.arn
  }

}



# --- Testing EC2 Container ---
/* FOR TESTING
# --- SSH Access to cluster
resource "aws_key_pair" "ec2_keypair" {
  key_name   = "mongokey"
  public_key = file("~/.ssh/cs361-mongodb.pub")
}

variable "ec2_sg" {}
resource "aws_instance" "mongolab_ec2_instance" {
  ami = "ami-0f3caa1cf4417e51b" # Amazon Linux 2023 Free Tier on us-east-1
  instance_type = "t3.micro"
  subnet_id     = var.subnet[0].id
  key_name      = aws_key_pair.ec2_keypair.key_name
  security_groups = [var.ec2_sg.id]
  user_data = <<-EOF
                #!/bin/bash
                # Add the MongoDB repository
                echo '[mongodb-org-7.0]
                name=MongoDB Repository
                baseurl=https://repo.mongodb.org/yum/amazon/2/mongodb-org/7.0/x86_64/
                gpgcheck=1
                enabled=1
                gpgkey=https://www.mongodb.org/static/pgp/server-7.0.asc' | sudo tee /etc/yum.repos.d/mongodb-org-7.0.repo
                # Update your system
                sudo yum update -y
                # Install MongoDB
                sudo yum install -y mongodb-org
                # Start the MongoDB service
                sudo systemctl start mongod
                # Enable MongoDB to start on boot
                sudo systemctl enable mongod
                # MongoDB Shell installation for testing
                sudo yum install -y mongodb-mongosh
              EOF
}
*/