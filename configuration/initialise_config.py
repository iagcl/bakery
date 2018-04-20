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
Module which accesses values from a config file and assigns them to a variable.
"""
from collections import namedtuple
import yaml

BakeryConfig = namedtuple(
    'BakeryConfig',
    [
        'TeamName',
        'BillingCode',
        'BakeryAccount',
        'SlackChannel',
        'SlackChannelHookUrl',
        'AdminGroups',
        'Environments',
        'AccessTypes'
    ]
)

def load_config(file_name):
    """Loads the yml file.

    Args:
        file_name: Filename
    """
    with open(file_name) as stream:
        try:
            return yaml.load(stream)

        except yaml.YAMLError as exc:
            print exc

BAKERY_VARS = BakeryConfig(**load_config('configuration/config.yml'))
