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
  default = "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"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}