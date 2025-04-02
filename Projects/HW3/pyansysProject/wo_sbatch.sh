#!/bin/bash
conda activate /home1/harry261/miniconda3/envs/pyaedt_env

export ANSYSEM_ROOT242=/opt/ohpc/pub/Electronics/v242/Linux64/
export PATH=$ANSYSEM_ROOT242/ansysedt/bin:$PATH
export ANSYSLMD_LICENSE_FILE=1055@172.16.10.81

python /home1/harry261/Documents/Projects/HW3/pyansysProject/usingSubProcesses.py