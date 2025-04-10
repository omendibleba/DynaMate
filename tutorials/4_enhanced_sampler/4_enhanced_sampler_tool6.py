## Define class for description of inputs in structured tool 
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
class MetaD_analysis_Inputs(BaseModel):
    path: str = Field(description="Path to the umbrella production folders")
    dim: int = Field(description="Dimension of the free energy surface (1 or 2)")
    cv: str = Field(description="Name of the collective variable to be analyzed")

## Define function
def MetaD_analysis(path,dim,cv="cv1"):
    import plumed
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import glob
    import natsort

    # Load data
    data = plumed.read_as_pandas(f"{path}")
    ## Plot CVs vs Time
    plt.scatter(data["time"], data["cv1"], label=f"CV1")
    plt.scatter(data["time"], data["cv2"], label=f"CV2")
    plt.xlabel("Time (ps)")
    plt.ylabel("Angle (radians)")
    plt.legend()
    #plt.savefig("angle_v_time.png")
    plt.show()

    ## PLot CV vs CV
    plt.scatter(data["cv1"], data["cv2"])
    plt.xlabel("CV1")
    plt.ylabel("CV2")
    #plt.savefig("cv1_v_cv2.png")
    plt.show()

    ## Run the sum_hills command to obtain the 2Dfree energy surface
    if dim == 2:
        os.system("rm bck.*")
        os.system("plumed sum_hills --hills HILLS --stride 1000 --mintozero")

        ## Load the 2D free energy surface and plot 
        dim2_data = plumed.read_as_pandas(natsort.natsorted(glob.glob("fes_*.dat"))[-1])
        # Load the FES data
        fes = np.loadtxt(natsort.natsorted(glob.glob("fes_*.dat"))[-1])

        # Extract the phi, psi, and FES values
        phi = fes[:, 0]
        psi = fes[:, 1]
        fes_values = fes[:, 2]

        # Reshape the FES values into a grid
        nbins_phi = len(np.unique(phi))
        nbins_psi = len(np.unique(psi))
        fes_grid = fes_values.reshape(nbins_phi, nbins_psi)

        # Create meshgrid for phi and psi
        phi_grid, psi_grid = np.meshgrid(np.unique(phi), np.unique(psi))

        # Convert the energy to kcal/mol
        fes_grid_kcal = fes_grid * 0.239

        # Set the size and background color of the plot
        plt.figure(figsize=(8, 6))
        plt.rcParams['axes.facecolor'] = 'white'

        # Plot the FES as a surface or grid with modified color scale
        plt.pcolormesh(phi_grid, psi_grid, fes_grid_kcal, cmap='plasma', shading='nearest', vmin=0, vmax=20)
        plt.colorbar(label="Free Energy (kcal/mol)", ) #ticks=np.arange(0, 21, 5)
        plt.xlabel("phi (rad)", fontsize=14)
        plt.ylabel("psi (rad)", fontsize=14)
        #plt.title("OnlyMins 1000 Frames SPC",fontsize=18,fontweight='bold')
        # Add contour lines every 2.5 kcal/mol
        contour_levels = np.arange(0, 20, 0.5)
        plt.contourf(phi_grid, psi_grid, fes_grid_kcal, levels=contour_levels,cmap='plasma')
        plt.show()

    elif dim == 1:
        os.system(f"plumed sum_hills --hills HILLS --stride 1000 --mintozero --kt 2.49 --idw {cv}")

        ## Load the 1D free energy surface and plot 
        reweight_data = plumed.read_as_pandas(natsort.natsorted(glob.glob("fes_*.dat"))[-1])
        plt.figure(figsize=(8, 6), dpi=150,facecolor='w', edgecolor='k')
        plt.plot(reweight_data["{cv}"], reweight_data["projection"]*0.239006, label=f"Reweighted {cv}", color='black',linewidth=2)
        plt.xlabel("$\phi$ [radians]", fontsize=18, fontweight='bold')
        plt.ylabel("Free energy [Kcal/mol]", fontsize=18, fontweight='bold')
        plt.tick_params(axis='both', which='major', labelsize=16)
        plt.xlim(-180, 180)
        # plt.legend()
        plt.show()
    return

# # test function
# path = './'
# MetaD_analysis(path,2,cv="cv1")

## Define Structured Tool
MetaD_analysis_tool = StructuredTool.from_function(
    func=MetaD_analysis, # Function to be used
    name="MetaD_analysis_tool", # Function to be used
    description="Analyze the output of a metadynamics simulation in one or two dimensions. The inputs are the path to the metadynamics production run, the dimension of the free energy surface (1 or 2), and the name of the collective variable to be analyzed.", # Description of the tool
    args_schema=MetaD_analysis_Inputs, # Schema of the inputs defined in class
    return_direct=True, # Return the output directly
    handle_error=False, # Handle errors
    # Use dictionary as input
    )


## Define LLM
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# Define list of tools the LLM is going to use 
tools = [MetaD_analysis_tool]

## Propomt for openai function
prompt = hub.pull("hwchase17/openai-functions-agent")
#print(prompt)

# Create OpenAI functions agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# ## Create Agent executor
agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

def MetaD_Analysis_response(input_text:str):
    return agent_executor.invoke({"input": input_text})['output']

## Define test prompt 
test_prompt_1 = "Analyze the output of a metadynamics simulation in two dimensions. The path to the metadynamics production run is './colvar.dat'. The dimension of the free energy surface is 2 and the name of the collective variable to be analyzed is 'cv1'."

# Create and move to tool_1 directory
os.chdir("tool_5")
print(MetaD_Analysis_response(test_prompt_1))
os.chdir("..")