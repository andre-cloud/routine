#!/data/bin/python_env/bin/python



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


POSS_CALC = [
    'orca', 
    'crest', 
    'censo', 
    'xtb', 
    'gaussian', 
    'enan',
    'molcas',
]

CALC_ABBREVIATION = {
    'orca'      : 'o', 
    'crest'     : 's', 
    'censo'     : 'c',
    'xtb'       : 'x', 
    'gaussian'  : 'g',
    'enan'      : 'p',
    'molcas'    : 'm',
}


MODULE_NEEDED = {
    'orca'      : 'orca', 
    'crest'     : 'xtb',
    'censo'     : 'xtb/6.4.1 orca', 
    'xtb'       : 'xtb',
    'gaussian'  : 'gaussian', 
    'enan'      : 'orca',
    'molcas'    : 'openmolcas',
}

LAUNCHERS = {
    'orca'      : '$(which orca)',
    'crest'     : 'crest',
    'censo'     : 'censo --input',
    'xtb'       : 'xtb',
    'gaussian'  : 'g16',
    'enan'      : 'ensemble_analyser.py -e',
    'molcas'    : 'pymolcas',
}


QM_ALL_FILES = {
    'orca'      : 'inp xyz interp out hess final.interp',
    'crest'     : 'xyz out',
    'censo'     : 'xyz out',
    'xtb'       : 'xyz out',
    'gaussian'  : 'gjf out log',
    'enan'      : 'xyz json',
    'molcas'    : 'xyz molden out',
}


OUTPUT_FILE = {
    'orca'      : '{input}.out',
    'crest'     : 'crest.out',
    'censo'     : 'censo.out',
    'xtb'       : 'xtb.out',
    'gaussian'  : '{input}.log',
    'enan'      : 'output.out',
    'molcas'    : '{input}.out',
}

SMTP_SERVER_IP = '137.204.158.6:8025'
DEFAULT_MAIL='AP_tgram@mailrise.xyz,PR_tgram@mailrise.xyz'


PREFIX = {
    'k' : 1e-3,
    'm' : 1e0,
    'g' : 1e3
}


