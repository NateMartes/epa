# --- Kafka node count ---
variable node_count {}

# --- EFS File System for Kafka ---
resource "aws_efs_file_system" "kafka_file_system" {
 creation_token = "kafkaefs"
 encrypted = true
  tags = {
    Name = "kafkaefs"
  }
}

# Access points for nodes into the EFS
resource "aws_efs_access_point" "epa_kafka_ap" {
  count          = var.node_count
  file_system_id = aws_efs_file_system.kafka_file_system.id

  # Kafka user/group premissions
  posix_user {
    gid = 1000
    uid = 1000
  }

  root_directory {
    path = "/kafka-node-${count.index}" 
    creation_info {
      owner_gid   = 1000
      owner_uid   = 1000
      permissions = "0755"
    }
  }
}

# --- Tell EFS where to mount the File System ---
variable subnet {}
variable efs_sg {}
resource "aws_efs_mount_target" "efs_mount_target" {
  count           = length(var.subnet.*.id)
  file_system_id  = aws_efs_file_system.kafka_file_system.id
  subnet_id       = var.subnet[count.index].id
  security_groups = [var.efs_sg.id]
}

# --- Logging for the Cluser ---
resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name = "Kafka-Nodes"
  tags = {
    Environment = "production"
    Application = "kafka"
  }
}

# --- ECS Cluster ---
resource "aws_ecs_cluster" "epa_kafka_cluster" {
  name = "epa-kafka-cluster"
  # --- Logging for the Cluser ---
  configuration {
      execute_command_configuration {
        logging = "OVERRIDE"
  
        log_configuration {
          cloud_watch_encryption_enabled = false
          cloud_watch_log_group_name     = aws_cloudwatch_log_group.ecs_log_group.name
        }
      }
  }
}

# --- ECS Task Definition (Bascially, what should a EC2 machine do) ---
variable kafka_dns_namespace {}
variable kafka_discovery_service {}
variable ecs_task_execution_role {}
variable ecs_kafka_task_role {}
variable kafka_admin_password { sensitive = true }
resource "aws_ssm_parameter" "kafka_admin_password_ssm" {
  name  = "/kafka/EPA_KAFKA_ADMIN_PASSWORD"
  type  = "SecureString"
  value = var.kafka_admin_password
  overwrite = true

  lifecycle {
    ignore_changes = [value]
  }
}
variable kafka_producer_password { sensitive = true }
resource "aws_ssm_parameter" "kafka_producer_password_ssm" {
  name  = "/kafka/EPA_KAFKA_PRODUCER_PASSWORD"
  type  = "SecureString"
  value = var.kafka_producer_password
  overwrite = true

  lifecycle {
    ignore_changes = [value]
  }
}
variable kafka_consumer_password { sensitive = true }
resource "aws_ssm_parameter" "kafka_consumer_password_ssm" {
  name  = "/kafka/EPA_KAFKA_CONSUMER_PASSWORD"
  type  = "SecureString"
  value = var.kafka_consumer_password
  overwrite = true

  lifecycle {
    ignore_changes = [value]
  }
}
resource "random_uuid" "cluster_id" {}
resource "aws_ecs_task_definition" "kafka_task_definition" {
  count                    = var.node_count
  family                   = "kafka-node${count.index}"
  requires_compatibilities = ["EC2"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "1024"
  execution_role_arn       = var.ecs_task_execution_role.arn
  task_role_arn            = var.ecs_kafka_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "kafka",
      image     = "apache/kafka:latest",
      cpu       = 256,
      memory    = 1024,
      essential = true,
      command = [
              "sh", 
              "-c",
              <<-EOT
                echo 'Waiting for DNS...'
                sleep 60
                
                echo 'Generating jaas.config file...'
                cat <<EOF > /opt/kafka/config/jaas.conf
                KafkaServer {
                    org.apache.kafka.common.security.plain.PlainLoginModule required
                    user_admin="$EPA_KAFKA_ADMIN_PASSWORD"
                    user_post_producer="$EPA_KAFKA_PRODUCER_PASSWORD"
                    user_post_consumer="$EPA_KAFKA_CONSUMER_PASSWORD";
                };
                EOF
                
                /etc/kafka/docker/run
              EOT
      ]
      portMappings = [
        {
          protocol      = "tcp",
          containerPort = 9092,
          hostPort      = 9092
        },
        {
          protocol      = "tcp",
          containerPort = 9093,
          hostPort      = 9093
        },
        {
          protocol      = "tcp",
          containerPort = 9094,
          hostPort      = 9094
        }
      ],
      mountPoints = [
        {
          sourceVolume  = "kafkaEfsVolume",
          containerPath = "/kafka-data",
          readOnly      = false
        }
      ],
      environment = [
        {
          name  = "KAFKA_NODE_ID"
          value = tostring(count.index)
        },
        {
          name  = "CLUSTER_ID"
          value = random_uuid.cluster_id.result
        },
        {
          name  = "KAFKA_PROCESS_ROLES"
          value = "controller,broker"
        },
        {
          name  = "KAFKA_LISTENERS"
          value = "PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:9094"
        },
        {
          name  = "KAFKA_CFG_ADVERTISED_LISTENERS"
          value = "PLAINTEXT://localhost:9092,EXTERNAL://${var.kafka_discovery_service[count.index].name}.${var.kafka_dns_namespace.name}:9094"
        },
        {
          name = "KAFKA_SASL_ENABLED_MECHANISMS"
          value = "PLAIN"
        },
        {
          name = "KAFKA_SUPER_USERS"
          value = "User:ANONYMOUS;User:admin"
        },
        {
          name = "KAFKA_AUTHORIZER_CLASS_NAME"
          value = "org.apache.kafka.metadata.authorizer.StandardAuthorizer"
        },
        {
          name = "KAFKA_OPTS"
          value = "-Djava.security.auth.login.config=/opt/kafka/config/jaas.conf"
        },
        {
          name  = "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP"
          value = "CONTROLLER:PLAINTEXT,EXTERNAL:SASL_PLAINTEXT,PLAINTEXT:PLAINTEXT"
        },
        {
          name  = "KAFKA_CONTROLLER_LISTENER_NAMES"
          value = "CONTROLLER"
        },
        {
          name  = "KAFKA_CONTROLLER_QUORUM_VOTERS"
          value = join(",", [for id in range(var.node_count) : "${id}@${var.kafka_discovery_service[id].name}.${var.kafka_dns_namespace.name}:9093"])
        },
        {
          name  = "KAFKA_LOG_DIRS",
          value = "/kafka-data"
        },
        {
          name  = "KAFKA_CONNECTION_SETUP_TIMEOUT_MS"
          value = "60000"
        }
      ],
      secrets = [
        {
          name      = "EPA_KAFKA_ADMIN_PASSWORD"
          valueFrom = aws_ssm_parameter.kafka_admin_password_ssm.name
        },
        {
          name      = "EPA_KAFKA_PRODUCER_PASSWORD"
          valueFrom = aws_ssm_parameter.kafka_producer_password_ssm.name
        },
        {
          name      = "EPA_KAFKA_CONSUMER_PASSWORD"
          valueFrom = aws_ssm_parameter.kafka_consumer_password_ssm.name
        },
      ],
      healthCheck = {
        command     = [
          "CMD-SHELL",
          "/opt/kafka/bin/kafka-cluster.sh cluster-id --bootstrap-server localhost:9092"
        ],
        interval    = 30,
        timeout     = 15,
        retries     = 10,
        startPeriod = 120
      },
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_log_group.name,
          "awslogs-region"        = "us-east-1",
          "awslogs-stream-prefix" = "epa-kafka"
        }
      }
    }
  ])
  volume {
      name = "kafkaEfsVolume"
  
      efs_volume_configuration {
        file_system_id     = aws_efs_file_system.kafka_file_system.id
        transit_encryption = "ENABLED"
        authorization_config {
          access_point_id = aws_efs_access_point.epa_kafka_ap[count.index].id
          iam = "ENABLED"
        }
      }
    }
}

# --- The Actual ECS service running Kafka ---
variable kafka_ecs_tasks_sg {}
resource "aws_ecs_service" "epa_kafka_service" {
  count           = var.node_count
  name            = "epa-ecs-kafka-node-${count.index}"
  cluster         = aws_ecs_cluster.epa_kafka_cluster.id
  task_definition = aws_ecs_task_definition.kafka_task_definition[count.index].id
  desired_count   = 1
  launch_type     = "EC2"
  enable_execute_command = true # For automated database setup

  network_configuration {
    subnets          = var.subnet[*].id
    security_groups  = [var.kafka_ecs_tasks_sg.id]
  }

  service_registries {
    registry_arn = var.kafka_discovery_service[count.index].arn
  }

}

# --- EC2 Launch Template ---
variable ec2_instance_profile {}
data "aws_ssm_parameter" "ecs_node_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"
}
resource "aws_launch_template" "epa_ecs_lt" {
  name_prefix   = "epa-ecs-node-"
  image_id      = data.aws_ssm_parameter.ecs_node_ami.value
  instance_type = "t3.small"

  # Make sure the EC2 instance knows it is part of a cluster
  user_data = base64encode(<<-EOF
              #!/bin/bash
              echo "ECS_CLUSTER=${aws_ecs_cluster.epa_kafka_cluster.name}" >> /etc/ecs/ecs.config
              EOF
  )
  
  iam_instance_profile {
    name = var.ec2_instance_profile.name
  }
  
}

# --- Auto Scaling Group ---
resource "aws_autoscaling_group" "epa_ecs_asg" {
  name                = "epa-kafka-ecs-asg"
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
resource "aws_ecs_capacity_provider" "epa_kafka_cp" {
  name = "epa-kafka-capacity-provider"

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.epa_ecs_asg.arn
    managed_scaling {
      status          = "ENABLED"
      target_capacity = 100
    }
  }
}

resource "aws_ecs_cluster_capacity_providers" "epa_cluster_cp" {
  cluster_name       = aws_ecs_cluster.epa_kafka_cluster.name
  capacity_providers = [aws_ecs_capacity_provider.epa_kafka_cp.name]
}