



import subprocess

def grep(patter, str):
    return [i for i in str.splitlines() if patter in i]

def get_index_table(idx,splitter,row):
    return [i.split(splitter)[idx].strip("'\"") for i in row]

def get_output(command):
    print(command.split())
    cmd = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return cmd.communicate() # (out, err)




########################
#    DEFAULT VALUES    #
########################


# VALID_NODES = get_index_table(1, '-', grep('ALL', get_output("sinfo --Node -o '%R-%N'")[0].decode('utf-8')))

# VALID_PARTITION = get_index_table(0, '-', grep('up', get_output('sinfo -o "%R-%a"')[0].decode('utf-8')))

# MAX_CPU = sorted([int(i.strip("'\"")) for i in get_output('sinfo --Node -o "%c"')[0].decode('utf-8').splitlines() if i.strip('\'"').isdigit() ])[-1]

# EMAIL_REGEX = regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


CALC_ABBREVIATION = {
    'orca': 'o', 
    'crest': 's', 
    'censo': 'c',
    'xtb': 'x', 
    'gaussian': 'g'
}


MODULE_NEEDED = {
    'censo': 'xtb/6.4.1 orca', 
    'crest': 'xtb', # NON CAPISCO IL PERCHÉ 
    'orca': 'orca', 
    'gaussian': 'gaussian', 
    'xtb': 'xtb'
}


SMTP_SERVER_IP = '192.168.114.75:8025'
DEFAULT_MAIL='AP_tgram@mailrise.xyz,PR_tgram@mailrise.xyz'

