terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

resource "aws_cognito_user_pool_domain" "itsag1t1" {
  domain       = "g1t1userdomain${var.waftech_region}"
  user_pool_id = aws_cognito_user_pool.userpool.id
}

resource "aws_cognito_user_pool_client" "client" {
  name = "client${var.waftech_region}"
  user_pool_id = aws_cognito_user_pool.userpool.id
}

resource "aws_cognito_user_pool" "userpool" {
  name = "userpool${var.waftech_region}"

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }

    recovery_mechanism {
      name     = "verified_phone_number"
      priority = 2
    }
  }
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["amplify.amazonaws.com"]
    }
  }
}

resource "aws_amplify_backend_environment" "dev" {
  app_id               = aws_amplify_app.Waftech.id
  environment_name     = "dev"
}

resource "aws_amplify_branch" "fe" {
  app_id      = aws_amplify_app.Waftech.id
  branch_name = var.waftech_branch
}

# resource "aws_amplify_domain_association" "g1t1" {
#   app_id      = aws_amplify_app.Waftech.id
#   domain_name = "itsag1t1.com"

#   sub_domain {
#     branch_name = aws_amplify_branch.fe.branch_name
#     prefix      = ""
#   }

#   # https://www.example.com
#   sub_domain {
#     branch_name = aws_amplify_branch.fe.branch_name
#     prefix      = "www"
#   }
# }

resource "aws_iam_role" "amplify-github" {
  name                = "AmplifyGithub${var.waftech_region}"
  assume_role_policy  = join("", data.aws_iam_policy_document.assume_role.*.json)
}

resource "aws_amplify_app" "Waftech" {
  name                        = "Waftech ${var.waftech_region}"
  description                 = "Frontend for Waftech"
  repository                  = "https://github.com/cs301-itsa/project-2022-23t1-g1-t1-waffles"
  access_token                = var.github_token
  iam_service_role_arn        = aws_iam_role.amplify-github.arn
  enable_branch_auto_build    = true

  build_spec = <<-EOT
    version: 1
    backend:
      phases:
        build:
          commands:
            - '# Execute Amplify CLI with the helper script'
            - amplifyPush --simple
    frontend:
      phases:
        preBuild:
          commands:
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: build
        files:
          - '**/*'
      cache:
  EOT

  custom_rule {
    source = "/<*>"
    status = "404"
    target = "/index.html"
  }
}
