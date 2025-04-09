import os
from dotenv import load_dotenv
import subprocess
import warnings
warnings.filterwarnings("ignore")
# from langchain.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor,create_react_agent,create_openai_functions_agent # To load simple ReAct agent. Reason an act
from langchain import hub


# Define API key for OPenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
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


## Define LLM
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# Define list of tools the LLM is going to use 
tools = [lmp_run_tool]

## Propomt for openai function
prompt = hub.pull("hwchase17/openai-functions-agent")
#print(prompt)

# Create OpenAI functions agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# ## Create Agent executor
agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

def lmp_gen_run_response(input_text:str):
    return agent_executor.invoke({"input": input_text})['output']

## Define test prompt 
test_prompt_1 = "Run LAMMPS simulation for the input file 'system.in' using 4 CPUs"
# Create and move to tool_1 directory
os.makedirs("tool_2", exist_ok=True)
os.chdir("tool_2")
print(lmp_gen_run_response(test_prompt_1))
os.chdir("..")