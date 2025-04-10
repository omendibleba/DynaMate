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

## Define class for description of inputs in structured tool 
class parral_sim_runs_Inputs(BaseModel):
    path: str = Field(description="Path to the production folder")

### Function to run multiple simulations in parallel
def run_sims_parallel(path:str):
    parralel_script  = "/scratch365/omendibl/Molec_Mindset/DynaMate_V2/tutorials/4_enhanced_sampler/multi_runs.sh"

    ## get current path
    current_path = os.getcwd()

    ## Move to the production path
    os.chdir(current_path+path)

    ## Copy bash scrip to this path
    os.system(f"cp {parralel_script} .")

    ## Run the bash script in the background
    os.system(f"nohup bash multi_runs.sh &")

    ## Move back to the original path
    os.chdir(current_path)

    return
# ## test function
# run_sims_parallel("/production_runs", 10)


## Define Structured Tool
submit_umbrellas_tool = StructuredTool.from_function(
    func=run_sims_parallel, # Function to be used
    name="run_sims_parall", # Function to be used
    description="Run multiple umbrella sampling simulations in parallel.", # Description of the tool
    args_schema=parral_sim_runs_Inputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    # Use dictionary as input
    )


## Define LLM
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# Define list of tools the LLM is going to use 
tools = [submit_umbrellas_tool]

## Propomt for openai function
prompt = hub.pull("hwchase17/openai-functions-agent")
#print(prompt)

# Create OpenAI functions agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# ## Create Agent executor
agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

def mosdef_response(input_text:str):
    return agent_executor.invoke({"input": input_text})['output']

## Define test prompt 
test_prompt_1 = "Run multiple umbrella sampling simulations in parallel. The path to the production folder is '/production_runs'."

# Create and move to tool_1 directory
os.makedirs("tool_1", exist_ok=True)
os.chdir("tool_1")
print(mosdef_response(test_prompt_1))
os.chdir("..")