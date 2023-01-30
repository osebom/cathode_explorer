from ase.io import read, write
from ase import io
from pathlib import Path
import os
import sys

file_path = sys.argv[1]

# Read the CIF file
atoms = read(file_path)

# Write the POSCAR file
write("POSCAR", atoms)

poscar_file_path = Path("POSCAR").resolve()
print("CIF file successfully converted to POSCAR")
print("The directory of the converted POSCAR file is:", poscar_file_path)
