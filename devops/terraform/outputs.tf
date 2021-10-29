output "rds_subnets" {
  value = module.vpc.database_subnets
}

output "default_security_group" {
  value = module.vpc.default_security_group_id
}