terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
  }
  cloud {
      organization = "epa-terraform"
      workspaces {
        name = "terraform-github-actions-operations"
      }
    }
  required_version = ">= 1.2"
}