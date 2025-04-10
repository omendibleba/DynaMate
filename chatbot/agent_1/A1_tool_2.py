# imports
import os
from dotenv import load_dotenv
# import mbuild
# import foyer
import warnings
warnings.filterwarnings("ignore")
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
# from langchain_openai import ChatOpenAI
# from langchain.agents import AgentExecutor,create_react_agent,create_openai_functions_agent # To load simple ReAct agent. Reason an act
# from langchain import hub

# Define API key for OPenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

"""
## Tool 2: rdkit_template_tool

This tool uses RDKit, moltemplate and packmol to generate a LAMMPS data file from a molecule's SMILE string. By default it uses the GAFF force field for interaction parameters, but this can be modified by defining the name of the force field of interest in the `run_mol22lt.sh` script. 
You can vizualize the molecule generate in the rdkit-charges-and-imgs directory. In this example the tool is used to generate a data file of a system of pure DMF and DMSO.This file can then be used to run simulations. 
"""

## Define class for description of inputs in structured tool 
class Smiles_to_Data_Inputs(BaseModel):
    name: str = Field(description="Name of the molecule of interest")
    smiles: str = Field(description="SMILES string of the molecule of interest")
    charge: int = Field(description="Charge of the molecule of interest")
    nmol: int = Field(description="Number of molecules to put in the system")
    box: int = Field(description="Size of the box in Angstroms")

def pdb_to_lt_system(name:str, smiles:str,charge:int,nmol:int,box:int):
    """
    Generate an optimized pdb file from SMILES string.

    Notes:
    - SMILES strings can be found among the molecular identifiers in PubChem or can be generated from a molecule drawing tool like molview.org
    - The residue may not be recognized by rdkit so the residue name in the pdb file will appear as unknown. I normally change this manually to the 3-letter residue name I want.
    """
    import os
    from rdkit import Chem
    from rdkit.Chem import AllChem 
    from rdkit.Chem import Draw

    # Define residue name and create molecule from smiles string
    mol_name = name
    m = Chem.MolFromSmiles(smiles)

    # add hydrogens and calculate partial charges
    m = Chem.AddHs(m)
    AllChem.ComputeGasteigerCharges(m)

    # Make a directory to store the charges and images
    os.makedirs("rdkit-charges-and-imgs", exist_ok=True)

    # Print charge info to file
    with open(f"rdkit-charges-and-imgs/{mol_name}-charges.txt", "w") as f:
        # Write header
        f.write("Atom_idx, Charge\n")

        # initialize total charge 
        q_sum = 0

        # loop over atoms and get charge
        for atom in m.GetAtoms():
            # Change atom label to atom index (useful for seeing atom indices in the image)
            atom_idx = atom.GetIdx()
            atom.SetProp('atomLabel', str(atom_idx))
            # Get atomic charge
            q = m.GetAtomWithIdx(atom_idx).GetDoubleProp('_GasteigerCharge')
            print(f'Atom {atom_idx} has charge {q}')
            q_sum += q
            # write charge to file
            f.write(f"{atom_idx}, {q}\n")

        f.write(f"\n#Total charge = {q_sum}")

    print(f'\nTotal charge = {q_sum}')

    # Generate the molecule image
    img = Draw.MolToImage(m, kekulize=True)
    # Save 2D molecule image to file
    img.save(f"rdkit-charges-and-imgs/numbered_{mol_name}.png")

    # Optimize the geometry
    AllChem.EmbedMolecule(m)
    AllChem.MMFFOptimizeMolecule(m)

    # Generate the molecule pdb file
    os.makedirs("pdb-files", exist_ok=True)
    Chem.MolToPDBFile(m, f"pdb-files/{mol_name}.pdb", )

    ## Define path for files
    files_path = '../tutorials/1_system_prep/tool_2/'

    ## Run the run_pdb2mol2.sh script to convert the pdb file to mol2 file
    os.system(f"bash {files_path}run_pdb2mol2.sh {mol_name} {charge}")

    ## Run the run_mol22lt.sh script to convert the mol2 file to moltemplate file
    os.system(f"bash {files_path}run_mol22lt.sh {mol_name} {charge}")

    ## Copy the generated template file to the rott templates directory
    # template_root = './templates/'
    home = os.getenv("HOME")
    template_root = f'{home}/moltemplate/moltemplate/force_fields/'
    os.system(f"cp {mol_name}.lt {template_root}/{mol_name}_.lt")
    

    ## Writing packmol input 
    ## Define system lt file 
    with open("packmol.inp", "w") as f:
        print(f"""
tolerance 2.0

# The file type of input and output files is PDB
filetype pdb

# The name of the output file
output system.pdb

# The system components

structure pdb-files/{mol_name}.pdb
  number {nmol}
  inside box 0. 0. 0. {box} {box} {box} 
end structure
    """,file=f)

    ## Run packmol
    os.system("packmol < packmol.inp")

    ## Writing moltemplate system.lt file
    ## Define system lt file 
    with open("system.lt", "w") as f:
        print(f"""
## import the template
import "{mol_name}.lt"

#Define the number of molecules
molec = new {mol_name}[{nmol}] #.move(0,0,15.5171) 

## Create the box. The box size is in Angstrom
write_once("Data Boundary") {{
   0.0  {box}  xlo xhi
   0.0  {box}  ylo yhi
   0.0  {box}  zlo zhi
}}
""",file=f)
        
    ## Run moltemplate
    os.system(f"moltemplate.sh -pdb system.pdb system.lt")

    ## Create a copy of the .data file with the name of the molecule
    os.system(f"cp system.data {mol_name}.data")

    ## remove temporary files
    os.system("rm -r output_ttree")

# # test the function for 100 molecules of DMF in a 40 Angstrom box
# pdb_to_lt_system("DMF", "CN(C)C=O",0,nmol=10,box=40.0)


## Define Structured Tool
smile_to_lt_tool = StructuredTool.from_function(
    func=pdb_to_lt_system, # Function to be used
    name="templates_tool", # Name of the tool
    description="Generate LAMMPS files and molecular template for a molecular system Starting from the SMILES string of the system of interest. The inputs are the name of the molecule, the SMILES string, charge, number of molecules, and box size.", # Description of the tool
    args_schema=Smiles_to_Data_Inputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    )

################# FOR TESTING PURPOSES #################
# ## Define LLM
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [smile_to_lt_tool]

# ## Propomt for openai function
# prompt = hub.pull("hwchase17/openai-functions-agent")
# # print(prompt)

# # Create OpenAI functions agent
# agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# # ## Create Agent executor
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

# def templates_response(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']

# ## Define test prompt 
# test_prompt_2 = "Generate LAMMPS files for a molecular system starting from its smiles string. The inputs are the name of the molecule, the SMILES string, charge, number of molecules, and box size. Name: DMF, SMILES: CN(C)C=O, charge: 0, Number of molecules: 10,  Box size: 30.0 Angstrom"

# ## Create and move to tool_2 directory
# os.makedirs("tool_2", exist_ok=True)
# os.chdir("tool_2")
# print(templates_response(test_prompt_2))
# os.chdir("..")