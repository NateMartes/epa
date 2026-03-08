output "endpoint" {
  value = upstash_redis_database.epa-redis.endpoint
}

output "redis_password" {
  value = upstash_redis_database.epa-redis.password
  sensitive = true
}