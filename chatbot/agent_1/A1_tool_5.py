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
## Tool 5: packmol_moltemplate_tool

This tool generates a packmol input file that uses previously generated coordinate files (pdb or xyz) and template files to generate a newly packed system. Then the templates are used to create the LAMMPS data file with forcefield parameters. 

NOTE: If the templates have parameter from distinc force fields issues can arise due to the styles used to defined interaction parameters. This would require manual editing of the hybrid functions used to describe each type of interaction. Future versions will deal with the agent editing these changes. It is very important to mantain consistency when naming the files.
"""

## Define class for description of inputs in structured tool 
class packmol_moltemplate_Inputs(BaseModel):
    # num_types: int = Field(description="Number of types of molecules in the system")
    names: list = Field(description="Names of molecules of interest")
    nmol: list = Field(description="Number of molecules of each type")
    box: int = Field(description="Size of the box in Angstroms")

def pack_template_func(names: list, nmol: list, box: int):
    """
    Generate a LAMMPS data file using packmol and moltemplate for a system with multiple types of molecules.
    """

    # Writing packmol input
    with open("packmol.inp", "w") as f:
        print(f"""tolerance 2.0

# The file type of input and output files is PDB
filetype pdb

# The name of the output file
output system.pdb

# The system components
""", file=f)
        
        for i in range(len(names)):
            print(f"""
structure {names[i]}.pdb
  number {nmol[i]}
  inside box 0. 0. 0. {box} {box} {box}
end structure
            """, file=f)
    ## Run packmol
    os.system("packmol < packmol.inp")

    # Writing moltemplate system.lt file
    with open("system.lt", "w") as f:
        print(f"""
## Import the templates
""", file=f)
        
        # Loop to import each molecule's template file
        for name in names:
            print(f'import "{name}.lt"', file=f)
        
        print("\n# Define the number of molecules", file=f)
        
        # Loop to define each molecule with its respective count
        for i in range(len(names)):
            print(f"molec_{i+1} = new {names[i]}[{nmol[i]}] #.move(0,0,15.5171)", file=f)
        
        # Define the box size
        print(f"""
## Create the box. The box size is in Angstrom
write_once("Data Boundary") {{
   0.0  {box}  xlo xhi
   0.0  {box}  ylo yhi
   0.0  {box}  zlo zhi
}}
""", file=f)
    # Run moltemplate
    os.system(f"moltemplate.sh -pdb system.pdb system.lt")

    ## Create a copy of the .data file with the name of the molecule
    # os.system(f"cp system.data {names[:]}.data")

    ## remove temporary files
    os.system("rm -r output_ttree")

# ## test the function 
# os.chdir("tool_5")
# pack_template_func(["IRMOF-1","EtOH"],[1,20],40)
# os.chdir("..")


## Define Structured Tool
pack_template_tool = StructuredTool.from_function(
    func=pack_template_func, # Function to be used
    name="pack_template_tool", # Name of the tool
    description="Generate LAMMPS files for a system with multiple types of molecules. The inputs are a list with the number of molecules of each type, a list with the names of molecules of interest, and the size of the box. Make sure to use lists as inputs", # Description of the tool
    args_schema=packmol_moltemplate_Inputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    )

############################### TESTING ########################################
# ## Define LLM
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [pack_template_tool]

# ## Propomt for openai function
# prompt = hub.pull("hwchase17/openai-functions-agent")
# # print(prompt)

# # Create OpenAI functions agent
# agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# # ## Create Agent executor
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

# def packmolTemplates_response(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']
