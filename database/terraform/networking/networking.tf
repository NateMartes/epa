# --- VPC ---

data "aws_availability_zones" "available" { state = "available" }

locals {
  azs_count = 2
  azs_names = data.aws_availability_zones.available.names
}

resource "aws_vpc" "mongo_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = { Name = "epa-db-vpc" }
}

resource "aws_subnet" "mongo_subnet" {
  count                   = local.azs_count
  vpc_id                  = aws_vpc.mongo_vpc.id
  availability_zone       = local.azs_names[count.index]
  cidr_block              = "10.0.${count.index}.0/24"
  map_public_ip_on_launch = true
  tags                    = { Name = "epa-db-public-${local.azs_names[count.index]}" }
}

# --- Internet Gateway ---

resource "aws_internet_gateway" "mongo_internet_gateway" {
  vpc_id = aws_vpc.mongo_vpc.id
  tags   = { Name = "epa-db-internet-gateway" }
}

resource "aws_eip" "main" {
  count      = local.azs_count
  depends_on = [aws_internet_gateway.mongo_internet_gateway]
  tags       = { Name = "epa-eip-${local.azs_names[count.index]}" }
}

# --- Public Route Table ---

resource "aws_route_table" "mongo_route_table" {
  vpc_id = aws_vpc.mongo_vpc.id
  tags   = { Name = "epa-db-rt-public" }

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.mongo_internet_gateway.id
  }
}

resource "aws_route_table_association" "mongo_route_table_association" {
  count          = local.azs_count
  subnet_id      = aws_subnet.mongo_subnet[count.index].id
  route_table_id = aws_route_table.mongo_route_table.id
}

# --- Private DNS namespace for MongoDB discovery ---
resource "aws_service_discovery_private_dns_namespace" "mongo_monitoring" {
  name = "mongo.local"
  vpc  = aws_vpc.mongo_vpc.id
}

resource "aws_service_discovery_service" "mongo_discovery_service" {
  name = "mongodb"
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.mongo_monitoring.id
    dns_records {
      ttl  = 10
      type = "A"
    }
  }
  health_check_custom_config {
    failure_threshold = 1
  }
}