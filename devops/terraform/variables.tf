variable "STAGE" {
  type = string
  default = "ENVPREFIX"
}

variable "pgdatabase" {
  type = string
  default = "ENVPREFIX_reclada_k8s"
}

variable "pghost" {
  type = string
  default = "RDSINSTANCE"
}

variable "pgpassword" {
  type = string
  default = "PGPASSWORD"
}

variable "pguser" {
  type = string
  default = "reclada"
}

variable "company" {
  default = "infra"
}

variable "project" {
  default = "prj"
}

variable "env" {
  default = "dev"
}

variable "vpc_name" {
  description = "VPC Infra"
  type        = string
  default     = "eks-infra-vpc"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  default = [
    "10.0.0.0/19",
    "10.0.32.0/19",
  ]
}

variable "private_subnet_cidrs" {
  default = [
    "10.0.64.0/19",
    "10.0.96.0/19",
  ]
}

variable "db_subnet_cidrs" {
  default = [
    "10.0.128.0/19",
    "10.0.160.0/19",
  ]
}

variable "shared_tags" {
  default = {
    Project   = "MVPP"
    Env       = "dev"
    Owner     = "maksim.vasilev@quantori.com"
  }
}

