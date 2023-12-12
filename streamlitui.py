import os
import datetime
import streamlit as st
# from streamlit_chat import message
from pdfquery import PDFQuery
import dotenv, json
from Util import yaml_dump, yaml_load
import pydash as py_
import re
# import litellm
# litellm.set_verbose=True # 👈 this is the 1-line change you need to make

# from langchain.schema import HumanMessage, AIMessage

dotenv.load_dotenv()
cfg=yaml_load("config.yaml")
    
def save_state():  
    yaml_dump(py_.pick(st.session_state,['messages']) ,"session.yaml")
def load_state():  
    sess=yaml_load("session.yaml")
    for k in sess:
        st.session_state[k]=sess[k]

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# st.set_page_config(page_title="ChatPDF")
# st.write(st.session_state)

def display_messages():
    st.subheader("Chat")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        st.message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()

def process_input():
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
            query_text = queryEngine.ask(coll_name,user_text)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((query_text, False))
    save_state()

def create_binary_file(folder_path, file_name):
  """
  Creates a new binary file in a new folder.

  Args:
    folder_path: The path to the new folder.
    file_name: The name of the binary file.
    data: The binary data to write to the file.
  """
  # Create the new folder
  try:
    os.makedirs(folder_path)
  except OSError:
    if not os.path.isdir(folder_path):
      raise

  # Create the file name
  return os.path.join(folder_path, file_name)


def main():
    
    queryEngine = PDFQuery("together_ai/togethercomputer/llama-2-70b-chat")
    # if not "pdfquery" in st.session_state:
    #     queryEngine = PDFQuery("together_ai/togethercomputer/llama-2-70b-chat")
    if not "messages" in st.session_state.keys():
        st.toast("Starting")
        # st.success("select a collection")
        st.session_state["messages"] = []
        # load_state()        
    else:
        st.write()

    st.image('./static/imageedit_3_8432864280.gif') #/catalog-banner-light398a.svg  vani-gif.gif, , width=200
    st.title(cfg['title'])
    # st.header(cfg['header'])
    # st.subheader("Upload a document")
    # st.toast(",".join([x for x in os.environ if 'API' in x]))
    collections=queryEngine.get_collections()
    coll_name=st.selectbox('Collection', 
                           [ 'New...']+collections,
                           key="collection",)
    

        
    # def update_selected_option():
    #   st.session_state.selected_option = ["selected_option"]
    # [""]
    # options = ["Option 1", "Option 2", "Option 3"]
    
    # selected_option = st.selectbox("Choose an option:", options, key="selected_option", on_change=update_selected_option)
    
    # print(f"Selected option: {st.session_state.selected_option}")
    
    if coll_name=="New...":
        with st.expander("Ingestion", expanded= True):
            coll_name = st.text_input("Collction Name", f'Sess_{datetime.datetime.now().strftime("%y%m%d%H%M")}')
            files=st.file_uploader(   #.sidebar
                    "Upload document",
                    type=cfg['supported_extensions'],
                    # key="file_uploader",
                    # on_change=read_and_save_file,
                    label_visibility="collapsed",
                    accept_multiple_files=True,
                    # disabled=not is_openai_api_key_set(),
                )
            
            ingest_control=st.empty()
            if ingest_control:=st.button("Process", type="primary"):
                print('> ',coll_name )
                for file in files: #st.session_state["file_uploader"]:
                    with open(create_binary_file(f'{cfg["tempfiles"]}/{coll_name}',file.name), "wb") as tf:
                    # with tempfile.NamedTemporaryFile(delete=False) as tf:
                        tf.write(file.getbuffer())
                        file_path = tf.name
            
                    ingest_control = st.progress(0)
                    for progress_pct in queryEngine.ingest(
                                            coll_name, 
                                            # f"{file.name} ({file.size})",
                                            file_path):
                        ingest_control.progress(progress_pct)
                    ingest_control.progress(100)
                    ingest_control=st.empty
                    # os.remove(file_path)
                ingest_control=st.success(f'Processed as {coll_name}')
    
                collections.insert(0, coll_name)
                # need to get this to work
                # st.session_state["collection"]=collections[0]
                
            st.session_state["ingestion_spinner"] = st.empty()
    else:
        try:
            coll_info=queryEngine.get_collection_info(coll_name)
            replace_str=cfg['tempfiles']+r"\/"+coll_name+r"[\/\\]*"  #tmpfiles\/Sess_2312110041[\/\\]
            st.sidebar.success(", ".join([re.sub(replace_str, '', x) 
                                for x in coll_info['docs']])+ f"/ {coll_info['count']} documents")
            if st.sidebar.button("Delete collection?"):
                st.sidebar.write("This can not be reversed")
                queryEngine.delete_collection(coll_name)
        except Exception as e:
            st.warning(f"collection does not exist: {e!r}")
        
    # display_messages()
    # st.text_input("Message", key="user_input", on_change=process_input)
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
    
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            # message_placeholder.markdown("...")
            with st.spinner(text='In progress'):
                full_response = ""
                full_response = queryEngine.ask(
                                    st.session_state["collection"] 
                                        if "collection" in st.session_state 
                                        else coll_name,
                                prompt)

                message_placeholder.markdown(full_response + "▌")
                
                # message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

    st.divider()
    st.markdown("Team: Richa, Avinash, Ratnakar")


if __name__ == "__main__":
    main()