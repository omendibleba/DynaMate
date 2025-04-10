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
### Tool 1: RAG_gen_database_tool

This tool can be used to process a PDF and generate a vector store using OpenAI embeddings and LLMs, And FAISS for storage and similarity search. 

"""
## Define class for description of inputs in structured tool
class RAG_Gen_DB_Inputs(BaseModel):
    pdf_filename: str = Field(description="Path to the PDF file to be embedded")
    name: str = Field(description="Name of the directory to save the vector store")

## Define fucntion to generate vectorestore from PDF file
def generate_vectorstore_from_pdf(pdf_filename, name):
    # Load the PDF with PyMuPDF
    pdf_loader = PyMuPDFLoader(pdf_filename)

    # Load documents
    documents = pdf_loader.load()

    # Load embeddings
    embeddings = OpenAIEmbeddings()

    ##Get the embeddings of the documents in the FAISS vector store
    doc_embeddings = FAISS.from_documents(documents, embeddings)

    ## Save the vector store locally 
    doc_embeddings.save_local('knowledge_base/'+name)

    return

# # Define name of PDF
# pdf_filename = "./formation-mech-SBU-Cr-BDC-MOF.pdf"
# ## Test the function 
# generate_vectorstore_from_pdf(pdf_filename, "SBU_form",)

## Define Structured Tool
RAG_DB_gen_tool = StructuredTool.from_function(
    func=generate_vectorstore_from_pdf, # Function to be used
    name="RAG_DB_gen_tool", # Name of the tool
    description="Generate a vector store from a PDF file. First embeeded the daata and stores it for later usage.", # Description of the tool
    args_schema=RAG_Gen_DB_Inputs, # Input schema
    return_direct=False, # Return the output directly
    handle_error=True, # Handle errors
    # Use dictionary as input
    )


################### Test the tool ############################
# ## Define LLM
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# # Define list of tools the LLM is going to use 
# tools = [RAG_DB_gen_tool]

# ## Propomt for openai function
# prompt = hub.pull("hwchase17/openai-functions-agent")
# #print(prompt)

# # Create OpenAI functions agent
# agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# # ## Create Agent executor
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True,handle_parsing_errors=True)

# def RAG_DB_gen_response(input_text:str):
#     return agent_executor.invoke({"input": input_text})['output']

# ## Define test prompt 
# test_prompt_1 = "Generate a vector store from the PDF file 'formation-mech-SBU-Cr-BDC-MOF.pdf' and save it as 'SBU_form'."

# # Create and move to tool_1 directory
# # os.chdir("tool_5")
# print(RAG_DB_gen_response(test_prompt_1))
# # os.chdir("..")
