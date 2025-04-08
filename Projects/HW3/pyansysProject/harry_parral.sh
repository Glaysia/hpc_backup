#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=gpu4
#SBATCH --cpus-per-task=48
#SBATCH --job-name=HARRYPYAEDT
#SBATCH -o /home1/harry261/log/SLURM.%N.%j.out
#SBATCH -e /home1/harry261/log/SLURM.%N.%j.err

conda activate /home1/harry261/miniconda3/envs/pyaedt_env
source /home1/harry261/miniconda3/etc/profile.d/conda.csh

export ANSYSEM_ROOT242=/opt/ohpc/pub/Electronics/v242/Linux64/
export PATH=$ANSYSEM_ROOT242/ansysedt/bin:$PATH
export ANSYSLMD_LICENSE_FILE=1055@172.16.10.81

python /home1/harry261/Documents/Projects/HW3/pyansysProject/usingSubProcesses.py