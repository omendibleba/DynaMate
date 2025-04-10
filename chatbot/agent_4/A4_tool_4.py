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
### Tool 4: UmbSamp_analysis_tool

Tool to visualize the Sampled CV values in the umbrella simulations

"""

## Define class for description of inputs in structured tool 
class UmbSamp_analysis_Inputs(BaseModel):
    path: str = Field(description="Path to the umbrella production folders")
    n_umbrellas: int = Field(description="Number of umbrella sampling simulations")

## Define function
def UmbSamp_analysis(path, n_umbrellas):
    import plumed
    import matplotlib.pyplot as plt

    for i in range(n_umbrellas):
        data = plumed.read_as_pandas(f"{path}/umbrella_{i}/dihedral_{i}.dat")
        plt.scatter(data["time"], data["d1"], label=f"Umbrella {i}")
    plt.xlabel("Time (ps)")
    plt.ylabel("Distance (nm)")
    plt.savefig("distance_v_time.png")
    plt.show()

    for i in range(n_umbrellas):
        data = plumed.read_as_pandas(f"{path}/umbrella_{i}/dihedral_{i}.dat")
        plt.scatter( data["d1"][5:],data["bb.bias"][5:], label=f"Umbrella {i}")

    plt.xlabel("Distance (nm)")
    plt.ylabel("Bias (kJ/mol)")
    plt.savefig("bias_v_distance.png")
    plt.show()

    return

# path = 'tool_3/production_runs'
# n_umbrellas = 10
# UmbSamp_analysis(path, n_umbrellas)

## Define Structured Tool
UmbSamp_analysis_tool = StructuredTool.from_function(
    func=UmbSamp_analysis, # Function to be used
    name="UmbSamp_analysis_tool", # Function to be used
    description="Analyze umbrella sampling simulations using one collective variable.", # Description of the tool
    args_schema=UmbSamp_analysis_Inputs, # Schema of the inputs defined in class
    return_direct=True, # Return the output directly
    handle_error=False, # Handle errors
    # Use dictionary as input
    )

######################## TESTING THE AGENT ############################
# ## Define LLM
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [UmbSamp_analysis_tool]

# ## Propomt for openai function
# prompt = hub.pull("hwchase17/openai-functions-agent")
# #print(prompt)

# # Create OpenAI functions agent
# agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# # ## Create Agent executor
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

# def UmbSamp_response(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']

# ## Define test prompt
# test_prompt_4 = "Analyze umbrella sampling simulations using one collective variable. The path to the umbrella production folders is 'production_runs' and the number of umbrella sampling simulations is 10."

# # Create and move to tool_1 directory
# # os.makedirs("tool_3", exist_ok=True)
# os.chdir("tool_3")
# print(UmbSamp_response(test_prompt_4))
# os.chdir("..")