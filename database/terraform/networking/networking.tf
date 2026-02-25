
data "aws_availability_zones" "available" { state = "available" }

locals {
  azs_count = 2
  azs_names = data.aws_availability_zones.available.names
}

# --- VPC ---
resource "aws_vpc" "mongo_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = { Name = "epa-db-vpc" }
}

# --- Public Subnets (For NAT Gateway) ---
resource "aws_subnet" "mongo_subnet" {
  count                   = local.azs_count
  vpc_id                  = aws_vpc.mongo_vpc.id
  availability_zone       = local.azs_names[count.index]
  cidr_block              = "10.0.${count.index}.0/24"
  tags                    = { Name = "epa-db-public-${local.azs_names[count.index]}" }
}

# --- Private Subnets (For the MongoDB EC2 Instances) ---
resource "aws_subnet" "private_mongo_subnet" {
  count             = local.azs_count
  vpc_id            = aws_vpc.mongo_vpc.id
  availability_zone = local.azs_names[count.index]
  cidr_block        = "10.0.${count.index + 10}.0/24"
  tags              = { Name = "epa-db-private-${local.azs_names[count.index]}" }
}

# --- Internet Gateway ---
resource "aws_internet_gateway" "mongo_internet_gateway" {
  vpc_id = aws_vpc.mongo_vpc.id
  tags   = { Name = "epa-db-internet-gateway" }
}

# --- NAT Gateway & Elastic IP ---
resource "aws_eip" "nat_eip" {
  domain = "vpc"
  tags   = { Name = "epa-nat-eip" }
}
resource "aws_nat_gateway" "mongo_nat" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.mongo_subnet[0].id
  depends_on    = [aws_internet_gateway.mongo_internet_gateway]
  tags          = { Name = "epa-db-nat-gateway" }
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

# --- Private Route Table ---
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.mongo_vpc.id
  tags   = { Name = "epa-db-rt-private" }

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.mongo_nat.id
  }
}
resource "aws_route_table_association" "private_rt_assoc" {
  count          = local.azs_count
  subnet_id      = aws_subnet.private_mongo_subnet[count.index].id
  route_table_id = aws_route_table.private_rt.id
}

# --- Private DNS namespace for MongoDB discovery ---
resource "aws_service_discovery_private_dns_namespace" "mongo_monitoring" {
  name = "node.mongo.epa"
  vpc  = aws_vpc.mongo_vpc.id
}

resource "aws_service_discovery_service" "mongo_discovery_service" {
  count = 3
  name  = "mongodb-${count.index}"
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.mongo_monitoring.id
    dns_records {
      ttl  = 10
      type = "A"
    }
  }
}

# --- DNS Setup for MongoDB SRV and TXT records (needed for clustering) ---
resource "aws_route53_zone" "mongo_cluster" {
  name = "mongo.epa"

  vpc {
    vpc_id = aws_vpc.mongo_vpc.id
  }
}

# Replica set txt record
variable replica_set_name {}
resource "aws_route53_record" "mongo_txt" {
  zone_id = aws_route53_zone.mongo_cluster.zone_id
  name    = "cluster.mongo.epa"
  type    = "TXT"
  ttl     = 300
  
  records = ["authSource=admin&replicaSet=${var.replica_set_name}"]
}

# SRV record for mongodb+srv://
variable node_count {}
resource "aws_route53_record" "mongo_srv" {
  zone_id = aws_route53_zone.mongo_cluster.zone_id
  name    = "_mongodb._tcp.cluster.mongo.epa"
  type    = "SRV"
  ttl     = 300

  records = [
    for i in range(var.node_count) : "0 0 27017 ${aws_service_discovery_service.mongo_discovery_service[i].name}.${aws_service_discovery_private_dns_namespace.mongo_monitoring.name}"
  ]
}