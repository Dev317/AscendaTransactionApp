terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

resource "aws_cognito_user_pool_domain" "itsag1t1" {
  domain       = "g1t1userdomain-${var.waftech_region}"
  user_pool_id = aws_cognito_user_pool.userpool.id
}

resource "aws_cognito_user_pool_client" "client" {
  name = "client-${var.waftech_region}"
  user_pool_id = aws_cognito_user_pool.userpool.id
}

resource "aws_cognito_user_pool_client" "clientWeb" {
  name = "clientWeb-${var.waftech_region}"
  user_pool_id = aws_cognito_user_pool.userpool.id
}

resource "aws_cognito_user_pool" "userpool" {
  name = "userpool-${var.waftech_region}"

  username_attributes = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length = 6
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject = "Account Confirmation"
    email_message = "Your confirmation code is {####}"
  }

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

  lifecycle {
    ignore_changes = [password_policy]
  }

}

resource "aws_cognito_identity_pool" "identity_pool" {
  identity_pool_name               = "identity_pool-${var.waftech_region}"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.client.id
    provider_name           = aws_cognito_user_pool.userpool.endpoint
    server_side_token_check = true
  }
}

resource "aws_cognito_identity_pool_roles_attachment" "main" {
  identity_pool_id = aws_cognito_identity_pool.identity_pool.id

  roles = {
    authenticated   = aws_iam_role.auth_iam_role.arn
    unauthenticated = aws_iam_role.unauth_iam_role.arn
  }
}

resource "aws_iam_role" "auth_iam_role" {
  name = "auth_iam_role-${var.waftech_region}"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Federated": "cognito-identity.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role" "unauth_iam_role" {
  name = "unauth_iam_role-${var.waftech_region}"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Federated": "cognito-identity.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "web_iam_unauth_role_policy" {
  name = "web_iam_unauth_role_policy"
  role = aws_iam_role.unauth_iam_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Action": "*",
      "Effect": "Deny",
      "Resource": "*"
    }
  ]
}
EOF
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

data "aws_iam_policy" "amplify-access-policy" {
  name = "AdministratorAccess-Amplify"
}

resource "aws_iam_role_policy_attachment" "attach-amplify-access-policy" {
  role       = aws_iam_role.amplify-github.name
  policy_arn = data.aws_iam_policy.amplify-access-policy.arn
}

resource "aws_amplify_backend_environment" "dev" {
  app_id               = aws_amplify_app.Waftech.id
  environment_name     = "dev"
  deployment_artifacts = "waftech-deployment-${var.waftech_region}"
  stack_name           = "amplify-Waftech-${var.waftech_region}"
}

resource "aws_amplify_branch" "fe" {
  app_id      = aws_amplify_app.Waftech.id
  branch_name = var.waftech_branch

  lifecycle {
    ignore_changes = [backend_environment_arn]
  }
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
  name                = "AmplifyGithub-${var.waftech_region}"
  assume_role_policy  = join("", data.aws_iam_policy_document.assume_role.*.json)
}

resource "aws_amplify_app" "Waftech" {
  name                        = "waftech-${var.waftech_region}"
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
            - nvm use $VERSION_NODE_14
            - npm ci
        build:
          commands:
            - nvm use $VERSION_NODE_14
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

  environment_variables = {
    AMPLIFY_USERPOOL_ID = aws_cognito_user_pool.userpool.id
    AMPLIFY_WEBCLIENT_ID = aws_cognito_user_pool_client.client.id
    AMPLIFY_NATIVECLIENT_ID = aws_cognito_user_pool_client.clientWeb.id
    AMPLIFY_IDENTITYPOOL_ID = aws_cognito_identity_pool.identity_pool.id
  }

  lifecycle {
    ignore_changes = [build_spec, environment_variables, access_token]
  }
}

resource "aws_cognito_user_group" "admin" {
  name         = "admin"
  user_pool_id = aws_cognito_user_pool.userpool.id
  description  = "admin user group"
}

resource "aws_cognito_user_group" "banker" {
  name         = "banker"
  user_pool_id = aws_cognito_user_pool.userpool.id
  description  = "banker user group"
}

resource "aws_cognito_user_group" "customer" {
  name         = "customer"
  user_pool_id = aws_cognito_user_pool.userpool.id
  description  = "customer user group"
}
