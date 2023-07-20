# Cathode Material Explorer

Eco-friendly Zn-ion batteries offer a cost-effective and safer alternative to Li-ion batteries, particularly in grid-scale energy storage. While MnO2 is the primary cathode material in commercial Zn-ion batteries, improving the cyclic stability of Zn/MnO2 remains a challenge. For my final year capstone project, my group decided to select a topic that combines materials engineering and computer science. 

The goal of the project is to create an interface that will allow zinc-ion battery researchers to easily determine a material's ability (mostly metal oxides) to act as a cathode for zinc-ion batteries. We had initially planned to create a website using Flask and React but we had to scale down as we advanced in this project. Therefore, we decided to make a tkinter GUI instead that will act as an app that anyone within our supervisor's research team can access. The GUI automates several tasks: it automatically submits all the DFT job submissions and runs all the computations need to determine the material's ability to act as a cathode for a zinc-ion battery, keeps a log of your calculations, and displays the final results of the investigation on a dashboard as shown below. Previously, most of this work had to be done manually and resulted in a lot of time wasted on managing files. With our interface, the researchers would only need to provide an input CIF file and select the name for the calculation. Everything else is handled and this allows them to reach conclusions about the materials faster. The GUI was developed primarily with Python, batch scripts, Tkinter, the Scipy stack, the Materials Project 's API and pymatgen (python materials genomics) for material properties.

# Next Steps
We leveraged mostly the scipy-stack (matplotlib, numpy, scikit-learn, etc.) for this project, but we've also made use of APIs from public databases such as the Materials Project and COD database. Currently, our next step is to use MySQL to store all relevant information (such as file directories, calculation name, date submitted, etc.) so its users don't have to manually look through folders anymore.
