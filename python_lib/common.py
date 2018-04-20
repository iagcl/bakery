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
Module contains common functions used in other modules.
"""
import os

def generate_file(file_path, content):
    """Creates a file with the specified content.

    Args:
        file_path: Path and filename
        content: The content to write into the file
    """
    path = os.path.dirname(file_path)

    # If the path does not exist, create it
    if not os.path.exists(path):
        os.makedirs(path)

    # Remove the file if it exists
    if os.path.exists(file_path):
        print "Removing \"{}\"".format(file_path)
        os.remove(file_path)

    with open(file_path, "w") as filer:
        filer.write(content)

def get_template(template_file):
    """Gets the content of the file.

    Args:
        template_file: Template path and filename

    Returns:
        Content of the specified file
    """
    template = ""

    with open(template_file) as filer:
        template = filer.read()

    return template
