## Agent to get average density,box side length, temperature and pressure from a LAMMPS log file

# Importing required libraries
import lammps_logfile as lmplog
import numpy as np
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor,create_react_agent # To load simple ReAct agent. Reason an act
from langchain import hub
import os 
from dotenv import load_dotenv
import warnings
warnings. filterwarnings('ignore') 


### Define Agent tools

@tool
def get_lammps_density(filename:str):
    """
    Get the average density in g/cm^3 from a LAMMPS log file. The input is the name of the log file.
    """
    # Load the log file 
    log = lmplog.File(filename)

    # Get the density and calculate the average
    density = log.get("Density")
    density_avg = np.mean(density[:-round(len(density)*0.3)])
    
    return density_avg # g/cm^3 (depends on the units used in the log file)

@tool
def get_lammps_lx(filename:str):
    """
    Get the average box length in Angstroms from a LAMMPS log file. The input is the name of the log file.
    """
    # Load the log file 
    log = lmplog.File(filename)

    # Get the density and calculate the average
    lx = log.get("Lx")
    lx_avg = np.mean(lx[:-round(len(lx)*0.2)])
    return lx_avg # Angstrom

@tool
def get_lammps_temp(filename:str):
    """
    Get the average temperature in Kelvin (K) from a LAMMPS log file. The input is the name of the log file.
    """
    # Load the log file 
    log = lmplog.File(filename)

    # Get the density and calculate the average
    Temp = log.get("Temp")
    Temp_avg = np.mean(Temp[:-round(len(Temp)*0.2)])
    return Temp_avg

@tool
def get_lammps_pressure(filename:str):
    """
    Get the average pressure in bar from a LAMMPS log file. The input is the name of the log file.
    """
    # Load the log file 
    log = lmplog.File(filename)

    # Get the density and calculate the average
    pressure = log.get("Press")
    pressure_avg = np.mean(pressure[:-round(len(pressure)*0.2)])
    return pressure_avg


## Define Agent parameters

# Define API key for OPenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

## Define LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

# Define list of tools the LLM is going to use 
list_tools = [get_lammps_density, get_lammps_lx, get_lammps_temp, get_lammps_pressure]

# Get the template prompt to use - you can modify this!
prompt = hub.pull("hwchase17/react")

## Construct the ReAct agent by defining the llm, tools and prompt template
lmp_log_get_Agent = create_react_agent(llm=llm,tools=list_tools,prompt=prompt)

# Create an agent executor by passing in the agent and tools
lmp_log_agnt_exec = AgentExecutor(agent=lmp_log_get_Agent, tools=list_tools, verbose=False)