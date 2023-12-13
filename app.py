from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.retrievers.multi_query import MultiQueryRetriever

import streamlit as st
import re
import process

sb = st.sidebar # defining the sidebar

sb.markdown("🛰️ **Navigation**")
page_names = ["DBChat", "CreateDB"]
page = sb.radio("", page_names, index=0)

def get_vectorstor(directory, openai_api_key):
    vectordb = Chroma(persist_directory=directory, embedding_function=OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-ada-002"))
    return vectordb

def get_retriver(vectorstor):   
    retriever = vectorstor.as_retriever(search_kwargs={"k": 20})
    return retriever

def get_qachain(openai_api_key, retriever):
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(
            model_name="gpt-3.5-turbo", temperature=0.3, openai_api_key=openai_api_key
            ),
        chain_type="stuff", 
        retriever=retriever, 
        return_source_documents=True)

def parse_llm_response(llm_response):
    st.write("QUERY: {}".format(llm_response['query']))
    st.write("RESPONSE: {}".format(llm_response['result']))
    for item in llm_response['source_documents']:
        tempdict = {
            "Text":item.metadata['text'],
            "Citation":item.metadata['citation'],
            "Filepath":item.metadata['file_path']
        }
        st.write(tempdict)
        
def main():
    with open ("./keys.txt", 'r') as f:
        keyfile = f.read()
        f.close()
    OPENAI_API_KEY = re.findall(r'"(.*?)"', keyfile)[0]
    
    if page == "DBChat":
        dirname = st.text_input("Enter the name for sub-folder housing the ChromaDB you would like to load.", '', key=1)
        DIRECTORY = "./databases/{}/".format(dirname)
        query = st.text_input("Ask questions about your PDF file:", key=3)
        if query:
            vectordb = Chroma(persist_directory=DIRECTORY, embedding_function=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002"))
            retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 10})
            MultiQueryRetriever.from_llm(
                retriever=vectordb.as_retriever(), 
                llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=.1, openai_api_key=OPENAI_API_KEY)
            )

            qa_chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(
                    model_name="gpt-3.5-turbo", temperature=.1, openai_api_key=OPENAI_API_KEY
                    ),
                chain_type="stuff", 
                retriever=retriever, 
                return_source_documents=True)
            llm_response = qa_chain(str(query))
            parse_llm_response(llm_response)

    if page == "CreateDB":
        dirname = st.text_input("Enter the name for sub-folder to house the ChromaDB you would like to create.", '', key=1)
        DIRECTORY = "./databases/{}/".format(dirname)
        LIBRARY = st.text_input("What is the name of the Zotero BetterBibtex library folder you would like to use for this database?", key=5)
        st.button("Waiting", type="primary")
        if st.button('CreateDB'):
            process.main(LIBRARY, DIRECTORY, OPENAI_API_KEY)


if __name__ == '__main__':
    main()
