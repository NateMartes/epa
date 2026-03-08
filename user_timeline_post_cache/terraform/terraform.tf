terraform {
  cloud { 
    
    organization = "epa-terraform" 

    workspaces { 
      name = "terraform-github-actions-redis" 
    } 
  }
  
  required_providers {
    upstash = {
      source = "upstash/upstash"
      version = "2.1.0"
    }
  }
}

provider "upstash" {
  api_key  = var.EPA_UPSTASH_API_TOKEN
  email = var.EPA_UPSTASH_EMAIL
}