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
## Tool 3: data_from_cif

Tool to generate LAMMPS data files from CIF files usign lammps-interface. CIF files must have P1 symmetry.

"""

## Define class for description of inputs in structured tool 
class cif_to_data_Inputs(BaseModel):
    cif_file: str = Field(description="Name of the cif file")
    FF: str = Field(description="Forcefield to be used")
    pdb: bool = Field(description="Generate pdb file or not")

## Define function in the class to be used as a tool
def lmp_interface_tool(cif_file:str, FF:str, pdb:bool=True):
    """
    Generate LAMMPS data file using the CIF file of the system of interest.
    """
    ## Run lammps interface command to generate the data file
    os.system(f"lammps-interface {cif_file} -ff {FF}")

    if pdb:
        ## Run lammps interface command to generate the pdb file
        os.system(f"lammps-interface {cif_file} -ff {FF} -p")

# # Test  the function
# os.chdir("tool_3")
# lmp_interface_tool("IRMOF-1.cif ", "UFF4MOF")
# os.chdir("..")

## Define Structured Tool
lmp_interface_tool = StructuredTool.from_function(
    func=lmp_interface_tool, # Function to be used
    name="lmp_interface_tool", # Name of the tool
    description="Generate LAMMPS data file using the CIF file of the system of interest. The inputs are the name of the CIF file, forcefield to be used, and whether to generate a pdb file or not.", # Description of the tool
    args_schema=cif_to_data_Inputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    )
