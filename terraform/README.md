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

| Name                                                   | Version |
| ------------------------------------------------------ | ------- |
| <a name="requirement_aws"></a> [aws](#requirement_aws) | ~> 4.0  |

## Providers

| Name                                             | Version |
| ------------------------------------------------ | ------- |
| <a name="provider_aws"></a> [aws](#provider_aws) | ~> 4.0  |

## Modules

| Name                                                                                                                       | Source                   | Version |
| -------------------------------------------------------------------------------------------------------------------------- | ------------------------ | ------- |
| <a name="module_api_north_virginia"></a> [api_north_virginia](#module_api_north_virginia)                                  | ./modules/api            | n/a     |
| <a name="module_api_sg"></a> [api_sg](#module_api_sg)                                                                      | ./modules/api            | n/a     |
| <a name="module_file_processor_north_virginia"></a> [file_processor_north_virginia](#module_file_processor_north_virginia) | ./modules/file-processor | n/a     |
| <a name="module_file_processor_sg"></a> [file_processor_sg](#module_file_processor_sg)                                     | ./modules/file-processor | n/a     |
| <a name="module_frontend"></a> [frontend](#module_frontend)                                                                | ./modules/frontend       | n/a     |
| <a name="module_iam"></a> [iam](#module_iam)                                                                               | ./modules/iam            | n/a     |

## Resources

| Name                                                                                                                                                                                     | Type     |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [aws_dynamodb_table.terraform_locks](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table)                                                         | resource |
| [aws_s3_bucket.terraform_state](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket)                                                                   | resource |
| [aws_s3_bucket_public_access_block.public_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block)                             | resource |
| [aws_s3_bucket_server_side_encryption_configuration.default](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_server_side_encryption_configuration) | resource |
| [aws_s3_bucket_versioning.enabled](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_versioning)                                                     | resource |

## Inputs

| Name                                                                  | Description         | Type     | Default | Required |
| --------------------------------------------------------------------- | ------------------- | -------- | ------- | :------: |
| <a name="input_github_token"></a> [github_token](#input_github_token) | Github access token | `string` | n/a     |   yes    |

## Outputs

| Name                                                                                         | Description                    |
| -------------------------------------------------------------------------------------------- | ------------------------------ |
| <a name="output_dynamodb_table_name"></a> [dynamodb_table_name](#output_dynamodb_table_name) | The name of the DynamoDB table |
| <a name="output_s3_bucket_arn"></a> [s3_bucket_arn](#output_s3_bucket_arn)                   | The ARN of the S3 bucket       |

<!-- END_TF_DOCS -->
