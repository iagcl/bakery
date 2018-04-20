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
Lambda function to send slack message with "noncompliant bakery users" with restricted access
"""
import os
import json
import logging
from urllib2 import Request, urlopen, URLError, HTTPError

import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def get_non_compliant_users():
    """ Returns list of non compliant users i.e. users attached to restricted groups.

    Returns:
        non_compliant_users: list of users attached to restricted groups
    """
    iam = boto3.client('iam')
    bakery_users = iam.list_users()
    non_compliant_users = []

    for user in bakery_users['Users']:
        user_groups = iam.list_groups_for_user(UserName=user['UserName'])
        for group in user_groups['Groups']:
            if group['GroupName'] in os.environ["adminGroups"].split(","):
                non_compliant_users.append(user['UserName'])

    return non_compliant_users


def send_slack_notification(non_compliant_users):
    """ Send slack notification with non compliant users list if applicable.

    Args:
        non_compliant_users: list of users attached to restricted groups
    """
    # The Slack channel details to send a message to , are stored in the
    # 'slackChannel' and 'slackChannelHookUrl' environment variables
    slack_channel = os.environ['slackChannel']
    hook_url = os.environ['slackChannelHookUrl']

    if non_compliant_users:
        non_compliant_users = str(non_compliant_users).replace(
            "[",
            ""
        ).replace(
            "]",
            ""
        ).replace(
            "'",
            ""
        )

        text = "Following user(s) are members of one of the following groups:\n{}".format(
            os.environ["adminGroups"].replace(",", "\n")
        )

        fields = [
            {
                'title': "UserName(s)",
                'value': non_compliant_users
            }
        ]
        color = "warning"

    else:
        text = "No Bakery users are members of the following groups:\n{}".format(
            os.environ["adminGroups"].replace(",", "\n")
        )

        fields = []
        color = "good"

    slack_message = {
        'channel': slack_channel,
        'attachments': [
            {
                'title': ":burger: Bakery Alert",
                'text': text,
                'color': color,
                'fields': fields
            }
        ]

    }

    req = Request(hook_url, json.dumps(slack_message))

    try:
        response = urlopen(req)
        response.read()
        LOGGER.info('Message posted to channel %s:  \"%s\"', slack_message['channel'],
                    slack_message['attachments'][0]['text'])

    except HTTPError as error:
        LOGGER.error("Request failed: %d %s", error.code, error.reason)

    except URLError as error:
        LOGGER.error("Server connection failed: %s", error.reason)


def lambda_handler(event, context):
    """Main function.

    Args:
        event: Lambda event
        context: Lambda context
    """
    LOGGER.info("Event: %s", str(event))

    non_compliant_users = get_non_compliant_users()

    send_slack_notification(non_compliant_users)
