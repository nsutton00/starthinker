###########################################################################
# 
#  Copyright 2019 Google Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################

import json
from random import choice

from starthinker.util.colab import Colab
from starthinker.script.parse import json_get_fields, json_set_auths

def script_to_colab(name, description, instructions, tasks, parameters={}):
  colab = Colab(name)

  colab.header("1. Install Dependencies")
  colab.paragraph("First install the libraries needed to execute recipes, this only needs to be done once, then click play.")
  colab.code("!pip install git+https://github.com/google/starthinker")

  colab.header("2. Get Cloud Project ID")
  colab.paragraph("To run this recipe [requires a Google Cloud Project](https://github.com/google/starthinker/blob/master/tutorials/cloud_project.md), this only needs to be done once, then click play.")
  #colab.image('Client Project ID', 'https://github.com/google/starthinker/raw/master/tutorials/images/cloud_project.png')
  colab.code('CLOUD_PROJECT = \'PASTE PROJECT ID HERE\'')
  colab.code('\nprint("Cloud Project Set To: %s" % CLOUD_PROJECT)')

  colab.header("3. Get Client Credentials")
  #colab.image('Client Credentials', 'https://github.com/google/starthinker/raw/master/tutorials/images/cloud_client_installed.png')
  colab.paragraph('To read and write to various endpoints requires [downloading client credentials](https://github.com/google/starthinker/blob/master/tutorials/cloud_client_installed.md), this only needs to be done once, then click play.')
  colab.code('CLIENT_CREDENTIALS = \'PASTE CREDENTIALS HERE\'')
  colab.code('\nprint("Client Credentials Set To: %s" % CLIENT_CREDENTIALS)')

  fields = json_get_fields(tasks)
  if fields:
    colab.header('4. Enter %s Parameters' % name)
    colab.paragraph(description)
    colab.list(instructions)
    colab.paragraph('Modify the values below for your use case, can be done multiple times, then click play.')

    fields = json_get_fields(tasks)
    colab.code('FIELDS = {')
    for field in fields:

      if field['kind'] in ('string', 'email', 'text'):
        value = '"%s"' % parameters.get(field['name'], field.get('default', ''))
      elif field['kind'] in ('integer', 'boolean'):
        value = parameters.get(field['name'], field.get('default', 'None'))
      elif field['kind'] in ('choice', 'integer_list', 'string_list'):
        value = parameters.get(field['name'], field.get('default', '[]'))
      elif field['kind'] in ('json'):
        value = parameters.get(field['name'], field.get('default', '{}'))
      elif field['kind'] == 'timezone':
        value = '"%s"' % parameters.get(field['name'], field.get('default', 'America/Phoenix'))
        field['description'] = '%s https://github.com/google/starthinker/blob/master/starthinker_ui/ui/timezones.py' % field.get('description', '')
      else:
        raise NotImplementedError("%s is not a suported field type" % field)
  
      if 'description' in field: 
        colab.code('  "%s":%s, # %s' % (field['name'], value, field['description']))
      else:
        colab.code('  "%s":%s,' % (field['name'], value))

    colab.code('}')
    colab.code('\nprint("Parameters Set To: %s" % FIELDS)')

  colab.header('%d. Execute %s' % (5 if fields else 4, name))
  colab.paragraph('This does NOT need to be modified unles you are changing the recipe, click play.')

  colab.code('from starthinker.util.project import project')
  colab.code('from starthinker.script.parse import json_set_fields')
  colab.code('')
  colab.code("USER_CREDENTIALS = '/content/user.json'")
  colab.code('')
  colab.code('TASKS = %s' % json.dumps(json_set_auths(tasks, 'user'), indent=2))
  colab.code('')

  if fields: colab.code('json_set_fields(TASKS, FIELDS)')

  colab.code("project.initialize(_recipe={ 'tasks':TASKS }, _project=CLOUD_PROJECT, _user=USER_CREDENTIALS, _client=CLIENT_CREDENTIALS, _verbose=True)")
  colab.code('project.execute()')

  return colab.render()