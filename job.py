#!/usr/bin/python3

import os

from src.parser_input import parse_args
from src.write_job_file import write_job_file
from src.initiate_readme import write_md
from src.check import check_folder

def main():
    
    input_file, calculation, calc_cmd, slurm_cmd = parse_args()

    check_folder()

    write_md(calculation, input_file, calc_cmd)
    
    write_job_file(input_file, calculation, calc_cmd, slurm_cmd)

    print("Take your time to edit the README.md file to explain the purpose of this calculation")
    os.system('sbatch job-slurm.sh')
    

if __name__ == '__main__':

    main()

