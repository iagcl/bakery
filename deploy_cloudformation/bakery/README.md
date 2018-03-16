# Bakery

This folder contains CloudFormation templates written in YML format.

## `bakery_stack.yml`

This CloudFormation template creates below nested CloudFormation stacks.

### (1) `bakery_account.yml`

This CloudFormation nested stack creates below resources in your Bakery AWS account.

- `BakeryAdminsGroup` *(An IAM group with Administrator access).*
- `BakeryUsersGroup` *(An IAM group with Read Only access to IAM).*
- `BakeryUsersPolicy` *(An IAM Managed Policy linked attached to *'BakeryUsersGroup'* which allow users to manage their password and MFA devices).*

### (2) `bakery_env.yml`

This CloudFormation nested stack is triggered recursively by `bakery_stack.yml` for each 'Environment' (i.e. Prod, NonProd, Mgmt) and 'AccessType' (i.e. Admin, PowerUser, ReadOnly) to create following resources.

- `AccessTypeGroup` *(An IAM group for each 'environment' and 'access type').*
- `AccessTypeGroupPolicy` *(An IAM Managed Policy attached to above 'AccessTypeGroup' which allows STS access).*

> Please note that this template has a section called **Mappings** which __must be updated manually as per your business needs__. Mappings section defines the access level for each of your **Burger AWS Accounts**.

An example is already given in the template file which has following configuration:

| Environment | AccessType | IAM Roles (Burger accounts) |
|-------------|------------|---------------------------------------------------------------------------------------------------------------|
| NonProd | Admin | arn:aws:iam::222222222222:role/BurgerIAMBakeryNonProdAdmins, <br/> arn:aws:iam::333333333333:role/BurgerIAMBakeryNonProdAdmins |
|  | PowerUser | arn:aws:iam::222222222222:role/BurgerIAMBakeryNonProdPowerUser,<br/> arn:aws:iam::333333333333:role/BurgerIAMBakeryNonProdPowerUser |
|  | ReadOnly | arn:aws:iam::222222222222:role/BurgerIAMBakeryNonProdReadOnly,<br/> arn:aws:iam::333333333333:role/BurgerIAMBakeryNonProdReadOnly |
| Prod | Admin | arn:aws:iam::444444444444:role/BurgerIAMBakeryProdAdmins |
|  | PowerUser | arn:aws:iam::444444444444:role/BurgerIAMBakeryProdPowerUser |
|  | ReadOnly | arn:aws:iam::444444444444:role/BurgerIAMBakeryProdReadOnly |
| Mgmt | Admin | arn:aws:iam::555555555555:role/BurgerIAMBakeryMgmtAdmins |
|  | PowerUser | arn:aws:iam::555555555555:role/BurgerIAMBakeryMgmtPowerUser |
|  | ReadOnly | arn:aws:iam::555555555555:role/BurgerIAMBakeryMgmtReadOnly |

From the table above, if you read the first row, you can say that an IAM group named 'NonProdAdmin' (Environment+AccessType) will be created in Bakery AWS account with corresponding role assignment for STS access to Burger AWS Accounts as follows:

  ```text
  arn:aws:iam::222222222222:role/BurgerIAMBakeryNonProdAdmins
  arn:aws:iam::333333333333:role/BurgerIAMBakeryNonProdAdmins
  ```

This also means that above mentioned roles must be already created into your Burger AWS Account.

#### How to create above STS roles in Burger AWS Account?

You must deploy Burger CloudFormation Stack into Burger AWS Account which will automatically create necessary roles as per your config. Please refer Burger readme file located in folder 'burger'.

#### In what circumstances you would update `bakery_env.yml` file?

1. You want to add more Access Types.
2. You want to add more Environment Types.
3. You want to onboard new AWS Account as Burger.

***

## Customizing Bakery

## Adding more Access Types

By default the template supports three levels of access types i.e. 'Admin', 'PowerUser', and 'ReadOnly'. However, if you need to add more access type you need to update below three files.

- `../burger/burger_account.yml`
- `bakery_env.yml`
- `bakery_stack.yml`

#### Example use case: You want to add a new Access Type called 'EC2FullAccess' in your Production AWS Account (Burger) '444444444444'.

<br>

- **Step 1: Update `../burger/burger_account.yml`**

  Add a snippet mentioned below

  ```yml
  EC2FullAccess:
    Type: "AWS::IAM::Role"
    Properties:
      AssumeRolePolicyDocument:
        Statement:
        - Effect: Allow
          Principal:
            AWS: !Sub "arn:aws:iam::${BakeryAccount}:root"
          Action: sts:AssumeRole
      RoleName: !Sub BurgerIAMBakeryStagingEC2FullAccess
      ManagedPolicyArns:
      - arn:aws:iam::aws:policy/AmazonEC2FullAccess
  ```

<br>

- **Step 2: Deploy `../burger/burger_account.yml` to your Prod Burger Account.**

  Login to AWS Management Console of your prod account '444444444444', and deploy/update the CloudFormation template created in step 1 above. You will be asked for entering parameters, please enter as mentioned below.

  ```text
  TeamName = IAMBakery
  BakeryAccount = 111111111111 (replace with your Bakery AWS Account)
  Environment = Prod
  ```
<br>

- **Step 3: Update `bakery_env.yml`**

  Update **Prod** section under **Mappings** with the snippet below.

  ```yml
  EC2FullAccess:
    roles: arn:aws:iam::444444444444:role/BurgerIAMBakeryProdEC2FullAccess
  ```

  So, the 'Prod' section should look like this

  ```yml
  Prod:
    Admin:
      roles: arn:aws:iam::444444444444:role/BurgerIAMBakeryProdAdmins
    PowerUser:
      roles: arn:aws:iam::444444444444:role/BurgerIAMBakeryProdPowerUser
    ReadOnly:
      roles: arn:aws:iam::444444444444:role/BurgerIAMBakeryProdReadOnly
    EC2FullAccess:
      roles: arn:aws:iam::444444444444:role/BurgerIAMBakeryProdEC2FullAccess
  ```

<br>

- **Step 4: Update `bakery_stack.yml`**

  Add the snippet below

  ```yml
  ProdEC2FullAccess:
    Type: "AWS::CloudFormation::Stack"
    Properties:
      TemplateURL: !Sub "https://s3.amazonaws.com/${CloudFormationS3Bucket}/bakery_env.yml"
      Parameters:
        Environment: Prod
        AccessType: EC2FullAccess
  ```

<br>

- **Step 5: Re-deploy Bakery Stack**

  This step will deploy the changes made in steps 3 and 4 above to the Bakery account.

  ```bash
  $ export AWS_ACCESS_KEY_ID=#your access Bakery account key here
  $ export AWS_SECRET_ACCESS_KEY=#your access Bakery account secret access key here
  $ export AWS_SESSION_TOKEN=#your access Bakery account STS session token here
  $ export bakery_cf_bucket=#S3 bucket name here (where the cloudformation templates will be stored)
  $ make deploy-bakery-cf-in-docker
  ```

***

## Adding new Environments, and on-boarding new AWS Account

By default, the Bakery stack comes with three environments i.e. Prod, NonProd, and Mgmt. However, if you like to add a new environment type, you need to make corresponding changes in the files below.

- `../burger/burger_account.yml`
- `bakery_env.yml`
- `bakery_stack.yml`

#### Example use case: You have a new AWS account with ID '666666666666' and you want to use it as a 'staging' environment.

This example covers:

1. Adding new Environment type called 'staging'
2. On-boarding new AWS Account as Burger

<br>

- **Step 1: Update `../burger/burger_account.yml`**

  Add keyword 'Staging' in AllowedValues section. So the Environment section should look like this

  ```yml
  Environment:
    Description: "Please enter NonProd, Prod, Mgmt, or Staging"
    Type: String
    AllowedValues:
    - NonProd
    - Prod
    - Mgmt
    - Staging
  ```

<br>

- **Step 2: Deploy `../burger/burger_account.yml` to your Staging Burger Account.**

  Login to AWS Management Console of your Staging account '666666666666', and deploy the CloudFormation template created in step 1 above. You will be asked for entering parameters, please enter as mentioned below.

  ```text
  TeamName = IAMBakery
  BakeryAccount = 111111111111 (replace with your Bakery AWS Account)
  Environment = Staging
  ```

  This stack will create below three IAM Roles in your staging account:

  - BurgerIAMBakeryStagingAdmins
  - BurgerIAMBakeryStagingPowerUser
  - BurgerIAMBakeryStagingReadOnly

<br>

- **Step 3: Update `bakery_env.yml`**

  Add a new section called **Staging** section under **Mappings** with the snippet below.

  ```yml
  Staging:
    Admin:
      roles: arn:aws:iam::666666666666:role/BurgerIAMBakeryStagingAdmins
    PowerUser:
      roles: arn:aws:iam::666666666666:role/BurgerIAMBakeryStagingPowerUser
    ReadOnly:
      roles: arn:aws:iam::666666666666:role/BurgerIAMBakeryStagingReadOnly
  ```

<br>

- **Step 4: Update `bakery_stack.yml`**

  Add the snippet below

  ```yml
  StagingAdmin:
    Type: "AWS::CloudFormation::Stack"
    Properties:
      TemplateURL: !Sub "https://s3.amazonaws.com/${CloudFormationS3Bucket}/bakery_env.yml"
      Parameters:
        Environment: Staging
        AccessType: Admin

  StagingPowerUser:
    Type: "AWS::CloudFormation::Stack"
    Properties:
      TemplateURL: !Sub "https://s3.amazonaws.com/${CloudFormationS3Bucket}/bakery_env.yml"
      Parameters:
        Environment: Staging
        AccessType: PowerUser

  StagingReadOnly:
    Type: "AWS::CloudFormation::Stack"
    Properties:
      TemplateURL: !Sub "https://s3.amazonaws.com/${CloudFormationS3Bucket}/bakery_env.yml"
      Parameters:
        Environment: Staging
        AccessType: ReadOnly
  ```

<br>

- **Step 5: Re-deploy Bakery Stack**

  This step will deploy the changes made in steps 3 and 4 above to the Bakery account.

  ```bash
  $ export AWS_ACCESS_KEY_ID=#your access Bakery account key here
  $ export AWS_SECRET_ACCESS_KEY=#your access Bakery account secret access key here
  $ export AWS_SESSION_TOKEN=#your access Bakery account STS session token here
  $ export bakery_cf_bucket=#S3 bucket name here (where the cloudformation templates will be stored)
  $ make deploy-bakery-cf-in-docker
  ```
