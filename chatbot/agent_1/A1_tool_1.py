# imports
import os
from dotenv import load_dotenv
# import mbuild
# import foyer
import warnings
warnings.filterwarnings("ignore")
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool
#from langchain_openai import ChatOpenAI
#from langchain.agents import AgentExecutor,create_react_agent,create_openai_functions_agent # To load simple ReAct agent. Reason an act
#from langchain import hub

# Define API key for OPenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

"""
## Tool 1: mosdef_tool

This tool uses the MosDEF workflow to generate a LAMMPS data file from a molecule's SMILE string. By default it uses the OPLS-AA force field for interaction parameters, but this can be modified by defining the name of the force field of interest. 
In this example the tool is used to generate a data file of a system of dense Ethanol.This file can then be used to run simulations. 
"""

## Define class for description of inputs in structured tool 
class MosDEFInputs(BaseModel):
    name: str = Field(description="Name of the molecule of interest")
    smiles: str = Field(description="SMILES string of the molecule of interest")
    box_size: float = Field(description="Size of the box in nm")
    n_molecs: int = Field(description="Number of molecules in the box")


# Define function in the class to be used as a tool
def MosdDEF(name:str, smiles:str, box_size:float, n_molecs:int):

    import mbuild
    import foyer 
    import warnings
    warnings.filterwarnings("ignore")
    
    """Function to create a data file for LAMMPS simulations using only 1 input. The input is a smiles string of a molecule."""
    #Define inputs 
    system_smiles = smiles     ##'CCO'  # Ethanol for example
    box_size = box_size # nano meter = 
    n_molecules = n_molecs # Number of molecules
    #density = 789 ## kg/m^3
    forcefield_name = 'oplsaa' # OPLS-AA forcefield. Can be changed by available forcefileds in mbuild
    system_name = name # Name of the system

    # Load system using its SMILES strings
    system_unparad = mbuild.load(system_smiles, smiles=True)

    # assign name 
    system_unparad.name = system_name

    # build box
    box = mbuild.Box(3*[box_size])

    # Fill the box with the molecule of interest
    # filled_box = mbuild.fill_box(compound=system_unparad, density=density, box=box, overlap=0.2)
    filled_box = mbuild.fill_box(compound=system_unparad, n_compounds=n_molecules, box=box, overlap=0.2)

    ## apply the forcefield to the system
    ff = foyer.Forcefield(name=forcefield_name)
    filled_box_param = filled_box.to_parmed(infer_residues=True) # Parmed structure
    filled_box_parametrized = ff.apply(filled_box_param) # ff applied

    ## Pass the parametrized system to a Lammps data file 
    mbuild.formats.lammpsdata.write_lammpsdata(
    filled_box_parametrized, 
    str(system_name)+".data",
    atom_style="full",
    unit_style="real",
    use_rb_torsions=True,)
    
    return

## Define Structured Tool
mosdef_tool = StructuredTool.from_function(
    func=MosdDEF, # Function to be used
    name="Mosdef_tool", # Function to be used
    description="Generate LAMMPS data file for a molecular system using the smiles string. The inputs are the name of the molecule, smiles string, box size and number of molecules.", # Description of the tool
    args_schema=MosDEFInputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    # Use dictionary as input
    )


######### FOR TESTING PURPOSES #########
# ## Define LLM
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [mosdef_tool]

# ## Propomt for openai function
# prompt = hub.pull("hwchase17/openai-functions-agent")
# #print(prompt)

# # Create OpenAI functions agent
# agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# # ## Create Agent executor
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

# def mosdef_response(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']

# ## Define test prompt 
# test_prompt_1 = "Generate LAMMPS data file for a molecular system using the smiles string. The inputs are the name of the molecule, smiles string, box size and number of molecules. Name: Ethanol, SMILES: CCO, Box size: 2.0 nm, Number of molecules: 1"

# # Create and move to tool_1 directory
# os.makedirs("tool_1", exist_ok=True)
# os.chdir("tool_1")
# print(mosdef_response(test_prompt_1))
# os.chdir("..")