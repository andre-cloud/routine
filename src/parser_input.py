#!/usr/bin/python3


import argparse, os

from src.cpu_memory import get_censo_prm, get_crest_prm, get_gaussian_prm, get_orca_prm, get_xtb_prm



def is_slurm(k):
    if '=' in k: return k

def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('calc', choices=['orca', 'crest', 'censo', 'gaussian', 'xtb'])
    parser.add_argument('file')

    args, unknown = parser.parse_known_args()
    if not check_input(args.file):
        raise IOError('Input not existing')



    sbatchrc = []
    if os.path.exists(os.path.join('/', os.getlogin(), '.sbatchrc')):
        with open(os.path.join('/', os.getlogin(), '.sbatchrc')) as f:
            sbatchrc = [i.split()[1] for i in f.readlines()]
    else: 
        fl = """#SBATCH --mail-user=AP_tgram@mailrise.xyz
#SBATCH --mail-type=NONE
#SBATCH --exclude=motoro"""
        sbatchrc = [i.split()[1] for i in fl.splitlines()]   

    slurm_commands = {i.split('=')[0].strip('-'):i.split('=')[1] for i in sbatchrc}


    for i in list(filter(is_slurm, unknown)):
        slurm_commands[i.split('=')[0].strip('-')] = i.split('=')[1] 

    sl = list(filter(is_slurm, unknown))
    calc_commands = f'{args.calc} {args.file} ' + ' '.join([i for i in unknown if i not in sl])


    # get the cpu and the memory required for the calculation
    cpu, mem = get_cpu_memory(args.file, args.calc, calc_commands)

    slurm_commands['ntasks'] = cpu
    slurm_commands['mem-per-cpu'] = mem

    return args.file, args.calc, calc_commands, slurm_commands



def check_input(file):
    return os.path.exists(os.path.join(os.getcwd(), file))


def get_cpu_memory(input, calculation, calc_commands):
    return {
        'orca': get_orca_prm,
        'gaussian': get_gaussian_prm,
        'crest' : get_crest_prm,
        'censo' : get_censo_prm,
        'xtb' : get_xtb_prm
    }[calculation](input, calc_commands)



def check_slurm_command(commands):

    return

if __name__ == '__main__':
    print(parse_args())