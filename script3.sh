#!/bin/bash

# Get the directory of the CIF file
echo "Enter the directory of the CIF file:"
read cif_file

# Call the Python script to convert the CIF file to a POSCAR file
python3 /Users/ojonyeagwu/Desktop/scripts/POSCAR.py "$cif_file"

# Get the directory of the POSCAR file
local_file=$(ls -t | grep 'POSCAR' | head -1)

# Perform other actions with the POSCAR file
echo "The POSCAR file is located at: $local_file"
read -p "Enter the name of the new folder on the remote server: " folder_name

# Copy the file to the remote server
scp "$local_file" group5@graham.computecanada.ca:/home/group5/scratch

# Connect to the remote server and create the new folder
ssh group5@graham.computecanada.ca "mkdir /home/group5/scratch/$folder_name; mv /home/group5/scratch/$(basename $local_file) /home/group5/scratch/$folder_name"

remote_script="/home/group5/scratch/test.sh"
# Define the source and destination folders
src_folder="/home/group5/scratch/TiO2"
dest_folder="/home/group5/scratch/$folder_name"
new_file="/home/group5/scratch/$folder_name/INCAR-1"
second_file="/home/group5/scratch/$folder_name/INCAR-2"
direc="/home/group5/scratch/'"$folder_name"'/POSCAR"

ssh group5@graham.computecanada.ca "bash -c '$remote_script $src_folder $dest_folder $new_file $second_file $direc $local_file'"

#Delete file
rm $local_file