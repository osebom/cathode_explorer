#!/bin/bash

if [ "$#" -ne 3 ]; then
  echo "Error: Script expects three input files"
  exit 1
fi

sub_path=$1
poscar_path=$2
email=$3

# Read the first line of the first file into a variable called 'elements'
elements=$(sed '1q;d' $poscar_path)

# Replace 'MnO2' with the contents of the 'elements' variable in the third line of the second file
sed -i "3s/MnO2/$elements/" "$sub_path"

# Insert two new lines after the 7th line of the second file
sed -i '7a\
#SBATCH --mail-user='"$email"'\
#SBATCH --mail-type=ALL\
' "$sub_path"
