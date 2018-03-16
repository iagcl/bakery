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
import boto3
BAKERY_ENV_GROUPS = ['NonProd','Prod','Mgmt']

ASSUME_TEMP = """
#!/bin/bash
#set -e

if [ "$1" == "-h" ]; then
  echo "usage: source assume.sh [-h] {{number}}
example:
    * source assume.sh
    * source assume.sh 0
    * source assume.sh -h
where:
    {{number}} role number (optional)
    -h  show this help text"
  return
fi
if [ "$#" -gt 0 ]; then
    user_option=$1
else
    user_option=""
fi
roles=()
role_num=""

get_roles(){{
    roles=({0})
}}

interactivly_pick_role(){{
  echo "Roles Available To Assume:"
    for i in "${{!roles[@]}}"; do
      printf "%s\t%s\n" "$i" "${{roles[$i]}}"
    done
  echo Pick a role:
  read role_number
  role_num=$role_number
}}

assume_role(){{
  local temp_role=$(aws sts assume-role \
                --role-arn ${{roles[$1]}} \
                --role-session-name assumeRoleSession \
                --profile default --no-verify-ssl)

  [ "$temp_role" ] || {{ echo "aws sts assume-role failed" ; return; }}

  export AWS_ACCESS_KEY_ID=$(echo $temp_role | jq -r .Credentials.AccessKeyId)
  export AWS_SECRET_ACCESS_KEY=$(echo $temp_role | jq -r .Credentials.SecretAccessKey)
  export AWS_SESSION_TOKEN=$(echo $temp_role | jq -r .Credentials.SessionToken)

  env | grep -i AWS_
}}

clean_up(){{
  unset user_option
  unset role_num
  unset roles
}}

pick_role(){{
  get_roles || {{ echo "get_roles failed" ; return; }}

  re='^[0-9]+$'
  if ! [[ $user_option =~ $re ]] ; then
    interactivly_pick_role || {{ echo "interactivly_pick_role failed" ; return; }}
  else
    role_num=$user_option
  fi
  assume_role $role_num || {{ echo "assume_role failed" ; return; }}
}}

pick_role || {{ echo "pick_role failed" ; return; }}
clean_up || {{ echo "clean_up failed" ; return; }}
"""

class AssumeRoleGenerator(object):

    def __init__(self):
        self._client = boto3.client("iam", verify=False)
        self._resource = boto3.resource('iam', verify=False)

    def generate_assume_role_script(self):
        """
        This method generates the bash script to assume role
        """
        f = open('assume.sh','w')
        f.write(self.generate_file(self.get_roles()))
        f.close()

    def generate_file(self, roles):
        return ASSUME_TEMP.format(" ".join(roles))

    def get_roles(self):
        username = self.get_username()
        groups = self.get_groups(username)
        return self.get_assume_roles(groups)

    def get_username(self):
        return self._client.get_user().get('User',{}).get('UserName')

    def get_groups(self, username):
        return self._resource.User(username).groups.all()

    def get_assume_roles(self, groups):
        docos = [
            self.get_policy_doco(p.arn, p.default_version_id)
            for g in self.get_bakery_group(groups.all())
            for p in g.attached_policies.all()
        ]
        return self.get_roles_from_docos(docos)

    def get_policy_doco(self, arn, doco_version):
        return self._client.get_policy_version(
            PolicyArn=arn,
            VersionId=doco_version
        ) \
        .get('PolicyVersion',{}) \
        .get('Document')

    def get_bakery_group(self, groups):
        matchers = map(self.to_pascal_case, BAKERY_ENV_GROUPS)
        return [
            g
            for g in groups
            if any(xs in g.arn for xs in matchers)
        ]

    def get_roles_from_docos(self, docos):
        return self.flatten_list([
            self.get_resources_from_statement(r.get('Statement'))
            for r in docos
        ])

    def get_resources_from_statement(self, statements):
        return self.flatten_list([ s.get('Resource') for s in statements ])

    def flatten_list(self, init_list):
        return [
            item
            for sublist in init_list
            for item in sublist
        ]

    def to_pascal_case(self, snake_str):
        components = snake_str.split('_')
        return "".join(x.title() for x in components)

if __name__ == "__main__":
    AssumeRoleGenerator().generate_assume_role_script()
