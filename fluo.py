#!/data/bin/python_env/bin/python

FUNC = "cam-b3lyp"
BASIS_SMALL = "6-31g(d)"
BASIS_BIG = "6-31+g(d,p)"

import os
import cclib
from periodictable import core

from src.write_job_file import write_job_file
from src.parser_input import read_sbatchrc

import argparse
pt = core.PeriodicTable(table="1=H")



SLURM_COMMANDS = read_sbatchrc()

def parser():

    parser = argparse.ArgumentParser()
    parser.add_argument('-cpu')
    parser.add_argument('-log')
    parser.add_argument('-solv', nargs='+')

    return parser.parse_args()





def get_opt(logfile): 
    data = cclib.cc.ioread(logfile)
    atoms = [pt[i] for i in data.atomnos]
    xyz_coordinates = data.atomcoords[-1]
    txt = ''
    for at, coord in zip(atoms, xyz_coordinates):
        txt += f'{at}\t{coord[0]:.6f}\t{coord[1]:.6f}\t{coord[2]:.6f}\n'
    return txt



def thf_s1(coord, cpu):
    # step 1
    txt = f'''%chk=THF-step1.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_SMALL} Opt freq(savenormalmodes) SCRF=(Solvent=THF)
iop(1/7=450) Geom=allCheck Guess=Read

S0 

0 1
{coord}



'''
    file = "THF-step1.gjf"
    with open(file, "w") as f:
        f.write(txt)

    sc = SLURM_COMMANDS.copy()
    sc['ntasks'] = cpu
    sc['mem-per-cpu'] = f"{int(int(cpu)*1.7)}GB"

    # When THF-s1 ends, THF-s2 and SOLV*-s1 starts
    command_1 = """
cd ../step_2 # for the second step
sbatch job-slurm.sh -d afterok:$SLURM_JOB_ID
cd ../step_3 # for the third step
sbatch job-slurm.sh -d afterok:$SLURM_JOB_ID
cd ../../
for i in *
do
  if [ "$i" != "THF" ]
  then
    cd $i/step_1
    sbatch job-slurm.sh -d afterok:$SLURM_JOB_ID
    cd -
  fi
done

cd THF/step_1
"""

    command_2 = """
cp qm_all/THF-step1.chk ../step_2
cp qm_all/THF-step1.chk ../step_3
for i in *
do
  if [ "$i" != "THF" ]
  then
    cp qm_all/THF-step1.chk $i/step_1
  fi
done

"""

    write_job_file(file, "gaussian", f"g16 {file}", slurm_cmd=sc, command_1=command_1, command_2=command_2)
    return True
    




def thf_s2(cpu):
    txt = f"""!step 2 - UV absorption spectrum with TD-DFT and 3 states
%oldchk=THF-step1.chk
%chk=THF-step2.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_BIG} TD(NStates=3) SCRF(solvent=THF) Geom=allCheck Guess=Read



"""
    command_1 = """
cd ../step_5 # for the second step
sbatch job-slurm.sh -d afterok:$SLURM_JOB_ID
"""

    command_2 = """
cp qm_all/THF-step2.chk ../step_5
"""
    file = "THF-step2.gjf"
    with open(file, "w") as f:
        f.write(txt)

    sc = SLURM_COMMANDS.copy()
    sc['ntasks'] = cpu
    sc['mem-per-cpu'] = f"{int(int(cpu)*1.7)}GB"
    write_job_file(file, "gaussian", f"g16 {file}", slurm_cmd=sc, command_1=command_1, command_2=command_2)
    return True

def thf_s3(cpu):
    txt = f"""
!step 3 - Solvatation on GS of the PES with unquilibrated solvent
%oldchk=THF-step1.chk
%chk=THF-step3.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_BIG} SCRF(Solvent=THF,NonEquilibrium=Save) Geom=allCheck Guess=Read


--link1--
!Step 4 - Excitation on first state (Root=2) with solvent contribution out-of-equilibrium 
!Excitation energy can be calculated as E4-E3
%oldchk=THF-step3.chk
%chk=THF-step4.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_BIG} TD(NStates=1,Root=2) Geom=allCheck Guess=Read SCRF(Solvent=THF,ExternalIteration,NonEquilibrium=Read)




    """

    file = "THF-step3.gjf"
    with open(file, "w") as f:
        f.write(txt)

    command_1 = command_2 = None 

    sc = SLURM_COMMANDS.copy()
    sc['ntasks'] = cpu
    sc['mem-per-cpu'] = f"{int(int(cpu)*1.7)}GB"
    write_job_file(file, "gaussian", f"g16 {file}", slurm_cmd=sc, command_1=command_1, command_2=command_2)
    return True

def thf_s5(cpu):
    txt = f"""!Step 5 - geometry optimization with small basis set and 150% threshold values, frequency on the EES 
!removed selectnormalmodes from the frequency calculation
%oldchk=THF-step2.chk
%chk=THF-step5.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_SMALL} opt freq(savenormalmodes) TD(NStates=1,Root=2) SCRF(Solvent=THF) Geom=allCheck Guess=Read
iop(1/7=450)


    """

    command_1 = """
cd ../step_6 # for the sixth step
sbatch job-slurm.sh -d afterok:$SLURM_JOB_ID 
cd ../../
for i in *
do
  if [ "$i" != "THF" ]
  then
    cd $i/step_5
    sbatch job-slurm.sh -d afterok:$SLURM_JOB_ID
    cd -
  fi
done

cd THF/step_5
"""

    command_2 = """
cp qm_all/THF-step1.chk ../step_6
for i in *
do
  if [ "$i" != "THF" ]
  then
    cp qm_all/THF-step5.chk $i/step_5
  fi
done

"""

    file = "THF-step5.gjf"
    with open(file, "w") as f:
        f.write(txt)


    sc = SLURM_COMMANDS.copy()
    sc['ntasks'] = cpu
    sc['mem-per-cpu'] = f"{int(int(cpu)*1.7)}GB"
    write_job_file(file, "gaussian", f"g16 {file}", slurm_cmd=sc, command_1=command_1, command_2=command_2)
    return True

def thf_s6(cpu):
    txt = f"""!step 6 TD calculation on the EES to evaluate solvent contribution out-of-equilibrium - equiv to step 4
%oldchk=THF-step5.chk 
%chk=THF-step6.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_BIG} TD(NStates=1, Root=2) Geom=allCheck Guess=Read SCRF(Solvent=THF,ExternalIteration,NonEquilibrium=Save)


--link1--
!step 7 PES energy with geometry of the EES + solvent contribution from step 6
!emission energy = E6-E7
%oldchk=THF-step6.chk
%chk=THF-step7.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_BIG} SCRF(Solvent=THF, NonEquilibrium=Read) Geom=allCheck Guess=Read


"""
    file = "THF-step6.gjf"
    with open(file, "w") as f:
        f.write(txt)

    command_1 = command_2 = None 

    sc = SLURM_COMMANDS.copy()
    sc['ntasks'] = cpu
    sc['mem-per-cpu'] = f"{int(int(cpu)*1.7)}GB"
    write_job_file(file, "gaussian", f"g16 {file}", slurm_cmd=sc, command_1=command_1, command_2=command_2)
    return True





def solv_s1(cpu, solv, gau_solv):
    txt = f"""!step 1 - PEs optimization with standard grid and small basis set with threshold raised to 150% of the standard
!removed selectnormalmodes in the frequency calculation
%oldchk=THF-step1.chk
%chk={solv}-step1.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_SMALL} Opt freq(savenormalmodes) SCRF=(Solvent={gau_solv}) geom=allcheck
iop(1/7=450) 


--link1--
!step 2 - UV absorption spectrum with TD-DFT and 3 states
%oldchk={solv}-step1.chk
%chk={solv}-step2.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_BIG} TD(NStates=3) SCRF(solvent={gau_solv}) Geom=allCheck Guess=Read


--link1--
!step 3 - Solvatation on GS of the PES with unquilibrated solvent
%oldchk=/{solv}-step1.chk
%chk={solv}-step3.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_BIG} SCRF(Solvent={gau_solv},NonEquilibrium=Save) Geom=allCheck Guess=Read


--link1--
!Step 4 - Excitation on first state (Root=1) with solvent contribution out-of-equilibrium 
!Excitation energy can be calculated as E4-E3
%oldchk={solv}-step3.chk
%chk={solv}-step4.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_BIG} TD(NStates=1,Root=1) Geom=allCheck Guess=Read SCRF(Solvent={gau_solv},ExternalIteration,NonEquilibrium=Read)


"""

    file = f"{solv}-step1.gjf"
    with open(file, "w") as f:
        f.write(txt)

    command_1 = command_2 = None 

    sc = SLURM_COMMANDS.copy()
    sc['ntasks'] = cpu
    sc['mem-per-cpu'] = f"{int(int(cpu)*1.7)}GB"
    write_job_file(file, "gaussian", f"g16 {file}", slurm_cmd=sc, command_1=command_1, command_2=command_2)
    return True



def solv_s5(cpu, solv, gau_solv):
    txt = f"""!Step 5 - geometry optimization with small basis set and 150% threshold values, frequency on the EES 
!removed selectnormalmodes from the frequency calculation
%oldchk=THF-step5.chk
%chk={solv}-step5.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_SMALL} opt freq(savenormalmodes) TD(NStates=1,Root=1) SCRF(Solvent={gau_solv}) Geom=allCheck Guess=Read
iop(1/7=450)


--link1--
!step 6 TD calculation on the EES to evaluate solvent contribution out-of-equilibrium - equiv to step 4
%oldchk={solv}-step5.chk
%chk={solv}-step6.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_BIG} TD(NStates=1, Root=1) Geom=allCheck Guess=Read SCRF(Solvent={gau_solv},ExternalIteration,NonEquilibrium=Save)


--link1--
!step 7 PES energy with geometry of the EES + solvent contribution from step 6
!emission energy = E6-E7
%oldchk={solv}-step6.chk
%chk={solv}-step7.chk
%nprocshared={cpu}
%mem={int(int(cpu)*1.7)}GB
# {FUNC}/{BASIS_BIG} SCRF(Solvent={gau_solv}, NonEquilibrium=Read) Geom=allCheck Guess=Read


    """


def write_THF(cpu):
    PATH = os.getcwd()
    os.mkdir("step_1")
    os.chdir("step_1")
    thf_s1(cpu)
    os.chdir(PATH)
    os.mkdir("step_2")
    os.chdir("step_2")
    thf_s2(cpu)
    os.chdir(PATH)
    os.mkdir("step_3")
    os.chdir("step_3")
    thf_s3(cpu)
    os.chdir(PATH)
    os.mkdir("step_5")
    os.chdir("step_5")
    thf_s5(cpu)
    os.chdir(PATH)
    os.mkdir("step_6")
    os.chdir("step_6")
    thf_s6(cpu)
    os.chdir(PATH)


def write_solv(cpu, solv, gau_solv):
    PATH = os.getcwd()
    os.mkdir("step_1")
    os.chdir("step_1")
    solv_s1(cpu, solv, gau_solv)
    os.chdir(PATH)
    os.mkdir("step_5")
    os.chdir("step_5")
    solv_s5(cpu, solv, gau_solv)
    os.chdir(PATH)




GAU_SOLV = {
"HEX": "n-Hexane",
"ACN": "Acetonitrile",
"TOL": "Toluene",
"DCM": "DCM",
"MeOH": "Methanol"
}

def main():
    args = parser()
    os.chdir(os.path.split(args.log)[0])
    PATH = os.getcwd()
    os.mkdir("THF")
    os.chdir("THF")
    write_THF(args.cpu)
    os.chdir(PATH)
    for i in args.sol:
        write_solv(args.cpu, i, gau_solv=GAU_SOLV[i])
        os.chdir(PATH)
    
if __name__ == '__main__':
    main()