terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region     = "ap-southeast-2"
  access_key = "AKIAXZOQQX5N22KFDK72"
  secret_key = "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"
}

# convenience
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
