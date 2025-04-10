# imports
import os
from dotenv import load_dotenv
# import mbuild
# import foyer
import warnings
warnings.filterwarnings("ignore")
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
# from langchain_openai import ChatOpenAI
# from langchain.agents import AgentExecutor,create_react_agent,create_openai_functions_agent # To load simple ReAct agent. Reason an act
# from langchain import hub

# Define API key for OPenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

"""
## Tool 3: data_from_cif

Tool to generate LAMMPS data files from CIF files usign lammps-interface. CIF files must have P1 symmetry.

"""

## Define class for description of inputs in structured tool 
class Template_from_data_Inputs(BaseModel):
    molname: str = Field(description="Name of the molecule in the template")
    input_file: str = Field(description="Input file with force field parameters")
    data_file: str = Field(description="Data file with atomic coordinates,bonds,angles, etc.")
    template: str = Field(description="Template of the molecule of interest")

## Define tool to define system.lt files for moltemplate
def template_from_data(molname:str,  input_file:str, data_file:str, template:str):


    import subprocess
    # # Go to the directory and run the moltemplate command
    # os.chdir(name)

    # Run the command and capture any errors
    try:
        #print(molname, input_file, data_file, template)
        # Construct the command string
        command = f"ltemplify.py -name {molname} {input_file} {data_file} > {template}"

        # Run the command using os.system
        os.system(command)
    
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")

    # Go back to the previous directory
    os.chdir('../')

    ## Define Structured Tool
templates_from_Data_tool = StructuredTool.from_function(
    func=template_from_data, # Function to be used
    name="templates_from_Data_tool", # Name of the tool
    description="Generate moltemplate files from the data file and the input file with force field parameters. The inputs are the name of the molecule, template file, input file, data file and the name of the molecule in the template.", # Description of the tool, # Description of the tool
    args_schema=Template_from_data_Inputs, # Schema of the inputs defined in class
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    )

### Test the function

# ## Define LLM
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [templates_from_Data_tool]

# ## Propomt for openai function
# prompt = hub.pull("hwchase17/openai-functions-agent")
# # print(prompt)

# # Create OpenAI functions agent
# agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# # ## Create Agent executor
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

# def templatesData_response(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']