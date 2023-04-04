#!/data/bin/python_env/bin/python


import os
import datetime



from src.defaults import DEFAULT_MAIL, CALC_ABBREVIATION, SMTP_SERVER_IP, MODULE_NEEDED, launchers, qm_all_files
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


def create_qm_all(calculation, input_file_no_extention):
    cmd = f'ext=({qm_all_files[calculation]})'
    cmd += f'''
mkdir qm_all
mv *.* qm_all/

for i in ${"{ext[@]}"}; do 
    echo {input_file_no_extention}.$i
    if [[ -e qm_all/{input_file_no_extention}.$i ]]; then
	    cp -v qm_all/{input_file_no_extention}.$i ./ 
    fi
done
'''
    
    return cmd 


def censorc():
    return '''if ! [[ -e .censorc ]]; then cp /data/$(whoami)/.censorc .; fi; cp  $SLURM_SUBMIT_DIR/.censorc $SCRATCH_DIR'''


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

    ext = 'out' if calculation != 'gaussian' else 'log'
    cm = calc_cmd + (
        f' > $SLURM_SUBMIT_DIR/{input_file_no_extention}.{ext}' if calculation in ['orca'] else '' if calculation in ['gaussian'] else  f' > $SLURM_SUBMIT_DIR/{calculation}.out 2> $SLURM_SUBMIT_DIR/{calculation}.error')

    cmd_not_prog = ' '.join(cm.split()[1:])


    with open('job-slurm.sh', 'w') as f:
        f.write(job_template.format(
            abr = CALC_ABBREVIATION[calculation],
            slurm_sbatchrc = convert_slurm_cmd(slurm_cmd),
            modules = MODULE_NEEDED[calculation],
            command_line = cm,
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            input_file = input_file_no_extention,
            output_file = f'{input_file_no_extention}.{ext}',
            calculation = calculation, 
            launcher = launchers[calculation],
            command_line_no_prog = cmd_not_prog, 
            creating_qm_all = create_qm_all(calculation, input_file_no_extention), 
            update_README = f'update_readme.py {calculation} {input_file_no_extention if calculation in ["orca", "gaussian"] else calculation}.{ext}',
            SMTP = SMTP_SERVER_IP, 
            email = email_address,
            censorc = '' if calculation != 'censo' else censorc()
        ))

    os.system('chmod u+x job-slurm.sh')

    return




if __name__ == '__main__':
    write_job_file(
        'tests/orca_procs.inp', 
        'censo',
        'orca tests/orca_procs.inp',
        {'mail-user': 'AP_tgram@mailrise.xyz', 'mail-type': 'NONE', 'exclude': 'motoro', 'nodelist': 'motoro', 'nodes-list': 'mume', 'ntasks': '44', 'mem-per-cpu': '1000'}, test=True
        )