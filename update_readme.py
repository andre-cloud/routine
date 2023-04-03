#!/data/bin/python_env/bin/python

import cclib
import re, sys
import numpy as np
from scipy.constants import physical_constants as ph

EV_TO_HARTREE = 1 / ph["Hartree energy in eV"][0]



def tail(fname, rows):

    return '\n'.join(fname.splitlines()[-rows:])



def orca_parser(output):

    data = cclib.io.ccread(output)

    with open(output) as f:
        fl = f.read()

    if 'ORCA TERMINATED NORMALLY' in fl:        
        e = re.search('\-[0-9]{1,}\.[0-9]{1,}', re.findall('FINAL SINGLE POINT ENERGY.*', fl)[-1])[0]
        try:
            vib = data.vibfreqs
            g = re.search('\-[0-9]{1,}\.[0-9]{1,}', re.search('Final Gibbs free energy.*', fl)[0])[0]
            corr = re.search('[0-9]{1,}\.[0-9]{1,} Eh', re.search('G-E\(el\) .*', fl)[0])[0].split(' ')[0]
        except Exception:
            vib = np.array([])

        text = '-'*20 + '\nCALCULATION COMPLETED CORRECLY\n'+'-'*20
        text += f'\nFinal single point: {e} Eh'
        if vib.size > 0: 
            text += f'\nGibbs energy: {g} Eh'
            text += f'\nThermal correction: {corr} Eh'
            text += f'\nNumber of imaginary frequency: {len(vib[vib<0])}'
            if vib[vib<0].size>0: 
                text += f'\n\tImaginary freq: {", ".join([str(i) for i in vib[vib<0]])}'
    
    else:
        text = '-'*20 + '\nCALCULATION ABORTED\n'+'-'*20
        text += '\n\n' + tail(fl, 10)
          

    return text

def crest_parser(output):

    with open(output) as f:
        fl = f.read()

    txt = '' 
    if 'CREST terminated normally' in fl:
        text = '-'*20 + '\nCALCULATION COMPLETED CORRECLY\n'+'-'*20
    else:
        text = '-'*20 + '\nCALCULATION NOT COMPLETED\n'+'-'*20

    return text


def censo_parser(output):

    with open(output) as f:
        fl = f.read()

    txt = '' 
    
    if 'CENSO all done!' in fl:
        text = '-'*20 + '\nCALCULATION COMPLETED CORRECLY\n'+'-'*20
    else:
        text = '-'*20 + '\nCALCULATION NOT COMPLETED\n'+'-'*20
    
    text += '\n\n'+tail(fl, 20)

    return text

def xtb_parser(output):

    text = '-'*20 + '\nCALCULATION ENDED\n'+'-'*20

    return text

def gaussian_parser(output):

    data = cclib.io.ccread(output)

    with open(output) as f:
        fl = f.read()

    if 'Normal termination of Gaussian' in fl:        
        e = data.scfenergies[-1]*EV_TO_HARTREE
        g = data.freeenergy
        corr = g-e
        try:
            vib = data.vibfreqs
        except Exception:
            vib = np.array([])

        text = '-'*20 + '\nCALCULATION COMPLETED CORRECLY\n'+'-'*20
        text += f'\nFinal single point: {e} Eh'
        if vib.size > 0: 
            text += f'\nGibbs energy: {g} Eh'
            text += f'\nThermal correction: {corr} Eh'
            text += f'\nNumber of imaginary frequency: {len(vib[vib<0])}'
            if vib[vib<0].size>0: 
                text += f'\n\tImaginary freq: {", ".join([str(i) for i in vib[vib<0]])}'
    
    else:
        text = '-'*20 + '\nCALCULATION ABORTED\n'+'-'*20
        text += '\n\n' + tail(fl, 10)

    return text


parser = {
    'orca'     : orca_parser,
    'crest'    : crest_parser,
    'censo'    : censo_parser,
    'xtb'      : xtb_parser,
    'gaussian' : gaussian_parser,
}




def update_readme(calculation, output):

    text = parser[calculation](output)

    with open('README.md', 'a') as f:
        f.write(text)

    return 


if __name__=='__main__':

    calculation, output = sys.argv[1:]
    update_readme(calculation, output)
