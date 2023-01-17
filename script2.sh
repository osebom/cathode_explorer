#!/bin/bash

# Prompt the user for the file to copy
read -p "Enter the path to the file to copy: " local_file

# Prompt the user for the name of the new folder on the remote server
read -p "Enter the name of the new folder on the remote server: " folder_name

# Prompt the user for the destination folder on the remote server
read -p "Enter the destination folder on the remote server: " destination_folder

# Prompt the user for the remote server's hostname
read -p "Enter the hostname of the remote server: " hostname

# Prompt the user for their username on the remote server
read -p "Enter your username on the remote server: " username

# Copy the file to the remote server
scp "$local_file" "$username@$hostname:$destination_folder"

# Connect to the remote server and create the new folder
ssh "$username@$hostname" "mkdir $destination_folder/$folder_name"

# Move the copied file to the new folder on the remote server
ssh "$username@$hostname" "mv $destination_folder/$(basename $local_file) $destination_folder/$folder_name"


