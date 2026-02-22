terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
  }
  cloud {
      organization = "your-terraform-org-name"
      workspaces {
        name = "epa-workspace-name"
      }
    }
  required_version = ">= 1.2"
}