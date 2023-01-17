#!/bin/bash

# Prompt the user for the file to copy
read -p "Enter the path to the file to copy: " local_file

# Prompt the user for the name of the new folder on the remote server
read -p "Enter the name of the new folder on the remote server: " folder_name

# Copy the file to the remote server
scp "$local_file" group5@graham.computecanada.ca:/home/group5/scratch

# Connect to the remote server and create the new folder
ssh group5@graham.computecanada.ca "mkdir /home/group5/scratch/$folder_name"

# Move the copied file to the new folder on the remote server
ssh group5@graham.computecanada.ca "mv /home/group5/scratch/$(basename $local_file) /home/group5/scratch/$folder_name"


# Define the source and destination folders
src_folder="/home/group5/scratch/TiO2"
dest_folder="/home/group5/scratch/$folder_name"

# Connect to the SSH server
ssh group5@graham.computecanada.ca << EOF

# Navigate to the source folder
cd $src_folder

# Use the 'cp' command to copy all files from the source to the destination folder
cp -r INCAR-1 INCAR-2 KPOINTS-1 KPOINTS-2 sub_vasp_std.sh $dest_folder

# Confirm the files were copied
echo "Files from $src_folder successfully copied to $dest_folder"

EOF


