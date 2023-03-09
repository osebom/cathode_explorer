#!/bin/bash

vals="/home/group5/scratch/U_values.csv"
my_array=()
new_array=()
last_arr=()
line_number=37

if [ "$#" -ne 2 ]; then
  echo "Error: Script expects two input files"
  exit 1
fi

incar_path=$1
poscar_path=$2

if [ -r "$incar_path" ] && [ -r "$poscar_path" ]; then

  first_line=$(sed '1q;d' $poscar_path)

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

  for val in "${new_array[@]}"; do
    # Check if the value is present in the first column of the CSV file
      #match=$(awk -F "," '$1 == "'"$val"'" {print $2}' $vals)
      if [ $val == "0" ]; then
      last_arr+=("-1")

      else
      last_arr+=("2")
      fi
  done

  sed -i '36s/.*/LDAUL = '"${last_arr[*]}"'       # Fe-d    O    H    P (-1 no onsite +U)/' $incar_path
  # join array values with ' ' separator
  values_str=$(IFS=' '; echo "${new_array[*]}")

  # construct new line
  new_line="LDAUU = $values_str        # U-value (eV) [DOI: 10.1103/PhysRevB.84.045115]"

  # replace line
  sed -i "${line_number}s|.*|$new_line|" $incar_path

  array_length=${#last_arr[@]}

  # Create a new array of zeroes
  zeroes=()
  for ((i=0; i<array_length; i++)); do
    zeroes+=(0)
  done

  sed -i '38s/.*/LDAUJ = '"${zeroes[*]}"'            # J-value (eV)/' $incar_path
  
  echo "INCAR modified successfully!"

else
  echo "Error: One or both files do not exist or are not readable."
fi





