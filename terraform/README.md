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

| Name | Source | Version |
|------|--------|---------|
| <a name="module_api_north_virginia"></a> [api\_north\_virginia](#module\_api\_north\_virginia) | ./modules/api | n/a |
| <a name="module_api_sg"></a> [api\_sg](#module\_api\_sg) | ./modules/api | n/a |
| <a name="module_file_processor_north_virginia"></a> [file\_processor\_north\_virginia](#module\_file\_processor\_north\_virginia) | ./modules/file-processor | n/a |
| <a name="module_file_processor_sg"></a> [file\_processor\_sg](#module\_file\_processor\_sg) | ./modules/file-processor | n/a |
| <a name="module_frontend_north_virginia"></a> [frontend\_north\_virginia](#module\_frontend\_north\_virginia) | ./modules/frontend | n/a |
| <a name="module_frontend_sg"></a> [frontend\_sg](#module\_frontend\_sg) | ./modules/frontend | n/a |
| <a name="module_iam"></a> [iam](#module\_iam) | ./modules/iam | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_dynamodb_table.terraform_locks](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table) | resource |
| [aws_s3_bucket.terraform_state](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_s3_bucket_public_access_block.public_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block) | resource |
| [aws_s3_bucket_server_side_encryption_configuration.default](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_server_side_encryption_configuration) | resource |
| [aws_s3_bucket_versioning.enabled](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_versioning) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_github_token"></a> [github\_token](#input\_github\_token) | Github access token | `string` | `"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"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_base_url_calculation_sg"></a> [base\_url\_calculation\_sg](#output\_base\_url\_calculation\_sg) | Base URL for API Gateway for Calculation in SG. |
| <a name="output_base_url_calculation_us"></a> [base\_url\_calculation\_us](#output\_base\_url\_calculation\_us) | Base URL for API Gateway for Calculation in US. |
| <a name="output_base_url_campaign_sg"></a> [base\_url\_campaign\_sg](#output\_base\_url\_campaign\_sg) | Base URL for API Gateway for Campaign in SG. |
| <a name="output_base_url_campaign_us"></a> [base\_url\_campaign\_us](#output\_base\_url\_campaign\_us) | Base URL for API Gateway for Campaign in US. |
| <a name="output_base_url_exclusion_sg"></a> [base\_url\_exclusion\_sg](#output\_base\_url\_exclusion\_sg) | Base URL for API Gateway for Exclusion in SG. |
| <a name="output_base_url_exclusion_us"></a> [base\_url\_exclusion\_us](#output\_base\_url\_exclusion\_us) | Base URL for API Gateway for Exclusion in US. |
| <a name="output_dynamodb_table_name"></a> [dynamodb\_table\_name](#output\_dynamodb\_table\_name) | The name of the DynamoDB table |
| <a name="output_s3_bucket_arn"></a> [s3\_bucket\_arn](#output\_s3\_bucket\_arn) | The ARN of the S3 bucket |
<!-- END_TF_DOCS -->
