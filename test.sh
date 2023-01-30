#!/bin/bash

src_folder=$1
dest_folder=$2
new_file=$3
second_file=$4
direc=$5
vals="/home/group5/scratch/U_values.csv"

cd $src_folder
cp -r INCAR-1 INCAR-2 KPOINTS-1 KPOINTS-2 sub_vasp_std.sh $dest_folder
cd ..
cd $dest_folder
echo "${local_file}"

my_array=()
new_array=()
last_arr=()
line_number=37

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
echo "Results: ${my_array[*]}"
echo "Results ${new_array[*]}"

for val in "${new_array[@]}"; do
  # Check if the value is present in the first column of the CSV file
    #match=$(awk -F "," '$1 == "'"$val"'" {print $2}' $vals)
    if [ $val == "0" ]; then
    last_arr+=("-1")

    else
    last_arr+=("2")
    fi
done
echo "${last_arr[*]}"

sed -i '36s/.*/LDAUL = '"${last_arr[*]}"'       # Fe-d    O    H    P (-1 no onsite +U)/' $new_file
sed -i '36s/.*/LDAUL = '"${last_arr[*]}"'       # Fe-d    O    H    P (-1 no onsite +U)/' $second_file
# join array values with ' ' separator
values_str=$(IFS=' '; echo "${new_array[*]}")

# construct new line
new_line="LDAUU = $values_str        # U-value (eV) [DOI: 10.1103/PhysRevB.84.045115]"

# replace line
sed -i "${line_number}s|.*|$new_line|" $new_file
sed -i "${line_number}s|.*|$new_line|" $second_file

array_length=${#last_arr[@]}

# Create a new array of zeroes
zeroes=()
for ((i=0; i<array_length; i++)); do
  zeroes+=(0)
done

sed -i '38s/.*/LDAUJ = '"${zeroes[*]}"'           # J-value (eV)/' $new_file
sed -i '38s/.*/LDAUJ = '"${zeroes[*]}"'           # J-value (eV)/' $second_file

