provider "aws" {
  region = "us-west-2"
}

variable node_count {default = 3}

module networking {
  source = "./networking"
}