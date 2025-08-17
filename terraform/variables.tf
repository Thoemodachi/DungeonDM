variable "aws_region" {
  type    = string
  default = "ap-southeast-2"
}

variable "project_name" {
  type    = string
  default = "dungeondm"
}

variable "openai_api_key" {
  type      = string
  default = "PUT_API_HERE"
  
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}