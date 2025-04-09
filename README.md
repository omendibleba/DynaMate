
# DynaMate: A Modular Multi-Agent Framework for Scientific Workflows

DynaMate is a template that provides a modular and flexible codebase for developing multi-agent frameworks tailored to your scientific workflows. This template allows researchers to easily define custom Python functions, which can then be called, coordinated, and executed by LLM-based agents to perform complex and time consuming tasks.

The Multi-Agent framework was tested in the context of molecular dynamics (MD), but the given its modularity it can be easily modified for cstom worksflows that can be controlled with python functions. For this reason, the template can be used for applications in catalysis, drug delivery, colloidal systems, management of scintific equipment, etc. 

Additional details can be found this publication:
REF

<br>

## Installation 

The creation of a new conda enviroment is recommended, and the requirements.txt file can be used to install the main packages and libraries that enable the usage of the template. Use the following commands.

`conda create -n myenv python=3.10.13`

The requirements.txt file includes optional dependencies for the current agents in the framework. Comment this lines if you are not interested in using the chatbot for this application.

`pip install -r requirements.txt --no-cache-dir`

*** After installition, is recommended to run the ./tutorials/0_chatbot_vs_agent.ipynb notebook to ensure importatnt dependecies were successfully installed. 

<br>

## Tutorials 

The tutorials folders include folders for each agent included in the workflow and within there are python notebooks with detailed description of the tools, how to used them, and what they do. Tihs is a good practice to mantain a "live documentation" of the multi-agent framework. As new tools and agetns are developed their instructions will be updated in these folders. 

<br>

## List of Agents and tools currently available:

### Agent 1: MD System Preparation 

This agent has acces to MoSDEF, moltemplate, packmol and rdkit packages which are useful for preparing files required for MD simulations using LAMMPS. It can generate data files from SMILE strings and CIF files (using lammps_interface). By default it uses the GAFF forcefield file provided by Moltemplate but this can be modified in the source code of the file to use other available or custom force fields. The agent algo generates template files form provided data files and can use them to generate more com,plex systems. 


### Agent 2: MD Simulation Runner

This agents requires an available LAMMPS executable to run simulations with LAMMPS. Its tool can generate a provicional simulation file that runs an energy minimization, NPT and NVT simulations. THe type and length of the simulations can be modified in the source code of this agent's tools. If the simulation files are availablke the agent can read them to directly run the simulaiton. 