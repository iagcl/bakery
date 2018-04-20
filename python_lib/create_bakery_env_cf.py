# Copyright 2017 Insurance Australia Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Module for creating the bakery environment CloudFormation file.
"""
import os
import common
from configuration.initialise_config import BAKERY_VARS

TEMPLATE_SOURCE = os.environ["LOCATION_CORE"] + \
    "/deploy_cloudformation/bakery/templates/bakery_env.tmpl"

TEMPLATE_DESTINATION = os.environ["LOCATION_CORE"] + "/deploy_cloudformation/bakery/bakery_env.yml"

def get_roles(environment, access_type):
    """Gets the role arns for the specified environment and access type.

    Args:
        environment: Environment, e.g. NonProd, Prod, Stg
        access_type: Access type, e.g. Admin, PowerUser, ReadOnly

    Returns:
        String with the role arns
    """
    roles = ""

    for account in environment["Accounts"]:
        if roles:
            roles += "\n"

        roles += "{}- arn:aws:iam::{}:role/{}-{}-{}".format(
            " " * 14,
            account["Id"],
            account["Name"],
            environment["Environment"],
            access_type
        )

    return roles

def get_groups_policies():
    """Gets the CloudFormation snippet for IAM groups and IAM managed policies.

    Returns:
        String with the CloudFormation snippet for IAM groups and IAM policies.
    """
    groups_policies = ""

    for environment in BAKERY_VARS.Environments:
        for access_type in BAKERY_VARS.AccessTypes:
            snippet = \
"""  Group{1}{2}:
    Type: AWS::IAM::Group
    Properties:
      GroupName: {0}{1}{2}

""".format(BAKERY_VARS.TeamName, environment["Environment"], access_type["Type"])

            snippet += \
"""  Policy{1}{2}:
    Type: AWS::IAM::ManagedPolicy
    Properties:
      ManagedPolicyName: {0}{1}{2}
      Description: This policy allows to assume a role
      Groups:
        - !Ref Group{1}{2}
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Action: sts:AssumeRole
            Resource:
__roles__

""".format(
    BAKERY_VARS.TeamName,
    environment["Environment"],
    access_type["Type"]
).replace(
    "__roles__",
    get_roles(environment, access_type["Type"])
)

            groups_policies += snippet

    return groups_policies

def main():
    """Main function."""
    template = common.get_template(TEMPLATE_SOURCE).replace(
        "{{groups_policies}}",
        get_groups_policies()
    )

    common.generate_file(TEMPLATE_DESTINATION, template)

if __name__ == "__main__":
    main()
