data "aws_availability_zones" "available" { state = "available" }

locals {
  azs_count = 2
  azs_names = data.aws_availability_zones.available.names
}

# --- VPC ---
resource "aws_vpc" "operations_vpc" {
  cidr_block           = "10.4.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = { Name = "epa-operations-vpc" }
}

# --- Public Subnets (For NAT Gateway) ---
resource "aws_subnet" "operations_subnet" {
  count                   = local.azs_count
  vpc_id                  = aws_vpc.operations_vpc.id
  availability_zone       = local.azs_names[count.index]
  cidr_block              = "10.4.${count.index}.0/24"
  tags                    = { Name = "epa-operations-public-${local.azs_names[count.index]}" }
}

# --- Private Subnets ---
resource "aws_subnet" "private_operations_subnet" {
  count             = local.azs_count
  vpc_id            = aws_vpc.operations_vpc.id
  availability_zone = local.azs_names[count.index]
  cidr_block        = "10.4.${count.index + 10}.0/24"
  tags              = { Name = "epa-operations-private-${local.azs_names[count.index]}" }
}

# --- Internet Gateway ---
resource "aws_internet_gateway" "operations_internet_gateway" {
  vpc_id = aws_vpc.operations_vpc.id
  tags   = { Name = "epa-operations-internet-gateway" }
}

# --- NAT Gateway & Elastic IP ---
resource "aws_eip" "nat_eip" {
  domain = "vpc"
  tags   = { Name = "epa-nat-eip" }
}
resource "aws_nat_gateway" "operations_nat" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.operations_subnet[0].id
  depends_on    = [aws_internet_gateway.operations_internet_gateway]
  tags          = { Name = "epa-operations-nat-gateway" }
}

# --- Public Route Table ---
resource "aws_route_table" "operations_route_table" {
  vpc_id = aws_vpc.operations_vpc.id
  tags   = { Name = "epa-operations-rt-public" }

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.operations_internet_gateway.id
  }
}

resource "aws_route_table_association" "operations_route_table_association" {
  count          = local.azs_count
  subnet_id      = aws_subnet.operations_subnet[count.index].id
  route_table_id = aws_route_table.operations_route_table.id
}

# --- Private Route Table ---
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.operations_vpc.id
  tags   = { Name = "epa-operations-rt-private" }

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.operations_nat.id
  }
}
resource "aws_route_table_association" "private_rt_assoc" {
  count          = local.azs_count
  subnet_id      = aws_subnet.private_operations_subnet[count.index].id
  route_table_id = aws_route_table.private_rt.id
}