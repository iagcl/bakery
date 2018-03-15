# deploy_cloudformation

This folder contains CloudFormation templates for deploying both Bakery and Burger AWS Accounts.

- For Bakery Deployment, please refer `bakery/README.md`
- For Burger Deployment, please refer `burger/README.md`

## `deploy_bakery.yml`

This is an Ansible file written in YML format. This is the entry point for deploying Bakery in your account. Below are the tasks conducted by this Ansible playbook

1. Uploads Bakery CloudFormation templates to a S3 bucket named 'bakery-cloudformation-deployment' which is hard coded into the playbook. *You should change it to your desired bucket name.*
2. Deploys above CloudFormation templates into Bakery account.
