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
Module for creating the burger account CloudFormation file.
"""
import os
import common
from configuration.initialise_config import BAKERY_VARS

TEMPLATE_SOURCE = os.environ["LOCATION_CORE"] + \
    "/deploy_cloudformation/burger/templates/burger_account.tmpl"

TEMPLATE_DESTINATION = os.environ["LOCATION_CORE"] + \
    "/deploy_cloudformation/burger/burger_account.yml"

def get_access_type_roles():
    """Gets the CloudFormation snippet for IAM roles.

    Returns:
        String with the CloudFormation snippet for IAM roles.
    """
    access_type_roles = ""

    for access_type in BAKERY_VARS.AccessTypes:
        snippet = \
"  Role" + access_type["Type"] + """:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Statement:
        - Effect: Allow
          Principal:
            AWS: !Sub "arn:aws:iam::${BakeryAccount}:root"
          Action: sts:AssumeRole
      RoleName: !Sub "${AccountName}-${Environment}-""" + access_type["Type"] + "\"\n" + \
"""      ManagedPolicyArns:
      - """ + access_type["PolicyArn"] + "\n\n"

        access_type_roles += snippet

    return access_type_roles

def main():
    """Main function."""
    template = common.get_template(TEMPLATE_SOURCE).replace(
        "{{bakery_account}}",
        BAKERY_VARS.BakeryAccount
    ).replace(
        "{{access_type_roles}}",
        get_access_type_roles()
    )

    common.generate_file(TEMPLATE_DESTINATION, template)

if __name__ == "__main__":
    main()
