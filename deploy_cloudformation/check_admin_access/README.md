# Check Admin Access

## Introduction

Check Admin Access is an alerting tool which sends a Slack message informing you if there are any AWS IAM users who are members of AWS Admin IAM groups specified in [configuration/config.yml](../../configuration/config.yml). The value of **AdminGroups** within config.yml is used to identify the admin groups.

We wanted to be alerted of "Principle of least privilege" IAM users who had Admin or PowerUser access to higher environments like Prod or Pre-Prod, and that is why we created this tool.

This tool will come in handy to detect if any users have "higher access" than they might need.

You may choose to deploy this tool, but it is not essential.

## Deployment

An ansible playbook together with a CloudFormation template are used to deploy the components needed. The main components are CloudWatch event rule and Lambda function.

### Steps to Deploy

1. Ensure your Bakery AWS account's credentials are within the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables
2. Run the following commands from the root of the repo
    ```bash
    $ export bakery_cf_bucket=<Name of your S3 bucket>  # Must be already created in your Bakery Account

    $ make deploy-check-admin-access-cf-in-docker
    ```
