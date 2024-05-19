# AWS Account Support Tier Update Automation

This project contains a CloudFormation template designed to automate the process of updating the support tier for newly created AWS accounts to a specified level. It leverages AWS Lambda and the AWS Support API to programmatically create support cases, aiming to simplify account management and ensure the desired support level is applied to each new account. </br>
- Due to restrictions that support API can be used only by **Business, Enterprise On-Ramp, or Enterprise Support plan** as described here: https://docs.aws.amazon.com/awssupport/latest/user/about-support-api.html this automation will work only when run from Organizatinal root account only!

## Features

- **Automatic Support Tier Update**: Automatically updates the support tier of new AWS accounts to a specified level (basic, business, or enterprise) by creating support cases through the AWS Support API.
- **Customizable Support Level**: Allows the specification of the desired support level via CloudFormation parameters, providing flexibility across different environments and requirements.
- **CloudFormation Deployment**: Easy deployment and management through AWS CloudFormation, encapsulating resources provisioning and configuration in a single template.

## Prerequisites

- AWS Account with permissions to create AWS CloudFormation stacks, AWS Lambda functions, and IAM roles.
- An existing AWS Support subscription that allows for the creation of support cases via the AWS Support API.

## Installation

1. **Prepare the CloudFormation Template**: Ensure the provided CloudFormation template is accessible, either by saving it locally or by uploading it to an S3 bucket.
2. **Launch the CloudFormation Stack**:
   - Navigate to the AWS CloudFormation console.
   - Choose *Create stack* > *With new resources (standard)*.
   - Upload the CloudFormation template file or input the S3 URL of the template.
   - Specify stack details as required, including the desired support level under the `Parameters` section.
   - Follow the prompts to create the stack, acknowledging that AWS CloudFormation might create IAM resources with custom names.

## Usage

Once the CloudFormation stack is successfully deployed, the automation takes effect for new AWS account creations within your organization. The Lambda function triggered during the account creation process checks the current support plan and updates it by creating a support case if the plan does not match the specified level.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
