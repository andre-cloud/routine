#!/usr/bin/python3


'''
if [ -e *out ]; then
        echo "Output file(s) are present in this folder. Create one folder for one calculation."

        dir_n=${PWD##*/}
        dir_n=${dir_n%.*}
        n=$(ls -d ../$(echo $dir_n)* | wc -l)
        new_dir=$(echo $dir_n).$(echo $n)
        echo "Creating ../$new_dir with input files stored in .originals/ and the new modified input"

        mkdir ../$new_dir
        cp .originals/* ../$new_dir
        cp $jobfile ../$new_dir
        cp .originals/$jobfile .
        if [ -e ../$new_dir/README.md ]; then rm ../$new_dir/README.md; fi
        exit
fi
'''

import re, shutil
from os import listdir, getcwd, getlogin, mkdir, system
from os.path import isfile, join, isdir, split

DEBUG = getlogin() == 'andrea'

def check_folder(input_file):

    output = [f for f in listdir(getcwd()) if isfile(join(getcwd(), f)) and str(f).endswith('out')]

    if not output and DEBUG:
        return

    print('Output file(s) are present in this folder. Use one folder for one calculation.')

    dir_n = split(getcwd())[-1].split('.')[0]
    root = split(getcwd())[0]
    n = len([f for f in listdir(root) if isdir(join(root, f)) and re.search(dir_n, f)])

    n_dir = dir_n+'.'+str(n)
    print(f"Creating ../{n_dir} with input files stored in .originals/ and the new modified input")

    mkdir(join(root, n_dir))
    system(f'cp .originals/* ../{n_dir}')
    system(f'{input_file} ../{n_dir}')
    system(f'cp .originals/{input_file} .')


