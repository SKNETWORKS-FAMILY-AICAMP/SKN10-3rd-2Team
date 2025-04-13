import streamlit as st 
import os

########################################################
# 데이터베이스 영역
# @st.cache_resource -> 만약 connector가 메모리 존재하지 않을 때만, connector 생성 
# -> 메모리에 존재한다면, 기존 connector 리턴 
########################################################
@st.cache_resource 
def get_connector():
  return st.connection(
    name="my_db",
    type="sql",
    dialect="postgresql",
    host=os.getenv("host"),
    port=os.getenv("port"),
    database=os.getenv("database"),
    username=os.getenv("uname"),
    password=os.getenv("password")
  )