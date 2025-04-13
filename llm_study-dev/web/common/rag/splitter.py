
from langchain.text_splitter import RecursiveCharacterTextSplitter

def get_splitter(chunk_size:int=500, chunk_overlap:int=50):
  return RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

