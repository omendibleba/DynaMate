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
### Tool 1: RDF_calc_tool

This tool reads a LAMMPS data file and a trajectory in the DCD format and uses the MDAnalaysis to calculate the RDF
"""

## Define class for description of inputs in structured tool 
class calc_rdf_Inputs(BaseModel):
    data_file: str = Field(description="LAMMPS data file")
    dcd_file: str = Field(description="LAMMPS trajectory file in DCD format")
    names: list = Field(description="Names of the atoms to calculate RDF")
    selections: list = Field(description="Selections of the atoms to calculate RDF")
    output_file: str = Field(description="Output file name for the RDF plot")


## Function to obtain the RDF from an NVT simulation 
def get_rdf(data_file, dcd_file, names,selections, output_file):
## Import MDAnalysis to analyze trajectory
    import MDAnalysis
    from MDAnalysis.analysis.rdf import InterRDF
    # Define Universe
    u = MDAnalysis.Universe(data_file, dcd_file, format="LAMMPS")

    ## Define selections
    selection1 = u.select_atoms(selections[0])
    selection2 = u.select_atoms(selections[1])

    ## Calculate RDF
    rdf = InterRDF(selection1, selection2, range=(0.2, 10.0), nbins=50,norm='rdf')
    rdf.run()
    #save to file using numpy
    import numpy as np
    np.savetxt('rdf.dat', np.column_stack((rdf.bins, rdf.rdf)), header='r (Angstrom) g(r)', comments='#')

    ## Plot RDF
    import matplotlib.pyplot as plt
    plt.plot(rdf.bins, rdf.rdf, label=f'{names[0]}-{names[1]}')
    plt.xlabel('r ($\AA$)')
    plt.ylabel('g(r)')
    plt.legend()
    plt.savefig(output_file)
    plt.show()

    return

# ## test 
# data_file = 'system.data'
# dcd_file = 'trajectory.dcd'
# names = ['O','O']
# selections = ['type 1','type 1']
# output_file = 'rdf.png'

# os.makedirs('tool_1', exist_ok=True)
# os.chdir('tool_1')
# get_rdf(data_file, dcd_file, names,selections, output_file)
# os.chdir('..')

## Define Structured Tool
calc_rdf_tool = StructuredTool.from_function(
    func=get_rdf, # Function to be used
    name="calc_rdf_tool", # Function to be used
    description="Calculate RDF from LAMMPS trajectory using the data file, trajectory file, names of the atoms, selections of the atoms, and output file name", # Description of the function
    args_schema=calc_rdf_Inputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    # Use dictionary as input
    )

####################  TESTING THE AGENT ############################


# ## Define LLM
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [calc_rdf_tool]

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
# test_prompt_1 = "Calculate the RDF from a LAMMPS trajectory using the data file 'system.data', \
#     trajectory file 'trajectory.dcd', names of the atoms 'O' and 'O',\
#     selections of the atoms 'type 1' and 'type 1', and output file name 'rdf.png'."

# # Create and move to tool_1 directory
# os.makedirs("tool_1", exist_ok=True)
# os.chdir("tool_1")
# print(mosdef_response(test_prompt_1))
# os.chdir("..")
