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
## Tool 1: Sim_runner_tool

Generates a LAMMPS input files that runs an equilibration workflow that includes a minimization, npt and nvt simulation.
"""

## Define class for description of inputs in structured tool 
class lmp_ge_run_Inputs(BaseModel):
    lammps_file: str = Field(description="Name of the LAMMPS input file")
    Temp: float = Field(description="Temperature in K")
    Pres: float = Field(description="Pressure in bar")
    cpus: int = Field(description="Number of CPUs to use for LAMMPS simulation")


## Define function to create LAMMPS input file including files from moltemplate
#  T and P units based on units in lammps input file. Here, T in K, P in bar
def create_lammps_input_file(lammps_file,Temp=298.0,Pres=1.0,cpus=1):

    with open(f'{lammps_file}', 'w') as file:
        print(f'''
# ----------------- Init Section -----------------
include "system.in.init"
              
# ----------------- Atom Definition Section -----------------
read_data "system.data"

# ----------------- Settings Section -----------------
include "system.in.settings"

thermo 100
#  -- minimize -- (Minimization without fix shake)
minimize 1.0e-5 1.0e-7 1000 10000
write_data system_minimized.data

# ----------------- Constraints Section -----------------
include "system.in.constraints"

# ----------------- Run Section -----------------              
# Setup timestep
timestep        1 #fs

reset_timestep 0
# Define thermo output
thermo          1000
thermo_style    custom step time temp pe ke etotal enthalpy press lx vol density


#Create initial velocity distribution
velocity   all create {Temp} 097865 dist gaussian

## Fix commands
fix 1 all npt temp {Temp} {Temp} 100 iso {Pres} {Pres} 1000.0
run 1000000 # 1 ns


write_data system_npt_equil.data
unfix 1

fix 2 all nvt temp {Temp} {Temp} 100
unfix 2

# Define Dumping
#dump 1 all xyz 1000 test.xyz
dump 3 all dcd 1000 trajectory.dcd
#dump myDump2 all custom 1000 forces.dump id type x y z fx fy fz

run 500000 # 0.5 ns

write_data system_nvt_equil.data
''', file=file)
        
    # ## Run lammps using the terminal command
    # command = f"lmp -in {lammps_file}.in"
    # #os.system(command, shell=True)
    # subprocess.run(["module load lammps"], check=True,shell=True)
    # #subprocess.run(["mpirun","-np","12","lmp", "-in", f"{lammps_file}.in"], check=True,shell=True)
    # subprocess.run(["mpirun -np 12",f"lmp -in {lammps_file}.in"], check=True,shell=True)

    command = f"nohup mpirun -np {cpus} lmp -in {lammps_file} > tmp.log &"
    subprocess.run(command, check=True, shell=True)
    print(f"Running LAMMPS simulation for {lammps_file}.in\n\n \
          Path: {os.getcwd()}\n \
          Log file: {os.getcwd()}/tmp.log")

    return 

## Define Structured Tool
lmp_create_run_tool = StructuredTool.from_function(
    func=create_lammps_input_file, # Function to be used
    name="lammp_gen_run_tool", # Function to be used
    description="Generate LAMMPS input file and run the simulation. Inputs are LAMMPS input file name, Temperature, Pressure, and number of CPUs to use", # Description of the tool
    args_schema=lmp_ge_run_Inputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    # Use dictionary as input
    )



##################################### Test the agent ########################################
# ## Define LLM
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [lmp_create_run_tool]

# ## Propomt for openai function
# prompt = hub.pull("hwchase17/openai-functions-agent")
# #print(prompt)

# # Create OpenAI functions agent
# agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# # ## Create Agent executor
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

# def lmp_gen_run_response(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']

# ## Define test prompt 
# test_prompt_1 = "Generate LAMMPS input file and run the simulation. Inputs are LAMMPS input file name, Temperature, Pressure, and number of CPUs to use. \n \
#                 lammps_file: system.in, Temp: 298.0, Pres: 1.0, cpus: 4"
# # Create and move to tool_1 directory
# os.makedirs("tool_1", exist_ok=True)
# os.chdir("tool_1")
# print(lmp_gen_run_response(test_prompt_1))
# os.chdir("..")