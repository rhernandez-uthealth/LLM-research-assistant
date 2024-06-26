from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.retrievers.multi_query import MultiQueryRetriever

import streamlit as st
import re
import process

sb = st.sidebar # defining the sidebar

sb.markdown("🛰️ **Navigation**")
page_names = ["DBChat", "CreateDB"]
page = sb.radio("", page_names, index=0)

with open ("./keys.txt", 'r') as f:
    keyfile = f.read()
    f.close()
OPENAI_API_KEY = re.findall(r'"(.*?)"', keyfile)[0]

def parse_llm_response(llm_response):
    st.write("QUERY: {}".format(llm_response['question']))
    st.write("RESPONSE: {}".format(llm_response['answer'].replace('\n\n','\n')))

    st.write("Sources: {}".format(llm_response['sources']))
    idlist = []
    for item in llm_response['source_documents']:
        tempdict = {
            "Text":item.page_content,
            "Source":item.metadata['source'],
            "Filepath":item.metadata['file_path'],
            "ID":item.metadata['id']
        }
        st.write(tempdict)
        idlist.append(item.metadata['id'])
    return idlist


def query_func(query_input, vectordb):
    # Default query is set below
    query_text = 'Carefully interpret the context and generate a response to the query. The language should be suitable for an academic journal, concise, and thoughtful. Use in-text citations. Your response should be around 400 words. "Query:"{}"'.format(query_input)    
    retriever = vectordb.as_retriever(
        search_type="mmr", 
        search_kwargs={
            "k": 15, 
        }
    )
    mqr = MultiQueryRetriever.from_llm(
            retriever=retriever, 
            llm=ChatOpenAI(model_name="gpt-4", temperature=0.1, openai_api_key=OPENAI_API_KEY)
        )
    qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=ChatOpenAI(
            model_name="gpt-4", temperature=0.3, openai_api_key=OPENAI_API_KEY
        ),
        chain_type="stuff", 
        retriever=mqr, 
        return_source_documents=True
        )
    llm_response = qa_chain(str(query_text))
    idlist = parse_llm_response(llm_response)
    return idlist

def query_reroll(query_input, vectordb, idlist2, sources):
    # Default query is set below
    query_text = 'The content of the answer should be fitting for academic publication. Use in-text citations. Make your response over 400 words. "Query:"{}"'.format(query_input)    
    retriever = vectordb.as_retriever(
        search_type="mmr", 
        search_kwargs={
            "k": 15,
            "filter":{
                'id':{'$nin':idlist2},
                'source':{'$nin':sources}}
        }
    )
    mqr = MultiQueryRetriever.from_llm(
            retriever=retriever, 
            llm=ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=OPENAI_API_KEY)
        )
    qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=ChatOpenAI(
            model_name="gpt-4", temperature=0.3, openai_api_key=OPENAI_API_KEY
        ),
        chain_type="stuff", 
        retriever=mqr, 
        return_source_documents=True
        )
    llm_response = qa_chain(str(query_text))
    idlist = parse_llm_response(llm_response)
    return idlist


def del_index(del_input, vectordb):
    if ',' in str(del_input):
        dellist = del_input.split(", ")
    else:
        dellist=[del_input]
    print('deleting index {}'.format(dellist))
    vectordb.delete(ids=dellist)

def main():
    if page == "DBChat":
        dirname = st.text_input("Enter the name for sub-folder housing the ChromaDB you would like to load.", '', key=1)
        DIRECTORY = "./databases/{}/".format(dirname)
        vectordb = Chroma(persist_directory=DIRECTORY, embedding_function=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002"))

        
        query_input = st.text_input("Ask questions about your PDF file:", key=3)
        query = st.button("Query")
        reroll = st.button("Reroll")
        sources = st.text_input("Write the sources you wish to exclude")

        del_input=''
        del_input = st.text_input("Write the IDs of entries you wish to delete, seperated by a comma")
        del_requery = st.button("Delete by ID")

        # re_roll = st.button("Find different responses")

        
        if query or query_input:
            idlist = query_func(query_input, vectordb)
            print(idlist)
        if reroll:
            idlist = query_reroll(query_input, vectordb, idlist, sources)
            print(idlist)
        if del_requery:
            print("del input:"+del_input)
            del_index(del_input, vectordb)


            
    if page == "CreateDB":
        dirname = st.text_input("Enter the name for sub-folder to house the ChromaDB you would like to create.", '', key=1)
        DIRECTORY = "./databases/{}/".format(dirname)
        LIBRARY = st.text_input("What is the name of the Zotero BetterBibtex library folder you would like to use for this database?", key=5)
        createdb = st.button("CreateDB", type="primary")
        if createdb:
            process.main(LIBRARY, DIRECTORY, OPENAI_API_KEY)


if __name__ == '__main__':
    main()
