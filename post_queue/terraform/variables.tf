variable "EPA_KAFKA_ADMIN_PASSWORD" {
  type      = string
  sensitive = true
  default = "dummy"
}

variable "EPA_KAFKA_PRODUCER_PASSWORD" {
  type      = string
  sensitive = true
  default = "dummy"
}

variable "EPA_KAFKA_CONSUMER_PASSWORD" {
  type      = string
  sensitive = true
  default = "dummy"
}

variable "EPA_KAFKA_CERT_CONTENT" {
  type      = string
  sensitive = true
  default = "dummy"
}

variable "EPA_KAFKA_CERT_KEY" {
  type      = string
  sensitive = true
  default = "dummy"
}