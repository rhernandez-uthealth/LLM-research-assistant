import numpy as np
import chromadb
from chromadb.config import Settings
import spacy
import bibparse
from pypdf import PdfReader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from chromadb.utils import embedding_functions
 

 

from langchain.text_splitter import RecursiveCharacterTextSplitter
from stqdm import stqdm
# Retrieve OpenAI api-key from text file
import re

# PDF reader function
def readPDF(filename):
    reader = PdfReader(filename)
    doctext = ''
    for page in reader.pages:
        pagetext = page.extract_text().replace('\n', ' ').replace('- ', '').strip()
        doctext+=re.sub('\.[a-zA-Z]', '\. ', pagetext).replace('  ', '').replace('[ ', '[')
    return doctext

def format_chunks(chunklist):
    chunks=chunklist
    for i in range(1, len(chunks)):
        if chunks[i-1].endswith('.') is False:
            first = chunks[i].split('. ')[0]
            chunks[i]=chunks[i].replace(first, '').lstrip('. ')
            chunks[i-1]=chunks[i-1]+first+'.'
    return chunks


# text_splitter = RecursiveCharacterTextSplitter(chunk_size=600)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=700)

# Functions for reducing chunks containing irrelevant information using Spacy natural language processing
# /// English-language nlp model to categorize textual content
nlp = spacy.load('en_core_web_sm')


# /// Count the number of sentence-entities recognized as "persons" or "organizations"; (ents)
def ent_count(chunk):
    sents = nlp(chunk)
    ents = sents.ents
    entity_count=len([e for e in ents if e.label_=="PERSON"])+len([e for e in ents if e.label_=="ORG"])
    return entity_count

# /// Reduce the initial list of chunks with counts of persons/organizations higher than the mean counts of persons/organizations+ 1 standard-deviation of counts among all documents' chunks
# // (ents) > (mean(ents)+1*standard-deviation(ents))
def ent_cutoff(chunks):
    ent_count_list=[ent_count(chunk) for chunk in chunks]
    cutlevel = np.mean(ent_count_list)+np.std(ent_count_list)
    filtered = [chunk for chunk in chunks if ent_count(chunk)<cutlevel]
    return filtered

def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)


    
    
def main(project_name, DIRECTORY, OPENAI_API_KEY):
    print("Enter the name of the Zotero library export (using Better-Bibtext)")
    bibdata = bibparse.main(project_name)
    embeddings=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002")
    import re
    import pandas as pd
    allchunks=[]
    allmeta = []
    for i in stqdm(range(0, len(bibdata))):
        meta = bibdata[i]
        print(meta['source'], meta['file_path'])
        metadata=[]
        ids=[]
        filepath = './zotero_libraries/{}'
        text = readPDF(meta['file_path'])
        text_re = ''.join(re.split(r'Abstract', text, flags=re.IGNORECASE)[1:])
        text_re = ''.join(re.split(r'References', text_re, flags=re.IGNORECASE)[:-1])
        if len(str(text_re))>5000:
            text=text_re
        chunks = text_splitter.split_text(text)
        chunks=format_chunks(chunks)
        print(len(text), len(chunks))
        # reduced_chunks = ent_cutoff(chunks)
        # print("orig chunks:"+str(len(chunks)))
        # omissions = []
        for n, chunk in enumerate(chunks):
            meta['text']=chunks[n]
            idnum="ID-{}-{}".format(str(i),str(n))
            meta['id'] = idnum
            ids.append(idnum)
            metadata.append(dict(meta)) 
        # omissions = []
        # for index, value in enumerate(chunks):
        #     if value not in reduced_chunks:
        #         omissions.append(index)
        # delete_multiple_element(chunks, omissions)
        # delete_multiple_element(metadata, omissions)
        # delete_multiple_element(ids, omissions)

        # print("reduced chunks:"+str(len(chunks)))
        # allmeta.append(metadata)
        # allchunks.append(chunks)
        # for index, value in enumerate(chunks):
        #     if value not in reduced_chunks:
        #         omissions.append(index)
        # delete_multiple_element(chunks, omissions)
        # delete_multiple_element(metadata, omissions)
        # chunks=format_chunks(chunks)

        vector_index = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings, 
            persist_directory=DIRECTORY, 
            metadatas=metadata,
            ids=ids
            )
    print("Database created from {} at {}".format(len(bibdata), DIRECTORY))