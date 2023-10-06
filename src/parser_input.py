#!/data/bin/python_env/bin/python


import argparse, os
import getpass


from src.defaults import POSS_CALC
from src.cpu_memory import get_censo_prm, get_crest_prm, get_gaussian_prm, get_orca_prm, get_xtb_prm, get_enan_prm




def is_slurm(k):
    if '=' in k: return k

def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('calc', choices=POSS_CALC)
    parser.add_argument('file')

    args, unknown = parser.parse_known_args()



    if not check_input(args.file):
        raise IOError('Input not existing')



    slurm_commands = read_sbatchrc()


    for i in list(filter(is_slurm, unknown)):
        slurm_commands[i.split('=')[0].strip('-')] = i.split('=')[1] 

    sl = list(filter(is_slurm, unknown))
    calc_commands = f'{args.calc} {args.file} ' + ' '.join([i for i in unknown if i not in sl])


    # get the cpu and the memory required for the calculation
    cpu, mem = get_cpu_memory(args.file, args.calc, calc_commands)

    slurm_commands['ntasks'] = cpu
    slurm_commands['mem-per-cpu'] = mem

    return args.file, args.calc, calc_commands, slurm_commands

def read_sbatchrc():
    sbatchrc = []
    if os.path.exists(os.path.join('/', 'data', getpass.getuser(), '.sbatchrc')):
        with open(os.path.join('/', 'data', os.getlogin(), '.sbatchrc')) as f:
            sbatchrc = [i.split()[1] for i in f.readlines()]
    else: 
        fl = """#SBATCH --mail-user=AP_tgram@mailrise.xyz
#SBATCH --mail-type=NONE
#SBATCH --exclude=motoro"""
        sbatchrc = [i.split()[1] for i in fl.splitlines()]   

    slurm_commands = {i.split('=')[0].strip('-'):i.split('=')[1] for i in sbatchrc}
    return slurm_commands



def check_input(file):
    
    return os.path.exists(os.path.join(os.getcwd(), file))


def get_cpu_memory(input, calculation, calc_commands):
    
    return {
        'orca'      : get_orca_prm,
        'crest'     : get_crest_prm,
        'censo'     : get_censo_prm,
        'xtb'       : get_xtb_prm,
        'gaussian'  : get_gaussian_prm,
        'enan'      : get_enan_prm
    }[calculation](input, calc_commands)



if __name__ == '__main__':
    print(parse_args())