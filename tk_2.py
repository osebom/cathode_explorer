import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from pymatgen.core.structure import Structure
from pymatgen.io.cif import CifParser, CifBlock
import shutil
import subprocess
import pandas as pd
import re

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
        self.filepath_label.pack(pady=20)

        # Add label for charge potential
        self.charge = tk.Label(root, text='', font=('Arial', 14), bg='black', fg='white')
        self.charge.pack(pady=20)

        # Add button to select CIF file
        select_cif_button = tk.Button(root, text='Select CIF file', font=('Arial', 16), bg='white', fg='black', command=self.select_cif)
        select_cif_button.pack(pady=20)

        # Add label for calculation name
        calc_name_label = tk.Label(root, text='Calculation Name', font=('Arial', 14), bg='black', fg='white')
        calc_name_label.pack(pady=10)

        # Add entry for calculation name
        self.calculation_name_entry = tk.Entry(root, font=('Arial', 14), bg='white', fg='black')
        self.calculation_name_entry.pack(pady=20)

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

            #Create withZinc and withoutZinc folders
            os.mkdir(f'/home/group5/scratch/{calculation_name}/withZinc')
            os.mkdir(f'/home/group5/scratch/{calculation_name}/noZinc')

            # Convert CIF to POSCAR withZinc and save in new folder
            cif_filepath = self.filepath_label['text']

            structure = Structure.from_file(cif_filepath)
            structure.to(fmt="poscar", filename=os.path.join(os.getcwd(), f'/home/group5/scratch/{calculation_name}/withZinc',"POSCAR"))

            poscar_file_path = os.path.join(os.getcwd(), f'/home/group5/scratch/{calculation_name}/withZinc/POSCAR')
            parser = CifParser(cif_filepath)
            structure = parser.get_structures()[0]

            # Create a list of site indices to remove
            sites_to_remove = []
            for i, site in enumerate(structure):
                if 'Zn' in str(site.specie):
                    sites_to_remove.append(i)

            # Create a new Structure object without the Zinc sites
            new_sites = [site for i, site in enumerate(structure) if i not in sites_to_remove]
            new_structure = Structure(lattice=structure.lattice, species=[site.specie for site in new_sites], coords=[site.frac_coords for site in new_sites])
            new_structure.to(fmt="poscar", filename=os.path.join(os.getcwd(), f'/home/group5/scratch/{calculation_name}/noZinc/POSCAR'))

            input_files_dir = os.path.join(os.getcwd(), '/home/group5/scratch/input_files')
            for incar_file in ['KPOINTS-1', 'KPOINTS-2']:
                src = os.path.join(input_files_dir, incar_file)
                dst_Zn = os.path.join(f'/home/group5/scratch/{calculation_name}/withZinc', incar_file)
                dst_noZn = os.path.join(f'/home/group5/scratch/{calculation_name}/noZinc', incar_file)
                shutil.copy2(src, dst_Zn)
                shutil.copy2(src, dst_noZn)

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
                shutil.copy2(src, dst_Zn)

                #Modify files for withZinc
                if incar_file == 'sub_vasp_std.sh':
                    #Maybe use subprocess?
                    os.system(f'/home/group5/scratch/mod_subvasp.sh /home/group5/scratch/{calculation_name}/withZinc/sub_vasp_std.sh /home/group5/scratch/{calculation_name}/withZinc/POSCAR {email_name}') 
                else:
                    os.system(f'/home/group5/scratch/mod_incar.sh /home/group5/scratch/{calculation_name}/withZinc/{incar_file} /home/group5/scratch/{calculation_name}/withZinc/POSCAR')                

                shutil.move(src, dst_noZn)

                #Modify files for noZinc
                if incar_file == 'sub_vasp_std.sh':
                    #Maybe use subprocess?
                    os.system(f'/home/group5/scratch/mod_subvasp.sh /home/group5/scratch/{calculation_name}/noZinc/sub_vasp_std.sh /home/group5/scratch/{calculation_name}/noZinc/POSCAR {email_name}') 
                else:
                    os.system(f'/home/group5/scratch/mod_incar.sh /home/group5/scratch/{calculation_name}/noZinc/{incar_file} /home/group5/scratch/{calculation_name}/noZinc/POSCAR')                 

            # Print message confirming submission
            self.submit_button.configure(text='Calculation Submitted!', bg='green', fg='white')

    def get_poscarnum(self, poscar_path):
        with open(poscar_path, 'r') as f:
            first_line = f.readline().split()
        element_of_interest = None
        for element in first_line:
            if "Zn" not in element and "O" not in element:
                element_of_interest = element
                break
                
        if element_of_interest is not None:
            nums = re.findall(r'\d+', element_of_interest)
            num = nums[0]
        else:
            print("Could not find the element of interest")
        return num

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

    def get_ratio(self, poscarpath):
        with open(poscarpath, 'r') as f:
            first_line = f.readline().split()

        #Element of interest
        element_of_interest = None
        for element in first_line:
            if "Zn" not in element and "O" not in element:
                element_of_interest = element
                break        
        if element_of_interest is not None:
            nums = re.findall(r'\d+', element_of_interest)
            num = nums[0]
        else:
            print("Could not find the element of interest")
        
        #For Zinc
        for element in first_line:
            if "Zn" in element:
                Zn = element
                break        
        if Zn is not None:
            Zn_nums = re.findall(r'\d+', Zn)
            Zn_num = Zn_nums[0]
        else:
            print("Could not find Zn")
        
        ratio = float(num)/float(Zn_num)
        return ratio

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
            withZn_fu = self.get_poscarnum(withZn_poscar_path)

            # Get values from POSCAR file without Zn
            noZn_poscar_path = os.path.join(folderpath,"noZinc","POSCAR")
            noZn_fu = self.get_poscarnum(withZn_poscar_path)

            # get a list of files in the folder with a .out extension
            withZn_slurm_path = [f for f in os.listdir(folderpath + "/withZinc") if f.startswith("slurm")][0]
            withZn_slurmpath = os.path.join(folderpath,"withZinc",withZn_slurm_path)
            EO_withZn = self.get_E0(withZn_slurmpath)

            # get a list of files in the folder with a .out extension
            noZn_slurm_path = [f for f in os.listdir(folderpath+ "/noZinc") if f.startswith("slurm")][0]
            noZn_slurmpath = os.path.join(folderpath,"noZinc",noZn_slurm_path)
            EO_noZn = self.get_E0(noZn_slurmpath)

            E0_Zn_norm = -2.8920807 / 2
            E0_withZn_norm = float(EO_withZn) / float(withZn_fu)
            E0_noZn_norm = float(EO_noZn) / float(noZn_fu)
            ratio = self.get_ratio(withZn_poscar_path)
            E0_rxn_norm = float(E0_Zn_norm) + (float(ratio)*float(E0_noZn_norm))
            charge_pot = (float(E0_rxn_norm) - float(E0_Zn_norm)) / 2

            #label_ = tk.Label(results_window, text=self.charge.cget(charge_pot))
            label_ = tk.Label(results_window, text=charge_pot)
            label_.pack()

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