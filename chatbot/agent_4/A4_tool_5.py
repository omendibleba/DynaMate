import os
from dotenv import load_dotenv
import subprocess
import warnings
warnings.filterwarnings("ignore")
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor,create_react_agent,create_openai_functions_agent # To load simple ReAct agent. Reason an act
from langchain import hub
# Define API key for OPenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

"""
### Tool 5: MetaD_prep_tool 

Tool to generate PLUMED input files for Metadynamics simulations using a torsion angle CV. The tool assumes availability of previously generated data and input files for LAMMPS.

"""

## Define class for description of inputs in structured tool 
class Prep_MetaD_Inputs(BaseModel):
    input_file: str = Field(description="Input file for LAMMPS")
    atoms_dihed_1: list = Field(description="Atoms for dihedral 1")
    atoms_dihed_2: list = Field(description="Atoms for dihedral 2")
    pace: int = Field(description="Pace for Gaussian deposition")
    height: float = Field(description="Initial height of Gaussian")
    bias_factor: int = Field(description="Bias factor")
    sigma: float = Field(description="Sigma value for Gaussian")
    T: float = Field(description="Temperature in K")
    


def prep_MetaD_inp(input_file, atoms_dihed_1, atoms_dihed_2, pace, height, bias_factor, sigma, T):
    import numpy as np

    ### write plumed input 
    with open("plumed_MetaD.dat","w") as f:
        print(f"""

# vim:ft=plumed
cv1: TORSION ATOMS={','.join(str(i) for i in atoms_dihed_1)}   
cv2: TORSION ATOMS={','.join(str(i) for i in atoms_dihed_2)}
                            

# Activate well-tempered metadynamics in phi
metad: METAD ARG=cv1,cv2 ...
   # Deposit a Gaussian every 500 time steps, with initial height
   # equal to 0.3 kJ/mol and bias factor equal to 5
   PACE={pace} HEIGHT={height} BIASFACTOR={bias_factor}
   # Gaussian width (sigma) should be chosen based on the CV fluctuations in unbiased run
   SIGMA={sigma},{sigma}
   TEMP={T}
   CALC_RCT
   # Gaussians will be written to file and also stored on grid
   FILE=HILLS GRID_MIN=-pi,-pi GRID_MAX=pi,pi GRID_BIN=100,100
...

PRINT ARG=* FILE=colvar.dat STRIDE=100 """,file=f)

    # Read the contents of the template file once
    with open(input_file, 'r') as file:
        template_lines = file.readlines()

    # Create a copy of the template lines for each file
    lines = template_lines[:]
    
    # Identify the first 'fix ' command and modify it to 'fix plumed'
    first_fix_index = None
    for index, line in enumerate(lines):
        if line.strip().startswith("fix "):
            first_fix_index = index
            break  # Stop at the first occurrence

    # Insert 'fix plumed' as the first 'fix' command
    if first_fix_index is not None:
        lines.insert(first_fix_index, f"fix umb all plumed plumedfile plumed_MetaD.dat outfile plumed.out\n")
    else:
        # If no 'fix' command is found, add 'fix plumed' at the end
        lines.append(f"No fix commands found\n")
    
    # Define the new filename
    new_filename = f"modified_input_MetaD.in"
    
    # Write the modified lines to the new file
    with open(new_filename, 'w') as new_file:
        new_file.writelines(lines)

    return
# input_file = "in.ADP_Example"
# atoms_dihed_1 = 5, 7, 9, 15
# atoms_dihed_2 = 7, 9, 15, 17
# pace = 100
# height = 1.0
# bias_factor = 4
# sigma = 0.3
# T = 300
# os.chdir("tool_5")
# prep_MetaD_inp(input_file, atoms_dihed_1, atoms_dihed_2, pace, height, bias_factor, sigma, T)
# os.chdir("..")

## Define Structured Tool
Prep_Metad_Inps_tool = StructuredTool.from_function(
    func=prep_MetaD_inp, # Function to be used
    name="prep_MetaD_inp_tool", # Function to be used
    description="Generate PLUMED input files for metadynamics simulations using dihedral angles as collective variables.", # Description of the tool
    args_schema=Prep_MetaD_Inputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    # Use dictionary as input
    )

################### TESTING THE AGENT ############################
# ## Define LLM
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [Prep_Metad_Inps_tool]

# ## Propomt for openai function
# prompt = hub.pull("hwchase17/openai-functions-agent")
# #print(prompt)

# # Create OpenAI functions agent
# agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# # ## Create Agent executor
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

# def Metad_gen_response(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']

# ## Define test prompt 
# test_prompt_1 = "Generate PLUMED input files for metadynamics simulations using dihedral angles as collective variables. \
#     The input file for LAMMPS is 'in.ADP_Example', the atoms for dihedral 1 are 5, 7, 9, 15, the atoms for dihedral 2 are 7, 9, 15, 17, \
#             the pace for Gaussian deposition is 100, the initial height of Gaussian is 1.0, the bias factor is 4, the sigma value for Gaussian is 0.3, \
#                 and the temperature is 300 K."

# os.chdir("tool_5")
# print(Metad_gen_response(test_prompt_1))
# os.chdir("..")