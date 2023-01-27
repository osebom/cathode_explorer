#!/bin/bash

direc="/Users/ojonyeagwu/Downloads/Ni2O3.poscar"
vals="/Users/ojonyeagwu/Desktop/U_values.csv"
new_file="/Users/ojonyeagwu/Downloads/INCAR-1_copy"
# Create an empty array
my_array=()
new_array=()

first_line=$(sed '1q;d' $direc)

# Get the elements and append them to the array
while IFS=' ' read -ra element; do
  for i in "${element[@]}"; do
    my_array+=("$i")
  done
done <<< "$(echo $first_line | grep -oE '[A-Z][a-z]*')"

# Print the array
echo "Results: ${my_array[*]}"

# Loop through the initial array
list=""
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
echo "Results ${new_array[*]}"

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
echo "${last_arr[*]}"

line_number=37
gsed -i '36s/.*/LDAUL = '"${last_arr[*]}"'       # Fe-d    O    H    P (-1 no onsite +U)/' $new_file
# join array values with ' ' separator
values_str=$(IFS=' '; echo "${new_array[*]}")

# construct new line
new_line="LDAUU = $values_str        # U-value (eV) [DOI: 10.1103/PhysRevB.84.045115]"

# replace line
gsed -i "${line_number}s|.*|$new_line|" $new_file