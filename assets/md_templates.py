#!/data/bin/python_env/bin/python


common_template = '''
# {directory}

Commands:
{command}
'''


note_template = '''
---
Note: 
1.

'''

orca_template = common_template + '''
---
{parsed_input}
''' + note_template


crest_template = common_template + '''
---
{parsed_input}
''' + note_template


censo_template = common_template + '''
---
{parsed_input}
''' + note_template


xtb_template = common_template + '''
---
{parsed_input}
''' + note_template


gaussian_template = common_template + '''
---
{parsed_input}
''' + note_template

enan_template = common_template + '''
---
{parsed_input}
''' + note_template

molcas_template = common_template + '''
---
{parsed_input}
''' + note_template