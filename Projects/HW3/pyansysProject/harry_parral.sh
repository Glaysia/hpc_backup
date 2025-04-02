#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=gpu6
#SBATCH --cpus-per-task=48
#SBATCH --gres=gpu:1
#SBATCH --job-name=HARRYPYAEDT
#SBATCH -o ./log/SLURM.%N.%j.out
#SBATCH -e ./log/SLURM.%N.%j.err

conda activate pyaedt_env

export ANSYSEM_ROOT242=/opt/ohpc/pub/Electronics/v242/Linux64/
export PATH=$ANSYSEM_ROOT242/ansysedt/bin:$PATH
export ANSYSLMD_LICENSE_FILE=1055@172.16.10.81

python ./usingSubProcesses__.py