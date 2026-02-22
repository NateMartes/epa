# --- MongoDB EC2 node count ---
variable node_count {}

# --- EFS File System for MongoDB ---
resource "aws_efs_file_system" "mongo_file_system" {
 creation_token = "mongoefs"
 encrypted = true
  tags = {
    Name = "mongoefs"
  }
}

# Access points for nodes into the EFS
resource "aws_efs_access_point" "epa_mongo_ap" {
  count          = var.node_count
  file_system_id = aws_efs_file_system.mongo_file_system.id

  # MongoDB user/group premissions
  posix_user {
    gid = 999 
    uid = 999
  }

  root_directory {
    path = "/mongo-node-${count.index}" 
    creation_info {
      owner_gid   = 999
      owner_uid   = 999
      permissions = "0755"
    }
  }
}

# --- Tell EFS where to mount the File System ---
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

# --- ECS Task Definition (Bascially, what should a EC2 machine do) ---
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
  count                    = var.node_count
  family                   = "mongolab-mongodb-node${count.index}"
  requires_compatibilities = ["EC2"]
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
          access_point_id = aws_efs_access_point.epa_mongo_ap[count.index].id
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
  count           = var.node_count
  name            = "epa-ecs-mongodb-node-${count.index}"
  cluster         = aws_ecs_cluster.epa_mongo_db_cluster.id
  task_definition = aws_ecs_task_definition.mongo_task_definition[count.index].id
  desired_count   = 1
  launch_type     = "EC2"

  network_configuration {
    subnets          = var.subnet[*].id
    security_groups  = [var.mongo_ecs_tasks_sg.id]
    assign_public_ip = true
  }
  
  load_balancer {
    target_group_arn = var.mongo_tg.arn
    container_name = "mongo"
    container_port = 27017
  }

  service_registries {
    registry_arn = var.mongo_discovery_service[count.index].arn
  }

}


# --- EC2 Launch Template ---
data "aws_ssm_parameter" "ecs_node_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"
}
resource "aws_launch_template" "epa_ecs_lt" {
  name_prefix   = "epa-ecs-node-"
  image_id      = data.aws_ssm_parameter.ecs_node_ami.value
  instance_type = "t3.micro" # Adjust based on your DB requirements

  # Make sure the EC2 instance knows it is part of a cluster
  user_data = base64encode(<<-EOF
              #!/bin/bash
              echo "ECS_CLUSTER=${aws_ecs_cluster.epa_mongo_db_cluster.name}" >> /etc/ecs/ecs.config
              EOF
  )
}

# --- Auto Scaling Group ---
resource "aws_autoscaling_group" "epa_ecs_asg" {
  name                = "epa-mongo-ecs-asg"
  vpc_zone_identifier = var.subnet[*].id
  min_size            = var.node_count
  max_size            = var.node_count
  desired_capacity    = var.node_count

  launch_template {
    id      = aws_launch_template.epa_ecs_lt.id
    version = "$Latest"
  }
}

# --- Capacity Provider for the cluster ---
resource "aws_ecs_capacity_provider" "epa_mongo_cp" {
  name = "epa-mongo-capacity-provider"

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.epa_ecs_asg.arn
    managed_scaling {
      status          = "ENABLED"
      target_capacity = 100
    }
  }
}

resource "aws_ecs_cluster_capacity_providers" "epa_cluster_cp" {
  cluster_name       = aws_ecs_cluster.epa_mongo_db_cluster.name
  capacity_providers = [aws_ecs_capacity_provider.epa_mongo_cp.name]
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