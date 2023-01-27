#!/bin/bash

# Prompt the user for the file to copy
read -p "Enter the path to the file to copy: " local_file

# Prompt the user for the name of the new folder on the remote server
read -p "Enter the name of the new folder on the remote server: " folder_name

# Copy the file to the remote server
scp "$local_file" group5@graham.computecanada.ca:/home/group5/scratch

# Connect to the remote server and create the new folder
ssh group5@graham.computecanada.ca "mkdir /home/group5/scratch/$folder_name; mv /home/group5/scratch/$(basename $local_file) /home/group5/scratch/$folder_name"

# Define the source and destination folders
src_folder="/home/group5/scratch/TiO2"
dest_folder="/home/group5/scratch/$folder_name"

# Connect to the SSH server
ssh group5@graham.computecanada.ca << EOF

# Navigate to the source folder
cd $src_folder

# Use the 'cp' command to copy all files from the source to the destination folder
cp -r INCAR-1 INCAR-2 KPOINTS-1 KPOINTS-2 sub_vasp_std.sh $dest_folder

cd ..
cd $dest_folder

#mv $(basename $local_file) POSCAR

#POSCAR path
direc="/home/group5/scratch/$folder_name/POSCAR"

vals="/home/group5/scratch/U_values.csv"
new_file="/home/group5/scratch/$folder_name/INCAR-1"
second_file="/home/group5/scratch/$folder_name/INCAR-2"

my_array=()
new_array=()

first_line=$(sed '1q;d' $direc)

# Get the elements and append them to the array
while IFS=' ' read -ra element; do
  for i in "${element[@]}"; do
    my_array+=("$i")
  done
done <<< "$(echo $first_line | grep -oE '[A-Z][a-z]*')"

for val in "${my_array[@]}"; do
  # Check if the value is present in the first column of the CSV file
    #match=$(awk -F "," '$1 == "'"$val"'" {print $2}' $vals)
    match=$(awk -F "," '$1 == "'"$val"'" {print $2}' $vals)

    if [ -n "$match" ]; then
    echo "$match"
    match=$(echo $match | awk '{print ($0+0)}')
        #new_array[${#new_array[@]}]=$match
    new_array+=("$match")
    else
    # If no match is found, add 0 to the new array
    #new_array[${#new_array[@]}]=0
        #new_array+=("0")
    new_array+=("0")
    fi
done

last_arr=()
for val in "${new_array[@]}"; do
  # Check if the value is present in the first column of the CSV file
    #match=$(awk -F "," '$1 == "'"$val"'" {print $2}' $vals)
    if [ $val == "0" ]; then
    last_arr+=("-1")

    else
    last_arr+=("2")
    fi
done

line_number=37
perl -i -pe '$_="LDAUL = '"${last_arr[*]}"' # Fe-d O H P (-1 no onsite +U)" if $.==36' $new_file
# join array values with ' ' separator
values_str=$(IFS=' '; echo "${new_array[*]}")

# construct new line
new_line="LDAUU = $values_str        # U-value (eV) [DOI: 10.1103/PhysRevB.84.045115]"

# replace line
perl -i -pe "s/.*/$new_line/ if $.==$line_number" $new_file


#For INCAR-2
perl -i -pe '$_="LDAUL = '"${last_arr[*]}"' # Fe-d O H P (-1 no onsite +U)" if $.==36' $second_file
perl -i -pe "s/.*/$new_line/ if $.==$line_number" $second_file

EOF
