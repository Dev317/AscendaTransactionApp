# Application Setup

There are 3 main branches that govern the production of Waftech application

1. infrastructure
 - project-2022-23t1-g1-team1-infrastructure
2. microservices
 - project-2022-23t1-g1-team1-microservices
3. front-end branches for SG and US region:
 - project-2022-23t1-g1-team1-frontend-ap-southeast-1
 - project-2022-23t1-g1-team1-frontend-us-east-1
  
  


## Terraform resources provision

- Check out to `infrastructure` branch:

    ```
    git switch  - project-2022-23t1-g1-team1-infrastructure
    ```

- Configure AWS credentials, use the G1T1's aws access key and aws secret access key (provided that [aws cli](https://aws.amazon.com/cli/) and [aws-vault](https://github.com/99designs/aws-vault) is installed)

    ```bash
    aws configure
    
    AWS Access Key ID [****************AAAA]: 
    AWS Secret Access Key [****************aaaa]: 
    Default region name [ap-southeast-1]: 
    Default output format [json]:
    ```
- Go into terraform folder and initialise the tf state

   ```bash
   cd terraform
   terraform init
   ```
 
- Terraform files are split into modules for the purpose of resusability and failover. 

    ```
    provider "aws" {
      alias  = "singapore"
      region = "ap-southeast-1"
    }
    
    provider "aws" {
      alias  = "northvirginia"
      region = "us-east-1"
    }

    module "iam" {
        ...
    }

    module "route53" {
        ...
    }

    module "kms" {
        ...
    }
    
    # -----------------------------------
    # Singapore Configuration
    # -----------------------------------
    
    module "acm_sg" {
        ...
    }
    
    module "api_sg" {
        ...
    }
    
    module "file_processor_sg" {
        ...
    }
    
    module "frontend_sg" {
        ...
    }
    
    module "sns_sg" {
        ...
    }
    
    # -----------------------------------
    # North Virginia Configuration
    # -----------------------------------
    module "acm_north_virginia" {
        ...
    }
    
    module "api_north_virginia" {
        ...
    }
    
    module "file_processor_north_virginia" {
        ...
    }
    
    module "frontend_north_virginia" {
        ...
    }
    
    module "sns_us" {
        ...
    }

    ```


- To provision all infrastructure
    
    ```terraform apply```

- To provision a specific module

   ```terraform apply -target module.api_sg```

- To provision a specific resource

   ```terraform apply -target module.api_sg.aws_api_gateway_rest_api.orchestrator_apigw```
   
- To destroy all resources

    ```terraform destroy```

- To destroy a module

    ```terraform destroy -target module.api_sg```

- To destroy a specific resource

    ```terraform destroy -target module.api_sg.aws_api_gateway_rest_api.orchestrator_apigw```


## Amplify front-end setup

- Checkout to any of front-end branch

    ```git switch project-2022-23t1-g1-team1-frontend-ap-southeast-1```
    
- Always pull the amplify for the most updated backend

    ```amplify pull``

- In the situtation that the `amplify` folder does not appear
 
    ``` amplify pull --appId {appID} ```
    
- In the situation that the Cognito authentication is missing

   ``` amplify import auth ```

- If the authentication is mismatched, remove the existing Cognito authentication and reimport

   ``` amplify remove auth ```

- Due to incompatibility issue when building images on Amplify build console, go to the app on Amplify, then to App settings, then to Build settings and under Build image settings, set the package Amplify CLI to the lastest version

- If there is any update to the Amplify backend, please remember to push

  ```amplify push```
  
## Copyright
G1T1 - CS302 - Semester 1 - 2022/2023
