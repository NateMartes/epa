
data "aws_availability_zones" "available" { state = "available" }

locals {
  azs_count = 2
  azs_names = data.aws_availability_zones.available.names
}

# --- VPC ---
resource "aws_vpc" "kafka_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = { Name = "epa-kafka-vpc" }
}

# --- Public Subnets (For NAT Gateway) ---
resource "aws_subnet" "kafka_subnet" {
  count                   = local.azs_count
  vpc_id                  = aws_vpc.kafka_vpc.id
  availability_zone       = local.azs_names[count.index]
  cidr_block              = "10.0.${count.index}.0/24"
  tags                    = { Name = "epa-kafka-public-${local.azs_names[count.index]}" }
}

# --- Private Subnets (For the kafka EC2 Instances) ---
resource "aws_subnet" "private_kafka_subnet" {
  count             = local.azs_count
  vpc_id            = aws_vpc.kafka_vpc.id
  availability_zone = local.azs_names[count.index]
  cidr_block        = "10.0.${count.index + 10}.0/24"
  tags              = { Name = "epa-kafka-private-${local.azs_names[count.index]}" }
}

# --- Internet Gateway ---
resource "aws_internet_gateway" "kafka_internet_gateway" {
  vpc_id = aws_vpc.kafka_vpc.id
  tags   = { Name = "epa-kafka-internet-gateway" }
}

# --- NAT Gateway & Elastic IP ---
resource "aws_eip" "nat_eip" {
  domain = "vpc"
  tags   = { Name = "epa-nat-eip" }
}
resource "aws_nat_gateway" "kafka_nat" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.kafka_subnet[0].id
  depends_on    = [aws_internet_gateway.kafka_internet_gateway]
  tags          = { Name = "epa-kafka-nat-gateway" }
}

# --- Public Route Table ---
resource "aws_route_table" "kafka_route_table" {
  vpc_id = aws_vpc.kafka_vpc.id
  tags   = { Name = "epa-kafka-rt-public" }

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.kafka_internet_gateway.id
  }
}

resource "aws_route_table_association" "kafka_route_table_association" {
  count          = local.azs_count
  subnet_id      = aws_subnet.kafka_subnet[count.index].id
  route_table_id = aws_route_table.kafka_route_table.id
}

# --- Private Route Table ---
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.kafka_vpc.id
  tags   = { Name = "epa-kafka-rt-private" }

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.kafka_nat.id
  }
}
resource "aws_route_table_association" "private_rt_assoc" {
  count          = local.azs_count
  subnet_id      = aws_subnet.private_kafka_subnet[count.index].id
  route_table_id = aws_route_table.private_rt.id
}

# --- Private DNS namespace for kafkaDB discovery ---
resource "aws_service_discovery_private_dns_namespace" "kafka_monitoring" {
  name = "node.kafka.epa"
  vpc  = aws_vpc.kafka_vpc.id
}

variable node_count {}
resource "aws_service_discovery_service" "kafka_discovery_service" {
  count = var.node_count
  name  = "kafka-${count.index}"
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.kafka_monitoring.id
    dns_records {
      ttl  = 10
      type = "A"
    }
  }
}