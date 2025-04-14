# imports
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
#from langchain.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool, tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor,create_openai_functions_agent # To load simple ReAct agent. Reason an act
from langchain import hub

# Define API key for OPenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

"""
Tool Template:

1. Define the class for the inputs of the tool
2. Define the function that will be used as the tool
3. Define the Structured Tool
4. Define the LLM
5. Define the list of tools the LLM is going to use
6. Define the prompt for the openai function
7. Create the OpenAI functions agent
8. Create the Agent executor
9. Define a function to get the response from the agent
10. Test the agent

"""

#### Define class for description of inputs in structured tool 
class HelloWorld_inps(BaseModel):
    message: str = Field(description="Message to print")
    times: int = Field(description="Amount of times to print message")


# Define function in the class to be used as a tool
def hello_world(message: str, times: int):
    return message * times

## Define Structured Tool
HelloWorld_Tool = StructuredTool.from_function(
    func=hello_world, # Function to be used
    name="HelloWorld", # Function to be used
    description="Prints a message a number of times",  # Description of the tool
    args_schema=HelloWorld_inps,
    return_direction=False,
    handle_error=True,)



## Define LLM
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# Define list of tools the LLM is going to use 
tools = [HelloWorld_Tool]

## Propomt for openai function
prompt = hub.pull("hwchase17/openai-functions-agent")
#print(prompt)

# Create OpenAI functions agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# ## Create Agent executor
agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

def agent_response(input_text:str):
    return agent_executor.invoke({"input": input_text})['output']

## Test the agent
test_prompt = "Prints a message a number of times. \n \
                Message: Hello, Times: 5"

print(agent_response(test_prompt))