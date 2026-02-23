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

# --- Allow access to MongoDB password and replica set key for ECS ---
variable replica_set_key { sensitive = true }
variable mongodb_secret_password { sensitive = true }
resource "aws_iam_policy" "ecs_ssm_parameter_access" {
  name        = "ssm_parameter_access"
  description = "Allow ECS tasks to access SSM parameters"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath",
          "kms:Decrypt"
        ]
        Resource = [
          var.mongodb_secret_password.arn,
          var.replica_set_key.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name_prefix        = "epa-db-ecs-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_role_policy.json
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_node_ssm_policy" {
  role       = aws_iam_role.ecs_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ecs_ssm_access_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_ssm_parameter_access.arn
}


# --- ECS Task Role (For access for the containers running MongoDB to AWS stuff) ---
data "aws_iam_policy_document" "ecs_mongo_task_role_policy" {
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
variable mongo_file_system {}
resource "aws_iam_policy" "ecs_efs_access_policy" {
  name        = "ecs_efs_access_policy"
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
        Resource = [var.mongo_file_system.arn]
      },
    ]
  })
}

resource "aws_iam_role" "ecs_mongo_task_role" {
  name_prefix        = "epa-db-ecs-mongo-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_mongo_task_role_policy.json
}

resource "aws_iam_role_policy_attachment" "ecs_efs_access_policy_attachment" {
  role       = aws_iam_role.ecs_mongo_task_role.name
  policy_arn = aws_iam_policy.ecs_efs_access_policy.arn
}

# --- For ECS Exec Access ---
resource "aws_iam_role_policy" "ecs_exec_ssm_policy" {
  name = "ecs-exec-ssm-and-logging-policy"  
  role = aws_iam_role.ecs_mongo_task_role.name 

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
  name = "epa-ecs-node-role"
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
  name = "epa-ecs-node-profile"
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

# --- MongoDB access on default port ---
resource "aws_security_group" "mongo_ecs_tasks_sg" {
  name        = "mongo-ecs-tasks-sg"
  description = "Security group for ECS MongoDB tasks"
  vpc_id      = var.vpc.id
  
  ingress {
    from_port       = 27017
    to_port         = 27017
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
    Name = "mongo-ecs-tasks-sg"
  }
}

# --- MongoDB access for the data from EFS (Elastic File System), on the default NFS port ---
resource "aws_security_group" "efs_sg" {
  name        = "efs-mongolab-sg"
  description = "Security group for EFS"
  vpc_id      = var.vpc.id
  
  ingress {
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    cidr_blocks = [var.vpc.cidr_block]
  }
}