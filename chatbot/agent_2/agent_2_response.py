from .A2_tool_1 import lmp_create_run_tool
from .A2_tool_2 import lmp_run_tool
# imports
import os
from dotenv import load_dotenv
# import mbuild
# import foyer
import warnings
warnings.filterwarnings("ignore")
# from langchain.pydantic_v1 import BaseModel, Field
# from langchain.tools import BaseTool, StructuredTool, tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor,create_react_agent,create_openai_functions_agent # To load simple ReAct agent. Reason an act
from langchain import hub

# Define API key for OPenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


## Define LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# Define list of tools the LLM is going to use 
tools = [lmp_create_run_tool,lmp_run_tool]

## Propomt for openai function
prompt = hub.pull("hwchase17/openai-functions-agent")
#print(prompt)

# Create OpenAI functions agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# ## Create Agent executor
agent_2_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

######################## Test the agent ############################
# def Agent_1_output(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']

# ## Define test prompt 
# test_prompt_1 = "Generate LAMMPS data file for a molecular system using the smiles string. The inputs are the name of the molecule, smiles string, box size and number of molecules. Name: Ethanol, SMILES: CCO, Box size: 2.0 nm, Number of molecules: 1"

# # Create and move to tool_1 directory
# os.makedirs("tool_1", exist_ok=True)
# os.chdir("tool_1")
# print(mosdef_response(test_prompt_1))
# os.chdir("..")