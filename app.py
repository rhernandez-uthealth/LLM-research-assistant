import sys
import streamlit as st

st.write(f"Python executable: {sys.executable}")

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain_classic.chains import RetrievalQAWithSourcesChain
from langchain_classic.retrievers  import MultiQueryRetriever

import re
import process

sb = st.sidebar # defining the sidebar

sb.markdown("🛰️ **Navigation**")
page_names = ["DBChat", "CreateDB"]
page = sb.radio("", page_names, index=0)

with open ("./keys.txt", 'r') as f:
    keyfile = f.read()
OPENAI_API_KEY = re.findall(r'"(.*?)"', keyfile)[0]

def parse_llm_response(llm_response):
    st.write("QUERY: {}".format(llm_response['question']))
    st.write("RESPONSE: {}".format(llm_response['answer'].replace('\n\n','\n')))
    st.write("Sources: {}".format(llm_response['sources']))
    idlist = []
    for item in llm_response['source_documents']:
        tempdict = {
            "Text": item.page_content,
            "Source": item.metadata['source'],
            "Filepath": item.metadata['file_path'],
            "ID": item.metadata['id']
        }
        st.write(tempdict)
        idlist.append(item.metadata['id'])
    return idlist

def query_func(query_input, vectordb):
    query_text = (
        'Carefully interpret the context and generate a response to the query. '
        'The language should be suitable for an academic journal, concise, and thoughtful. '
        'Use in-text citations. Your response should be around 400 words. "Query:"{}"'
    ).format(query_input)

    retriever = vectordb.as_retriever()  # no args to avoid errors
    # We can add k for max docs if needed later on to retriever or chain

    mqr = MultiQueryRetriever.from_llm(
        retriever=retriever,
        llm=ChatOpenAI(model_name="gpt-4", temperature=0.1, openai_api_key=OPENAI_API_KEY)
    )
    qa_chain = RetrievalQAWithSourcesChain.from_llm(
        llm=ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=OPENAI_API_KEY),
        retriever=mqr,
        return_source_documents=True,
    )
    llm_response = qa_chain({"query": query_text})  # call chain with dict input
    idlist = parse_llm_response(llm_response)
    return idlist

def query_reroll(query_input, vectordb, idlist2=None, sources=None):
    if not idlist2:
        idlist2 = []
    if not sources:
        sources = []

    query_text = (
        'The content of the answer should be fitting for academic publication. '
        'Use in-text citations. Make your response over 400 words. "Query:"{}"'
    ).format(query_input)

    retriever = vectordb.as_retriever()  # no args, filter usage needs manual filtering later

    mqr = MultiQueryRetriever.from_llm(
        retriever=retriever,
        llm=ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=OPENAI_API_KEY)
    )

    # NOTE: Filtering by id and source is not supported in this call directly 
    # Could implement custom filtering retriever if needed.

    qa_chain = RetrievalQAWithSourcesChain.from_llm(
        llm=ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=OPENAI_API_KEY),
        retriever=mqr,
        return_source_documents=True,
    )
    llm_response = qa_chain({"query": query_text})
    idlist = parse_llm_response(llm_response)
    return idlist

def del_index(del_input, vectordb):
    # split by comma with optional spaces around
    dellist = [x.strip() for x in del_input.split(",")] if del_input else []
    print('deleting index {}'.format(dellist))
    if dellist:
        vectordb.delete(ids=dellist)

def main():
    if page == "DBChat":
        dirname = st.text_input("Enter the name for sub-folder housing the ChromaDB you would like to load.", '', key=1)
        DIRECTORY = f"./databases/{dirname}/"
        vectordb = Chroma(persist_directory=DIRECTORY, embedding_function=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002"))

        query_input = st.text_input("Ask questions about your PDF file:", key=3)
        query = st.button("Query")
        reroll = st.button("Reroll")
        sources = st.text_input("Write the sources you wish to exclude")

        del_input = st.text_input("Write the IDs of entries you wish to delete, separated by a comma")
        del_requery = st.button("Delete by ID")

        if query and query_input:
            idlist = query_func(query_input, vectordb)
            print(idlist)
        if reroll and query_input:
            # Pass empty lists to avoid error if idlist undefined
            idlist = query_reroll(query_input, vectordb, idlist if 'idlist' in locals() else [], sources.split(",") if sources else [])
            print(idlist)
        if del_requery:
            print("del input:"+del_input)
            del_index(del_input, vectordb)

    if page == "CreateDB":
        dirname = st.text_input("Enter the name for sub-folder to house the ChromaDB you would like to create.", '', key=1)
        DIRECTORY = f"./databases/{dirname}/"
        LIBRARY = st.text_input("What is the name of the Zotero BetterBibtex library folder you would like to use for this database?", key=5)
        createdb = st.button("CreateDB", type="primary")
        if createdb:
            process.main(LIBRARY, DIRECTORY, OPENAI_API_KEY)


if __name__ == '__main__':
    main()
