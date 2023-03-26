import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from pymatgen.core.structure import Structure
#from pymatgen.core.formula_composition import Composition
from pymatgen.core.composition import Composition
from pymatgen.io.cif import CifParser, CifBlock
import shutil
import subprocess
import pandas as pd
import re
from chempy import balance_stoichiometry
import math
from fractions import Fraction
import csv

class DFTInterface:
    def __init__(self, root):
        # Set window properties
        root.title('DFT Interface')
        root.geometry('600x600')
        root.configure(bg='black')

        # Add title label
        title_label = tk.Label(root, text='DFT Interface', font=('Arial', 24), bg='black', fg='white')
        title_label.pack(pady=20)

        # Add label for file path
        self.filepath_label = tk.Label(root, text='', font=('Arial', 14), bg='black', fg='white')
        self.filepath_label.pack(side='top', pady=20)

        # Add label for Element file path
        self.filepath_elem_label = tk.Label(root, text='', font=('Arial', 14), bg='black', fg='white')
        self.filepath_elem_label.pack(pady=20)

        # Add label for charge potential
        self.charge = tk.Label(root, text='', font=('Arial', 14), bg='black', fg='white')
        self.charge.pack(pady=20)

        # Add button to select CIF file
        select_cif_button = tk.Button(root, text='Select Zn CIF file', font=('Arial', 16), bg='white', fg='black', command=self.select_cif)
        select_cif_button.pack(side='left',pady=20)

        # Add button to select Element CIF file
        select_elem_button = tk.Button(root, text='Select Element CIF file', font=('Arial', 16), bg='white', fg='black', command=self.select_ele)
        select_elem_button.pack(side='left',pady=20)

        # Add label for calculation name
        calc_name_label = tk.Label(root, text='Calculation Name', font=('Arial', 14), bg='black', fg='white')
        calc_name_label.pack(pady=10)

        # Add entry for calculation name
        self.calculation_name_entry = tk.Entry(root, font=('Arial', 14), bg='white', fg='black')
        self.calculation_name_entry.pack(pady=20)

        # Add label for valence charge
        valence_label = tk.Label(root, text='Valence Charge', font=('Arial', 14), bg='black', fg='white')
        valence_label.pack(pady=10)

        # Add entry for valence charge
        self.valence_entry = tk.Entry(root, font=('Arial', 14), bg='white', fg='black')
        self.valence_entry.pack(pady=20)

        # Add label for email name
        email_name_label = tk.Label(root, text='Email', font=('Arial', 14), bg='black', fg='white')
        email_name_label.pack(pady=10)

        # Add entry for email
        self.email = tk.Entry(root, font=('Arial', 14), bg='white', fg='black')
        self.email.pack(pady=20)

        # Add button to submit calculation
        self.submit_button = tk.Button(root, text='Submit Calculation', font=('Arial', 16), bg='white', fg='black', command=self.submit_calculation)
        self.submit_button.pack(pady=20)

        # Add button to view calculation results
        self.view_results_button = tk.Button(root, text='View Calculation Results', font=('Arial', 16), bg='white', fg='black', command=self.view_results)
        self.view_results_button.pack(pady=20)

    def select_cif(self):
        # Prompt user to select CIF file
        filepath = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select CIF file', filetypes=(('CIF Files', '*.cif'), ('All Files', '*.*')))
        if filepath:
            # Display filepath in label
            self.filepath_label.configure(text=filepath)

    def select_ele(self):
        # Prompt user to select CIF file
        file_ele_path = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select Element CIF file', filetypes=(('CIF Files', '*.cif'), ('All Files', '*.*')))
        if file_ele_path:
            # Display filepath in label
            self.filepath_elem_label.configure(text=file_ele_path)

    def submit_calculation(self):
        # Get user input for calculation name and email
        calculation_name = self.calculation_name_entry.get()
        email_name = self.email.get()

        # Check if folder already exists
        if Path(f'/home/group5/scratch/{calculation_name}').exists():
            # Print message if folder already exists
            self.submit_button.configure(text='That name already exists, please pick a new one', bg='red', fg='white')
        else:
            # Create new folder for calculation
            os.mkdir(f'/home/group5/scratch/{calculation_name}')

            #Create withZinc, withoutZinc and Element folders
            os.mkdir(f'/home/group5/scratch/{calculation_name}/withZinc')
            os.mkdir(f'/home/group5/scratch/{calculation_name}/noZinc')
            os.mkdir(f'/home/group5/scratch/{calculation_name}/Element')

            # Convert CIF to POSCAR for withZinc and save in new folder
            cif_filepath = self.filepath_label['text']

            structure = Structure.from_file(cif_filepath)
            structure.to(fmt="poscar", filename=os.path.join(os.getcwd(), f'/home/group5/scratch/{calculation_name}/withZinc',"POSCAR"))

            poscar_file_path = os.path.join(os.getcwd(), f'/home/group5/scratch/{calculation_name}/withZinc/POSCAR')

            # Convert CIF to POSCAR for Element and save in new folder
            elem_cif_filepath = self.filepath_elem_label['text']
            structure = Structure.from_file(elem_cif_filepath)
            structure.to(fmt="poscar", filename=os.path.join(os.getcwd(), f'/home/group5/scratch/{calculation_name}/Element',"POSCAR"))

            poscar_elem_file_path = os.path.join(os.getcwd(), f'/home/group5/scratch/{calculation_name}/Element/POSCAR')

            # Create a new Structure object without the Zinc sites
            parser = CifParser(cif_filepath)
            structure = parser.get_structures()[0]

            # Create a list of site indices to remove
            sites_to_remove = []
            for i, site in enumerate(structure):
                if 'Zn' in str(site.specie):
                    sites_to_remove.append(i)

            new_sites = [site for i, site in enumerate(structure) if i not in sites_to_remove]
            new_structure = Structure(lattice=structure.lattice, species=[site.specie for site in new_sites], coords=[site.frac_coords for site in new_sites])
            new_structure.to(fmt="poscar", filename=os.path.join(os.getcwd(), f'/home/group5/scratch/{calculation_name}/noZinc/POSCAR'))

            #First copy for K-POINTS files because they don't need to be modified
            input_files_dir = os.path.join(os.getcwd(), '/home/group5/scratch/input_files')
            for incar_file in ['KPOINTS-1', 'KPOINTS-2']:
                src = os.path.join(input_files_dir, incar_file)
                dst_Zn = os.path.join(f'/home/group5/scratch/{calculation_name}/withZinc', incar_file)
                dst_noZn = os.path.join(f'/home/group5/scratch/{calculation_name}/noZinc', incar_file)
                dst_Elem = os.path.join(f'/home/group5/scratch/{calculation_name}/Element', incar_file)
                shutil.copy2(src, dst_Zn)
                shutil.copy2(src, dst_noZn)
                shutil.copy2(src, dst_Elem)

            #Second copy for other files that need modification
            for incar_file in ['INCAR-1', 'INCAR-2', 'sub_vasp_std.sh']:
                src = os.path.join(input_files_dir, incar_file)
                dst = os.path.join(f'/home/group5/scratch/{calculation_name}', incar_file)
                shutil.copy2(src, dst)

            #Modify INCAR-1 and INCAR-2 
            # os.system(f'/home/group5/scratch/process.sh /home/group5/scratch/{calculation_name}/INCAR-1')
            # os.system(f'/home/group5/scratch/process.sh /home/group5/scratch/{calculation_name}/INCAR-2')

            input_files_dir = os.path.join(os.getcwd(), f'/home/group5/scratch/{calculation_name}')
            for incar_file in ['INCAR-1', 'INCAR-2', 'sub_vasp_std.sh']:
                src = os.path.join(input_files_dir, incar_file)
                dst_Zn = os.path.join(f'/home/group5/scratch/{calculation_name}/withZinc', incar_file)
                dst_noZn = os.path.join(f'/home/group5/scratch/{calculation_name}/noZinc', incar_file)
                dst_Elem = os.path.join(f'/home/group5/scratch/{calculation_name}/Element', incar_file)
                shutil.copy2(src, dst_Zn)
                shutil.copy2(src, dst_noZn)

                #Modify files for withZinc
                if incar_file == 'sub_vasp_std.sh':
                    #Maybe use subprocess?
                    os.system(f'/home/group5/scratch/mod_subvasp.sh /home/group5/scratch/{calculation_name}/withZinc/sub_vasp_std.sh /home/group5/scratch/{calculation_name}/withZinc/POSCAR {email_name}') 
                else:
                    os.system(f'/home/group5/scratch/mod_incar2.sh /home/group5/scratch/{calculation_name}/withZinc/{incar_file} /home/group5/scratch/{calculation_name}/withZinc/POSCAR')                

                #Modify files for noZinc
                if incar_file == 'sub_vasp_std.sh':
                    #Maybe use subprocess?
                    os.system(f'/home/group5/scratch/mod_subvasp.sh /home/group5/scratch/{calculation_name}/noZinc/sub_vasp_std.sh /home/group5/scratch/{calculation_name}/noZinc/POSCAR {email_name}') 
                else:
                    os.system(f'/home/group5/scratch/mod_incar2.sh /home/group5/scratch/{calculation_name}/noZinc/{incar_file} /home/group5/scratch/{calculation_name}/noZinc/POSCAR') 

                shutil.move(src, dst_Elem)
                #Modify files for Element
                if incar_file == 'sub_vasp_std.sh':
                    #Maybe use subprocess?
                    os.system(f'/home/group5/scratch/mod_subvasp.sh /home/group5/scratch/{calculation_name}/Element/sub_vasp_std.sh /home/group5/scratch/{calculation_name}/Element/POSCAR {email_name}') 
                else:
                    os.system(f'/home/group5/scratch/mod_incar2.sh /home/group5/scratch/{calculation_name}/Element/{incar_file} /home/group5/scratch/{calculation_name}/Element/POSCAR')                  

                # # specify the Bash commands to run with Zn calculation
                # bash_commands = "cd /home/group5/scratch/{}/withZinc;sbatch sub_vasp_std.sh".format(calculation_name)
                # # run the Bash commands
                # subprocess.run(["bash", "-c", bash_commands])

                # # specify the Bash commands to run with no Zn calculation
                # bash_commands = "cd /home/group5/scratch/{}/noZinc;sbatch sub_vasp_std.sh".format(calculation_name)
                # # run the Bash commands
                # subprocess.run(["bash", "-c", bash_commands])

                # # specify the Bash commands to run with Element
                # bash_commands = "cd /home/group5/scratch/{}/Element;sbatch sub_vasp_std.sh".format(calculation_name)
                # # run the Bash commands
                # subprocess.run(["bash", "-c", bash_commands])

            # Print message confirming submission
            #Before showing Submitted!, make it just if sbatch was run
            self.submit_button.configure(text='Calculation Submitted!', bg='green', fg='white')

    def get_poscarnum(self, poscar_path):
        # Open the file for reading
        with open(poscar_path, 'r') as file:

            # Read the lines of the file into a list
            lines = file.readlines()

            # Get the elements from line 6 and the numbers from line 7
            elements = lines[5].split()
            numbers = lines[6].split()

            # Create a dictionary to store the element-number pairs
            element_dict = {}

            # Loop over the elements and numbers and add them to the dictionary
            for i in range(len(elements)):
                element_dict[elements[i]] = int(numbers[i])

            # Print the dictionary
            print("Element-Number dictionary:", element_dict)

            # Look up the value for the element that is not 'Zn' nor 'O'
            for element in element_dict:
                if element not in ['Zn', 'O']:
                    value = element_dict[element]
                    break

            # Print the value for the element that is not 'Zn' nor 'O'
            print("Value for element {}: {}".format(element, value))
            return value

    def get_poscarnumzinc(self, poscar_path):
        # Open the file for reading
        with open(poscar_path, 'r') as file:

            # Read the lines of the file into a list
            lines = file.readlines()

            # Get the elements from line 6 and the numbers from line 7
            elements = lines[5].split()
            numbers = lines[6].split()

            # Create a dictionary to store the element-number pairs
            element_dict = {}

            # Loop over the elements and numbers and add them to the dictionary
            for i in range(len(elements)):
                element_dict[elements[i]] = int(numbers[i])

            Zn_value = element_dict['Zn']
            return Zn_value            

    def get_E0(self, slurm_path):
        with open(slurm_path, 'r') as f:
            # Read the file into a string
            file_contents = f.read()

        # Define the regular expression pattern to match "E0=" followed by a number
        pattern = r"E0= *([-+]?\d*\.\d+[Ee][-+]?\d+)"

        # Find all matches of the pattern in the file contents
        matches = re.findall(pattern, file_contents)

        # If there are any matches, print the last one
        if len(matches) > 0:
            e0_value = matches[-1]
            e0_value = float(e0_value)
        else:
            print("No matches found.")
        return e0_value

    def get_ratio(self, poscar_path):
        # Open the file for reading
        with open(poscar_path, 'r') as file:

            # Read the lines of the file into a list
            lines = file.readlines()

            # Get the elements from line 6 and the numbers from line 7
            elements = lines[5].split()
            numbers = lines[6].split()

            # Create a dictionary to store the element-number pairs
            element_dict = {}

            # Loop over the elements and numbers and add them to the dictionary
            for i in range(len(elements)):
                element_dict[elements[i]] = int(numbers[i])

            # Print the dictionary
            print("Element-Number dictionary:", element_dict)

            # Look up the value for the element that is not 'Zn' nor 'O'
            for element in element_dict:
                if element not in ['Zn', 'O']:
                    element_value = element_dict[element]
                    break

            # Print the value for the element that is not 'Zn' nor 'O'
            Zn_value = element_dict['Zn']
            ratio = float(element_value)/float(Zn_value)
            return ratio
        
        ratio = float(num)/float(Zn_num)
        return ratio

    def get_oxide_coeffs(self, metal_oxide_poscar):
        # Open the file for reading
        structure = Structure.from_file(metal_oxide_poscar)  

        # Get the formula of the structure
        formula = Composition(structure.formula)

        # Balance the formula (aka the metal oxide)
        balanced_formula = formula.reduced_formula

        # Get the element from the formula
        element_counts = Composition(balanced_formula).as_dict()
        element = [k for k in element_counts.keys() if k != 'O'][0]

        reac, prod = balance_stoichiometry({element,'O2'}, {balanced_formula})

        stoichiometry = reac.copy()
        stoichiometry.update(prod)

        #Coefficients
        element_coeff = float(stoichiometry[element])
        oxygen_coeff = float(stoichiometry['O2']) / element_coeff
        metal_oxide_coeff = float(stoichiometry[balanced_formula]) / element_coeff

        elem_norm = element_coeff / element_coeff

        print(stoichiometry)

        return elem_norm, oxygen_coeff, metal_oxide_coeff

    def view_results(self):
        # Prompt user to select folder
        folderpath = filedialog.askdirectory(initialdir=os.getcwd(), title='Select folder')
        if folderpath:
            # Create new window for results
            results_window = tk.Toplevel()
            results_window.title('Calculation')
            results_window.geometry('600x600')
            results_window.configure(bg='black')

            # Add home button
            home_button = tk.Button(results_window, text='Home', font=('Arial', 16), bg='white', fg='black', command=results_window.destroy)
            home_button.pack(side='left', padx=20, pady=20)

            # Get values from POSCAR file with Zn
            withZn_poscar_path = os.path.join(folderpath,"withZinc","POSCAR")
            withZn_fu = self.get_poscarnumzinc(withZn_poscar_path)

            # Get values from POSCAR file without Zn
            noZn_poscar_path = os.path.join(folderpath,"noZinc","POSCAR")
            noZn_fu = self.get_poscarnum(noZn_poscar_path)

            # Get values from POSCAR file with only Element
            Elem_poscar_path = os.path.join(folderpath,"Element","POSCAR")
            Elem_fu = self.get_poscarnum(Elem_poscar_path)            

            # get a list of files in the folder with a .out extension
            withZn_slurm_path = [f for f in os.listdir(folderpath + "/withZinc") if f.startswith("slurm")][0]
            withZn_slurmpath = os.path.join(folderpath,"withZinc",withZn_slurm_path)
            EO_withZn = self.get_E0(withZn_slurmpath)

            # get a list of files in the folder with a .out extension
            noZn_slurm_path = [f for f in os.listdir(folderpath+ "/noZinc") if f.startswith("slurm")][0]
            noZn_slurmpath = os.path.join(folderpath,"noZinc",noZn_slurm_path)
            EO_noZn = self.get_E0(noZn_slurmpath)

            # get a list of files in the folder with a .out extension
            Elem_slurm_path = [f for f in os.listdir(folderpath+ "/Element") if f.startswith("slurm")][0]
            Elem_slurmpath = os.path.join(folderpath,"Element", Elem_slurm_path)
            EO_Elem = self.get_E0(Elem_slurmpath)


            #Charge Potentail
            E0_Zn_norm = -2.8920807 / 2
            E0_withZn_norm = float(EO_withZn) / float(withZn_fu)
            E0_noZn_norm = float(EO_noZn) / float(noZn_fu)
            ratio = self.get_ratio(withZn_poscar_path)
            E0_rxn_norm = float(E0_Zn_norm) + (float(ratio)*float(E0_noZn_norm))
            charge_pot = (float(E0_rxn_norm) - float(E0_withZn_norm)) / 2

            # Add table
            # Create a Pandas dataframe with the variables
            df = pd.DataFrame({
                'ZnMoO3': EO_withZn,
                'fu ZnMoO3': withZn_fu,
                'MoO3': EO_noZn,
                'fu MoO3': noZn_fu,
                'ZnMoO3 norm': E0_withZn_norm,
                'MoO3 norm': E0_noZn_norm,
                'Rxn': E0_rxn_norm,
                'ratio': ratio
            }, index=pd.RangeIndex(4))

            # Create label for the table
            table_label = tk.Label(results_window, text='Calculation Results', font=('Arial', 16), bg='black', fg='white')
            table_label.pack(pady=20)

            # Create a Pandas dataframe widget
            df_widget = tk.Frame(results_window, bg='white')
            df_widget.pack()

            # Create a scrollbar for the dataframe widget
            scrollbar = tk.Scrollbar(df_widget)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Create the table using the dataframe widget
            table = tk.Text(df_widget, wrap=tk.NONE, bg='white', yscrollcommand=scrollbar.set)
            table.pack()

            # Add the data to the table
            table.insert(tk.END, df.to_string(index=False))

            # Configure the scrollbar to work with the table
            scrollbar.config(command=table.yview)

            total_label = tk.Label(results_window, text=f"Total Charge Pot: {charge_pot}", font=("Helvetica", 10, "bold"), bg='black', fg='white')
            total_label.pack(pady=10)

            if charge_pot > 0: 
                #CHEMICAL POTENTIAL
                E0_Elem_norm = float(EO_Elem)/ float(Elem_fu)
                E0_Oxygen_norm = -19.861171 / 2

                element_coeff, oxygen_coeff, metal_oxide_coeff = self.get_oxide_coeffs(noZn_poscar_path)
                H_prod = E0_noZn_norm * float(metal_oxide_coeff)
                H_reac = E0_Elem_norm * float(element_coeff) + E0_Oxygen_norm * float(oxygen_coeff)

                #Also known as G_reactants
                H_rxn = H_prod - H_reac

                #e(pH=5)
                pH = 5
                # Load the structure from the POSCAR file
                structure = Structure.from_file(noZn_poscar_path)

                # Get the formula of the structure
                formula = Composition(structure.formula)

                # Get the element names and their counts in the formula
                element_counts = formula.as_dict()

                # Get the coefficient of the element that is not oxygen
                non_oxygen_element = [k for k in element_counts.keys() if k != 'O'][0]
                coefficient = element_counts[non_oxygen_element]

                # Normalize the coefficients of all elements
                normalized_counts = {k: v/coefficient for k, v in element_counts.items()}
                metal_ion_coeff = float(normalized_counts[non_oxygen_element])
                H_ions_num = float(normalized_counts['O']) * 2
                H2O_coeff = float(normalized_counts['O'])
                valence_charge = self.valence_entry.get()
                electrons_num = float(valence_charge) * float(metal_ion_coeff)

                # Open the CSV file for reading
                with open('/home/group5/scratch/Charge_Potentials.csv', 'r') as file:
                    reader = csv.reader(file)
                    found = False
                    chem_stability = None
                    # Iterate over each row in the file
                    for row in reader:
                        # Check if the string is in the first column
                        if row[0] == non_oxygen_element:
                            found = True
                            chem_stability = row[2]
                            break

                    # Check if the string was found
                    if found:
                        print('Chemical stability found')
                    else:
                        print('String not found in first column.')
                
                G_prod = metal_ion_coeff * float(chem_stability) + H2O_coeff * (-2.458)
                G_rxn = G_prod - H_rxn

                E = - (G_rxn / electrons_num)
                e_pH5 = E - ( (0.059* H_ions_num) / electrons_num ) * pH

                charge_pot_norm = charge_pot - 0.762

                if -0.295 < charge_pot_norm < 0.934:
                    if charge_pot_norm > e_pH5:
                        label14 = tk.Label(results_window, text=f"Material Works!, Charge Pot norm ({charge_pot_norm}) is higher than Electro-chem Stab ({e_pH5})", font=("Helvetica", 10, "bold"), bg='black', fg='white')
                        label14.pack(pady=20)  
                    else:
                        label15 = tk.Label(results_window, text=f"Material Doesn't Work!, e_pH5 ({e_pH5}) is higher than Charge Potential", font=("Helvetica", 10, "bold"), bg='black', fg='white')
                        label15.pack(pady=20) 

                else:
                    label13 = tk.Label(results_window, text=f"Material doesn't work with evolutions: Normalized Charge Pot ({charge_pot_norm}) is not between evolutions, G rxn = {G_rxn}, H rxn = {H_rxn}", font=("Helvetica", 10, "bold"), bg='black', fg='white')
                    label13.pack(pady=20)                    

            else:
                label12 = tk.Label(results_window, text=f"Charge potential is negative: {charge_pot}, therefore it doesn't work", font=("Helvetica", 10, "bold"), bg='black', fg='white')
                label12.pack(pady=20)



            # # Create table with pandas
            # data = {'Values': [val1, val2]}
            # df = pd.DataFrame(data)
            # table = tk.Label(results_window, text=df.to_string(index=False), font=('Arial', 14))
            # table.pack(pady=20)

        else:
            print("No folder")

# Create and run app
root = tk.Tk()
app = DFTInterface(root)
root.mainloop()
