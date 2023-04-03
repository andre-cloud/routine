#!/data/bin/python_env/bin/python


import re, os

PREFIX = {
    'k' : 1e-3,
    'm' : 1e0,
    'g' : 1e3
}

def get_orca_prm(input, calc_commands):

    with open(input) as f:
        fl = f.read()
    
    pal = re.search('^!.*pal[1-9][0-9]{0,1}', fl)
    if pal:
        # get the PAL8
        pal = re.search('[1-9][0-9]{0,1}', pal[0])[0]
    else:
        # get nprocs
        pal = re.search('nprocs[ ]+[1-9][0-9]{0,2}', fl)
        if pal:
            pal = re.search('[1-9][0-9]{0,2}', pal[0])[0]
        else:
            pal = 1

    maxcore = re.search('%( ){0,}maxcore[ ]+[1-9][0-9]{0,}', fl)
    if maxcore:
        maxcore = re.search('[1-9][0-9]{0,}', maxcore[0])[0]
    else: 
        maxcore = "1000"

    return pal, maxcore


def get_gaussian_prm(input, calc_commands):

    with open(input) as f:
        fl = f.read()
    
    pal = re.search('%( ){0,}nprocshared=( ){0,}[1-9][0-9]{0,2}', fl.lower())
    if pal:
        pal = re.search('[1-9][0-9]{0,1}', pal[0])[0]
    else:
        pal = 1

    maxcore = re.search('%( ){0,}mem=( ){0,}[1-9][0-9]{0,}[a-z]{0,2}', fl.lower())
    if maxcore:
        pre=PREFIX[re.search('[a-z]{2}$', maxcore[0])[0][0]]
        maxcore = str(int(re.search('[1-9][0-9]{0,}', maxcore[0])[0])*pre/int(pal))
    else: 
        maxcore = "1000"

    return pal, maxcore


def get_crest_prm(input, calc_commands):

    c = calc_commands.split()

    pal = [c[idx+1] for idx, i in enumerate(c) if i.startswith('-') and i.lower().endswith('t')][0]

    maxcore = str(22000/float(pal))

    return pal, maxcore


def get_censo_prm(input, calc_commands, test=None):
    
    pal, maxcore = 0, 4000

    c = calc_commands.split()
    if re.search('-{1,2}O', calc_commands):
        o = [c[idx+1] for idx, i in enumerate(c) if i.startswith('-') and i.lower().endswith('o')][0]
        p = [c[idx+1] for idx, i in enumerate(c) if i.startswith('-') and i.lower().endswith('p') and 'in' not in i.lower()][0]

        return str(int(o)*int(p)), str(maxcore)

    if os.path.exists(os.path.join(os.getcwd(), '.censorc')): 
        file = os.path.join(os.getcwd(), '.censorc')
    else: file = os.path.join('/', 'data', os.getlogin(), '.censorc')
    
    if test: file='tests/.censorc'

    with open(file) as f:
        fl = f.read() 

    o = re.search('[0-9]{1,3}', re.search('omp( ){0,}:( ){0,}[0-9]{1,4}', fl)[0])[0]
    p = re.search('[0-9]{1,3}', re.search('maxthreads( ){0,}:( ){0,}[0-9]{1,4}', fl)[0])[0]

    return str(int(o)*int(p)), str(maxcore)



def get_xtb_prm(input, calc_commands):

    c = calc_commands.split()

    pal = [c[idx+1] for idx, i in enumerate(c) if i.startswith('-') and i.lower().endswith('p')][0]

    maxcore = str(22000/float(pal))

    return pal, maxcore


if __name__ == '__main__':
    print(get_orca_prm('tests/orca_pal.inp'))
    print(get_orca_prm('tests/orca_procs.inp'))
    
    print(get_gaussian_prm('tests/gaussian.gjf'))

    print(get_crest_prm('--nci --T 44 --cluster 30 --alpb toluene'))
    print(get_xtb_prm('--opt -P 4 --input input'))

    print(get_censo_prm('-inp ensemble.xyz -solvent toluene', True))