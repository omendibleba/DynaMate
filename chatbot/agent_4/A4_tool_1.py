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
### Tool 1: UmbSamp_input_gen_tool

Prepare input files for PLUMED to perform umbrella sampling using Distance between two atoms as the Collective Variable (CV).
"""

## Define class for description of inputs in structured tool 
class Prep_UmbSamp_Inputs(BaseModel):
    n_points: int = Field(description="Number of umbrella sampling points")
    template_in: str = Field(description="Template input file for LAMMPS")
    cv_min: float = Field(description="Minimum value of the CV")
    cv_max: float = Field(description="Maximum value of the CV")
    atom_1: int = Field(description="Atom 1 for distance calculation")
    atom_2: int = Field(description="Atom 2 for distance calculation")
    k: float = Field(description="Force constant for the harmonic bias potential")
    
## define function to generate input files for plumed
def gen_umbrella_inps(n_points, template_in, cv_min, cv_max,atom_1,atom_2,k):
    import numpy as np

    ## Generate centers
    centers = np.linspace(cv_min, cv_max, n_points)

    # Check if tmp folder exists and create it if not. If it exists, delete it and create it again.
    os.makedirs("tmp_plumed_inps",exist_ok=True)

    ## Define inputs for plumed. Specific for this ADP molecule. Selects atoms for phi and psi angles. Add bias of 500 and T = 500 K. 
    for i in range(len(centers)):

        with open("tmp_plumed_inps/plumed_"+str(i)+".dat","w") as f:
            print(f"""
# vim:ft=plumed

d1:  DISTANCE ATOMS={atom_1},{atom_2}

bb: RESTRAINT ARG=d1 KAPPA={k} AT={centers[i]}
lw: REWEIGHT_BIAS TEMP=300                
                  
# Print everything every 1000 steps.
PRINT ARG=* STRIDE=1000 FILE=dihedral_{i}.dat""",file=f)

    ############ Modify input files to run each restraint simulaiton 
    ## Create folder to store modified files
    os.makedirs("tmp_input_files",exist_ok=True)

    # Read the contents of the template file once
    with open(template_in, 'r') as file:
        template_lines = file.readlines()

    # Loop to create modified files
    for i in range(n_points):
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
            lines.insert(first_fix_index, f"fix umb all plumed plumedfile plumed_{i}.dat outfile plumed.out\n")
        else:
            # If no 'fix' command is found, add 'fix plumed' at the end
            lines.append(f"No fix commands found\n")
        
        # Define the new filename
        new_filename = f"tmp_input_files/modified_input_{i}.in"
        
        # Write the modified lines to the new file
        with open(new_filename, 'w') as new_file:
            new_file.writelines(lines)

    ########################################Create submission files
    ## Create folder to store submission files
    os.makedirs("tmp_submission_files",exist_ok=True)

    ## Create submission files
    for i in range(n_points):
        with open("tmp_submission_files/sub_"+str(i)+".sh","w") as f:
            print(f"""#!/bin/bash

#$ -pe smp 12     # Specify parallel environment and legal core size
#$ -q hpc@@colon       # Specify queue
#$ -N sub_{i}       # Specify job name

module load lammps     # Required modules

mpirun -np $NSLOTS lmp_mpi -in modified_input_{i}.in  # Application to execute

                  """,file=f)


    ##################### Combine inputs and plumed files in production folders ###################
    os.makedirs("production_runs", exist_ok=True)
    for i in range(len(centers)):
        
        # Crete folder for each umbrella
        folder_name = "production_runs/umbrella_" + str(i)
        os.makedirs(folder_name, exist_ok=True)

        ## Move input files 
        subprocess.run(f"cp tmp_input_files/modified_input_{i}.in {folder_name}",shell=True)

        ## Move plumed files
        subprocess.run(f"cp tmp_plumed_inps/plumed_{i}.dat {folder_name}/plumed_{i}.dat",shell=True)

        ## Move submission files
        subprocess.run(f"cp tmp_submission_files/sub_{i}.sh {folder_name}/sub_{i}.sh",shell=True)

        # Move data file example.input
        os.system("cp data.* "+folder_name+"/")

    ## Remove tmp folders
    os.system("rm -r tmp_*")

    return 
# ## Test the function 
# # defin einputs
# n_points = 10
# cv_min = 0.15
# cv_max = 1.2
# atom_1 = 1
# atom_2 = 2
# os.chdir("tool_1")
# template = 'in.NaCl_ABF_example'  # Replace with your actual filename
# gen_umbrella_inps(n_points, template, cv_min, cv_max,atom_1,atom_2)

## Define Structured Tool
Prep_UmbSamp_Inps_tool = StructuredTool.from_function(
    func=gen_umbrella_inps, # Function to be used
    name="gen_UmbSamp_inps_tool", # Function to be used
    description="Generate PLUMED input files for umbrella sampling simulations using atomic distance as a collective variable.", # Description of the tool
    args_schema=Prep_UmbSamp_Inputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    # Use dictionary as input
    )

#################### TESTING THE AGENT ############################


# ## Define LLM
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [Prep_UmbSamp_Inps_tool]

# ## Propomt for openai function
# prompt = hub.pull("hwchase17/openai-functions-agent")
# #print(prompt)

# # Create OpenAI functions agent
# agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# # ## Create Agent executor
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

# def umbsamp_gen_response(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']

# ## Define test prompt 
# test_prompt_1 = "Generate PLUMED input files for umbrella sampling simulations using atomic distance as a collective variable. \
#     The number of umbrella sampling points is 10, the template input file for LAMMPS is 'in.NaCl_ABF_example', \
#          the minimum value of the CV is 0.15, the maximum value of the CV is 1.2, \
#             atom 1 for distance calculation is 319, and atom 2 for distance calculation is 320. The spring constant is 500"

# # Create and move to tool_1 directory
# os.makedirs("tool_1", exist_ok=True)
# os.chdir("tool_1")
# print(umbsamp_gen_response(test_prompt_1))
# os.chdir("..")