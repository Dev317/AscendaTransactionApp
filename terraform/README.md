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

1. `cd terraform` folder and initialize Terraform to download the defined provider

```bash
terraform init
```

1. Dry run the code to see any changes

```bash
terraform plan
```

1. Run the code to instantiate all the declared resources

```bash
terraform apply
```

Please make sure to update all the resources appropriately.
