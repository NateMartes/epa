# --- ECS Task Execution Role (For access to pull from ECR) ---

data "aws_iam_policy_document" "ecs_task_execution_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name_prefix        = "epa-kafka-ecs-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_role_policy.json
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# --- ECS Task Role (For access for the containers running Kafka to AWS stuff) ---
data "aws_iam_policy_document" "ecs_kafka_task_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# --- ECS access to EFS ---
variable kafka_file_system {}
resource "aws_iam_policy" "ecs_efs_access_policy" {
  name        = "ecs_kafka_efs_access_policy"
  description = "Allow ECS tasks to access EFS"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "elasticfilesystem:ClientMount",
          "elasticfilesystem:ClientWrite",
          "elasticfilesystem:DescribeFileSystems",
          "elasticfilesystem:DescribeMountTargets"
        ]
        Effect = "Allow"
        Resource = [var.kafka_file_system.arn]
      },
    ]
  })
}

resource "aws_iam_role" "ecs_kafka_task_role" {
  name_prefix        = "epa-kafka-ecs-mongo-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_kafka_task_role_policy.json
}

resource "aws_iam_role_policy_attachment" "ecs_efs_access_policy_attachment" {
  role       = aws_iam_role.ecs_kafka_task_role.name
  policy_arn = aws_iam_policy.ecs_efs_access_policy.arn
}

# --- For ECS Exec Access ---
resource "aws_iam_role_policy" "ecs_exec_ssm_policy" {
  name = "ecs-kafka-exec-ssm-and-logging-policy"  
  role = aws_iam_role.ecs_kafka_task_role.name 

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups",
          "logs:CreateLogStream",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# --- EC2 Instance Role ---
resource "aws_iam_role" "ecs_node_role" {
  name = "epa-ecs-kafka-node-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_node_role_policy" {
  role       = aws_iam_role.ecs_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role" 
}

resource "aws_iam_instance_profile" "ecs_node_profile" {
  name = "epa-kafka-ecs-node-profile"
  role = aws_iam_role.ecs_node_role.name
}

# --- Security Groups ---
variable vpc {}

# --- SSH access to EC2's in cluster ---
/* FOR TESTING
resource "aws_security_group" "ec2_sg" {
  description = "Security group for EC2 instance"
  name_prefix = "epa-db-ecs-node-sg-"
  vpc_id      = var.vpc.id
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
} */

# --- Kafka access on default ports ---
resource "aws_security_group" "kafka_ecs_tasks_sg" {
  name        = "kafka-ecs-tasks-sg"
  description = "Security group for ECS Kafka tasks"
  vpc_id      = var.vpc.id
  
  ingress {
    from_port       = 9092
    to_port         = 9092
    protocol        = "tcp"
    
    # This should be changed to the CIDR block of a VPC for production
    cidr_blocks      = ["0.0.0.0/0"] 
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "kafka-ecs-tasks-sg"
  }
}

resource "aws_security_group_rule" "kafka_internal_communication_9093" {
  type                     = "ingress"
  from_port                = 9093
  to_port                  = 9093
  protocol                 = "tcp"
  security_group_id        = aws_security_group.kafka_ecs_tasks_sg.id
  source_security_group_id = aws_security_group.kafka_ecs_tasks_sg.id
  description              = "Allow Kafka KRaft internal controller traffic"
}

resource "aws_security_group_rule" "kafka_external_communication_9094" {
  type                     = "ingress"
  from_port                = 9094
  to_port                  = 9094
  protocol                 = "tcp"
  security_group_id        = aws_security_group.kafka_ecs_tasks_sg.id
  source_security_group_id = aws_security_group.kafka_ecs_tasks_sg.id
  description              = "Allow Kafka external traffic"
}

# --- Kafka access for the data from EFS (Elastic File System), on the default NFS port ---
resource "aws_security_group" "efs_sg" {
  name        = "efs-kafka-sg"
  description = "Security group for EFS"
  vpc_id      = var.vpc.id
  
  ingress {
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    cidr_blocks = [var.vpc.cidr_block]
  }
}