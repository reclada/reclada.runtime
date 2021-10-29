module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.2.0"
  name    = var.vpc_name
  cidr    = var.vpc_cidr

  azs                  = slice(data.aws_availability_zones.azs.names, 0, 2)
  database_subnets     = var.db_subnet_cidrs
  private_subnets      = var.private_subnet_cidrs
  public_subnets       = var.public_subnet_cidrs
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  tags = var.shared_tags
}
