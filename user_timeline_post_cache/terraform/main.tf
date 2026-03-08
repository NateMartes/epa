resource "upstash_redis_database" "epa-redis" {
  database_name = "epa-redis"
  region         = "global"
  primary_region = "us-east-1"
  tls            = "true"
}