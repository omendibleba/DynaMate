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
### Tool 3: wham_analysis_tool 

This tool creates the wham_metafile nad wham_analysis.sh required to calculate the FES from umbrella sampling simulations.
### NOTE: 
Make sure to be in a submission file so the simulation scan be submitted. Also use the python script for this tool rather than the notebook.
"""

## Define class for description of inputs in structured tool 
class wham_analysis_Inputs(BaseModel):
    n_points: int = Field(description="Number of umbrella sampling points")
    cv_min: float = Field(description="Minimum value of the CV")
    cv_max: float = Field(description="Maximum value of the CV")
    k: float = Field(description="Force constant for the harmonic bias potential")
    T: float = Field(description="Temperature in K")


## Define function 
def wham_analysis(n_points,cv_min,cv_max,k,T):
    import numpy as np

    ## Define CV range
    values = np.linspace(cv_min, cv_max, n_points)

    ### Convert K in kJ/mol to kcal/mol
    k_kcal= k* 0.239006

    # Write the metafile
    with open('wham_metafile', 'w') as file:
        for i, value in enumerate(values):
            line = f"./production_runs/umbrella_{i}/dihedral_{i}.dat {round(values[i],2)} {k_kcal} \n"
            file.write(line)

    ## Write the wham_analysis.sh file
    with open('wham_analysis.sh', 'w') as file:
        print(f"""#!/bin/bash

# Usage: wham [P|Ppi|Pval] hist_min hist_max num_bins tol temperature numpad \
#        metadatafile freefile [num_MC_trials randSeed]
./wham/wham/wham {cv_min} {cv_max} 100 0.0001 {T} 1 wham_metafile wham_freefile > wham_output """,file=file)
        
    ## Create a soft link of the wham directory inside the current directory if it does not exist
    if not os.path.exists("wham"):
        os.system("ln -s /scratch365/omendibl/Molec_Mindset/DynaMate_V2/tutorials/4_enhanced_sampler/wham .")

    ## Run the wham_analysis.sh file
    os.system("bash wham_analysis.sh")

    ## plot the free energy profile
    free = np.loadtxt("wham_freefile")
    import matplotlib.pyplot as plt
    plt.plot(free[:,0], free[:,1])
    plt.xlabel("CV", fontsize=14, fontweight='bold')
    plt.ylabel("Free Energy (kcal/mol)", fontsize=14, fontweight='bold')
    plt.title("Free Energy Profile", fontsize=16, fontweight='bold')
    plt.savefig("free_energy_profile.png")
    plt.show()
    return
# ## Test the function 
# # defin einputs
# n_points = 10
# cv_min = 0.1
# cv_max = 1.2
# k = 4000
# T = 300
# atom_1 = 319
# atom_2 = 320

# os.chdir("tool_3")
# wham_analysis(n_points,cv_min,cv_max,k,T)
# os.chdir("..")

## Define Structured Tool
wham_analysis_tool = StructuredTool.from_function(
    func=wham_analysis, # Function to be used
    name="wham_analysis_tool", # Function to be used
    description="Perform WHAM analysis on umbrella sampling simulations using one collective variable.", # Description of the tool
    args_schema=wham_analysis_Inputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    # Use dictionary as input
    )

####################### TESTING THE AGENT ############################
# ## Define LLM
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [wham_analysis_tool]

# ## Propomt for openai function
# prompt = hub.pull("hwchase17/openai-functions-agent")
# #print(prompt)

# # Create OpenAI functions agent
# agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# # ## Create Agent executor
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

# def wham_response(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']

# ## Define test prompt
# test_prompt_4 = "Perform WHAM analysis on umbrella sampling simulations using one collective variable. The number of umbrella sampling points is 10, the minimum value of the CV is 0.1, the maximum value of the CV is 1.2, the force constant for the harmonic bias potential is 4000, and the temperature is 300 K."

# # Create and move to tool_1 directory
# # os.makedirs("tool_3", exist_ok=True)
# os.chdir("tool_3")
# print(wham_response(test_prompt_4))
# os.chdir("..")
