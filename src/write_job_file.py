#!/data/bin/python_env/bin/python


import os
import datetime



from src.defaults import DEFAULT_MAIL, CALC_ABBREVIATION, SMTP_SERVER_IP, MODULE_NEEDED
from assets.job_template import template as job_template





def convert_slurm_cmd(slurm_cmd):
    return '\n'.join([f'#SBATCH --{k}={v}' for k,v in slurm_cmd.items()])


def get_possible_versions(calculation, version, test=False):
    
    if not version: return (True, True)

    if test:
        disp_version = ['5.0.3', '5.0.4']
    else:
        disp_version = [i for i in os.listdir(os.path.join('/', 'data', 'modules', calculation)) if not str(i).startswith('.')]

    return (version in disp_version, disp_version)






def write_job_file(input_file, calculation, calc_cmd, slurm_cmd, test=False):
    """
    
    calc_cmd : str : orca tests/orca_procs.inp
    slurm_cmd : dict : {'mail-user': 'AP_tgram@mailrise.xyz', 'mail-type': 'NONE', 'exclude': 'motoro', 'nodelist': 'motoro', 'nodes-list': 'mume', 'ntasks': '44', 'mem-per-cpu': '1000'}
    """
    
    version = slurm_cmd.pop('version', None)
    version_ = get_possible_versions(calculation, version, test)

    if not version_[0]: 
        raise ValueError(f'Version of {calculation} required ({version}) not present. Available: {", ".join(version_[1])}')
    
    email_address = slurm_cmd.pop('mail-user', DEFAULT_MAIL)
    input_file_no_extention = os.path.splitext(input_file)[0]
    cm = calc_cmd + (
        f' > $SLURM_SUBMIT_DIR/{input_file_no_extention}.out' if calculation in ['orca', 'gaussian'] else  f' > $SLURM_SUBMIT_DIR/{input_file_no_extention}.out 2> $SLURM_SUBMIT_DIR/{input_file_no_extention}.error')

    cmd_not_prog = ' '.join(cm.split()[1:])

    with open('job-slurm.sh', 'w') as f:
        f.write(job_template.format(
            slurm_sbatchrc = convert_slurm_cmd(slurm_cmd),
            modules = MODULE_NEEDED[calculation],
            command_line = cm,
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            input_file = input_file_no_extention,
            output_file = f'{input_file_no_extention}.out',
            calculation = calculation, 
            command_line_no_prog = cmd_not_prog, 
            creating_qm_all = '', 
            update_README = f'python update_readme.py {calculation} {input_file_no_extention}.out',
            SMTP = SMTP_SERVER_IP, 
            email = email_address,
        ))

    os.system('chmod u+x job-slurm.sh')

    return




if __name__ == '__main__':
    write_job_file(
        'tests/orca_procs.inp', 
        'orca',
        'orca tests/orca_procs.inp',
        {'mail-user': 'AP_tgram@mailrise.xyz', 'mail-type': 'NONE', 'exclude': 'motoro', 'nodelist': 'motoro', 'nodes-list': 'mume', 'ntasks': '44', 'mem-per-cpu': '1000'}, test=True
        )