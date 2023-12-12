"""
    Collection
"""

import os, datetime
# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFium2Loader, UnstructuredPowerPointLoader, UnstructuredExcelLoader, TextLoader
from langchain.chains.question_answering import load_qa_chain
# from langchain.llms import OpenAI
# from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatLiteLLM
import pydash as py_
import chromadb
from Util import yaml_dump, yaml_load
cfg=yaml_load("config.yaml")


class PDFQuery:
    max_tokens=256
    temparature=0
    def __init__(self, 
                 llm_model_name = "together_ai/togethercomputer/llama-2-70b-chat", 
                 openai_api_key = None) -> None:
        """
            Should not have a Collection name
        """
        if cfg["chromadb_path"]!='memory':
            self.chromaClient=chromadb.PersistentClient(path=cfg["chromadb_path"])
            self.path_kw = {"persist_directory":cfg["chromadb_path"]}  
        else:
            self.chromaClient=chromadb.Client()
            self.path_kw = {}
            
        # self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        # os.environ["OPENAI_API_KEY"] = openai_api_key
        self.embeddings = HuggingFaceInferenceAPIEmbeddings(
                            api_key=os.environ['HUGGINGFACEHUB_API_TOKEN'],
                            model_name="sentence-transformers/all-MiniLM-l6-v2"
                        )
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        # self.llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
        
        self.set_model_with_params(llm_model_name,temparature=self.temparature)
        # self.chain = None
        self.db = {}

    def set_model_with_params(self,llm_model_name="together_ai/togethercomputer/llama-2-70b-chat",**kwargs):
        self.llm_model_name=llm_model_name
        for param in kwargs:
            setattr(self,param,kwargs[param])
        print(self.llm_model_name,kwargs)
        self.llm = ChatLiteLLM(model=self.llm_model_name,**kwargs)
        self.chain = load_qa_chain(self.llm, chain_type="stuff")
        
    def get_collections(self):
        return [c.name for c in #collection names
                            self.chromaClient.list_collections()]

    def get_collection_info(self,collection):
        coll=self.chromaClient.get_collection(collection)
        doc_names=py_.uniq([x['source'] for x in coll.get()['metadatas']])
        
        return dict(count=coll.count(), docs= doc_names)
        
    def delete_collection(self,collection_name):
        print("Deleting",collection_name)
        return self.chromaClient.delete_collection(name=collection_name)
        
    def get_chroma_coll(self,collection):
        if cfg["chromadb_path"]!="memory":
            return Chroma(collection,
                        self.embeddings,
                        persist_directory=cfg["chromadb_path"]) 
        else:
            return Chroma(collection,
                        self.embeddings) 
        
    def ask(self, collection, question: str) -> str:
        if self.chain is None:
            response = "Please, add a document."
        else:
            # docs = self.db[collection].get_relevant_documents(question)
            coll=self.get_chroma_coll(collection)
            print(f"Searching in {len(coll.get()['ids'])} docs")
            retriever = coll.as_retriever(
                search_type="mmr",
                search_kwargs={'k': 10, 'fetch_k': 50}
            )

            
            docs=retriever.get_relevant_documents(question)
            response = self.chain.run(input_documents=docs, 
                                      question=question)
            print(f"searching in "+ "\n".join([str(d.metadata) for d in docs]))
        return response
        
    def ingest(self, collection_name,file_path: os.PathLike,collection_metadata=None) -> str:
        
        collection_name = collection_name if (collection_name and collection_name!='New...'
                   ) else f'Sess_{datetime.datetime.now().strftime("%y%m%d%H%M")}'

        documents = self.load_documents(file_path)    
        print (f"{len(documents)} documents loaded forr {file_path}")
    
        splitted_documents = self.text_splitter.split_documents(documents)
        
        # self.db = Chroma.from_documents(splitted_documents, self.embeddings).as_retriever()
        print(">"*10,collection_name, f"Chunk add size: {cfg['chunk_add_size']}")
        coll=self.get_chroma_coll(collection_name)
        chunks=py_.chunk(splitted_documents,int(cfg['chunk_add_size']))
        for i,chunk in enumerate(chunks):
            
            try: 
                coll.add_documents(chunk)
                yield(i/len(chunks))
                print(i,chunk[-1].metadata)
                
            except Exception as e: 
                print(f"Error {e!r}",chunk)
            # print([d.metadata['page'] for d in chunk])
        coll.persist()
        self.db[collection_name] = coll.as_retriever()
        # self.chain = load_qa_chain(OpenAI(temperature=0), chain_type="stuff")
        # self.chain = load_qa_chain(ChatLiteLLM(temperature=0), chain_type="stuff")
        print(f"finished loading {collection_name}")

        
    def load_documents(self,file_path):
        ext = file_path.split(".")[-1]
        
        if ext =='pdf':
            loader = PyPDFium2Loader(file_path)
        elif ext =='txt':
            loader = TextLoader(file_path, encoding="utf8")
        elif ext  =='pptx':
            loader = UnstructuredPowerPointLoader(file_path, 
                                                  mode="elements", strategy="fast", encoding="utf8")
        elif ext =='xlsx':
            loader = UnstructuredExcelLoader(file_path, mode="elements",  encoding="utf8")
        else:
            print(f'Unknown extension {ext}')
            
        ## load now    
        try:
            documents = loader.load()
            return documents
        except Exception as e:
            print(f'error loading  {e!r}')
            return []

    
    def forget(self) -> None:
        self.db = None
        self.chain = None