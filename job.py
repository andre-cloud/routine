
#!/usr/bin/python3



from src.parser_input import parse_args
from src.write_job_file import write_job_file
from src.initiate_readme import write_md
from src.check import check_folder

def main():
    
    input_file, calculation, calc_cmd, slurm_cmd = parse_args()

    check_folder()

    write_md(calculation, input_file, calc_cmd)
    
    write_job_file(input_file, calculation, calc_cmd, slurm_cmd)

        





if __name__ == '__main__':

    # main()

    write_job_file(
        'tests/orca_procs.inp', 
        'orca',
        'orca tests/orca_procs.inp',
        {'mail-user': 'AP_tgram@mailrise.xyz', 'mail-type': 'NONE', 'exclude': 'motoro', 'nodelist': 'motoro', 'nodes-list': 'mume', 'ntasks': '44', 'mem-per-cpu': '1000'}, test=True
        )


