import streamlit as st 
from common.service.film_service import excution_by_sql

########################################################
# 화면 영역
########################################################
df_data, title_data = excution_by_sql()

st.title(title_data)
st.dataframe(df_data)
