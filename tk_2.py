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
import matplotlib.pyplot as plt
import nglview
import numpy as np
from PIL import ImageTk, Image
from matplotlib.patches import Rectangle
from tkinter import ttk
from tkinter.font import Font
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymatgen.core.structure import Structure
from chempy import balance_stoichiometry
from IPython.display import Latex


class DFTInterface:
    def __init__(self, root):
        # Set window properties
        # root.title('DFT Interface')
        # root.geometry('1200x600')
        # #root.attributes('-fullscreen', True)
        # root.resizable(0, 0)
        # root.configure(bg='white')
        root.title('DFT Interface')
        root.configure(bg='white')

        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate x and y coordinates for the window
        x = (screen_width // 2) - (1200 // 2)
        y = (screen_height // 2) - (600 // 2)

        # Set window position and size
        root.geometry('1200x600+{}+{}'.format(x, y))
        root.resizable(0, 0)



        # Add title label
        title_label = tk.Label(root, text='DFT Interface', font=('Kozuka Gothic Pro R', 24), bg='white', fg='black')
        title_label.place(relx=0.5, rely=0.1, anchor='center')

        # Add label for file path
        # self.filepath_label = tk.Label(root, text='', font=('Arial', 14), bg='black', fg='white')
        # self.filepath_label.pack(side='top', pady=20)
        self.filepath_label = tk.Label(root, text='', font=('Arial', 14), bg='black', fg='white')
        self.filepath_label.pack(side='bottom', anchor='center',padx=20)

        # Add label for Element file path
        # self.filepath_elem_label = tk.Label(root, text='', font=('Arial', 14), bg='black', fg='white')
        # self.filepath_elem_label.pack(pady=20)
        self.filepath_elem_label = tk.Label(root, text='', font=('Arial', 14), bg='black', fg='white')
        self.filepath_elem_label.pack(side='bottom', pady=20,padx=20)

        # Add label for charge potential
        # self.charge = tk.Label(root, text='', font=('Arial', 14), bg='black', fg='white')
        # self.charge.pack(pady=20)

        # Add frame for input fields
        input_frame = tk.LabelFrame(root, text='Input Parameters', font=('Arial', 16), bg='white', fg='black')
        input_frame.place(relx=0.3, rely=0.8, anchor='sw', width=500)
        #input_frame.place(rely=0.3, anchor='center', width=500)

        #THIS IS WHERE IT STOPS

        # Add button to select CIF file
        select_cif_button = tk.Button(input_frame, text='Select Zn + Cathode CIF file', font=('Arial', 12), bg='white', fg='black', command=self.select_cif)
        #select_cif_button.pack(side='bottom', anchor='center')
        select_cif_button.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        # Add button to select Element CIF file
        select_elem_button = tk.Button(input_frame, text='Select Metal CIF file', font=('Arial', 12), bg='white', fg='black', command=self.select_ele)
        #select_elem_button.pack(side='bottom',pady=20)
        select_elem_button.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        # Add label for calculation name
        calc_name_label = tk.Label(input_frame, text='Calculation Name:', font=('Arial', 14), bg='white', fg='black')
        calc_name_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        # Add entry for calculation name
        self.calculation_name_entry = tk.Entry(input_frame, font=('Arial', 14), bg='white', fg='black')
        self.calculation_name_entry.grid(row=1, column=1, padx=10, pady=10)

        # Add label for valence charge
        valence_label = tk.Label(input_frame, text='Valence Charge:', font=('Arial', 14), bg='white', fg='black')
        valence_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')

        # Add entry for valence charge
        self.valence_entry = tk.Entry(input_frame, font=('Arial', 14), bg='white', fg='black')
        self.valence_entry.grid(row=2, column=1, padx=10, pady=10)

        # Add label for email name
        email_name_label = tk.Label(input_frame, text='Email:', font=('Arial', 14), bg='white', fg='black')
        email_name_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')

        # Add entry for email
        self.email = tk.Entry(input_frame, font=('Arial', 14), bg='white', fg='black')
        self.email.grid(row=3, column=1, padx=10, pady=10)    

        # Add button to submit calculation
        self.submit_button = tk.Button(input_frame, text='Submit Calculation', font=('Arial', 16), bg='white', fg='black', command=self.submit_calculation)
        self.submit_button.grid(row=4, column=1, padx=10, pady=10) 

        # Add button to view calculation results
        self.view_results_button = tk.Button(input_frame, text='View Calculation Results', font=('Arial', 16), bg='white', fg='black', command=self.view_results)
        self.view_results_button.grid(row=5, column=1, padx=10, pady=10) 

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

                # specify the Bash commands to run with Zn calculation
                bash_commands = "cd /home/group5/scratch/{}/withZinc;sbatch sub_vasp_std.sh".format(calculation_name)
                # run the Bash commands
                subprocess.run(["bash", "-c", bash_commands])

                # specify the Bash commands to run with no Zn calculation
                bash_commands = "cd /home/group5/scratch/{}/noZinc;sbatch sub_vasp_std.sh".format(calculation_name)
                # run the Bash commands
                subprocess.run(["bash", "-c", bash_commands])

                # specify the Bash commands to run with Element
                bash_commands = "cd /home/group5/scratch/{}/Element;sbatch sub_vasp_std.sh".format(calculation_name)
                # run the Bash commands
                subprocess.run(["bash", "-c", bash_commands])

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

    def plot_graph(self,E, H_ions_num,electrons_num, charge_pot_norm, e_stab):
        # Generate some sample data
        x = np.linspace(0, 8, 100)
        y1 = 1.229 - 0.059 * x
        y2 = -0.059 * x

        y3 = E-(H_ions_num *0.059/electrons_num)*x
        y4 = np.full_like(x, charge_pot_norm) 

        # Create a figure and add a subplot
        #fig = Figure(figsize=(8,4), dpi=100)
        fig = Figure(figsize=(7.4,4.3), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(x, y1, color='yellow', label='Oxygen Evolution Reaction')
        ax.plot(x, y2, color='blue', label='Hydrogen Evolution Reaction')
        ax.plot(x, y4, color='purple', label='Normalized Charge Potential')
        ax.plot(x, y3, color='black', label='Electro-chemical Stability')

        if -0.295 < e_stab < 0.934:
            # Add the data to the plot
            # Fill area between y1 and y3 with green
            ax.fill_between(x, y1, y3, where=(y1 > y2), color='green', alpha=0.5)

            # Fill area above y1 with red
            ax.fill_between(x, y1, 1.5, where=(y3 < 1.5), color='red', alpha=0.5)

            # Fill area below y3 with green
            ax.fill_between(x, y3, -1, where=(y3 > -1), color='red', alpha=0.5)

        else:
            # Add the data to the plot
            # Fill area between y1 and y3 with green
            ax.fill_between(x, y1, y2, where=(y1 > y2), color='green', alpha=0.5)

            # Fill area above y1 with red
            ax.fill_between(x, y1, 1.5, where=(y3 < 1.5), color='red', alpha=0.5)

            # Fill area below y3 with green
            ax.fill_between(x, y2, -1, where=(y2 > -1), color='red', alpha=0.5)    

        # # compute angle in raw data coordinates (no manual transforms)
        # dy = y1[1] - y1[0]
        # dx = x[1] - x[0]
        # angle = np.rad2deg(np.arctan2(dy, dx))

        # # Find the index of the element in `x` closest to 2
        # idx = np.abs(x - 8).argmin()

        # # Get the value of `y` at that index
        # y_1 = y1[idx]

        # # annotate with transform_rotates_text to align text and line
        # ax.text(4.5, y_1+0.2, 'Oxy Rev Rxn', ha='left', va='bottom',
        #         transform_rotates_text=True, rotation=angle, rotation_mode='anchor')


        # # compute angle in raw data coordinates (no manual transforms)
        # dy2 = y2[1] - y2[0]
        # angle2 = np.rad2deg(np.arctan2(dy2, dx))

        # # Get the value of `y` at that index
        # y_2= y2[idx]

        # # annotate with transform_rotates_text to align text and line
        # ax.text(6.2, y_2+0.1, 'Hydrogen Rev Rxn', ha='left', va='bottom',
        #         transform_rotates_text=True, rotation=angle2, rotation_mode='anchor')


        # # compute angle in raw data coordinates (no manual transforms)
        # dy3 = y3[1] - y3[0]
        # angle3 = np.rad2deg(np.arctan2(dy3, dx))

        # # Get the value of `y` at that index
        # y_3 = y3[idx]

        # # annotate with transform_rotates_text to align text and line
        # ax.text(6, y_3+0.25, 'Electro-Chem Stablty', ha='left', va='bottom',
        #         transform_rotates_text=True, rotation=angle3, rotation_mode='anchor')

        # Set the x and y axis labels and title
        ax.set_xlabel('pH')
        ax.set_ylabel('V (SHE)')
        #ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1))

        # Adjust the size of the plot
        #ax.set_position([0.12, 0.35, 0.6, 0.6])  # [left, bottom, width, height]
        ax.set_position([0.12, 0.1, 0.6, 0.8])  # [left, bottom, width, height]
        ax.set_xlim([0.5, 3.5])
        ax.set_ylim([0, 20])

        # Add a legend and adjust its size
        ax.legend(loc='upper left',bbox_to_anchor=(1, 1), prop={'size': 8.2})
        #ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), prop={'size': 10}, ncol=2, fancybox=True, shadow=True, borderaxespad=0)

        # Set the x axis limits
        ax.set_xlim([2, 8])

        # Set the x axis limits
        ax.set_ylim([-1, 1.5])

        # Create the yellow rectangle patch
        rect = Rectangle((4, charge_pot_norm - 0.5), 2, 1, color='yellow', alpha=0.2, linewidth=2, capstyle='round', joinstyle='round')
        ax.add_patch(rect)
        ax.text(5, charge_pot_norm - 0.6, "ZIB Operation Range", ha='center', fontsize=10)

        # Convert the plot to an image
        canvas = plt.get_current_fig_manager().canvas
        canvas.draw()
        plot_image = ImageTk.PhotoImage(Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb()))   


        # return plot_image     
        return fig

    # Define a function to convert chemical formulas to LaTeX format
    def convert_formula(self, formula):
        # Use regular expressions to find groups of letters followed by numbers
        pattern = re.compile(r'([A-Za-z]+)(\d+)')
        # Replace each group with the same group with an underscore in between
        return pattern.sub(r'\1_\2', formula)



    def view_results(self):
        # Prompt user to select folder
        folderpath = filedialog.askdirectory(initialdir=os.getcwd(), title='Select folder')
        if folderpath:
            # Create new window for results
            results_window = tk.Toplevel()
            results_window.title('Calculation')
            results_window.geometry('1380x600')
            #results_window.resizable(0, 0)
            results_window.configure(bg='white')

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

            cp = round(charge_pot, 2)

            # # Add frame for input fields
            # c_frame = tk.LabelFrame(results_window, text='Calculations', font=('Arial', 16), bg='white', fg='black')
            # c_frame.place(relx=0.5, rely=0.5, anchor='center', width=500)

            # total_label = tk.Label(c_frame, text=f"Charge Potential = {cp} V vs Zn2+/Zn", font=("Helvetica", 20, "bold"), bg='black', fg='white')
            # total_label.pack(padx=10, pady=10)

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
                e_pH5 = round(e_pH5,2)
                charge_pot_norm = charge_pot - 0.762
                cp2 = round(charge_pot_norm,2)

                # Set up needed components, then plot graph afterwards

                # Define a new font for ttk widgets
                my_font = Font(
                    family = 'Waree',
                    size = 30,
                    weight = 'bold',
                    slant = 'roman',
                    underline = 1,
                    overstrike = 0
                )

                # Create a title label with custom font

                # Load the structure from the POSCAR file for zinc cathode compound
                struc_metal_ox = Structure.from_file(noZn_poscar_path)

                # Get the formula of the structure
                formula_metal_ox = Composition(struc_metal_ox.formula)

                # Balance the formula
                balanced_form_metox = formula_metal_ox.reduced_formula

                # Load the structure from the POSCAR file for zinc cathode compound
                struc_withZinc = Structure.from_file(withZn_poscar_path)

                # Get the formula of the structure
                formula_withZinc = Composition(struc_withZinc.formula)

                # Balance the formula
                balanced_form_withZinc = formula_withZinc.reduced_formula

                title_label = tk.Label(results_window, text=balanced_form_metox, font=my_font, bg = "white")
                title_label.grid(row=0, column=0, sticky='nw', padx=20, pady=20)

                plot_label = tk.Frame(results_window)
                plot_label.grid(row=1, column=0, sticky='nw', padx=20, pady=10)
                
                fig = self.plot_graph(E, H_ions_num, electrons_num, cp2, e_pH5)

                # Convert the plot to an image
                canvas = FigureCanvasTkAgg(fig, master=plot_label)
                canvas.draw()
                plot_image = ImageTk.PhotoImage(Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb()))

                # Create a label to display the plot image
                plot_image_label = tk.Label(plot_label, image=plot_image)
                plot_image_label.image = plot_image
                #plot_image_label.pack()
                plot_image_label.grid(row=1, column=0, sticky='w')

                #Chemical Equation
                structure_ = Structure.from_file(Elem_poscar_path)
                # Get the element symbols as a list of strings
                elements = structure_.symbol_set
                # Convert the list to a single string
                metal = ''.join(elements)
                # conv_metox = self.convert_formula(balanced_form_metox)
                # #reactants = fr"\mathrm{{{conv_metox} + {H_ions_num}H^{+} + {electrons_num}e^{-}}}"
                # arrow = r"\xrightarrow{\hspace{0.5cm}}\hspace{0.5cm}\xleftarrow{\hspace{0.5cm}}"
                # #prods = fr"\mathrm{{{metal}^{{valence_charge}}_{(aq)} + {H2O_coeff}H_2O}}"
                # latex_text = Latex(f"${reactants} + {manganese} {arrow} {prods}$")
                # fig = Figure(figsize=(5, 4), dpi=100)
                # ax = fig.add_subplot(111)
                # ax.axis('off')
                # ax.text(0.5, 0.5, latex_text.data, fontsize=20, ha='center', va='center')
                # # Create a canvas to display the figure in the tkinter window
                # canvas = FigureCanvasTkAgg(fig, master=root)
                # canvas.draw()
                # plot_eq = ImageTk.PhotoImage(Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb()))
                # # Create a label to display the plot image
                # plot_eq_label = tk.Label(plot_label, image=plot_eq)
                # #plot_image_label.pack()
                # plot_eq_label.grid(row=0, column=0, sticky='w')

                # Create a table with sample data
                table_frame = tk.Frame(results_window)
                table_frame.grid(row=1, column=1, sticky='nsew', padx=20, pady=10)
                table = ttk.Treeview(table_frame, columns=(1, 2, 3, 4), show="headings", height=4)
                table.grid(row=0, column=0, sticky='nw', padx=10, pady=10)

                table.column(1, width=130, anchor='center')
                table.column(2, width=110, anchor='center')
                table.column(3, width=150, anchor='center')
                table.column(4, width=150, anchor='center')

                font2 = Font(
                    family = 'Arial',
                    size = 15,
                    slant = 'roman',
                    overstrike = 0
                )

                # Set a new font for the table
                table_style = ttk.Style()
                table_style.configure("Custom.Treeview.Heading", font=("TkDefaultFont", 12, "bold"))
                table_style.configure("Custom.Treeview", font=font2)

                table.heading(1, text="Element")
                table.heading(2, text="E0 (eV)")
                table.heading(3, text="Number of Atoms")
                table.heading(4, text="E0 (eV/Formula Units)")

                table.insert("", tk.END, values=("Zn", -2.89, 2, -1.45), tags=('center'))
                table.insert("", tk.END, values=(balanced_form_metox, round(EO_noZn,2), noZn_fu, round(E0_noZn_norm,2)), tags=('center'))
                table.insert("", tk.END, values=(balanced_form_withZinc, round(EO_withZn,2), withZn_fu,round(E0_withZn_norm,2)), tags=('center'))
                table.insert("", tk.END, values=(f"Zn + {balanced_form_metox}","","", round(E0_rxn_norm,2)), tags=('center'))

                if -0.295 < charge_pot_norm < 0.934:
                    if charge_pot_norm > e_pH5:
                        message = f"{balanced_form_metox} is a suitable cathode for an aqueous zinc-ion battery as its charge potential SHE ({cp2} V) is higher than its electro-chem stability ({e_pH5} V SHE) at a pH of 5"

                    else:
                        message = f"{balanced_form_metox} is not a suitable cathode for an aqueous zinc-ion battery as its electro-chem stability ({e_pH5} V SHE) at a pH of 5, is higher than its normalized charge potential ({cp2} V vs Zn²⁺/Zn)"

                else:
                    message = f"{balanced_form_metox} is not a suitable cathode for an aqueous zinc-ion battery as its charge potential ({cp2} V vs Zn²⁺/Zn) is not between the oxygen and hydrogen evolutions"           

                mat_prop_frame = tk.Frame(table_frame, bg="white", bd=2, relief=tk.RAISED)
                mat_prop_frame.grid(row=1, column=0, padx=20, pady=10, sticky='w')

                # Charge potential label and value
                charge_label = tk.Label(mat_prop_frame, text="Charge Potential (Zn²⁺/Zn)", font=('Arial', 12),bg='white')
                charge_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
                charge_value = tk.Label(mat_prop_frame, text=f"{cp} V", font=('Arial', 12, 'bold'), fg='blue',bg='white')
                charge_value.grid(row=1, column=1, padx=10, pady=5, sticky='w')

                # Normalized Charge potential label and value
                ncharge_label = tk.Label(mat_prop_frame, text="Charge Potential (SHE)", font=('Arial', 12),bg='white')
                ncharge_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')
                ncharge_value = tk.Label(mat_prop_frame, text=f"{cp2} V", font=('Arial', 12, 'bold'), fg='blue',bg='white')
                ncharge_value.grid(row=2, column=1, padx=10, pady=5, sticky='w')

                # Electro-chemical stability label and value
                ecs_label = tk.Label(mat_prop_frame, text="Electro-Chemical Stability (at pH = 5)", font=('Arial', 12),bg='white')
                ecs_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')
                ecs_value = tk.Label(mat_prop_frame, text=f"{e_pH5} V SHE", font=('Arial', 12, 'bold'), fg='blue',bg='white')
                ecs_value.grid(row=3, column=1, padx=10, pady=5, sticky='w')

                # Reaction label and value
                rxn_label = tk.Label(mat_prop_frame, text=f"{balanced_form_metox} + {int(H_ions_num)}H⁺ + {int(electrons_num)}e⁻ ↔ {metal}{valence_charge}+(aq) + {int(H2O_coeff)}H₂O", font=('Arial', 12, 'italic', 'bold'),bg='white')
                rxn_label.grid(row=5, column=0, padx=10, pady=5, sticky='nswe')

                # Delta G of reaction label and value
                deltaG_label = tk.Label(mat_prop_frame, text="ΔGrxn", font=('Arial', 12),bg='white')
                deltaG_label.grid(row=6, column=0, padx=10, pady=5, sticky='w')
                deltaG_value = tk.Label(mat_prop_frame, text=f"{round(G_rxn,2)} eV", font=('Arial', 12, 'bold'), fg='blue',bg='white')
                deltaG_value.grid(row=6, column=1, padx=10, pady=5, sticky='w')

                #Recommendation frame
                rec_frame = tk.LabelFrame(table_frame, text='Recommendation',font=('Arial', 16))
                rec_frame.grid(row=2, column=0, padx=20, pady=10, sticky='w')

                rec_text = tk.Label(rec_frame, text=message, font=('Arial', 12), wraplength=500)
                rec_text.grid(row=0, column=0, padx=10, pady=5, sticky='w')

            else:
                message = f"The charge potential is negative: {cp} V vs Zn²⁺/Zn, therefore it is not suitable for an aqueous zinc-ion batter"


        else:
            print("No folder")

# Create and run app
root = tk.Tk()
app = DFTInterface(root)
root.mainloop()

