#!/data/bin/python_env/bin/python

import os, re

from assets.md_templates import orca_template, crest_template, censo_template, xtb_template, gaussian_template
from assets.phrases import phrases


def orca_parser(file, *args):

    with open(file) as f:
        fl = f.read().lower()

    cmd = ''.join(re.findall('!.*', fl))

    i = []
    if ('opt' in cmd) or ('%geom' in fl):
        if 'optts' in cmd:
            i.append(phrases['optts'])
        elif 'constrained' in fl:
            i.append(phrases['optf'])
        else:
            i.append(phrases['opt'])

        if 'maxstep' in fl:
            i.append(phrases['max_step'].format(ms = re.search('0\.[0-9]{0,}', re.search('maxstep.*', fl)[0])[0]))


    if 'freq' in cmd:
        i.append(phrases['freq'])

    if 'tddft' in fl:
        i.append(phrases['tddft'])

    if 'neb' in cmd:
        i.append(phrases['neb'])

    if 'irc' in cmd: 
        i.append(phrases['irc'])

    input_command = '\n'.join([f'{idx}. {ph}' for idx, ph in enumerate(i,start=1)])

    return cmd, input_command

def crest_parser(input_file, cmd_line):

    cmd = cmd_line
    if 'cinp' in cmd_line:
        file = [j[idx+1] for idx,j in enumerate(cmd_line.split()) if 'cinp' in j][0] 
        i = ['Constrained conformational search']
    else:
        i = ['Conformational search of the geometry']

    if 'nci' in cmd_line: i.append('Considering NCI ellipsoid')
    if 'cluster' in cmd_line: i.append('PCA-RMSD clustering')

    input_command = '\n'.join([f'{idx}. {ph}' for idx, ph in enumerate(i,start=1)])
    return cmd, input_command

def censo_parser(*args):

    cmd = ''
    input_command = '1. Prune and optimise the ensemble'

    return cmd, input_command

def xtb_parser(input_file, cmd_line):

    return '', ''

def gaussian_parser(file, *args):

    with open(file) as f:
        fl = f.read().lower()

    cmd = '\n'.join(re.findall('#.*', fl))

    i = []
    if 'opt' in cmd:
        if 'ts' in cmd:
            i.append(phrases['optts'])
        elif 'modredundant' in fl:
            i.append(phrases['optf'])
        else:
            i.append(phrases['opt'])
        if 'maxstep' in cmd: 
            i.append(phrases['max_step'].format(ms=0.01*int(re.search('[0-9]{1,3}', re.search('maxstep=[0-9]{1,3}', cmd)[0])[0])))

    if 'freq' in cmd:
        i.append(phrases['freq'])

    if 'td' in fl:
        i.append(phrases['tddft'])
    
    if 'irc' in cmd: 
        i.append(phrases['irc'])

    input_command = '\n'.join([f'{idx}. {ph}' for idx, ph in enumerate(i,start=1)])
    
    return cmd, input_command


template = {
    'orca'     : orca_template,
    'crest'    : crest_template,
    'censo'    : censo_template,
    'xtb'      : xtb_template,
    'gaussian' : gaussian_template
}

parser = {
    'orca'     : orca_parser,
    'crest'    : crest_parser,
    'censo'    : censo_parser,
    'xtb'      : xtb_parser,
    'gaussian' : gaussian_parser,
}


def write_md(calculation, input_file, cmd_line): 

    cmd, parse_input = parser[calculation](input_file, cmd_line)

    text = template[calculation].format(
        directory = os.getcwd(), 
        command = cmd,
        parsed_input = parse_input, 
    )

    with open('README.md', 'w') as f:
        f.write(text)
    
    return None



if __name__=='__main__':
    import sys

    calculation, input_file, cmd_line = sys.argv[1:]

    write_md(calculation, input_file, cmd_line)