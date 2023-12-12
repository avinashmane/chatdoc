import streamlit as st
import pandas 
from Util import yaml_dump, yaml_load
cfg=yaml_load("wireframe.yaml")

st.title(cfg['title'])

st.sidebar.header("Settings")

# Insert containers separated into tabs:
tabs = st.tabs(cfg['tab_names'])

with tabs[0]:
    st.write("Please upload the RFP or requirements documents")
    st.file_uploader('File uploader')
    st.button("process")
    
with tabs[1]:
    # Replace any single element.
    element = st.empty()
    # element.line_chart(...)
    with st.container():
        complexity = st.text_input("Project Complexity","Low")  # Replaces previous.
        st.selectbox("Override:","High Medium Low".split())

    st.button("Proceed to Sizing")
with tabs[2]:
    
    # Insert out of order.
    elements = st.container()
    # elements.line_chart(...)
    st.write("Hello")
    elements.text_input("Enter something")  # Appears above "Hello"3
    
with tabs[3]:
    st.help(pandas.DataFrame)
    # st.get_option(key)
    # st.set_option(key, value)
    # st.set_page_config(layout='wide')
    # st.experimental_show(st)
    # st.experimental_get_query_params()
    # st.experimental_set_query_params(**params)

# You can also use "with" notation:
with tabs[4]:
    st.radio('Select one:', 
           cfg['hyperscalers'])
    st.write("Total cost is : xxxxx")