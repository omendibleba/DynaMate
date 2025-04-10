import os
from dotenv import load_dotenv
import subprocess
import warnings
warnings.filterwarnings("ignore")
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool


# Define API key for OPenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


"""
### Tool 2: sim_run_tool

This tool takes as input the name of the input file to run and the number of cpus to use in the simulaiton.

"""
## Define class for description of inputs in structured tool 
class lmp_run_Inputs(BaseModel):
    lmp_file: str = Field(description="Name of the LAMMPS input file")
    cpus: int = Field(description="Number of CPUs to use for LAMMPS simulation")


## Define function to create LAMMPS input file including files from moltemplate
#  T and P units based on units in lammps input file. Here, T in K, P in bar
def run_lammps_input_file(lmp_file,cpus=1):

    # Set up the command
    command = f"nohup mpirun -np {cpus} lmp -in {lmp_file} > tmp.log &"

    # Run the command with Popen and capture the process
    process = subprocess.Popen(command, shell=True, executable="/bin/bash")

    # Print details including the PID
    print(f"Running LAMMPS simulation for {lmp_file}.in\n"
        f"Path: {os.getcwd()}\n"
        f"Log file: {os.getcwd()}/tmp.log\n"
        f"PID: {process.pid}\n")

    return 

## Define Structured Tool
lmp_run_tool = StructuredTool.from_function(
    func=run_lammps_input_file, # Function to be used
    name="lammp_run_tool", # Function to be used
    description="Run the LAMMPS simulation. Inputs are LAMMPS input file name and number of CPUs to use", # Description of the tool
    args_schema=lmp_run_Inputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    # Use dictionary as input
    )