#!/bin/bash
#SBATCH --job-name="ace2005"
#SBATCH --output="./NNER/headbased_nner/gum5.out"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --time=128:00:00
#SBATCH --mem-per-cpu=4G


source activate py36

python headbased_nner.py -n gpu -e 5 -s 0.1 -c gum5