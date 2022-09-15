# Terraform

Terraform is an infrastructure-as-code (IaC) tool that can programmatically spin up infrastructure.

The Terraform configuration language is declarative that describes the intended state of the infrastructure

## Installation

- MacOS: use homebrew to install

```bash
brew install terraform
```

- Window: use chocolatey to install

```bash
choco install terraform
```

- Check for Terraform version

```bash
terraform -v
```

## S3 Bucket Configuration

- Replace the name of all the s3 bucket resources with a globally unique name

```python
terraform {

  backend "s3" {
    bucket = "<unique_bucket_name>"
    key    = "terraform.tfstate"
    region = "ap-southeast-1"
  }
}

...

# Create S3 Bucket to store different versions of the code
resource "aws_s3_bucket" "lambda_function_bucket" {
  bucket        = "<unique_bucket_name>"
  force_destroy = true
}

# Create S3 Bucket that accepts files
resource "aws_s3_bucket" "file_upload_bucket" {
  bucket        = "<unique_bucket_name>"
  force_destroy = true
}

...

```

## Run Terraform

`cd terraform` folder and initialize Terraform to download the defined provider

```bash
terraform init
```

Dry run the code to see any changes

```bash
terraform plan
```

Run the code to instantiate all the declared resources

```bash
terraform apply
```

Please make sure to update all the resources appropriately.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 4.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | ~> 4.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_amplify_app.Waftech](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/amplify_app) | resource |
| [aws_amplify_branch.master](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/amplify_branch) | resource |
| [aws_amplify_domain_association.g1t1](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/amplify_domain_association) | resource |
| [aws_cognito_user_pool.fe_userpool](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user_pool) | resource |
| [aws_cognito_user_pool_client.client](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user_pool_client) | resource |
| [aws_cognito_user_pool_domain.itsag1t1](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user_pool_domain) | resource |
| [aws_iam_role.amplify-github](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_route53_record.waffle](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route53_record) | resource |
| [aws_route53_zone.primary](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route53_zone) | resource |
| [aws_iam_policy_document.assume_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.developer_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | AWS region | `string` | `"ap-southeast-1"` | no |
| <a name="input_force_destroy"></a> [force\_destroy](#input\_force\_destroy) | Force deleting a resource | `bool` | `true` | no |
| <a name="input_github_token"></a> [github\_token](#input\_github\_token) | Github access token | `string` | n/a | yes |
| <a name="input_lambda_role"></a> [lambda\_role](#input\_lambda\_role) | Name of IAM lambda role | `string` | `"iam-lambda-role"` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
