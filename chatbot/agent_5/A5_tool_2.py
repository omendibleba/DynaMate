import warnings
warnings.filterwarnings("ignore")
# Import PDF loader
#!pip install pymupdf
from langchain_community.document_loaders import PyMuPDFLoader
# Define Embedding Model
from langchain_openai import OpenAIEmbeddings
#import fitz ## FOr PyMuPDF
#from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores import  FAISS
## Define class for description of inputs in structured tool 
import os
import subprocess
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

import dotenv
dotenv.load_dotenv()

# Defien OPENAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

"""
## Tool 2: RAG_retreival_tool

This tool shas acces to a vectorstore database and is used for Retreival Augmented Generation (RAG). THe chatbot uses similarity search to find the most simiilar piece of information related to the input prompt, learns from it and generates an answer. 
"""

## Define class for description of inputs in structured tool
class RAG_Retreive_DB_Inputs(BaseModel):
    question: str = Field(description="Question to be asked to the vector store")
    name: str = Field(description="Name of the directory to save the vector store")


## Define function to get the answer
def RAG_retreiver(question, name):

    # Load embeddings
    embeddings = OpenAIEmbeddings()

    ## Rename the name variable adding the path to general knowledge base
    name = "./knowledge_base/"+name
    ## Load the vector store
    doc_embeddings = FAISS.load_local(name, embeddings,allow_dangerous_deserialization=True)

    ## Define retriever
    retreiver = doc_embeddings.as_retriever()

    # Define llm
    llm = ChatOpenAI()
    #llm = ChatOllama(model="gemma:2b",temperature=0.)

    # Define Chain type 
    chain_type = "stuff"

    # Define the QA model
    qa_model = RetrievalQA.from_chain_type(llm=llm, retriever=retreiver, chain_type=chain_type)

    answer = qa_model.invoke(question)
    return print(answer['result'])

# ## Test the function
# q_1 = "What are the main conclussions in this paper?"
# name = "knowledge_base/SBU_form"
# RAG_retreiver(q_1, name)

## Define Structured Tool
RAG_Retreive_DB_tool = StructuredTool.from_function(
    func=RAG_retreiver, # Function to be used
    name="RAG_Retreive_DB_tool", # Name of the tool
    description="Retreive information from a vector store.", # Description of the tool
    args_schema=RAG_Retreive_DB_Inputs, # Input schema
    return_direct=True, # Return the output directly
    handle_error=True, # Handle errors
    # Use dictionary as input
    )

################ Test the tool ############################
# ## Define LLM
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [RAG_Retreive_DB_tool]

# ## Propomt for openai function
# prompt = hub.pull("hwchase17/openai-functions-agent")
# #print(prompt)

# # Create OpenAI functions agent
# agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# # ## Create Agent executor
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

# def RAG_retreiver_response(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']

# ## Define test prompt 
# test_prompt_2 = "What are the main conclussions in this paper?. The vector store is called 'SBU_form'."
# print(RAG_retreiver_response(test_prompt_2))
