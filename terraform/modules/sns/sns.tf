terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

resource "aws_sns_topic" "reward_topic" {
  name = "email_reward_topic_${var.sns_region}"
}

