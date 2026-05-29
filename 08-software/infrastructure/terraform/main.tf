# CDOS Infrastructure — Terraform configuration
# Implements: TR-050 (Infrastructure as Code), 04-technical-design/deployment-design.md
#
# This provides the base AWS infrastructure for CDOS:
# - VPC networking
# - RDS PostgreSQL with pgvector
# - Amazon MSK (Kafka)
# - EKS Kubernetes cluster
# - S3 for object storage

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
  }

  backend "s3" {
    bucket         = "cdos-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "cdos-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CDOS"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------
variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.large"
}

variable "eks_node_instance_type" {
  description = "EKS node instance type"
  type        = string
  default     = "m6i.xlarge"
}

# ---------------------------------------------------------------------------
# VPC
# ---------------------------------------------------------------------------
resource "aws_vpc" "cdos" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "cdos-${var.environment}-vpc" }
}

resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.cdos.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = { Name = "cdos-${var.environment}-private-${count.index}" }
}

resource "aws_subnet" "public" {
  count                   = 3
  vpc_id                  = aws_vpc.cdos.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 100)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = { Name = "cdos-${var.environment}-public-${count.index}" }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# ---------------------------------------------------------------------------
# RDS PostgreSQL with pgvector
# Implements: TR-005 (Database), 03-technical-requirements
# ---------------------------------------------------------------------------
resource "aws_db_subnet_group" "cdos" {
  name       = "cdos-${var.environment}-db"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_rds_cluster" "cdos" {
  cluster_identifier      = "cdos-${var.environment}"
  engine                  = "aurora-postgresql"
  engine_version          = "15.4"
  database_name           = "cdos"
  master_username         = "cdos_admin"
  master_password         = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.cdos.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  backup_retention_period = 35
  deletion_protection     = var.environment == "prod"
  storage_encrypted       = true

  tags = { Name = "cdos-${var.environment}-rds" }
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

resource "aws_rds_cluster_instance" "cdos" {
  count              = var.environment == "prod" ? 3 : 1
  identifier         = "cdos-${var.environment}-${count.index}"
  cluster_identifier = aws_rds_cluster.cdos.id
  instance_class     = var.db_instance_class
  engine             = aws_rds_cluster.cdos.engine
  engine_version     = aws_rds_cluster.cdos.engine_version
}

# ---------------------------------------------------------------------------
# Amazon MSK (Kafka)
# Implements: TR-040 (Event-Driven Architecture)
# ---------------------------------------------------------------------------
resource "aws_msk_cluster" "cdos" {
  cluster_name           = "cdos-${var.environment}"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = var.environment == "prod" ? 6 : 3

  broker_node_group_info {
    instance_type  = "kafka.m5.large"
    client_subnets = aws_subnet.private[*].id
    storage_info {
      ebs_storage_info {
        volume_size = 1000
      }
    }
    security_groups = [aws_security_group.msk.id]
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
    encryption_at_rest_kms_key_arn = aws_kms_key.cdos.arn
  }

  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = true
        log_group = aws_cloudwatch_log_group.cdos.name
      }
    }
  }

  tags = { Name = "cdos-${var.environment}-msk" }
}

# ---------------------------------------------------------------------------
# EKS Cluster
# Implements: TR-050 (Kubernetes Deployment)
# ---------------------------------------------------------------------------
resource "aws_eks_cluster" "cdos" {
  name     = "cdos-${var.environment}"
  role_arn = aws_iam_role.eks.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = aws_subnet.private[*].id
    endpoint_private_access = true
    endpoint_public_access  = var.environment != "prod"
    security_group_ids      = [aws_security_group.eks.id]
  }

  encryption_config {
    resources = ["secrets"]
    provider {
      key_arn = aws_kms_key.cdos.arn
    }
  }

  tags = { Name = "cdos-${var.environment}-eks" }
}

# ---------------------------------------------------------------------------
# Security Groups
# ---------------------------------------------------------------------------
resource "aws_security_group" "rds" {
  name        = "cdos-${var.environment}-rds"
  description = "CDOS RDS security group"
  vpc_id      = aws_vpc.cdos.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "msk" {
  name        = "cdos-${var.environment}-msk"
  description = "CDOS MSK security group"
  vpc_id      = aws_vpc.cdos.id

  ingress {
    from_port       = 9094
    to_port         = 9094
    protocol        = "tcp"
    security_groups = [aws_security_group.eks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "eks" {
  name        = "cdos-${var.environment}-eks"
  description = "CDOS EKS security group"
  vpc_id      = aws_vpc.cdos.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------------------------------------------------------------------------
# Supporting Resources
# ---------------------------------------------------------------------------
resource "aws_kms_key" "cdos" {
  description             = "CDOS ${var.environment} encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_cloudwatch_log_group" "cdos" {
  name              = "/cdos/${var.environment}"
  retention_in_days = 90
}

resource "aws_iam_role" "eks" {
  name = "cdos-${var.environment}-eks"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
output "rds_endpoint" {
  description = "RDS cluster endpoint"
  value       = aws_rds_cluster.cdos.endpoint
}

output "msk_bootstrap_brokers" {
  description = "MSK bootstrap broker addresses"
  value       = aws_msk_cluster.cdos.bootstrap_brokers_tls
}

output "eks_cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = aws_eks_cluster.cdos.endpoint
}
