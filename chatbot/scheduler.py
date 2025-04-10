## Simple bot to only respond to an input
import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.tools import  tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor,create_react_agent # To load simple ReAct agent. Reason an act
from langchain import hub


##2. Shell tool
from langchain_community.tools import ShellTool

### Agent 1 Response
from agent_1.agent_1_response import agent_1_executor

### Agent 2 Response
from agent_2.agent_2_response import agent_2_executor

### Agent 3 Response
from agent_3.agent_3_response import agent_3_executor

### Agent 4 Response
from agent_4.agent_4_response import agent_4_executor

### Agent 5 Response
from agent_5.agent_5_response import agent_5_executor

# Define API key for OPenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

## Load default OpenAI chatbot
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

@tool
def bot_response(input: str) -> str:
    """Use Chatbot to answer questions that do not require any tools. Do not perform any action if this tool is used."""
    output = llm.invoke(
        [
            HumanMessage(
                content=str(input)
            )
        ])
    return output.content

@tool
def agent_1_response(input_text:str):
    """
    Use this tool to generate LAMMPS data file for a molecular system from SMILES string, CIF files, and molecular templates. 
    """
    output = agent_1_executor.invoke({"input":input_text})
    return output['output']

@tool
def agent_2_response(input_text:str):
    """
    Use this tool to generate a LAMMPS input to run an NPT, NVT simulaiton or tu directly run a simulation when given the input file. 
    """
    output = agent_2_executor.invoke({"input":input_text})
    return output['output']

@tool
def agent_3_response(input_text:str):
    """
    Use this tool to calculate the radial distribution function of a molecular system. 
    """
    output = agent_3_executor.invoke({"input":input_text})
    return output['output']

@tool
def agent_4_response(input_text:str):
    """
    Use this tool to run umbrella sampling simulations, WHAM analysis, and metadynamics simulations. 
    """
    output = agent_4_executor.invoke({"input":input_text})
    return output['output']

@tool
def agent_5_response(input_text:str):
    """
    Use this tool to generate a vector store from a PDF file and retrieve data from the vector store. 
    """
    output = agent_5_executor.invoke({"input":input_text})
    return output['output']

# Load tools
shell_tool = ShellTool()


# Define list of tools the LLM is going to use
tools_list = [bot_response,shell_tool,
              agent_1_response,
              agent_2_response,
              agent_3_response,
              agent_4_response,
              agent_5_response] # Add the tools to the list

# Get the template prompt to use - you can modify this!
prompt = hub.pull("hwchase17/react")
## Construct the ReAct agent by defining the llm, tools and prompt template
shell_Agent = create_react_agent(llm=llm,tools=tools_list,prompt=prompt)
# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=shell_Agent, tools=tools_list, verbose=False, handle_parsing_errors=True)

# Define function to get response
def Final_Agent(input):
    # Run executor to get response 
    response = agent_executor.invoke({"input":str(input)})
    
    return response['output']