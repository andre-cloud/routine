#!/data/bin/python_env/bin/python


template = '''#!/bin/bash
#SBATCH --job-name={abr}-{input_file}
#SBATCH --nodes=1-1
#SBATCH --time=8760:00:00
#SBATCH --error="err-%j-%N.slurm"
#SBATCH --output="out-%j-%N.slurm"
{slurm_sbatchrc}

module load {modules}{ver}
SCRATCH_DIR="/scratch/slurm-$SLURM_JOB_ID"

echo "Job execution cmd:   {command_line}"
echo "Job execution start: {date}"
echo "Slurm Job ID is:     $SLURM_JOB_ID"
echo "Slurm Job name is:   $SLURM_JOB_NAME"
echo
echo "SLURM_JOB_NODELIST:  $SLURM_JOB_NODELIST"
echo "SLURM_SUBMIT_DIR:    $SLURM_SUBMIT_DIR"
echo "SLURM_SUBMIT_HOST:   $SLURM_SUBMIT_HOST"
echo "SLURMD_NODENAME:     $SLURMD_NODENAME"
echo
echo "SCRATCH DIR:         $SCRATCH_DIR"
echo
echo "PATH:                $PATH"
echo "LD_LIBRAY_PATH:      $LD_LIBRARY_PATH"
echo


# CREATION OF ALL THE DIRECTORIES NEEDED ON EACH NODE

for node in $(scontrol show hostnames $SLURM_JOB_NODELIST)
do
        echo $node
        ssh $node mkdir -p $SCRATCH_DIR
done

source /data/bin/python_env/bin/activate

{command_1}

# SETTING THE FOLDER FOR THE CALCULATION

## CREATE THE ORIGINAL'S FOLDER
mkdir .originals
cp * .originals
rm .originals/README.md .originals/*slurm .originals/*sh

echo $SLURM_SUBMIT_DIR > WD

## COPYING THE FILES OF THE DIRECTORY IN THE SCRATCH
cp -v -r $SLURM_SUBMIT_DIR/* $SCRATCH_DIR
{censorc}
if [[ -e .censorc ]]; then cp .censorc .originals; fi

cd $SCRATCH_DIR
rm README.md


## ECHOING THE ID IN THE RUNNING LOG FILE

echo "$SLURM_JOB_ID - $SLURM_SUBMIT_DIR/{output_file} - {calculation}" >> /data/jobs/running.log

# RUNNING THE CALCULATION

{launcher} {command_line_no_prog}

## REMOVING FROM RUNNING LOG FILE
sed -n "/$SLURM_JOB_ID/!p" /data/jobs/running.log > /data/jobs/running.log_tmp && mv /data/jobs/running.log_tmp /data/jobs/running.log

rm *.slurm *.sh
{creating_qm_all}


# COPY BACK THE CALCULATION AND REMOVE THE SCRATCH FOLDER
cd $SLURM_SUBMIT_DIR
rsync -av --no-p --no-g --chmod=ugo=rwX --exclude '*.tmp' $SCRATCH_DIR/* ./ && rm -fr $SCRATCH_DIR

rm WD

{update_README}

# SEND NOTIFICATION EMAIL

ssh 192.168.111.100 email_sender.py {email} $SLURM_SUBMIT_DIR

{command_2}

deactivate
'''