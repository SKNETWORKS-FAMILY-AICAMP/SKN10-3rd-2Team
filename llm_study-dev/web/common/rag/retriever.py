import streamlit as st 

from .loader import get_loader 
from .splitter import get_splitter 
from langchain_community.vectorstores import FAISS 
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
import os 

@st.cache_resource
def get_retriever(file_path:str="./common/rag/new 질병.csv"):
  loader = get_loader(file_path)
  splitter = get_splitter()
  docs = loader.load()
  split_docs = splitter.split_documents(docs)
  return FAISS.from_documents(split_docs, embedding=OpenAIEmbeddings(
    model="text-embedding-3-small")).as_retriever()

@st.cache_resource
def get_rag_prompt():
  return PromptTemplate(
    template="""
    당신은 질문-답변(Question-Answering)을 수행하는 친절한 AI 어시스턴트입니다.
    당신의 임무는 주어진 문맥(context) 에서 주어진 질문(question) 에 답하는 것입니다.
    검색된 다음 문맥(context) 을 사용하여 질문(question) 에 답하세요.
    만약, 주어진 문맥(context) 에서 답을 찾을 수 없다면, 답을 모른다면 `주어진 정보에서 질문에 대한 정보를 찾을 수 없습니다` 라고 답하세요.
    한글로 답변해 주세요.
    단, 기술적인 용어나 이름은 번역하지 않고 그대로 사용해 주세요.

    #Context:
    {context}

    #Question:
    {question}

    #Answer:
    """
  )

def get_rag_result(user_input:str):
  retriever = get_retriever()
  context = retriever.invoke(user_input)
  return get_rag_prompt().format(context=context[0].page_content, question=user_input)

